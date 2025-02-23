# 🚀 GitHub Agent

An AI agent that interacts with GitHub and fetches repository information using GPT.

## 🛠️ Setup & Installation

### 1️⃣ Install Dependencies  
Run the following command to install the required libraries:

```sh
pip install -r requirements.txt
```

### 2️⃣ Configure API Keys  
Create a `config.py` file in the root directory and add the following credentials:

```python
OPENAI_API_KEY = "ENTER_YOUR_OPENAI_KEY"
GITHUB_TOKEN = "ENTER_YOUR_GITHUB_TOKEN"
```

Replace `"ENTER_YOUR_OPENAI_KEY"` and `"ENTER_YOUR_GITHUB_TOKEN"` with your actual API keys.

### 3️⃣ Run the Streamlit App  
Start the Streamlit UI by running:

```sh
streamlit run app.py
```

### 4️⃣ Interact with the AI Agent  
Once the app is running, open your browser and go to:  

➡️ [http://localhost:8501](http://localhost:8501)  

Start chatting with the GitHub AI agent! 🚀

---

## 📌 Features (so far)
- Retrieves github repository information.
- Can access root directory files, issues, pull requests, and commits.
- Uses OpenAI's GPT-4 to process this information and answer questions.

---

## 🔥 Example Queries
Here are some example queries you can ask the GitHub agent:
- **"Show me the latest commits."**
- **"List all open issues."**
- **"Get details about this repository."**
- **"What are the last 5 pull requests?"**

---
