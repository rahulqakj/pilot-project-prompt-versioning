# Prompt Versioning (Python + Gemini)

Simple prompt versioning using a `prompts/` folder and a `meta.json`, with a GitHub Actions workflow to create/switch versions.

## Structure

```text
prompts/
  v1.md
  v2.md
  template.md
  meta.json
scripts/
  prompt_versioning.py
src/
  gemini_client.py
app.py
requirements.txt
.github/workflows/
  prompt-versioning.yml
```

## Local usage

Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run app (needs GEMINI_API_KEY)

```bash
export GEMINI_API_KEY="<your_api_key>"
python app.py --input "Ringkas teks ini"
```

Manage prompts locally

```bash
# Create new version (auto-increment)
python scripts/prompt_versioning.py --mode create_new --last-updated-by you --reason "Experiment"

# Switch to an existing version
python scripts/prompt_versioning.py --mode use_existing --version v2 --last-updated-by you --reason "Rollback"
```

## GitHub Actions

Trigger the "Prompt Versioning" workflow via the Actions tab with inputs:

- mode: create_new or use_existing
- version: vX (optional for create_new, required for use_existing)
- last_updated_by: who
- reason: why

All changes are committed back to the repo automatically in CI.
