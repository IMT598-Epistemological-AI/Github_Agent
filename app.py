"""Script to launch the app"""

import streamlit as st
from github_agent import GitHubAI

# Streamlit UI
st.title("🦾 GitHub AI Assistant")
st.markdown(
    "Ask anything about a GitHub repository, and the AI will fetch and process relevant GitHub data."
)

# User inputs GitHub repo URL
repo_url = st.text_input(
    "🔗 Enter GitHub Repository URL (e.g., https://github.com/owner/repo):"
)


def convert_to_api_url(repo_url):
    """Convert GitHub repo URL to GitHub API URL."""
    if repo_url.startswith("https://github.com/"):
        parts = repo_url.rstrip("/").split("/")
        if len(parts) >= 5:  # Ensures it's a valid repo URL
            owner, repo = parts[3], parts[4]
            return f"https://api.github.com/repos/{owner}/{repo}"
    return None  # Return None if invalid


if repo_url:
    api_url = convert_to_api_url(repo_url)
    if api_url:
        st.success(f"Using repository: {api_url}")

        # Toggle button for selecting model
        model_choice = st.radio("🤖 Choose AI Model:", ("GPT", "Llama"))

        user_query = st.text_input("🔍 Enter your query:")

        if st.button("Run Query"):
            if user_query:
                github_ai = GitHubAI(api_url, model_choice)
                with st.spinner("Fetching response..."):
                    response = github_ai.chat(user_query)
                st.subheader("💬 AI Response:")
                st.write(response)
            else:
                st.warning("Please enter a query before running.")
    else:
        st.error(
            "❌ Invalid GitHub repository URL. Please enter a valid repo URL (e.g., https://github.com/owner/repo)."
        )
else:
    st.warning("Please enter a GitHub repository URL.")
