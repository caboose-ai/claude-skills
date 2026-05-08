#!/usr/bin/env python3
"""Print a safe, high-signal repository inventory for agent guidance work."""

from __future__ import annotations

import argparse
import os
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

IMPORTANT_NAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "README.md",
    "Makefile",
    "justfile",
    "mise.toml",
    "package.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "package-lock.json",
    "go.mod",
    "go.sum",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "Cargo.lock",
    "Dockerfile",
    "docker-compose.yml",
    "compose.yml",
    "Taskfile.yml",
}

IMPORTANT_SUFFIXES = {
    ".github/workflows",
    ".github/copilot-instructions.md",
}


def is_secretish(path: Path) -> bool:
    lowered = str(path).lower()
    return any(hint in lowered for hint in SECRET_HINTS)


def should_skip_dir(path: Path) -> bool:
    return path.name in SKIP_DIRS or is_secretish(path)


def is_important(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    return path.name in IMPORTANT_NAMES or any(rel.startswith(s) for s in IMPORTANT_SUFFIXES)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    parser.add_argument("--max-files", type=int, default=300)
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")

    print(f"# Repo inventory: {root}")
    print()
    print("## Top-level entries")
    for child in sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        if is_secretish(child):
            print(f"- {child.name}/ [redacted secret-like path]" if child.is_dir() else f"- {child.name} [redacted secret-like path]")
            continue
        suffix = "/" if child.is_dir() else ""
        print(f"- {child.name}{suffix}")

    print()
    print("## Important files")
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [d for d in dirnames if not should_skip_dir(current / d)]
        for filename in sorted(filenames):
            path = current / filename
            if is_secretish(path):
                continue
            if is_important(path, root):
                print(f"- {path.relative_to(root).as_posix()}")
                count += 1
                if count >= args.max_files:
                    print(f"- ... truncated at {args.max_files} files")
                    return 0

    print()
    print("## File extensions")
    counts: dict[str, int] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [d for d in dirnames if not should_skip_dir(current / d)]
        for filename in filenames:
            path = current / filename
            if is_secretish(path):
                continue
            ext = path.suffix or "[none]"
            counts[ext] = counts.get(ext, 0) + 1
    for ext, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:30]:
        print(f"- {ext}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
