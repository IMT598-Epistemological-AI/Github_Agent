import requests
from datetime import datetime
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

import config  # Ensure you have a config.py file with your API keys

# 🚀 Replace with your API Keys
GITHUB_TOKEN = config.GITHUB_TOKEN
OPENAI_API_KEY = config.OPENAI_API_KEY

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


class GitHubAI:
    def __init__(self, repo_url):
        self.repo_url = repo_url.rstrip("/")
        self.llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=OPENAI_API_KEY)

    def get_endpoints(self):
        """Dynamically create GitHub API endpoints based on the user's repo"""
        return {
            "repo_info": self.repo_url,
            "list_files": f"{self.repo_url}/contents",
            "list_issues": f"{self.repo_url}/issues?state=all&per_page=100",
            "list_prs": f"{self.repo_url}/pulls?state=all&per_page=100",
            "list_commits": f"{self.repo_url}/commits?per_page=100",
        }

    def decide_action(self, user_query):
        """Uses GPT-4 to determine which GitHub API action is needed"""
        system_message = SystemMessage(
            content="You are an AI that maps user queries to GitHub API actions."
            "Current actions: repo_info, list_files, list_issues, list_prs, list_commits."
            "Return only the action name as output."
        )
        user_message = HumanMessage(content=f"User Query: {user_query}\nWhich action should I take?")
        response = self.llm([system_message, user_message])
        return response.content.strip()

    def fetch_github_data(self, action):
        """Fetches raw data from GitHub API dynamically"""
        endpoints = self.get_endpoints()
        if action not in endpoints:
            return "❌ Invalid action"

        response = requests.get(endpoints[action], headers=HEADERS)
        if response.status_code == 200:
            data = response.json()

            # Process commits, issues, and PRs separately
            if action == "list_commits":
                return self.process_commits(data)
            elif action == "list_issues":
                return self.process_issues(data)
            elif action == "list_prs":
                return self.process_prs(data)

            return data

        return f"❌ Error fetching data: {response.json()}"

    def format_datetime(self, iso_string):
        """Helper function to convert ISO 8601 string to separate date and time"""
        try:
            dt = datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%SZ")
            return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
        except ValueError:
            return "Unknown", "Unknown"

    def process_commits(self, commit_data):
        """Processes all commits into a structured format with detailed information."""
        if not commit_data:
            return {"commit_count": 0, "commits": []}

        commit_details = []

        for num, commit in enumerate(commit_data, start=1):
            author_name = commit.get("commit", {}).get("author", {}).get("name", "Unknown")
            author_email = commit.get("commit", {}).get("author", {}).get("email", "Unknown")
            commit_datetime = commit.get("commit", {}).get("author", {}).get("date", "Unknown")
            commit_message = commit.get("commit", {}).get("message", "No message provided")
            commit_sha = commit.get("sha", "Unknown")
            commit_url = commit.get("html_url", "No URL available")

            commit_date, commit_time = self.format_datetime(commit_datetime)

            commit_details.append({
                "commit_num": num,
                "author": author_name,
                "email": author_email,
                "sha": commit_sha,
                "message": commit_message,
                "date": commit_date,
                "time": commit_time,
                "url": commit_url
            })

        return {"commit_count": len(commit_details), "commits": commit_details}

    def process_issues(self, issue_data):
        """Processes all issues into a structured format with detailed information."""
        if not issue_data:
            return {"issue_count": 0, "issues": []}

        issue_details = []

        for num, issue in enumerate(issue_data, start=1):
            author_name = issue.get("user", {}).get("login", "Unknown")
            issue_title = issue.get("title", "No title provided")
            issue_number = issue.get("number", "Unknown")
            issue_state = issue.get("state", "Unknown")
            issue_datetime = issue.get("created_at", "Unknown")
            issue_url = issue.get("html_url", "No URL available")
            comments = issue.get("comments", 0)

            issue_date, issue_time = self.format_datetime(issue_datetime)

            issue_details.append({
                "issue_num": num,
                "author": author_name,
                "number": issue_number,
                "title": issue_title,
                "state": issue_state,
                "date": issue_date,
                "time": issue_time,
                "url": issue_url,
                "comments": comments
            })

        return {"issue_count": len(issue_details), "issues": issue_details}

    def process_prs(self, pr_data):
        """Processes all PRs into a structured format with detailed information."""
        if not pr_data:
            return {"pr_count": 0, "prs": []}

        pr_details = []

        for num, pr in enumerate(pr_data, start=1):
            author_name = pr.get("user", {}).get("login", "Unknown")
            pr_title = pr.get("title", "No title provided")
            pr_number = pr.get("number", "Unknown")
            pr_state = pr.get("state", "Unknown")
            pr_datetime = pr.get("created_at", "Unknown")
            pr_url = pr.get("html_url", "No URL available")
            comments = pr.get("comments", 0)
            commits = pr.get("commits", 0)
            additions = pr.get("additions", 0)
            deletions = pr.get("deletions", 0)
            merged = pr.get("merged", False)

            pr_date, pr_time = self.format_datetime(pr_datetime)

            pr_details.append({
                "pr_num": num,
                "author": author_name,
                "number": pr_number,
                "title": pr_title,
                "state": pr_state,
                "date": pr_date,
                "time": pr_time,
                "url": pr_url,
                "comments": comments,
                "commits": commits,
                "additions": additions,
                "deletions": deletions,
                "merged": merged
            })

        return {"pr_count": len(pr_details), "prs": pr_details}

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
