# Log Analysis AI Toolkit - Documentation

This folder contains the Log Analysis AI Toolkit documentation, integrated with the ByteBite learning lab.

## Quick Links

- [Toolkit Architecture](./01-toolkit-architecture.md)
- [Semantic Search and Embeddings](./02-semantic-search.md)
- [LLM Integration Guide](./03-llm-integration.md)
- [Knowledge Base Management](./04-knowledge-base.md)

## Overview

The Log Analysis AI Toolkit provides a modern, AI-powered interface for analyzing application logs at scale. It works in conjunction with ByteBite (the failure injection lab) to provide hybrid root cause analysis combining:

- Manual log analysis
- Semantic (AI-powered) search
- Knowledge base retrieval
- Expert LLM analysis
- PDF report generation

## Features

- 📄 **Log Ingestion** - Upload and index logs automatically
- 🧠 **AI Analysis** - Expert RCA combining logs, KB, and web search
- 📚 **Knowledge Base** - Runbooks, past incidents, architecture docs
- 🤖 **Multi-LLM** - Ollama (local), OpenAI, Hugging Face support
- 🔍 **Semantic Search** - Find related incidents across your knowledge base
- 📊 **Pattern Analysis** - Identify recurring issues
- 📥 **PDF Export** - Generate incident reports

## Architecture Overview

```
Streamlit Web UI
    ↓
Log Processing & Analysis
    ├─ Semantic Search (Vector Embeddings)
    ├─ Knowledge Base Retrieval
    ├─ LLM Integration
    └─ Report Generation
    ↓
ChromaDB (Vector Store)
    ├─ Indexed Logs
    ├─ Knowledge Base Documents
    └─ Search Results
    ↓
LLM Backends
    ├─ Ollama (Local)
    ├─ OpenAI (Cloud)
    └─ Hugging Face (Cloud)
```

## Getting Started

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Start Ollama** (if using local): `ollama serve`
3. **Run the app**: `streamlit run app.py`
4. **Open browser**: http://localhost:8501

## Integration with ByteBite

The toolkit is designed to analyze logs from ByteBite failure scenarios:

1. Trigger a failure in ByteBite
2. Export logs from the container
3. Upload to the toolkit
4. Run hybrid RCA
5. Compare findings with expected root cause

## Configuration

Key environment variables:

- `OLLAMA_URL` - Ollama server (default: http://localhost:11434)
- `OPENAI_API_KEY` - OpenAI API key (if using OpenAI)
- `HF_TOKEN` - Hugging Face token (if using HF models)

## Documentation Structure

### For Users
- [Getting Started](./01-toolkit-architecture.md)
- [Using Semantic Search](./02-semantic-search.md)
- [Running RCA Analysis](./03-llm-integration.md)

### For Developers
- [Architecture Deep Dive](./01-toolkit-architecture.md)
- [Component API Reference](./03-llm-integration.md)
- [Adding Custom Integrations](./04-knowledge-base.md)

## Real-World Workflow

```
Incident Occurs in Production
         ↓
Capture logs from affected service
         ↓
Upload to AI Toolkit
         ↓
Run semantic search for anomalies
         ↓
Query knowledge base for similar incidents
         ↓
LLM generates root cause hypothesis
         ↓
Engineer validates and acts
         ↓
Update knowledge base with learnings
```

## Performance Characteristics

- **Log ingestion**: ~100 MB/minute
- **Semantic search**: <100ms for typical queries
- **RCA generation**: 10-30 seconds (depends on logs and LLM)
- **Vector database**: Local, no external calls needed for search

## Support

For questions or issues:
1. Check the relevant documentation chapter
2. See the main README.md for troubleshooting
3. Review the [ByteBite documentation](../log-analysis-ai-usecase-app/docs/) for context

## Version

- **Toolkit Version**: 1.0.0
- **Last Updated**: June 2026
- **Compatible with**: ByteBite v1.0.0+
