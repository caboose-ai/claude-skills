#!/usr/bin/env python3
"""Print a safe, high-signal repository inventory for code pattern analysis."""

from __future__ import annotations

import argparse
import os
from collections import Counter
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".next",
    ".nuxt",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",
    "coverage",
    "__pycache__",
    ".turbo",
    ".parcel-cache",
}

SECRET_HINTS = {
    ".env",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    "id_rsa",
    "id_ed25519",
    "secret",
    "secrets",
    "credential",
    "credentials",
    "token",
}

CONFIG_NAMES = {
    ".eslintrc",
    ".eslintrc.js",
    ".eslintrc.json",
    ".eslintrc.yml",
    "eslint.config.js",
    "eslint.config.mjs",
    "eslint.config.ts",
    ".prettierrc",
    ".prettierrc.js",
    ".prettierrc.json",
    "prettier.config.js",
    "prettier.config.mjs",
    ".editorconfig",
    "biome.json",
    "biome.jsonc",
    "rustfmt.toml",
    ".rustfmt.toml",
    "pyproject.toml",
    "setup.cfg",
    ".flake8",
    ".pylintrc",
    "ruff.toml",
    ".ruff.toml",
    ".stylelintrc",
    ".stylelintrc.json",
    "tsconfig.json",
    "jsconfig.json",
    "package.json",
    "go.mod",
    "Cargo.toml",
    "Makefile",
    "justfile",
    "Taskfile.yml",
    "mise.toml",
    ".tool-versions",
}


def is_secretish(path: Path) -> bool:
    lowered = str(path).lower()
    return any(hint in lowered for hint in SECRET_HINTS)


DOTDIR_ALLOWLIST = {".github", ".vscode", ".devcontainer"}


def should_skip_dir(path: Path) -> bool:
    if path.name in SKIP_DIRS:
        return True
    if is_secretish(path):
        return True
    if path.name.startswith(".") and path.name not in DOTDIR_ALLOWLIST:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Repository inventory for pattern analysis")
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    parser.add_argument("--scope", default=None, help="subdirectory to scope analysis to")
    parser.add_argument("--max-files", type=int, default=500)
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    if args.scope:
        scope_path = Path(args.scope)
        if scope_path.is_absolute() or ".." in scope_path.parts:
            raise SystemExit(f"--scope must be a relative path within the repo: {args.scope}")
        scan_root = (root / scope_path).resolve()
        if not scan_root.is_relative_to(root):
            raise SystemExit(f"--scope escapes repository root: {args.scope}")
    else:
        scan_root = root
    if not scan_root.is_dir():
        raise SystemExit(f"scope directory not found: {scan_root}")

    scope_label = args.scope or "entire repository"
    print(f"# Repo inventory: {root}")
    print(f"# Scope: {scope_label}")
    print()

    # Top-level entries
    print("## Top-level entries")
    for child in sorted(scan_root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        if is_secretish(child):
            suffix = "/" if child.is_dir() else ""
            print(f"- {child.name}{suffix} [redacted]")
            continue
        suffix = "/" if child.is_dir() else ""
        print(f"- {child.name}{suffix}")

    # Config and tooling files
    print()
    print("## Config & tooling files")
    config_found = []
    for dirpath, dirnames, filenames in os.walk(scan_root):
        current = Path(dirpath)
        dirnames[:] = [d for d in dirnames if not should_skip_dir(current / d)]
        for filename in sorted(filenames):
            if filename in CONFIG_NAMES:
                path = current / filename
                if not is_secretish(path):
                    config_found.append(path.relative_to(root).as_posix())
    for cf in config_found[:50]:
        print(f"- {cf}")
    if len(config_found) > 50:
        print(f"- ... truncated ({len(config_found)} total)")

    # File extension statistics
    print()
    print("## File extensions (by count)")
    ext_counts: Counter[str] = Counter()
    total_files = 0
    max_files = args.max_files
    for dirpath, dirnames, filenames in os.walk(scan_root):
        current = Path(dirpath)
        dirnames[:] = [d for d in dirnames if not should_skip_dir(current / d)]
        for filename in filenames:
            path = current / filename
            if is_secretish(path):
                continue
            ext = path.suffix or "[none]"
            ext_counts[ext] += 1
            total_files += 1
            if total_files >= max_files:
                break
        if total_files >= max_files:
            dirnames.clear()
            break
    if total_files >= max_files:
        print(f"(capped at {max_files} files)")
    print(f"Total files: {total_files}")
    for ext, count in ext_counts.most_common(30):
        pct = (count / total_files * 100) if total_files else 0
        print(f"- {ext}: {count} ({pct:.1f}%)")

    # Directory depth and size
    print()
    print("## Directory structure (depth 2)")
    depth_limit = 2
    for dirpath, dirnames, filenames in os.walk(scan_root):
        current = Path(dirpath)
        rel = current.relative_to(scan_root)
        depth = len(rel.parts)
        if depth > depth_limit:
            dirnames.clear()
            continue
        dirnames[:] = sorted(d for d in dirnames if not should_skip_dir(current / d))
        if depth == 0:
            continue
        file_count = len([f for f in filenames if not is_secretish(current / f)])
        indent = "  " * (depth - 1)
        print(f"{indent}- {current.name}/ ({file_count} files, {len(dirnames)} subdirs)")

    # Sample files by extension (for pattern analysis)
    print()
    print("## Sample source files (up to 10 per major extension)")
    major_exts = [ext for ext, _ in ext_counts.most_common(8) if ext in {
        ".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java",
        ".rb", ".swift", ".kt", ".cs", ".vue", ".svelte", ".astro",
    }]
    for ext in major_exts:
        print(f"\n### {ext}")
        count = 0
        for dirpath, dirnames, filenames in os.walk(scan_root):
            current = Path(dirpath)
            dirnames[:] = [d for d in dirnames if not should_skip_dir(current / d)]
            for filename in sorted(filenames):
                if Path(filename).suffix == ext and not is_secretish(current / filename):
                    print(f"- {(current / filename).relative_to(root).as_posix()}")
                    count += 1
                    if count >= 10:
                        break
            if count >= 10:
                break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
