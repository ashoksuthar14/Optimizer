# 🤖 Optimizer – AI-Powered Startup Assistant

> **Optimizer** is an AI-powered ideation, optimization, and self-challenge assistant for small startups — acting like an intelligent co-founder who researches, optimizes, and challenges your ideas with data-driven insights.

---

## 🚨 Problem Statement

Small startups often face:
- ⚙️ Limited manpower to research, brainstorm, and optimize ideas  
- 💬 Lack of diverse viewpoints (groupthink problem)  
- ⛔ Missed opportunities to leverage open-source tools or automation  

---

## 💡 Solution

**Optimizer** acts as an **AI Co-Founder** that:
- 🧩 Builds **blueprints, flowcharts**, and **project architectures**
- 🚀 Suggests **technical, financial, and strategic optimizations**
- 🧠 Challenges your team’s thinking with an **EchoChamber Breaker**
- 📊 Generates **comprehensive reports and dashboards** for founders

---

## 🏗️ System Architecture

### 🔹 Overview

Optimizer follows a **multi-agent orchestrated architecture** built with **LangChain**, **Gemini models**, and **FAISS-based RAG (Retrieval-Augmented Generation)**.

Each agent performs a distinct task, coordinated by the **Orchestrator**.


### 🔹 Core Components

| Agent | Role | Description |
|--------|------|-------------|
| 🧱 **BlueprintAgent** | Planning | Generates detailed project blueprints & ASCII architecture diagrams |
| 🕵️ **CrawlerAgent** | Research | Uses SerpAPI & GitHub to discover similar projects & insights |
| 🧠 **OptimizerAgent** | Enhancement | Suggests technical, business, and operational optimizations |
| ⚔️ **EchoAgent** | Challenge | Acts as devil’s advocate to find blind spots and biases |
| 🧩 **SynthesisAgent** | Reporting | Merges all results into a structured final report |

---

### 🧭 Flow Diagram

> **Flow Summary:** Upload → Index → Retrieve → Parallel Agents → Synthesis → Report

![Architecture Diagram Placeholder](./docs/optimizer_architecture.png)

*(You can replace the above placeholder with your flowchart image — the one you drew.)*

---

## ⚙️ Tech Stack

| Component | Technology |
|------------|-------------|
| **Backend** | Flask + LangChain |
| **AI Models** | Gemini 1.5 & Gemini 2.5 Flash (multiple keys for load balancing) |
| **Vector DB** | FAISS (local) |
| **Embeddings** | Sentence Transformers (`all-MiniLM-L6-v2`) |
| **Frontend** | HTML / CSS / JavaScript |
| **Crawler** | SerpAPI + GitHub API |
| **PDF Reports** | ReportLab |

---

## 🧩 High-Level Architecture

### 🔸 Pattern
- Orchestrated **multi-agent pipeline**
- Parallel execution for speed  
- Context-aware using **RAG (Retrieval-Augmented Generation)**

### 🔸 Flow


- Steps:
1. Index documents/transcripts  
2. Generate RAG context  
3. Run **Blueprint** & **Crawler** in parallel  
4. Run **Optimizer** & **Echo** in parallel  
5. Synthesize final report  
6. Generate **dashboard & action plan**

---

### 🧩 Backend API Overview (Flask)

| Endpoint | Method | Description |
|-----------|--------|-------------|
| `/` | GET | Serve frontend |
| `/api/health` | GET | Liveness probe |
| `/api/init` | GET/POST | Initialize orchestrator |
| `/api/agents` | GET | List available agents |
| `/api/upload` | POST | Upload project files |
| `/api/process` | POST | Start full processing pipeline |
| `/api/status` | GET | Check progress |
| `/api/results` | GET | Retrieve all results |
| `/api/synthesis/{dashboard|action-plan}` | GET | Generate reports |
| `/api/export/pdf` | GET | Export final PDF report |

---

## 🧩 Agents Breakdown

### 🧱 BlueprintAgent
- Model: `gemini-2.5-flash`
- Output: ASCII architecture diagram + detailed explanation

### 🕵️ CrawlerAgent
- Tools: SerpAPI + GitHub API
- Finds: GitHub repos, academic papers, trends
- Stores results in `data/crawler_results.json`

### 🧠 OptimizerAgent
- Uses RAG context for targeted improvement suggestions
- Optimizes architecture, cost, scalability, and strategy

### ⚔️ EchoAgent
- Simulates contrarian viewpoint
- Detects weak assumptions, risks, and echo chambers

### 🧩 SynthesisAgent
- Merges all results into a structured, multi-section report
- Generates PDF + dashboard via `ReportLab`

---

## 🧠 RAG Subsystem

- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector DB**: FAISS (`IndexFlatIP` with cosine similarity)
- **Documents Supported**: `.txt`, `.pdf`, `.docx`, `.doc`
- **Chunking**: ~500 words with 50 overlap
- **Retriever**: semantic context fetch for agents

---

## 🖥️ Frontend Interface

- Multi-tab interface for:
- Project overview  
- Blueprint  
- Optimizations  
- Echo analysis  
- Final synthesized report  

> Served by Flask from `frontend/templates/index.html` and `frontend/static/`.

---

## 🧰 Setup Instructions

# Optimizer - AI-Powered Startup Assistant

AI-powered ideation, optimization, and self-challenge assistant for small startups.


1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
GEMINI_API_KEY_1=your_gemini_key_1
GEMINI_API_KEY_2=your_gemini_key_2
GEMINI_API_KEY_3=your_gemini_key_3
GEMINI_API_KEY_4=your_gemini_key_4
GEMINI_API_KEY_5=your_gemini_key_5
SERPAPI_KEY=your_serpapi_key
```

3. Build FAISS index:
```bash
python scripts/build_index.py
```

4. Run the application:
```bash
python backend/app.py
```

5. Open http://localhost:5000 in your browser

## Usage

1. Upload startup documents, transcripts, and additional info
2. The system will process through all agents:
   - Index documents in vector DB
   - Generate blueprints and flowcharts
   - Research similar projects
   - Optimize ideas and challenge assumptions
   - Synthesize final report
3. View results in multi-tab interface

## Project Structure
```
optimizer/
├─ backend/
│  ├─ app.py             # Flask app + endpoints
│  ├─ orchestrator.py    # coordinates agents
│  ├─ agents/            # All AI agents
│  ├─ rag/              # RAG system
│  ├─ db/               # FAISS index
│  └─ data/             # Crawler results
├─ frontend/            # Web interface
├─ scripts/            # Utility scripts
└─ requirements.txt

```




