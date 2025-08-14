# Prompt Versioning with Streamlit and Gemini

A Streamlit application to manage and test different versions of prompts with Google's Gemini API.

## Structure

The project is organized as follows:

```text
prompts/              # Directory for prompt versions
  v1.md
  v2.md
  template.md
  meta.json           # Metadata for the active prompt
scripts/              # Scripts for prompt management
  prompt_versioning.py
src/                  # Source code
  gemini_client.py
streamlit_app.py      # The main Streamlit application
requirements.txt      # Python dependencies
.github/workflows/    # GitHub Actions workflows
  prompt-versioning.yml
```

## Local Usage

### Installation

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Set your Gemini API key as an environment variable:

   ```bash
   export GEMINI_API_KEY="<your_api_key>"
   ```

2. Run the Streamlit app:

   ```bash
   streamlit run streamlit_app.py
   ```

The application will open in your web browser. You can use the sidebar to switch between prompt versions and test them by providing input in the main area.

## Prompt Management

You can manage prompt versions in two ways:

1. **Via the Streamlit UI:** Use the sidebar in the application to switch between existing prompt versions.
2. **Via the command line:** Use the `prompt_versioning.py` script for more advanced operations like creating new versions.

```bash
# Create a new version (auto-increments)
python scripts/prompt_versioning.py --mode create_new --last-updated-by your_name --reason "Adding a new experiment"

# Switch to an existing version
python scripts/prompt_versioning.py --mode use_existing --version v2 --last-updated-by your_name --reason "Rolling back to a stable version"
```

## GitHub Actions

The GitHub Actions workflow can still be used to manage prompt versions directly from your repository's "Actions" tab.

- **mode**: `create_new` or `use_existing`
- **version**: `vX` (required for `use_existing`)
- **last_updated_by**: Your name or identifier
- **reason**: A brief explanation for the change

All changes are committed back to the repository automatically.
