#!/usr/bin/env python3
"""
Run docs-vs-code comparison slices using a configurable Claude Code CLI command.

This runner is designed for CI:
- Pipes the rendered prompt to Claude Code stdin and captures stdout as the report.
- Enforces safe non-interactive defaults: --print, Read/Bash only, bypass permissions, add-dir.
- Parallelizable: one subprocess per slice, controlled by --jobs.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class SliceDef:
    id: str
    name: str
    docs_scopes: list[str]
    code_scopes: list[str]
    test_signals: list[str]
    key_questions: list[str]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _is_glob(s: str) -> bool:
    return "*" in s or "?" in s or ("[" in s and "]" in s)


def _resolve_scopes(root: Path, scopes: list[str], *, keep_relative: bool) -> list[str]:
    if keep_relative:
        return scopes
    out: list[str] = []
    for s in scopes:
        if _is_glob(s):
            out.append(str((root / s)))
        else:
            out.append(str((root / s).resolve()))
    return out


def _render_prompt(
    template: str,
    *,
    slice_id: str,
    slice_name: str,
    code_repo_root: str,
    docs_repo_root: str,
    docs_repo_ref: str,
    product_version: str,
    docs_scopes: list[str],
    code_scopes: list[str],
    test_signals: list[str],
) -> str:
    docs_scopes_md = "\n".join([f"- `{x}`" for x in docs_scopes]) or "- (none)"
    code_scopes_md = "\n".join([f"- `{x}`" for x in code_scopes]) or "- (none)"
    test_signals_md = "\n".join([f"- `{x}`" for x in test_signals]) or "- (none)"

    replacements = {
        "{{slice_id}}": slice_id,
        "{{slice_name}}": slice_name,
        "{{code_repo_root}}": code_repo_root,
        "{{docs_repo_root}}": docs_repo_root,
        "{{docs_repo_ref}}": docs_repo_ref,
        "{{product_version}}": product_version,
        "{{docs_scopes}}": docs_scopes_md,
        "{{code_scopes}}": code_scopes_md,
        "{{test_signals}}": test_signals_md,
    }

    out = template
    for k, v in replacements.items():
        out = out.replace(k, v)
    return out


def _load_slices(yaml_path: Path) -> tuple[dict[str, Any], list[SliceDef]]:
    raw = yaml.safe_load(_read_text(yaml_path))
    defaults = raw.get("defaults", {}) if isinstance(raw, dict) else {}
    slices_raw = raw.get("slices", []) if isinstance(raw, dict) else []

    slices: list[SliceDef] = []
    for s in slices_raw:
        slices.append(
            SliceDef(
                id=str(s["id"]),
                name=str(s["name"]),
                docs_scopes=list(s.get("docs_scopes", [])),
                code_scopes=list(s.get("code_scopes", [])),
                test_signals=list(s.get("test_signals", [])),
                key_questions=list(s.get("key_questions", [])),
            )
        )
    return defaults, slices


def _looks_like_auth_error(stdout: str, stderr: str) -> bool:
    s = (stdout or "") + "\n" + (stderr or "")
    s_low = s.lower()
    if "invalid api key" in s_low and "/login" in s_low:
        return True
    if "unauthorized" in s_low or "not authenticated" in s_low:
        return True
    return False


def _ensure_claude_non_interactive_args(
    base_args: str,
    *,
    code_repo_root: Path,
    docs_repo_root: Path,
) -> str:
    toks = shlex.split(base_args)
    toks_set = set(toks)

    if "-p" not in toks_set and "--print" not in toks_set:
        toks.append("--print")
    if "--output-format" not in toks_set:
        toks.extend(["--output-format", "text"])
    if "--tools" not in toks_set:
        toks.extend(["--tools", "Read,Bash"])
    if "--permission-mode" not in toks_set:
        toks.extend(["--permission-mode", "bypassPermissions"])

    toks.extend(["--add-dir", str(code_repo_root.resolve())])
    toks.extend(["--add-dir", str(docs_repo_root.resolve())])

    return " ".join(shlex.quote(t) for t in toks)


def _preflight_claude(
    claude_cmd: str,
    claude_args: str,
    cwd: Path,
    timeout_s: int,
) -> tuple[bool, str]:
    cmd = [claude_cmd] + shlex.split(claude_args)
    prompt = "Return exactly: OK"
    try:
        proc = subprocess.run(
            cmd,
            input=prompt,
            text=True,
            capture_output=True,
            cwd=str(cwd),
            timeout=max(10, min(timeout_s, 60)),
            check=False,
        )
    except FileNotFoundError as e:
        return False, f"Claude command not found: {claude_cmd!r} ({e})"
    except subprocess.TimeoutExpired:
        return False, "Claude preflight timed out"

    if proc.returncode == 0:
        return True, "ok"
    if _looks_like_auth_error(proc.stdout or "", proc.stderr or ""):
        return False, "Claude Code is not authenticated. Configure auth in CI (see workflow README)."
    return False, f"Claude preflight failed (returncode={proc.returncode})."


def _run_one_slice(
    *,
    slice_def: SliceDef,
    prompt: str,
    out_dir: Path,
    claude_cmd: str,
    claude_args: str,
    cwd: Path,
    timeout_s: int,
) -> dict[str, Any]:
    slice_dir = out_dir / slice_def.id
    slice_dir.mkdir(parents=True, exist_ok=True)

    _write_text(slice_dir / "prompt.txt", prompt)

    cmd = [claude_cmd] + shlex.split(claude_args)
    started_at = time.time()
    proc = subprocess.run(
        cmd,
        input=prompt,
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=timeout_s,
        check=False,
    )
    duration_ms = int((time.time() - started_at) * 1000)

    _write_text(slice_dir / "stdout.txt", proc.stdout or "")
    _write_text(slice_dir / "stderr.txt", proc.stderr or "")
    _write_text(slice_dir / "slice_report.md", proc.stdout or "")

    return {
        "slice_id": slice_def.id,
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "duration_ms": duration_ms,
        "report_path": str((slice_dir / "slice_report.md").resolve()),
        "stderr_path": str((slice_dir / "stderr.txt").resolve()),
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Run slices via Claude Code CLI.")
    ap.add_argument("--slices-yml", default=str(Path(__file__).with_name("slices.yml")))
    ap.add_argument("--template", default=str(Path(__file__).with_name("prompt-claude-slice-template.md")))
    ap.add_argument("--out-dir", default=str(Path("reports") / "local"))
    ap.add_argument("--docs-repo-root", required=True)
    ap.add_argument("--docs-repo-ref", default="main")
    ap.add_argument("--product-version", default="latest")
    ap.add_argument("--code-repo-root", required=True)
    ap.add_argument("--slice-ids", default="", help="Comma-separated slice IDs (default: all)")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 4) // 2))
    ap.add_argument("--timeout-s", type=int, default=1800)
    ap.add_argument("--keep-scopes-relative", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-preflight", action="store_true")

    ap.add_argument("--claude-cmd", default=os.environ.get("CLAUDE_CMD", "claude"))
    ap.add_argument("--claude-args", default=os.environ.get("CLAUDE_ARGS", ""))

    args = ap.parse_args(argv)

    defaults, slices = _load_slices(Path(args.slices_yml))
    template = _read_text(Path(args.template))

    code_root = Path(args.code_repo_root)
    docs_root = Path(args.docs_repo_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    selected_ids = set(x.strip() for x in args.slice_ids.split(",") if x.strip())
    if selected_ids:
        slices = [s for s in slices if s.id in selected_ids]

    effective_claude_args = _ensure_claude_non_interactive_args(
        args.claude_args,
        code_repo_root=code_root,
        docs_repo_root=docs_root,
    )

    run_meta = {
        "started_at": int(time.time()),
        "code_repo_root": str(code_root.resolve()),
        "docs_repo_root": str(docs_root.resolve()),
        "docs_repo_ref": args.docs_repo_ref,
        "product_version": args.product_version,
        "claude_cmd": args.claude_cmd,
        "claude_args": effective_claude_args,
        "jobs": args.jobs,
        "timeout_s": args.timeout_s,
        "slice_ids": [s.id for s in slices],
    }
    _write_text(out_dir / "run.json", json.dumps(run_meta, indent=2) + "\n")

    rendered: dict[str, str] = {}
    for s in slices:
        docs_scopes = _resolve_scopes(docs_root, s.docs_scopes, keep_relative=args.keep_scopes_relative)
        code_scopes = _resolve_scopes(code_root, s.code_scopes, keep_relative=args.keep_scopes_relative)
        test_signals = _resolve_scopes(code_root, s.test_signals, keep_relative=args.keep_scopes_relative)
        rendered[s.id] = _render_prompt(
            template,
            slice_id=s.id,
            slice_name=s.name,
            code_repo_root=str(code_root.resolve()),
            docs_repo_root=str(docs_root.resolve()),
            docs_repo_ref=args.docs_repo_ref,
            product_version=args.product_version,
            docs_scopes=docs_scopes,
            code_scopes=code_scopes,
            test_signals=test_signals,
        )
        _write_text(out_dir / s.id / "prompt.txt", rendered[s.id])

    if args.dry_run:
        print(f"[dry-run] rendered {len(slices)} prompts under: {out_dir}")
        return 0

    if not args.skip_preflight:
        ok, msg = _preflight_claude(args.claude_cmd, effective_claude_args, code_root, args.timeout_s)
        if not ok:
            print(f"ERROR: {msg}", file=sys.stderr)
            return 2

    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = [
            ex.submit(
                _run_one_slice,
                slice_def=s,
                prompt=rendered[s.id],
                out_dir=out_dir,
                claude_cmd=args.claude_cmd,
                claude_args=effective_claude_args,
                cwd=code_root,
                timeout_s=args.timeout_s,
            )
            for s in slices
        ]
        for f in concurrent.futures.as_completed(futs):
            results.append(f.result())

    results_sorted = sorted(results, key=lambda r: r.get("slice_id", ""))
    _write_text(out_dir / "results.json", json.dumps(results_sorted, indent=2) + "\n")

    ok_cnt = sum(1 for r in results_sorted if r.get("ok"))
    bad_cnt = len(results_sorted) - ok_cnt
    print(f"done: ok={ok_cnt} failed={bad_cnt} out_dir={out_dir}")
    return 0 if bad_cnt == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


