from __future__ import annotations
import json
import streamlit as st
from pathlib import Path
import os
from src.gemini_client import get_active_prompt_text, GeminiClient, PromptMeta

# Configuration
PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
META_FILE = PROMPTS_DIR / "meta.json"

def list_available_versions() -> list[str]:
    """List all available prompt versions"""
    versions = []
    for p in PROMPTS_DIR.glob("v*.md"):
        versions.append(p.stem)
    return sorted(versions, key=lambda v: int(v[1:]) if v[1:].isdigit() else 0)

def switch_prompt_version(version: str) -> bool:
    """Switch to an existing prompt version by updating meta.json directly"""
    try:
        meta_data = {
            "used_version": version,
            "last_updated_by": "streamlit-app",
            "reason": f"Switched via UI to {version}"
        }
        META_FILE.write_text(json.dumps(meta_data, indent=2) + "\n")
        return True
    except Exception:
        return False

def main():
    st.set_page_config(page_title="Prompt Versioning with Gemini", page_icon="🤖")
    
    st.title("🤖 Prompt Versioning with Gemini")
    st.markdown("Switch between different prompt versions and test with Gemini AI")
    
    # Sidebar for prompt management
    with st.sidebar:
        st.header("📝 Prompt Versions")
        
        # Current prompt info
        try:
            meta, prompt_text = get_active_prompt_text()
            st.success(f"**Active:** {meta.used_version}")
            st.caption(f"Last updated: {meta.last_updated_by}")
        except Exception as e:
            st.error(f"Error loading prompt: {e}")
            return
        
        st.divider()
        
        # Switch to existing version (static only)
        st.subheader("Switch Version")
        available_versions = list_available_versions()
        
        if available_versions:
            selected_version = st.selectbox(
                "Choose version:", 
                available_versions,
                index=available_versions.index(meta.used_version) if meta.used_version in available_versions else 0
            )
            
            if st.button("Switch Version", type="primary"):
                if selected_version != meta.used_version:
                    if switch_prompt_version(selected_version):
                        st.success(f"✅ Switched to {selected_version}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to switch version")
                else:
                    st.info("Already using this version")
        
        st.divider()
        st.caption("📌 Prompts are read-only. Use CLI/GitHub Actions to create new versions.")
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📋 Current Prompt")
        st.code(prompt_text, language="markdown")
        
        # Show all available prompts
        st.subheader("📚 All Available Prompts")
        for version in available_versions:
            with st.expander(f"View {version}"):
                try:
                    version_file = PROMPTS_DIR / f"{version}.md"
                    if version_file.exists():
                        content = version_file.read_text()
                        st.code(content, language="markdown")
                except Exception as e:
                    st.error(f"Error loading {version}: {e}")
    
    with col2:
        st.header("🤖 Test with Gemini")
        
        # Gemini settings
        model_choice = st.selectbox(
            "Model:", 
            ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro"],
            index=0
        )
        
        # API Key input
        api_key = st.text_input(
            "Gemini API Key:", 
            type="password",
            value=os.getenv("GEMINI_API_KEY", ""),
            help="Enter your Gemini API key or set GEMINI_API_KEY environment variable"
        )
        
        # User input
        user_input = st.text_area(
            "Your input:", 
            placeholder="Type your question or request here...",
            height=100
        )
        
        if st.button("🚀 Generate Response", type="primary"):
            if not api_key:
                st.error("❌ Please provide a Gemini API key")
            elif not user_input.strip():
                st.warning("⚠️ Please enter some input")
            else:
                with st.spinner("Generating response..."):
                    try:
                        # Set API key temporarily
                        os.environ["GEMINI_API_KEY"] = api_key
                        
                        client = GeminiClient(model=model_choice)
                        response = client.generate(prompt_text, user_input)
                        
                        st.subheader("📤 Response")
                        st.markdown(response)
                        
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                    finally:
                        # Clean up
                        if "GEMINI_API_KEY" in os.environ and not os.getenv("GEMINI_API_KEY"):
                            del os.environ["GEMINI_API_KEY"]
    
    # Footer
    st.divider()
    st.caption("💡 To add new prompts, use: `python scripts/prompt_versioning.py --mode create_new --last-updated-by you --reason 'new prompt'`")

if __name__ == "__main__":
    main()
