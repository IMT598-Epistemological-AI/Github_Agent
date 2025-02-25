"""Github AI agent to parse github data and answer user queries."""
import json
from datetime import datetime
import requests
from langchain.chat_models import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.schema import SystemMessage, HumanMessage

import config  # Ensure you have a config.py file with your API keys

GITHUB_TOKEN = config.GITHUB_TOKEN
OPENAI_API_KEY = config.OPENAI_API_KEY

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


class GitHubAI:
    """GitHub AI agent to parse GitHub data and answer user queries."""

    def __init__(self, repo_url, model_name):
        self.repo_url = repo_url.rstrip("/")
        if model_name == "GPT":
            self.llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=OPENAI_API_KEY)
        else:
            self.llm = ChatOllama(model="llama3.1", temperature=0)

    def get_endpoints(self):
        """Dynamically create GitHub API endpoints based on the user's repo"""
        return {
            "repo_info": self.repo_url,
            "list_files": f"{self.repo_url}/contents",
            "list_issues": f"{self.repo_url}/issues?state=all&per_page=100",
            "list_issue_details": f"{self.repo_url}/issues",  # Base endpoint for individual issues
            "list_prs": f"{self.repo_url}/pulls?state=all&per_page=100",
            "list_commits": f"{self.repo_url}/commits?per_page=100",
        }

    def decide_action(self, user_query):
        """Uses LLM to determine which GitHub API action is needed"""
        system_message = SystemMessage(
            content="You are an AI that maps user queries to GitHub API actions."
            "Current actions: repo_info, list_files, list_issues, list_issue_details, list_prs, list_commits."
            "Use 'list_issue_details' only if the query asks for details about a specific issue, such as 'issue #38'."
            "Use 'list_issues' if the query asks for multiple issues, such as 'last 5 opened issues'."
            "Return only the action name as output."
        )
        user_message = HumanMessage(
            content=f"User Query: {user_query}\nWhich action should I take?"
        )
        response = self.llm([system_message, user_message])
        return response.content.strip()

    def fetch_github_data(self, action, issue_number=None):
        """Fetches raw data from GitHub API dynamically"""
        endpoints = self.get_endpoints()
        if action not in endpoints:
            return "❌ Invalid action"

        if action == "list_issue_details" and issue_number:
            url = f"{endpoints[action]}/{issue_number}"
        else:
            url = endpoints[action]

        response = requests.get(url, headers=HEADERS, timeout=20)
        if response.status_code == 200:
            data = response.json()

            # Process data appropriately
            if action == "list_commits":
                return self.process_commits(data)
            elif action == "list_issues":
                return self.process_issues(data)
            elif action == "list_prs":
                return self.process_prs(data)
            elif action == "list_issue_details":
                return self.process_issue_details(data)

            return data

        return f"❌ Error fetching data: {response.json()}"

    def format_datetime(self, dt_str):
        if dt_str and dt_str != "Unknown":
            dt_obj = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ")
            formatted_date = dt_obj.strftime("%d %b %Y")  # Example: 25 Feb 2025
            formatted_time = dt_obj.strftime("%H:%M:%S")  # Example: 04:00:47
            return {"date": formatted_date, "time": formatted_time}
        return {"date": "Unknown", "time": "Unknown"}

    def process_commits(self, commit_data):
        """Processes all commits into a structured format with detailed information."""
        if not commit_data:
            return {"commit_count": 0, "commits": []}

        commit_details = []

        for num, commit in enumerate(commit_data, start=1):
            author_name = (
                commit.get("commit", {}).get("author", {}).get("name", "Unknown")
            )
            author_email = (
                commit.get("commit", {}).get("author", {}).get("email", "Unknown")
            )
            commit_datetime = (
                commit.get("commit", {}).get("author", {}).get("date", "Unknown")
            )
            commit_message = commit.get("commit", {}).get(
                "message", "No message provided"
            )
            commit_sha = commit.get("sha", "Unknown")
            commit_url = commit.get("html_url", "No URL available")

            created_at_formatted = self.format_datetime(commit_datetime)

            commit_details.append(
                {
                    "commit_num": num,
                    "author": author_name,
                    "email": author_email,
                    "sha": commit_sha,
                    "message": commit_message,
                    "created_at": created_at_formatted,
                    "url": commit_url,
                }
            )

        return {"commit_count": len(commit_details), "commits": commit_details}

    def process_issues(self, issue_data):
        """Processes issues with essential details only (issue_num, issue_number, author, title, state, URL)."""
        if not issue_data:
            return {"issue_count": 0, "issues": []}

        issue_details = []

        for num, issue in enumerate(issue_data, start=1):
            author_name = issue["user"]["login"] if issue.get("user") else "Unknown"
            assignee_name = issue["assignee"]["login"] if issue.get("assignee") else "Unknown"
            issue_title = issue.get("title", "No title provided")
            issue_number = issue.get("number", "Unknown")
            issue_datetime = issue.get("created_at", "Unknown")
            issue_closed_datetime = issue.get("closed_at", "Unknown")
            issue_state = issue.get("state", "Unknown")
            issue_url = issue.get("html_url", "No URL available")

            created_at_formatted = self.format_datetime(issue_datetime)
            closed_at_formatted = self.format_datetime(issue_closed_datetime)

            issue_details.append(
                {
                    "issue_creator": author_name,
                    "assignee": assignee_name,
                    "title": f"#{issue_number}: {issue_title} - {issue_url}",
                    "created_at": created_at_formatted,
                    "closed_at": closed_at_formatted,
                    "state": issue_state,
                }
            )

        return {"issue_count": len(issue_details), "issues": issue_details}

    def process_issue_details(self, issue_data):
        """Processes a single issue with detailed information including description and comments."""
        if not issue_data:
            return {"error": "Issue not found"}

        issue_number = issue_data.get("number", "Unknown")
        author_name = issue_data["user"]["login"] if issue_data.get("user") else "Unknown"
        assignee_name = issue_data["assignee"]["login"] if issue_data.get("assignee") else "Unknown"
        issue_title = issue_data.get("title", "No title provided")
        issue_description = issue_data.get("body", "No description provided")
        issue_state = issue_data.get("state", "Unknown")
        issue_datetime = issue_data.get("created_at", "Unknown")
        issue_closed_datetime = issue_data.get("closed_at")
        issue_url = issue_data.get("html_url", "No URL available")
        comments_url = issue_data.get("comments_url", "")

        created_at_formatted = self.format_datetime(issue_datetime)
        closed_at_formatted = self.format_datetime(issue_closed_datetime)

        # Fetch comments
        comments = []
        if comments_url:
            response = requests.get(comments_url, headers=HEADERS, timeout=20)
            if response.status_code == 200:
                comments_data = response.json()
                comments = [c.get("body", "No comment content") for c in comments_data]

        return {
            "issue_number": issue_number,
            "issue_creator": author_name,
            "assignee": assignee_name,
            "title": issue_title,
            "description": issue_description,
            "comments": comments,
            "state": issue_state,
            "created_at": created_at_formatted,  # Now contains separate date and time
            "closed_at": closed_at_formatted,  # Now contains separate date and time
            "url": issue_url,
        }

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
            merged = pr.get("merged_at") is not None  # If merged_at is not None, it's merged

            pr_created_at_formatted = self.format_datetime(pr_datetime)

            pr_details.append(
                {
                    "pr_num": num,
                    "author": author_name,
                    "number": pr_number,
                    "title": pr_title,
                    "state": pr_state,
                    "created_at": pr_created_at_formatted,  # Now formatted with separate date and time
                    "url": pr_url,
                    "comments": comments,
                    "commits": commits,
                    "additions": additions,
                    "deletions": deletions,
                    "merged": merged,
                }
            )

        return {"pr_count": len(pr_details), "prs": pr_details}

    def process_data_with_LLM(self, user_query, raw_data):
        """Passes raw data + user query to GPT-4 for intelligent processing"""
        with open("raw_data_for_query.json", "w") as f:
            json.dump(raw_data, f)
        
        system_message = SystemMessage(
            content="You are an AI assistant that interprets GitHub data and answers user queries accurately."
        )
        user_message = HumanMessage(
            content=f"User Query: {user_query}\nGitHub Data:\n{raw_data}\n The dates are in YYYY:MM::DD format.\nProvide the most relevant answer."
        )
        response = self.llm([system_message, user_message])
        return response.content.strip()

    def chat(self, user_query):
        """Handles query interpretation, data fetching, and intelligent processing"""
        action = self.decide_action(user_query)

        # Extract issue number if the action is list_issue_details
        issue_number = None
        if action == "list_issue_details":
            words = user_query.split()
            for word in words:
                if word.startswith("#") and word[1:].isdigit():
                    issue_number = word[1:]
                    break
                elif word.isdigit():
                    issue_number = word
                    break

        if action == "❌ Invalid action":
            return "❌ Invalid action"

        raw_data = self.fetch_github_data(action, issue_number)
        return self.process_data_with_LLM(user_query, raw_data)
