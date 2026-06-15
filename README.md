# 🕵️‍♂️ Internal Prompt Review MCP Tool

An AI-powered internal tool built with MCP (Model Context Protocol) that helps team members review, improve, and log their AI prompts ensuring consistent quality across all client deliverables.

---

## 🌐 Live Demo

| Service | URL |
|---|---|
| Streamlit UI | https://terrific-fascination-production-162e.up.railway.app |
| MCP Server | https://prompt-review-tool-production.up.railway.app/sse |

---

## 🧠 What It Does

Every team member writes prompts daily. This tool acts as an **AI judge** that:

- ✅ Reviews any prompt and scores it out of 10
- ✅ Gives structured feedback on Clarity, Specificity, Context, and Output Format
- ✅ Suggests an improved version of the prompt
- ✅ Fetches high-scoring reference prompts from your department
- ✅ Logs everything to a database for future reference

---

## 🏗️ Architecture

```
Streamlit Chat UI
https://terrific-fascination-production-162e.up.railway.app
        ↓
NVIDIA NIM — llama-3.3-nemotron-super-49b-v1.5
(Drives the conversation, asks for name/department, decides when to call tools)
        ↓
MCP Client (client.py)
        ↓
MCP Server (Railway) — https://prompt-review-tool-production.up.railway.app/sse
(Runs 24/7 on the cloud — no local server needed)
        ↓
NVIDIA NIM — meta/llama-4-maverick-17b-128e-instruct
(AI Judge — reviews and improves the prompt)
        ↓
SQLite Database (db/prompts.db)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| MCP Framework | `mcp[cli]` Python SDK |
| Chat Model (UI) | NVIDIA NIM — `llama-3.3-nemotron-super-49b-v1.5` |
| AI Judge (MCP Tools) | NVIDIA NIM — `meta/llama-4-maverick-17b-128e-instruct` |
| Client Library | `openai` (OpenAI-compatible) |
| UI | Streamlit |
| Database | SQLite |
| Hosting | Railway |
| Total Cost | 100% Free |

---

## 📁 Project Structure

```
prompt_review/
├── db/
│   ├── database.py        # DB setup and schema
│   └── prompts.db         # SQLite database (auto-created)
├── server.py              # MCP server with all 4 tools
├── client.py              # MCP client + NVIDIA NIM connection
├── app.py                 # Streamlit chat UI
├── Procfile               # Railway deployment config
├── .env                   # API keys (not committed)
├── requirements.txt       # Dependencies
└── README.md
```

---

## ⚙️ MCP Tools

| Tool | Input | Output |
|---|---|---|
| `review_prompt` | Prompt text, member name, department | Score + structured feedback |
| `improve_prompt` | Prompt text | Rewritten, optimized prompt |
| `get_department_prompts` | Department name | High scoring prompts (score ≥ 9) from that department |
| `log_prompt` | Name, department, prompt, score, improved prompt | Saves to SQLite DB |

---

## 🚀 Getting Started

### Option 1 — Use the Live App (Recommended) ✅
Just open the link in your browser — no setup needed:
```
https://terrific-fascination-production-162e.up.railway.app
```

### Option 2 — Run Locally

#### Prerequisites
- Python 3.10+
- NVIDIA NIM API key from [build.nvidia.com](https://build.nvidia.com)

#### Steps

1. Clone the Repository
```bash
git clone https://github.com/IsaacNatarajan123/Prompt-review-tool.git
cd Prompt-review-tool
```

2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Set Up Environment Variables
```
NVIDIA_API_KEY=nvapi-your-key-here
```

5. Run the Streamlit UI
```bash
streamlit run app.py
```

> **Note:** The MCP Server is already hosted on Railway — no need to run `server.py` locally.

---

## 💬 How to Use

1. Open the Streamlit UI in your browser
2. Type your prompt — e.g. *"Review this prompt — Write a product roadmap"*
3. The AI will ask for your name and department
4. It fetches high-scoring reference prompts from your department
5. Reviews your prompt with a score and feedback
6. Suggests an improved version
7. Asks if you want to log it to the database

---

## 🤖 How the Two Models Work Together

```
User sends a message
        ↓
llama-3.3-nemotron-super-49b-v1.5 (Chat Model)
Drives the conversation — asks questions,
decides which MCP tool to call next
        ↓
MCP Tool is called on Railway server
        ↓
meta/llama-4-maverick-17b-128e-instruct (AI Judge)
Does the actual prompt review and improvement
        ↓
Result returned to Chat Model
        ↓
Chat Model presents the result to the user
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_name TEXT,
    department TEXT,
    original_prompt TEXT,
    score INTEGER,
    improved_prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📦 Requirements

```
mcp[cli]
openai
python-dotenv
streamlit
```

---

## 🔌 Claude Desktop Integration

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "prompt-review": {
      "command": "path/to/venv/Scripts/python.exe",
      "args": ["path/to/server.py"]
    }
  }
}
```

---

## 👤 Author

**Isaac Natarajan**

---
