# Homelab Architecture Audit Checks

## Expected Contracts

- Each `services/<slug>/service.yaml` slug must match its directory.
- Every manifest `compose_services` entry should exist in
  `dev/homelab/docker-compose.yml`, unless the service is intentionally
  external and documented that way.
- A manifest `configurator` should have a matching `ServiceConfigurator.Slug()`
  implementation and be included by `internal/servicebuilder.Build`.
- URL-bearing services should align with `internal/config/urls.go`
  `DeriveURLs` and `ServiceLinks`.
- Native OIDC services should appear in `DefaultProviderSpecs`; forward-auth
  services should appear in `DefaultProxySpecs`.
- Browser smoke coverage should be represented in
  `internal/smoketest/flows.go`, not only in static provider/proxy config tests.
- Dashboard inclusion belongs to one durable source of truth. If filtering stays
  in code, report stale or duplicated metadata.
- Docs and guidance should describe the current active service surface only.

## Safety Rules

- Do not read `.env`, `*.env`, generated smoke evidence, screenshots, logs,
  JSONL evidence, local agent/editor state, or live Docker/Authentik state.
- Treat the audit as read-only unless the user separately asks for fixes.
- Do not print secret values; only report secret key names from manifests or
  source code when needed for contract checks.

## Finding Severity

- High: a declared service surface cannot be exercised or provisioned through
  its documented path.
- Medium: duplicated metadata, partial coverage, or risky mutation paths that
  can drift without guardrails.
- Low: stale generated docs, missing guidance, or polish issues that do not
  block runtime behavior.
