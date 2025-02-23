import requests
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

import config  # Ensure you have a config.py file with your API keys

# 🚀 Replace with your API Keys
GITHUB_TOKEN = config.GITHUB_TOKEN
OPENAI_API_KEY = config.OPENAI_API_KEY

# Repo details
REPO_OWNER = "IMT598-Epistemological-AI"
REPO_NAME = "IMT598A"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# Base GitHub API URL
BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

# GitHub API Endpoints
ENDPOINTS = {
    "repo_info": BASE_URL,
    "list_files": f"{BASE_URL}/contents",
    "list_issues": f"{BASE_URL}/issues",
    "list_prs": f"{BASE_URL}/pulls",
    "list_commits": f"{BASE_URL}/commits",
}


class GitHubAI:
    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=OPENAI_API_KEY)

    def decide_action(self, user_query):
        """Uses GPT-4 to determine which GitHub API action is needed"""
        system_message = SystemMessage(
            content="You are an AI that maps user queries to GitHub API actions."
            "Current actions: repo_info, list_files, list_issues, list_open_issues, list_closed_issues, list_prs, list_commits."
            "Return only the action name as output."
        )
        user_message = HumanMessage(content=f"User Query: {user_query}\nWhich action should I take?")
        response = self.llm([system_message, user_message])
        return response.content.strip()

    def fetch_github_data(self, action):
        """Fetches raw data from GitHub API dynamically"""
        if action not in ENDPOINTS and action not in ["list_open_issues", "list_closed_issues"]:
            return "❌ Invalid action"

        # Dynamically construct URLs for open/closed issues
        if action == "list_open_issues":
            url = f"{BASE_URL}/issues?state=open"
        elif action == "list_closed_issues":
            url = f"{BASE_URL}/issues?state=closed"
        else:
            url = ENDPOINTS[action]

        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        return f"❌ Error fetching data: {response.json()}"

    def process_data_with_LLM(self, user_query, raw_data):
        """Passes raw data + user query to GPT-4 for intelligent processing"""
        system_message = SystemMessage(
            content="You are an AI assistant that interprets GitHub data and answers user queries accurately."
        )
        user_message = HumanMessage(
            content=f"User Query: {user_query}\nGitHub Data:\n{raw_data}\nProvide the most relevant answer."
        )
        response = self.llm([system_message, user_message])
        return response.content.strip()

    def chat(self, user_query):
        """Handles query interpretation, data fetching, and intelligent processing"""
        action = self.decide_action(user_query)
        if action == "❌ Invalid action":
            return "❌ Invalid action"
        raw_data = self.fetch_github_data(action)
        return self.process_data_with_LLM(user_query, raw_data)
