# 🤖 AI Code Review Agent

An intelligent AI-powered code review platform that automatically analyzes GitHub repositories, detects potential issues, and generates actionable code review reports using Large Language Models (LLMs).

Built with **Python**, **Streamlit**, **Ollama**, **AST Parsing**, **Token-Aware Chunking**, and **Interactive Analytics**.

---

## 📌 Overview

AI Code Review Agent helps developers perform automated code reviews on GitHub repositories by combining static analysis techniques with modern Large Language Models.

The system clones repositories, scans source files, intelligently chunks code, sends code segments to an LLM for analysis, and produces structured review reports containing:

* Bugs
* Security vulnerabilities
* Performance issues
* Code smells
* Best-practice violations
* Style improvements

---

## ✨ Features

### 🔍 Automated Repository Review

* Clone public GitHub repositories
* Scan source code files automatically
* Analyze multiple programming languages

### 🧠 AI-Powered Analysis

* Local LLM inference using Ollama
* Structured issue detection
* Confidence-based scoring system
* Severity classification

### 📂 Intelligent Code Processing

* AST-based parsing
* Token-aware chunking
* Large file support
* Context-preserving analysis

### 📊 Interactive Dashboard

* Streamlit-based UI
* Issue filtering
* Severity visualization
* File-level analysis
* Confidence histograms

### 📄 Export Reports

* JSON Export
* Markdown Export
* GitHub Pull Request Comments

### 🐙 GitHub Integration

* Repository cloning
* Pull Request review posting
* GitHub token authentication

---

# 🏗 System Architecture

```text
GitHub Repository
        │
        ▼
 Repository Cloner
        │
        ▼
 File Scanner
        │
        ▼
 AST Parser
        │
        ▼
 Chunk Engine
        │
        ▼
 Ollama LLM Reviewer
        │
        ▼
 Issue Extraction
        │
        ▼
 Confidence Ranking
        │
        ▼
 Streamlit Dashboard
```

---

# 📁 Project Structure

```text
ai_code_review_agent/
│
├── agent/
│   ├── orchestrator.py
│   ├── pipeline.py
│   └── state_manager.py
│
├── app/
│   ├── config.py
│   ├── logger.py
│   └── constants.py
│
├── chunking/
│   └── chunk_engine.py
│
├── formatter/
│   ├── json_formatter.py
│   └── markdown_formatter.py
│
├── github_api/
│   ├── auth.py
│   └── pr_commentor.py
│
├── ingestion/
│   ├── github_cloner.py
│   ├── file_scanner.py
│   └── repo_validator.py
│
├── llm/
│   ├── reviewer.py
│   ├── prompt_builder.py
│   └── response_parser.py
│
├── parser/
│   └── ast_parser.py
│
├── schemas/
│   └── review_schema.py
│
├── ui/
│   ├── charts.py
│   └── components.py
│
├── utils/
│   └── helpers.py
│
├── tests/
│
├── requirements.txt
├── run.py
└── README.md
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/ai-code-review-agent.git

cd ai-code-review-agent
```

---

## 2️⃣ Create Virtual Environment

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🧠 Install Ollama

Download Ollama:

```text
https://ollama.com/download
```

Pull the model:

```bash
ollama pull qwen2.5-coder:3b
```

Verify:

```bash
ollama list
```

Start Ollama:

```bash
ollama serve
```

---

# 🔑 Environment Variables

Create a `.env` file:

```env
GITHUB_TOKEN=your_github_token
```

---

# 🚀 Running the Application

Start Streamlit:

```bash
streamlit run app/main.py
```

Open:

```text
http://localhost:8501
```

---

# 📊 Dashboard Features

### Overview

* Severity Distribution
* Issue Type Distribution
* File Heatmaps

### Issue Table

* Filter by Severity
* Filter by Confidence
* Filter by Issue Type

### File Analysis

* File-wise review results
* Expandable issue cards

### Charts

* Confidence Histogram
* Severity over Files

### Export

* JSON Reports
* Markdown Reports

### GitHub PR Integration

* Post comments directly to Pull Requests

---

# 🔍 Review Workflow

```text
User enters GitHub URL
          │
          ▼
Repository Validation
          │
          ▼
Repository Clone
          │
          ▼
Source File Scan
          │
          ▼
AST Parsing
          │
          ▼
Code Chunking
          │
          ▼
LLM Review
          │
          ▼
Issue Extraction
          │
          ▼
Confidence Ranking
          │
          ▼
Visualization & Export
```

---

# 🛠 Technologies Used

### Backend

* Python
* Streamlit
* GitPython
* Tenacity
* Ollama

### AI

* Qwen 2.5 Coder
* DeepSeek Coder
* Local LLM Inference

### Data Processing

* AST Parsing
* Token Chunking
* JSON Processing

### Visualization

* Plotly
* Streamlit Components

### DevOps

* GitHub API
* GitHub Actions Ready
* Virtual Environments

---

# 📈 Future Improvements

* Multi-LLM Support
* OpenAI API Integration
* Claude Integration
* Gemini Integration
* Parallel File Processing
* Team Dashboards
* Repository History Database
* CI/CD Integration
* VS Code Extension

---

# 🤝 Contributing

Contributions are welcome.

```bash
Fork the repository

Create a feature branch

Commit your changes

Push your branch

Create a Pull Request
```

---

# 📜 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

## Rishiraj Chaurasiya

**B.Tech — Artificial Intelligence & Machine Learning**

AI Engineer | Full-Stack Developer | LLM Applications | Computer Vision | AI Agents | Automation Systems

### Skills

* Artificial Intelligence
* Machine Learning
* Deep Learning
* Large Language Models
* Agentic AI Systems
* RAG Pipelines
* Computer Vision
* FastAPI
* Streamlit
* React
* Python

---

⭐ If you found this project useful, please consider giving it a star on GitHub.
