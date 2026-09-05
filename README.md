# secure-edtech-agents

Systematic empirical analysis and literature benchmark evaluating security agent vulnerabilities across decentralized educational frameworks. Investigates indirect prompt injection, RAG memory poisoning, and enterprise-to-academic performance trade-offs while benchmarking heuristic detection, evasion vectors, and operational overhead.

## Project Overview

**Vulnerability of an AI-Based Education Framework Using Security Agents**

A framework investigating the vulnerabilities of an AI-powered educational system using security agents.

### Project Structure

```text
├── app/
│   ├── agent/        # AI Teacher Agent and OpenRouter LLM integration
│   ├── database/     # SQLite database setup and synthetic datasets
│   ├── interface/    # Local HTTP API (FastAPI) and test interfaces
│   └── tools/        # Educational database tools
├── data/             # SQLite database storage (data/education.db)
├── tests/            # Test suites
├── .env.example      # Example environment variables
├── .gitignore        # Git ignore rules
├── requirements.txt  # Project dependencies
├── teacher_agent_interface.py # Python callable interface for testing
└── README.md         # Project documentation
```

### Architecture Overview

The system architecture follows the flow:

```text
Student Interface (HTTP API / Callable)
              ↓
        Teacher Agent
              ↓
       Education Tools
              ↓
  SQLite Education Database
```

### Getting Started

1. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Update `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` in `.env`.

4. **Initialize Database:**
   ```bash
   python app/database/setup_database.py
   ```

5. **Run Local HTTP Server:**
   ```bash
   python -m uvicorn app.interface.api:app --host 127.0.0.1 --port 8000
   ```
