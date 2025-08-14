#!/usr/bin/env python3
"""
Simple prompt versioning helper.
Modes:
- create_new: create prompts/vX.md from prompts/template.md (auto-increment if version not provided)
- use_existing: switch used_version to an existing prompts/vX.md

Usage (local):
  python scripts/prompt_versioning.py --mode create_new --last-updated-by you --reason "New experiment"
  python scripts/prompt_versioning.py --mode use_existing --version v2 --last-updated-by you --reason "Rollback"

This script does not push by itself locally; in CI it will commit and push.
"""
from __future__ import annotations
import argparse
import json
import os
import re
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "prompts"
META_FILE = PROMPTS_DIR / "meta.json"
TEMPLATE_FILE = PROMPTS_DIR / "template.md"

VERSION_PATTERN = re.compile(r"^v(\d+)$")


def read_meta() -> dict:
    if META_FILE.exists():
        return json.loads(META_FILE.read_text())
    return {"used_version": "v1", "last_updated_by": "", "reason": ""}


def write_meta(used_version: str, last_updated_by: str, reason: str) -> None:
    META_FILE.write_text(
        json.dumps(
            {
                "used_version": used_version,
                "last_updated_by": last_updated_by,
                "reason": reason,
            },
            indent=2,
        )
        + "\n"
    )


def list_versions() -> list[str]:
    versions = []
    for p in PROMPTS_DIR.glob("v*.md"):
        name = p.stem
        if VERSION_PATTERN.match(name):
            versions.append(name)
    return sorted(versions, key=lambda v: int(VERSION_PATTERN.match(v).group(1)))


def next_version_label() -> str:
    versions = list_versions()
    if not versions:
        return "v1"
    last = versions[-1]
    n = int(VERSION_PATTERN.match(last).group(1))
    return f"v{n+1}"


def create_new(version: str | None, last_by: str, reason: str, prompt_content: str | None = None) -> str:
    if version is None:
        version = next_version_label()
    if not VERSION_PATTERN.match(version):
        raise ValueError("version must match pattern v<number>, e.g., v3")
    target = PROMPTS_DIR / f"{version}.md"
    if target.exists():
        raise FileExistsError(f"{target} already exists")

    if prompt_content:
        content = prompt_content
    else:
        content = TEMPLATE_FILE.read_text() if TEMPLATE_FILE.exists() else "# New Prompt\n\nWrite guidance here.\n"
    target.write_text(content)

    write_meta(version, last_by, reason)
    return version


def use_existing(version: str, last_by: str, reason: str) -> str:
    if not VERSION_PATTERN.match(version):
        raise ValueError("version must match pattern v<number>, e.g., v3")
    target = PROMPTS_DIR / f"{version}.md"
    if not target.exists():
        raise FileNotFoundError(f"{target} not found")

    write_meta(version, last_by, reason)
    return version


def git_commit_and_push(message: str) -> None:
    # Commit and push in CI when GITHUB_ACTIONS is set
    if os.getenv("GITHUB_ACTIONS") != "true":
        return
    subprocess.run(["git", "config", "user.name", os.getenv("GIT_USER_NAME", "gha-bot")], check=True)
    subprocess.run(["git", "config", "user.email", os.getenv("GIT_USER_EMAIL", "gha-bot@users.noreply.github.com")], check=True)
    subprocess.run(["git", "add", "prompts"], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["create_new", "use_existing"], required=True)
    parser.add_argument("--version", help="vX label; optional for create_new; required for use_existing")
    parser.add_argument("--last-updated-by", dest="last_by", required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()

    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

    if args.mode == "create_new":
        prompt_content = os.getenv("PROMPT_CONTENT")
        version = create_new(args.version, args.last_by, args.reason, prompt_content)
        msg = f"chore(prompts): create {version} by {args.last_by} — {args.reason}"
        print(msg)
        git_commit_and_push(msg)
    else:
        if not args.version:
            raise SystemExit("--version is required for use_existing")
        version = use_existing(args.version, args.last_by, args.reason)
        msg = f"chore(prompts): switch to {version} by {args.last_by} — {args.reason}"
        print(msg)
        git_commit_and_push(msg)


if __name__ == "__main__":
    main()
