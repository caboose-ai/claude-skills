from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import re
from pathlib import Path
from typing import Iterable


SKIP_DIRS = {
    ".agents",
    ".claude",
    ".codex",
    ".git",
    ".playwright-mcp",
    ".remember",
    ".superpowers",
    "node_modules",
}

SKIP_PARTS = {
    ".env",
    "evidence",
    "testdata/evidence",
}

SKIP_SUFFIXES = {
    ".env",
    ".jsonl",
    ".log",
    ".pid",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
}

URL_KEY_ALIASES = {
    "authentik": "Authentik",
    "forgejo": "Forgejo",
    "woodpecker": "Woodpecker",
    "portainer": "Portainer",
    "grafana": "Grafana",
    "open_webui": "OpenWebUI",
    "mattermost": "Mattermost",
    "dashboard": "Dashboard",
    "dash_alias": "DashAlias",
    "openclaw": "OpenClaw",
    "sonarqube": "SonarQube",
    "ghost": "Ghost",
    "paperclip": "Paperclip",
    "ci": "CI",
}


@dataclasses.dataclass
class Manifest:
    slug: str
    display_name: str
    url_key: str
    compose_services: list[str]
    secrets: list[str]
    configurator: str
    smoke_flow: str
    docs: list[str]
    path: str


@dataclasses.dataclass
class Finding:
    severity: str
    title: str
    refs: list[str]
    detail: str
    fix: str


class Scanner:
    def __init__(self, repo: Path) -> None:
        self.repo = repo.resolve()
        self.scanned: list[str] = []
        self.skipped: list[str] = []

    def rel(self, path: Path) -> str:
        return path.resolve().relative_to(self.repo).as_posix()

    def safe_path(self, path: Path) -> bool:
        try:
            rel = self.rel(path)
        except ValueError:
            return False
        parts = set(Path(rel).parts)
        if parts & SKIP_DIRS:
            return False
        if any(part in rel for part in SKIP_PARTS):
            return False
        if path.name.startswith(".env") or path.suffix in SKIP_SUFFIXES:
            return False
        return True

    def read(self, rel_path: str) -> str:
        path = self.repo / rel_path
        if not path.exists():
            return ""
        if not self.safe_path(path):
            self.skipped.append(rel_path)
            return ""
        self.scanned.append(rel_path)
        return path.read_text(encoding="utf-8", errors="replace")

    def glob(self, pattern: str) -> list[Path]:
        return sorted(p for p in self.repo.glob(pattern) if p.is_file() and self.safe_path(p))


def clean_value(value: str) -> str | list[str]:
    value = value.strip()
    if value == "[]":
        return []
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_manifest(scanner: Scanner, path: Path) -> Manifest:
    rel = scanner.rel(path)
    text = scanner.read(rel)
    data: dict[str, str | list[str] | dict[str, str]] = {}
    current_key = ""
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if re.match(r"^[a-zA-Z_]+:", raw):
            key, _, value = raw.partition(":")
            key = key.strip()
            value = value.strip()
            if value:
                data[key] = clean_value(value)
                current_key = ""
            else:
                data[key] = []
                current_key = key
            continue
        if raw.startswith("  - ") and current_key:
            item = clean_value(raw[4:])
            values = data.setdefault(current_key, [])
            if isinstance(values, list) and isinstance(item, str):
                values.append(item)
            continue
        if raw.startswith("  ") and current_key:
            key, _, value = raw.strip().partition(":")
            values = data.setdefault(current_key, {})
            if isinstance(values, dict):
                values[key] = str(clean_value(value))

    slug = str(data.get("slug") or path.parent.name)
    return Manifest(
        slug=slug,
        display_name=str(data.get("display_name") or slug),
        url_key=str(data.get("url_key") or ""),
        compose_services=list(data.get("compose_services") or []),
        secrets=list(data.get("secrets") or []),
        configurator=str(data.get("configurator") or ""),
        smoke_flow=str(data.get("smoke_flow") or ""),
        docs=list(data.get("docs") or []),
        path=rel,
    )


