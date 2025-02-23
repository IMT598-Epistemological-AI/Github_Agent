import streamlit as st
from github_agent import GitHubAI  # Import the GitHubAI class

# Streamlit UI
st.title("🦾 GitHub AI Assistant")
st.markdown("Ask anything about the repository, and the AI will fetch and process relevant GitHub data.")

user_query = st.text_input("🔍 Enter your query:")
if st.button("Run Query"):
    if user_query:
        github_ai = GitHubAI()
        with st.spinner("Fetching response..."):
            response = github_ai.chat(user_query)
        st.subheader("💬 AI Response:")
        st.write(response)
    else:
        st.warning("Please enter a query before running.")
