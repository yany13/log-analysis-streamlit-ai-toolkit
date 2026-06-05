# Log Analysis AI Toolkit

A modern, modular Streamlit-based tool for intelligent log analysis using AI and vector embeddings. Perform hybrid root cause analysis by correlating logs, knowledge bases, and web search results.

## Features

- 📄 **Log Ingestion & Search** - Upload logs, search by patterns, explore context
- 🧠 **Expert RCA** - Hybrid root cause analysis combining logs, KB, and web search
- 📚 **Knowledge Base** - Index runbooks and documentation for intelligent correlation
- 🤖 **Multi-LLM Support** - Works with Ollama (local), OpenAI, and Hugging Face
- 🔍 **Semantic Search** - Vector-based similarity search on log content
- 📊 **Pattern Analysis** - Identify and analyze recurring issues
- 📥 **PDF Export** - Generate RCA reports as PDF documents
- 🛠️ **Database Management** - Inspect and manage indexed content

## Project Structure

```
log-analysis-streamlit-ai-toolkit/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── config/
│   └── settings.py            # Configuration constants
├── utils/
│   ├── database.py            # ChromaDB operations
│   ├── llm_engines.py         # LLM initialization
│   ├── embeddings.py          # Embedding engine setup
│   ├── pdf_generator.py       # PDF report generation
│   └── search.py              # Web search utilities
├── components/
│   ├── sidebar.py             # Sidebar configuration UI
│   ├── log_analysis_tab.py    # Log analysis features
│   ├── knowledge_base_tab.py  # Knowledge base management
│   └── maintenance_tab.py     # Database maintenance
├── data/
│   ├── sample_logs/           # Sample log files
│   └── sample_kb/             # Sample knowledge base
├── docker/
│   ├── Dockerfile             # Container image definition
│   └── docker-compose.yml     # Docker Compose setup
└── logs/                      # Application logs directory
```

## Quick Start

### Local Setup

1. **Clone & Install Dependencies**
   ```bash
   cd log-analysis-streamlit-ai-toolkit
   pip install -r requirements.txt
   ```

2. **Run with Ollama (Recommended)**
   - Start Ollama: `ollama serve`
   - In another terminal: `ollama pull gemma3:4b llama3.2 nomic-embed-text`
   - Run the app: `streamlit run app.py`

3. **Or use Docker**
   ```bash
   cd docker
   docker-compose up --build
   ```
   - Ollama will be available at `http://localhost:11434`
   - App will be available at `http://localhost:8501`

### Configuration

Configure via the sidebar:
- **LLM Provider**: Ollama (Local), OpenAI, or Hugging Face
- **Models**: Select appropriate models for expert RCA and log summarization
- **Temperature**: Adjust reasoning vs. creativity (0.0 = deterministic)
- **Embedding Engine**: Choose embedding provider and model

## Usage

### 📄 Log Analysis Tab

1. **Upload Logs** - Drag/drop or select log files
2. **Pattern Analysis** - Search for specific patterns (e.g., "ERROR", "WARN")
3. **Context Explorer** - Query logs with semantic search
4. **Run RCA** - Describe an incident to get hybrid root cause analysis

### 📚 Knowledge Base Tab

1. **Upload Runbooks** - Add documentation, troubleshooting guides, or runbooks
2. **Auto-Indexing** - Documents are automatically chunked and embedded
3. **RCA Integration** - KB context is automatically included in RCA queries

### 🛠️ Maintenance Tab

- **View Inventory** - See all indexed logs and KB documents
- **Delete Records** - Remove specific files or clear entire databases
- **Database Management** - Maintain clean, organized vector databases

## Configuration Files

### `config/settings.py`
Core configuration constants:
- Database paths
- Default models per provider
- Text splitting parameters
- Search thresholds

### Environment Variables
- `OLLAMA_URL` - Ollama server URL (default: `http://localhost:11434`)

## Dependencies

Key libraries:
- **streamlit** - Web UI framework
- **chromadb** - Vector database
- **langchain** - LLM & embedding abstractions
- **fpdf2** - PDF generation
- **duckduckgo-search** - Web search

## Architecture Highlights

### Modular Design
- **config/** - Centralized settings
- **utils/** - Reusable business logic
- **components/** - UI components (one per feature)

### Separation of Concerns
- Database operations isolated in `utils/database.py`
- LLM interactions in `utils/llm_engines.py`
- UI tabs in separate component files

### Easy to Extend
Add new features by:
1. Creating utility functions in `utils/`
2. Creating a new component in `components/`
3. Importing and calling from `app.py`

## Performance Tips

- **Chunking**: Adjust `CHUNK_SIZE` in settings for better semantic search
- **Embedding Model**: Smaller models (e.g., `nomic-embed-text`) are faster
- **Temperature**: Lower values (0.0-0.3) for consistent analysis
- **Database**: ChromaDB stores locally, no remote calls needed

## Troubleshooting

### Ollama Connection Issues
- Verify Ollama is running: `curl http://localhost:11434/api/tags`
- Check `OLLAMA_URL` environment variable
- Models need `ollama pull <model-name>` first

### Memory Issues
- Reduce `MAX_SEARCH_RESULTS` in settings
- Use smaller embedding models
- Clear database via Maintenance tab

### API Key Issues
- OpenAI: Set valid key in sidebar
- Hugging Face: Set valid token in sidebar
- Check billing/quota limits

## License

[Your License Here]

## Support

For issues, questions, or contributions, please open an issue or contact the development team.