def parse_compose_services(text: str) -> set[str]:
    services: set[str] = set()
    in_services = False
    for line in text.splitlines():
        if line.strip() == "services:":
            in_services = True
            continue
        if in_services and line and not line.startswith(" "):
            break
        match = re.match(r"^  ([A-Za-z0-9_.-]+):\s*$", line)
        if in_services and match:
            services.add(match.group(1))
    return services


def function_body(text: str, name: str) -> str:
    start = text.find(f"func {name}")
    if start == -1:
        return ""
    end = text.find("\nfunc ", start + 1)
    return text[start:] if end == -1 else text[start:end]


def line_ref(scanner: Scanner, rel_path: str, pattern: str) -> str:
    text = scanner.read(rel_path)
    for index, line in enumerate(text.splitlines(), start=1):
        if pattern in line:
            return f"{rel_path}:{index}"
    return rel_path


def extract_specs(body: str) -> dict[str, str]:
    specs: dict[str, str] = {}
    for match in re.finditer(r'Name:\s*"([^"]+)".*?Slug:\s*"([^"]+)"', body):
        specs[match.group(2)] = match.group(1)
    return specs


def extract_flow_names(body: str) -> set[str]:
    return set(re.findall(r'Name:\s*"([^"]+)"', body))


def parse_service_links(urls_text: str) -> dict[str, str]:
    links: dict[str, str] = {}
    for match in re.finditer(r'Name:\s*"([^"]+)".*?URL:\s*u\.([A-Za-z0-9]+)', urls_text):
        links[match.group(1)] = match.group(2)
    return links


def parse_dashboard_exclusions(builder_text: str) -> set[str]:
    body = function_body(builder_text, "showInSSODashboard")
    exclusions: set[str] = set()
    for case_line in re.findall(r"case ([^\n]+):\n\s*return false", body):
        exclusions.update(re.findall(r'"([^"]+)"', case_line))
    return exclusions


def parse_configurator_slugs(scanner: Scanner) -> dict[str, str]:
    slugs: dict[str, str] = {}
    for path in scanner.glob("services/*/*.go"):
        if path.name.endswith("_test.go"):
            continue
        text = scanner.read(scanner.rel(path))
        match = re.search(r'Slug\(\) string \{ return "([^"]+)" \}', text)
        if match:
            slugs[match.group(1)] = scanner.rel(path)
    return slugs


