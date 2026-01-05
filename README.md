# RisingWave Docs ↔ Code Audit (Claude Code) — Repo Template

This is a **standalone repo template** to run a sliced docs-vs-code audit for:

- `risingwavelabs/risingwave`
- `risingwavelabs/risingwave-docs`

It is designed to run via **GitHub Actions (manual trigger)** and commit the generated reports back into this repo.

## What you get

- A slice manifest (`tools/docs-code-compare/slices.yml`) describing **docs scopes / code scopes / test signals**
- A Claude Code prompt template (`tools/docs-code-compare/prompt-claude-slice-template.md`)
- A runner that executes slices in parallel and writes reports (`tools/docs-code-compare/run_claude_slices.py`)
- A validator for periodic drift detection (`tools/docs-code-compare/validate_slices.py`)
- A simple aggregator (`tools/docs-code-compare/aggregate_reports.py`) that generates `SUMMARY.md`
- A GitHub Action workflow: `.github/workflows/docs-code-audit.yml`

## GitHub Action usage

Go to **Actions → “Docs ↔ Code Audit (RisingWave)” → Run workflow** and specify:

- `risingwave_ref`: branch/tag/sha for RisingWave
- `docs_ref`: branch/tag/sha for risingwave-docs
- `slices`: optional comma-separated list like `S1,S2` (empty means all)

The workflow will:

1. Checkout this audit repo
2. Checkout RisingWave into `work/risingwave`
3. Checkout docs into `work/risingwave-docs`
4. Validate `slices.yml` paths (optional but recommended)
5. Run Claude Code in non-interactive mode to generate per-slice reports
6. Generate `reports/<run_tag>/SUMMARY.md`
7. Commit `reports/<run_tag>/` back to this repo

## Secrets / Auth

You need to authenticate Claude Code in CI. The exact mechanism depends on your setup.

Recommended options:

- Provide an API key (commonly via `ANTHROPIC_API_KEY`) as a GitHub Actions secret.
- If your environment uses a different token mechanism, update the workflow step `Configure Claude auth`.

## Local run (optional)

```bash
python3 -m pip install -r tools/docs-code-compare/requirements.txt

python3 tools/docs-code-compare/validate_slices.py \
  --code-repo-root work/risingwave \
  --docs-repo-root work/risingwave-docs

python3 tools/docs-code-compare/run_claude_slices.py \
  --code-repo-root work/risingwave \
  --docs-repo-root work/risingwave-docs \
  --docs-repo-ref main \
  --jobs 6 \
  --out-dir reports/local-test
```


