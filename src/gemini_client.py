from __future__ import annotations
import json
from pathlib import Path
import os
import google.generativeai as genai

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
META_FILE = PROMPTS_DIR / "meta.json"


class PromptMeta:
    def __init__(self, used_version: str, last_updated_by: str, reason: str):
        self.used_version = used_version
        self.last_updated_by = last_updated_by
        self.reason = reason

    @classmethod
    def from_file(cls, path: Path = META_FILE) -> "PromptMeta":
        data = json.loads(path.read_text())
        return cls(
            used_version=data.get("used_version", "v1"),
            last_updated_by=data.get("last_updated_by", ""),
            reason=data.get("reason", ""),
        )


def get_active_prompt_text() -> tuple[PromptMeta, str]:
    meta = PromptMeta.from_file(META_FILE)
    prompt_file = PROMPTS_DIR / f"{meta.used_version}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Active prompt file not found: {prompt_file}")
    return meta, prompt_file.read_text()


class GeminiClient:
    def __init__(self, model: str = "gemini-2.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def generate(self, system_prompt: str, user_input: str) -> str:
        # Combine system prompt and user content
        content = f"{system_prompt}\n\nUser request:\n{user_input}"
        resp = self.model.generate_content(content)
        return resp.text if hasattr(resp, "text") else str(resp)