def parse_builder_slugs(builder_text: str) -> set[str]:
    imports: dict[str, str] = {}
    for match in re.finditer(r'(?m)^\s*(?:(\w+)\s+)?"github.com/caboose-ai/caboose-ai.io/services/([^"]+)"', builder_text):
        alias, slug = match.groups()
        imports[alias or slug] = slug
    slugs: set[str] = set()
    for alias in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\.New\(", builder_text):
        if alias in imports:
            slugs.add(imports[alias])
    return slugs


def url_field_for_key(url_key: str) -> str:
    return URL_KEY_ALIASES.get(url_key, "")


def dashboard_status(manifest: Manifest, service_links: dict[str, str], exclusions: set[str]) -> str:
    if manifest.display_name not in service_links:
        return "-"
    if manifest.display_name in exclusions:
        return "hidden"
    if manifest.display_name == "Open WebUI":
        return "shown (OIDC login URL)"
    return "shown"


def sso_status(
    manifest: Manifest,
    provider_specs: dict[str, str],
    proxy_specs: dict[str, str],
) -> str:
    if manifest.slug == "authentik":
        return "identity provider"
    if manifest.slug in provider_specs:
        return f"oidc provider: {provider_specs[manifest.slug]}"
    proxy_by_service = {
        "woodpecker": "ci-proxy",
        "homarr": "dashboard",
        "openclaw": "openclaw-proxy",
        "ghost": "ghost-proxy",
        "paperclip": "paperclip-proxy",
    }
    proxy_slug = proxy_by_service.get(manifest.slug)
    if proxy_slug and proxy_slug in proxy_specs:
        return f"proxy: {proxy_specs[proxy_slug]}"
    if manifest.slug == "social":
        return "social sources"
    if manifest.configurator:
        return "local/service auth"
    return "-"


def smoke_status(
    manifest: Manifest,
    oauth_flows: set[str],
    proxy_flows: set[str],
    provider_specs: dict[str, str],
    proxy_specs: dict[str, str],
) -> str:
    if manifest.slug in oauth_flows or manifest.smoke_flow in oauth_flows:
        return "browser oauth"
    if manifest.slug == "woodpecker" and "ci" in proxy_flows:
        return "browser proxy (ci)"
    if manifest.slug in proxy_flows:
        return "browser proxy"
    if manifest.slug in provider_specs:
        return "config only"
    proxy_by_service = {
        "homarr": "dashboard",
        "openclaw": "openclaw-proxy",
        "ghost": "ghost-proxy",
        "paperclip": "paperclip-proxy",
    }
    if proxy_by_service.get(manifest.slug) in proxy_specs:
        return "proxy config only"
    if manifest.slug == "authentik":
        return "config and health"
    if manifest.slug == "social":
        return "source config only"
    return "-"


def docs_status(scanner: Scanner, manifest: Manifest) -> str:
    if not manifest.docs:
        return "-"
    missing: list[str] = []
    for doc in manifest.docs:
        path = scanner.repo / "services" / manifest.slug / doc
        if not path.exists():
            missing.append(doc)
    return "ok" if not missing else "missing " + ", ".join(missing)


def build_audit(scanner: Scanner) -> tuple[str, list[str]]:
    manifests = [parse_manifest(scanner, path) for path in scanner.glob("services/*/service.yaml")]
    manifests.sort(key=lambda item: item.slug)

    compose_text = scanner.read("dev/homelab/docker-compose.yml")
    builder_text = scanner.read("internal/servicebuilder/builder.go")
    providers_text = scanner.read("internal/install/providers.go")
    outpost_text = scanner.read("internal/install/outpost.go")
    urls_text = scanner.read("internal/config/urls.go")
    flows_text = scanner.read("internal/smoketest/flows.go")
    service_command_text = scanner.read("internal/cli/service_command.go")
    scanner.read("README.md")
    scanner.read("CLAUDE.md")
    for path in scanner.glob("docs/*.md"):
        if path.name != "homelab-architecture-audit.md":
            scanner.read(scanner.rel(path))

    compose_services = parse_compose_services(compose_text)
    provider_specs = extract_specs(function_body(providers_text, "DefaultProviderSpecs"))
    proxy_specs = extract_specs(function_body(outpost_text, "DefaultProxySpecs"))
    oauth_flows = extract_flow_names(function_body(flows_text, "OAuthServiceFlows"))
    proxy_flows = extract_flow_names(function_body(flows_text, "ProxyFlows"))
    service_links = parse_service_links(function_body(urls_text, "(u URLs) ServiceLinks"))
    dashboard_exclusions = parse_dashboard_exclusions(builder_text)
    configurator_slugs = parse_configurator_slugs(scanner)
    builder_slugs = parse_builder_slugs(builder_text)

    findings = collect_findings(
        scanner,
        manifests,
        compose_services,
        provider_specs,
        proxy_specs,
        oauth_flows,
        proxy_flows,
        service_links,
        dashboard_exclusions,
        configurator_slugs,
        builder_slugs,
        service_command_text,
    )

    active_service_names = ", ".join(m.display_name for m in manifests)
    report = render_report(
        scanner,
        manifests,
        compose_services,
        provider_specs,
        proxy_specs,
        oauth_flows,
        proxy_flows,
        service_links,
        dashboard_exclusions,
        configurator_slugs,
        builder_slugs,
        findings,
        active_service_names,
    )
    return report, scanner.scanned


def collect_findings(
    scanner: Scanner,
    manifests: list[Manifest],
    compose_services: set[str],
    provider_specs: dict[str, str],
    proxy_specs: dict[str, str],
    oauth_flows: set[str],
    proxy_flows: set[str],
    service_links: dict[str, str],
    dashboard_exclusions: set[str],
    configurator_slugs: dict[str, str],
    builder_slugs: set[str],
    service_command_text: str,
) -> list[Finding]:
    findings: list[Finding] = []
    manifest_by_slug = {m.slug: m for m in manifests}

    missing_compose = {
        m.slug: [svc for svc in m.compose_services if svc not in compose_services]
        for m in manifests
    }
    missing_compose = {slug: services for slug, services in missing_compose.items() if services}
    if missing_compose:
        detail = "; ".join(f"{slug}: {', '.join(services)}" for slug, services in missing_compose.items())
        refs = [manifest_by_slug[slug].path for slug in missing_compose]
        refs.append("dev/homelab/docker-compose.yml")
        findings.append(
            Finding(
                "High",
                "Manifest compose services are missing from Compose",
                refs,
                detail,
                "Either add the missing compose service definitions or mark the service as external in a documented manifest field.",
            )
        )

    configurator_missing = [
        m for m in manifests if m.configurator and m.configurator not in configurator_slugs
    ]
    configurator_not_built = [
        m for m in manifests if m.configurator and m.configurator in configurator_slugs and m.configurator not in builder_slugs
    ]
    if configurator_missing or configurator_not_built:
        detail_parts = []
        if configurator_missing:
            detail_parts.append("missing implementation: " + ", ".join(m.slug for m in configurator_missing))
        if configurator_not_built:
            detail_parts.append("not built: " + ", ".join(m.slug for m in configurator_not_built))
        findings.append(
            Finding(
                "High",
                "Configurator manifests do not match servicebuilder",
                ["internal/servicebuilder/builder.go"] + [m.path for m in configurator_missing + configurator_not_built],
                "; ".join(detail_parts),
                "Keep manifest configurator slugs, ServiceConfigurator.Slug values, and servicebuilder.Build registration in one change.",
            )
        )

    smoke_gaps = []
    for m in manifests:
        if not m.smoke_flow:
            continue
        status = smoke_status(m, oauth_flows, proxy_flows, provider_specs, proxy_specs)
        if status in {"-", "config only", "proxy config only", "source config only"}:
            smoke_gaps.append(f"{m.slug} ({status})")
    if smoke_gaps:
        refs = ["internal/smoketest/flows.go"] + [m.path for m in manifests if m.slug in {g.split()[0] for g in smoke_gaps}]
        findings.append(
            Finding(
                "Medium",
                "Several manifest smoke flows are not backed by browser flow coverage",
                refs,
                ", ".join(smoke_gaps),
                "Add matching smoke flow definitions or downgrade manifest smoke_flow values to the actual config-only coverage they receive.",
            )
        )

    if '"TestSSO_Config"' in service_command_text:
        findings.append(
            Finding(
                "High",
                "Per-service smoke command ignores the manifest smoke_flow value",
                [line_ref(scanner, "internal/cli/service_command.go", "TestSSO_Config")],
                "`homelab service <slug> smoke` runs the same config test for every service instead of selecting the manifest's declared flow.",
                "Route manifest smoke_flow to a flow-specific test or make the command explicit that it is a config-only SSO check.",
            )
        )

    linked_names = set(service_links)
    manifest_names = {m.display_name for m in manifests}
    removed_exclusions = dashboard_exclusions - linked_names - manifest_names
    if removed_exclusions:
        findings.append(
            Finding(
                "Medium",
                "Dashboard filtering contains stale removed-service entries",
                [line_ref(scanner, "internal/servicebuilder/builder.go", "showInSSODashboard")],
                f"{len(removed_exclusions)} exclusion entry no longer maps to a service manifest or service link.",
                "Move dashboard visibility into service manifests or prune stale hard-coded exclusions during service removal.",
            )
        )

    if service_links:
        findings.append(
            Finding(
                "Medium",
                "Service metadata is duplicated across manifests, URLs, and dashboard filtering",
                [
                    "services/*/service.yaml",
                    line_ref(scanner, "internal/config/urls.go", "ServiceLinks"),
                    line_ref(scanner, "internal/servicebuilder/builder.go", "showInSSODashboard"),
                ],
                "URL keys, display names, dashboard visibility, provider specs, and manifest docs are maintained in separate files.",
                "Promote URL/dashboard/SSO attributes into the service manifest or generate derived tables from one registry.",
            )
        )

    risky_refs = [
        line_ref(scanner, "services/homarr/homarr.go", "ensureDefaultBoard"),
        line_ref(scanner, "internal/install/install.go", "func (inst *Installer) Reset"),
    ]
    findings.append(
        Finding(
            "Medium",
            "Live-state mutation paths need durable approval guardrails",
            risky_refs,
            "Homarr board seeding mutates SQLite through Docker exec and reset removes secrets/env-derived state.",
            "Use hooks or command wrappers to require explicit confirmation before live DB, secret, reset, or destructive Docker paths.",
        )
    )

    doc_mentions = []
    for rel in ["README.md", "CLAUDE.md"]:
        text = scanner.read(rel)
        for m in manifests:
            if m.display_name in text or m.slug in text:
                break
        else:
            doc_mentions.append(rel)
    if doc_mentions:
        findings.append(
            Finding(
                "Low",
                "Top-level docs do not mention any active service names",
                doc_mentions,
                "No active service names were detected in one or more top-level docs.",
                "Refresh docs from the service manifest registry.",
            )
        )

    order = {"High": 0, "Medium": 1, "Low": 2, "Info": 3}
    findings.sort(key=lambda finding: (order.get(finding.severity, 99), finding.title))
    return findings


def render_report(
    scanner: Scanner,
    manifests: list[Manifest],
    compose_services: set[str],
    provider_specs: dict[str, str],
    proxy_specs: dict[str, str],
    oauth_flows: set[str],
    proxy_flows: set[str],
    service_links: dict[str, str],
    dashboard_exclusions: set[str],
    configurator_slugs: dict[str, str],
    builder_slugs: set[str],
    findings: list[Finding],
    active_service_names: str,
) -> str:
    date = dt.datetime.now(dt.UTC).date().isoformat()
    lines: list[str] = [
        "# Homelab Architecture Audit",
        "",
        f"Repository: `{scanner.repo}`",
        f"Generated: `{date}`",
        "",
        "## Executive Summary",
        "",
        "This read-only audit checks the current homelab service surface across service manifests, Docker Compose, servicebuilder registration, Authentik provider/proxy specs, dashboard inclusion, smoke-test flows, and docs.",
        "",
        f"Active service manifests: {active_service_names}.",
        "",
        f"Findings: {sum(1 for f in findings if f.severity == 'High')} high, {sum(1 for f in findings if f.severity == 'Medium')} medium, {sum(1 for f in findings if f.severity == 'Low')} low.",
        "",
        "## Service Matrix",
        "",
        "| Service | Compose | Configurator | URL key | SSO | Smoke | Dashboard | Docs |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for manifest in manifests:
        missing = [svc for svc in manifest.compose_services if svc not in compose_services]
        compose = "ok"
        if missing:
            compose = "missing " + ", ".join(missing)
        elif not manifest.compose_services:
            compose = "-"
        configurator = "-"
        if manifest.configurator:
            if manifest.configurator in configurator_slugs and manifest.configurator in builder_slugs:
                configurator = "built"
            elif manifest.configurator in configurator_slugs:
                configurator = "implemented, not built"
            else:
                configurator = "missing"
        url_key = manifest.url_key or "-"
        if manifest.url_key and not url_field_for_key(manifest.url_key):
            url_key += " (unknown)"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{manifest.slug}`",
                    compose,
                    configurator,
                    url_key,
                    sso_status(manifest, provider_specs, proxy_specs),
                    smoke_status(manifest, oauth_flows, proxy_flows, provider_specs, proxy_specs),
                    dashboard_status(manifest, service_links, dashboard_exclusions),
                    docs_status(scanner, manifest),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Findings",
            "",
        ]
    )
    for index, finding in enumerate(findings, start=1):
        refs = ", ".join(f"`{ref}`" for ref in finding.refs)
        lines.extend(
            [
                f"### {index}. {finding.severity}: {finding.title}",
                "",
                f"- References: {refs}",
                f"- Detail: {finding.detail}",
                f"- Suggested fix: {finding.fix}",
                "",
            ]
        )

    lines.extend(
        [
            "## Automation Recommendations",
            "",
            "### Hooks",
            "",
            "- Add a stop-point branch/scope hook for edits touching `services/*/service.yaml`, `dev/homelab/docker-compose.yml`, `internal/servicebuilder`, `internal/install/providers.go`, `internal/install/outpost.go`, or `internal/smoketest/flows.go`.",
            "- Add a pre-tool safety hook that blocks `.env`, generated smoke evidence, screenshots, logs, JSONL, and live-state mutation commands unless the user explicitly asks for them.",
            "",
            "### Skills",
            "",
            "- Use `homelab-architecture-auditor` before and after service additions/removals or SSO/dashboard changes.",
            "- Keep `repo-agent-guidance-generator` for broader AGENTS/CLAUDE guidance refreshes; use this audit when the question is service architecture consistency.",
            "",
            "### Subagents",
            "",
            "- Service-contract reviewer: check manifest, compose, URL, provider/proxy, servicebuilder, smoke, and docs changes as one unit.",
            "- SSO-smoke reviewer: inspect Authentik provider/proxy flows and browser smoke coverage after login-path changes.",
            "",
            "### MCPs",
            "",
            "- GitHub MCP for PR/check triage and review-thread resolution on architecture changes.",
            "- Playwright MCP for browser verification when a service login or dashboard route changes.",
            "",
            "## Scanner Safety",
            "",
            f"- Files read: {len(set(scanner.scanned))}",
            "- Scope: whitelisted repo source, docs, manifests, and compose files only.",
            "- Excluded: `.env` files, generated smoke evidence, screenshots, logs, JSONL evidence, local agent/editor state, and live Docker/Authentik state.",
            "",
            "## Validation Commands",
            "",
            "```bash",
            f"uv run python {Path(__file__).resolve().as_posix()} . --check-safety",
            "go test ./internal/servicebuilder ./services/homarr",
            "git diff --check",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def forbidden_paths(paths: Iterable[str]) -> list[str]:
    forbidden = []
    for path in paths:
        if path.startswith(".env") or "/.env" in path or "testdata/evidence" in path:
            forbidden.append(path)
        elif Path(path).suffix in SKIP_SUFFIXES:
            forbidden.append(path)
    return forbidden


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit caboose-ai.io homelab architecture consistency.")
    parser.add_argument("repo", nargs="?", default=".", help="Path to the caboose-ai.io repository")
    parser.add_argument("--output", help="Write Markdown report to this path")
    parser.add_argument("--list-scanned-files", action="store_true", help="Print scanned file paths and exit")
    parser.add_argument("--check-safety", action="store_true", help="Fail if forbidden file paths were scanned")
    args = parser.parse_args()

    scanner = Scanner(Path(args.repo))
    report, scanned = build_audit(scanner)

    if args.list_scanned_files:
        print("\n".join(sorted(set(scanned))))
        return 0

    if args.check_safety:
        bad = forbidden_paths(scanned)
        if bad:
            print("Forbidden files were scanned:")
            print("\n".join(sorted(set(bad))))
            return 1
        print(f"OK: scanned {len(set(scanned))} safe files; no .env, generated evidence, logs, screenshots, or JSONL files were read.")
        return 0

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        print(output)
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
