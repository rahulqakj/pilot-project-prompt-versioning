from __future__ import annotations
import argparse
from src.gemini_client import get_active_prompt_text, GeminiClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="User input to send to Gemini")
    parser.add_argument("--model", default="gemini-2.5-flash")
    args = parser.parse_args()

    meta, prompt_text = get_active_prompt_text()
    print(f"Active Prompt: {meta.used_version} (by {meta.last_updated_by}) - {meta.reason}")

    client = GeminiClient(model=args.model)
    resp = client.generate(prompt_text, args.input)
    print("\n--- Response ---\n")
    print(resp)


if __name__ == "__main__":
    main()
