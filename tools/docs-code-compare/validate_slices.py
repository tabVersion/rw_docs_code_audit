#!/usr/bin/env python3
"""
Validate slices.yml for drift (schema + referenced path existence).

Intended usage:
  python3 tools/docs-code-compare/validate_slices.py \
    --code-repo-root work/risingwave \
    --docs-repo-root work/risingwave-docs
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Issue:
    level: str  # "ERROR" or "WARN"
    message: str


def _is_glob(s: str) -> bool:
    return "*" in s or "?" in s or ("[" in s and "]" in s)


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Top-level YAML must be a mapping/object")
    return raw


def _expect_list_of_str(x: Any) -> bool:
    return isinstance(x, list) and all(isinstance(i, str) for i in x)


def _check_scope_paths(
    issues: list[Issue],
    *,
    label: str,
    repo_root: Path,
    slice_id: str,
    scope_list: list[str],
) -> None:
    for scope in scope_list:
        if _is_glob(scope):
            continue
        p = repo_root / scope
        if not p.exists():
            issues.append(Issue("WARN", f"{slice_id}: {label} path not found: {scope} (resolved: {p})"))


def validate(
    slices_yml: Path,
    *,
    code_repo_root: Path,
    docs_repo_root: Path,
) -> list[Issue]:
    issues: list[Issue] = []
    raw = _load_yaml(slices_yml)

    if raw.get("schema_version") != 1:
        issues.append(Issue("ERROR", f"Unsupported schema_version: {raw.get('schema_version')!r} (expected 1)"))

    slices = raw.get("slices", [])
    if not isinstance(slices, list) or not slices:
        issues.append(Issue("ERROR", "slices must be a non-empty list"))
        return issues

    seen: set[str] = set()
    for s in slices:
        if not isinstance(s, dict):
            issues.append(Issue("ERROR", f"slice entry must be a mapping/object, got: {type(s)}"))
            continue
        sid = s.get("id")
        if not isinstance(sid, str) or not sid:
            issues.append(Issue("ERROR", f"slice has invalid id: {sid!r}"))
            continue
        if sid in seen:
            issues.append(Issue("ERROR", f"duplicate slice id: {sid}"))
        seen.add(sid)

        for k in ("docs_scopes", "code_scopes", "test_signals"):
            if not _expect_list_of_str(s.get(k)):
                issues.append(Issue("ERROR", f"{sid}: {k} must be a list of strings"))

        if isinstance(s.get("docs_scopes"), list):
            _check_scope_paths(issues, label="docs_scopes", repo_root=docs_repo_root, slice_id=sid, scope_list=s["docs_scopes"])
        if isinstance(s.get("code_scopes"), list):
            _check_scope_paths(issues, label="code_scopes", repo_root=code_repo_root, slice_id=sid, scope_list=s["code_scopes"])
        if isinstance(s.get("test_signals"), list):
            _check_scope_paths(issues, label="test_signals", repo_root=code_repo_root, slice_id=sid, scope_list=s["test_signals"])

    return issues


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Validate slices.yml for drift.")
    ap.add_argument("--slices-yml", default=str(Path(__file__).with_name("slices.yml")))
    ap.add_argument("--code-repo-root", required=True)
    ap.add_argument("--docs-repo-root", required=True)
    ap.add_argument("--fail-on-warn", action="store_true")
    args = ap.parse_args(argv)

    slices_yml = Path(args.slices_yml)
    code_root = Path(args.code_repo_root)
    docs_root = Path(args.docs_repo_root)

    if not slices_yml.exists():
        print(f"ERROR: slices.yml not found: {slices_yml}", file=sys.stderr)
        return 2
    if not code_root.exists():
        print(f"ERROR: code repo root not found: {code_root}", file=sys.stderr)
        return 2
    if not docs_root.exists():
        print(f"ERROR: docs repo root not found: {docs_root}", file=sys.stderr)
        return 2

    issues = validate(slices_yml, code_repo_root=code_root, docs_repo_root=docs_root)
    errors = [i for i in issues if i.level == "ERROR"]
    warns = [i for i in issues if i.level == "WARN"]

    for i in issues:
        print(f"{i.level}: {i.message}")

    if errors:
        return 2
    if args.fail_on_warn and warns:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


