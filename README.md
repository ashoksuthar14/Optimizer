# Optimizer - AI-Powered Startup Assistant

AI-powered ideation, optimization, and self-challenge assistant for small startups.

## Problem Statement
Small startups often suffer from:
- Limited manpower to research, brainstorm, and optimize ideas
- Lack of diverse viewpoints (everyone agrees easily — groupthink)
- Missing opportunities to improve projects using free/open-source tools or automation

## Solution
Optimizer acts as an AI co-founder that:
- Builds blueprints, flowcharts, and project structures for new ideas
- Optimizes those ideas technically, financially, and strategically
- Challenges your team's thinking via an EchoChamber Breaker — an intelligent devil's advocate

## Architecture
- **BlueprintAgent**: Generates project blueprints and flowcharts
- **CrawlerAgent**: Researches similar projects on GitHub using SerpApi
- **OptimizerAgent**: Proposes optimizations and alternatives using RAG
- **EchoAgent**: Acts as devil's advocate to break echo chambers
- **SynthesisAgent**: Merges all outputs into final report

## Tech Stack
- **Backend**: Flask + LangChain
- **AI Models**: Multiple Gemini API keys (rate limit management)
- **Vector DB**: FAISS (local)
- **Embeddings**: sentence-transformers
- **Frontend**: HTML/CSS/JS with multi-tab interface

## Setup

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