# System Directive: Log Analysis AI Toolkit

**Role**: AI Agent & RAG System Developer  
**Target Audience**: Backend Engineers, ML Engineers, DevOps (building AI-assisted diagnostics)  
**User Persona**: ML/Backend architect (Prefers architecture-first, robust validation, measurable accuracy)  
**Current Date Context**: June 2026

**Status**: v1.0.0 (Core RAG pipeline complete; structured output & testing in progress)

---

## 📌 Implementation Status

### ✅ Complete
- RAG pipeline: retrieval + augmentation + generation
- Multi-provider support (Ollama, OpenAI, Hugging Face)
- ChromaDB vector storage for logs and knowledge base
- Log ingestion with timestamp extraction
- Semantic search (hybrid: exact match + fallback to embedding-based)
- Web search integration (DuckDuckGo)
- PDF report export
- Docker deployment with health checks

### ⚠️ In Progress / Gaps
- **Structured LLM output** — Currently returns raw text; need JSON parsing for confidence, evidence, remediation
- **Sample knowledge base** — `data/sample_kb/` is empty; needs 5 runbooks (db_leak, ldap_timeout, oom, deadlock, ssl)
- **Test framework** — No integration tests against ByteBite failures
- **Retrieval tuning** — Chunk size (1000) and similarity threshold (0.15) are defaults; need per-failure-type optimization
- **Prompt engineering** — Current prompt is generic; needs structured reasoning and chain-of-thought guidance

---

## 🔗 Part of 3-Project Ecosystem

The Streamlit Toolkit is one of three interconnected projects teaching **AI Agents for Production Troubleshooting**:

| Project | Purpose | Role |
|---------|---------|------|
| **log-analysis-ai-usecase-app** | Generates failure logs | 🧪 Lab producing realistic failures |
| **log-analysis-streamlit-ai-toolkit** (this) | Analyzes logs with AI | 🤖 Agent diagnosing failures |
| **log-analysis-book** | Teaches the approach | 📚 Educational resource connecting both |

**Your responsibility**: Build an AI agent that accurately diagnoses failures from logs using RAG + LLM reasoning.

**Cross-project references**:
- App generates logs you analyze → understand log format, failure signatures, diagnostic breadcrumbs
- Book uses your agent in chapters 9-12 → ensure outputs are clear, confidence scores are meaningful
- See `../log-analysis-ai-usecase-app/CLAUDE.md` for log format and failure signatures
- See `../log-analysis-book/CLAUDE.md` for how chapters use your agent

---

## ⛔ CRITICAL RESPONSE RULES (STRICT COMPLIANCE REQUIRED)

1. **RAG Architecture First**: Always explain retrieval strategy *before* writing prompts. Good retrieval beats good prompting.
2. **Validation Required**: Every agent output must be testable against known root causes from ByteBite failures.
3. **Confidence Matters**: Provide confidence scores and explain uncertainty. Overconfident agents are worse than uncertain ones.
4. **Prompt Clarity**: Prompts must include actual log excerpts and context, not just descriptions.
5. **Testing Mandatory**: Test against all 5 ByteBite failure types before declaring feature complete.
6. **Modular Design**: Keep retrieval, prompting, and validation as separate, testable components.

---

## 🎯 Agent Purpose & Core Loop

The Streamlit Toolkit is an AI Agent that diagnoses production failures:

**Input**: Log files (from ByteBite or production)  
**Process**: 
1. Ingest logs → chunk and embed
2. Search knowledge base (semantic) + search logs (semantic)
3. Pass relevant context to LLM
4. LLM performs chain-of-thought reasoning for RCA
5. Return diagnosis with confidence scores

**Output**: Root cause analysis with remediation recommendations

**Key constraint**: Agent must be verifiable. Diagnosis must explain *why* the root cause is correct, not just state it.

---

## 🏗️ Architecture & Implementation

### Current Stack
- **Frontend**: Streamlit 1.55.0 (3 tabs: Log Analysis, Knowledge Base, Maintenance)
- **Vector DB**: ChromaDB 1.5.5 (persistent, local, two collections: logs & KB)
- **LLM Backends**: LangChain abstractions for Ollama/OpenAI/HuggingFace
- **Embeddings**: Multi-provider (Ollama, OpenAI, HuggingFace)
- **Deployment**: Docker Compose with health checks

### Key Files & Responsibilities

| File | Purpose | Status |
|------|---------|--------|
| `app.py` | Streamlit entry point, tab orchestration | ✅ Complete |
| `components/sidebar.py` | LLM/embedding config UI | ✅ Complete |
| `components/log_analysis_tab.py` | RCA workflow (ingest → search → analyze) | ⚠️ Output parsing needed |
| `components/knowledge_base_tab.py` | KB file upload & chunking | ✅ Complete |
| `components/maintenance_tab.py` | Database management UI | ✅ Complete |
| `utils/database.py` | ChromaDB operations | ✅ Complete |
| `utils/embeddings.py` | Embedding factory | ✅ Complete |
| `utils/llm_engines.py` | LLM factory + provider abstraction | ✅ Complete |
| `utils/search.py` | DuckDuckGo web search wrapper | ✅ Complete |
| `utils/pdf_generator.py` | PDF report generation | ✅ Complete |
| `config/settings.py` | Constants & defaults | ⚠️ Tuning parameters needed |
| `data/sample_kb/` | Knowledge base runbooks | ❌ Empty (populate with 5 KB docs) |

---

## 🧠 Architecture & Design Principles

### Retrieval-Augmented Generation (RAG)

The agent uses RAG for accuracy:
- **Retrieval**: Semantic search on logs + knowledge base
- **Augmentation**: Pass top-K results as context to LLM
- **Generation**: LLM reasons about root cause using context

**Critical**: Better retrieval beats better prompting. Optimize retrieval first.

### Knowledge Base Design

The knowledge base should include:
- **Runbooks**: Step-by-step diagnostic procedures for each failure type
- **Log patterns**: Known signatures and their meanings (e.g., `⚠️ Connection leak scenario`)
- **Remediation**: How to fix each failure type
- **Architecture docs**: System components, failure modes, dependencies

**Tagging strategy**: Tag by failure type (db_leak, ldap_timeout, oom, deadlock, ssl) so semantic search can find relevant context.

### Retrieval Tuning Parameters

Current defaults (in `config/settings.py`):
```python
CHUNK_SIZE = 1000          # Log/KB chunk size (bytes)
CHUNK_OVERLAP = 100        # Overlap between chunks
SIMILARITY_THRESHOLD = 0.15  # Min embedding similarity
MAX_SEARCH_RESULTS = 10    # Top-K results to retrieve
```

**Optimization strategy**:
- **For db_leak**: Tune to capture "Available connections: X" patterns → may need smaller chunks (500-700 chars)
- **For deadlock**: Need larger context (thread dumps are verbose) → 1500+ chars
- **For ldap_timeout**: Threshold may need raising (0.25+) to reduce noise
- **For oom**: OOM stack traces are distinctive; standard settings should work

### Prompting Strategy

**Current state**: Generic prompt in `log_analysis_tab.py` line 168-173  
**Needed**: Structured prompt requesting JSON output

Target prompt structure:
```python
prompt = f"""
Diagnose the root cause from these logs and knowledge base context.

LOGS (Top-K most relevant):
{log_context}

KNOWLEDGE BASE (Runbooks & past solutions):
{kb_context}

EXTERNAL CONTEXT:
{web_context}

ANALYSIS INSTRUCTIONS:
1. Identify symptoms (what log entries indicate problems?)
2. Form hypothesis (which failure type matches the symptoms?)
3. Rate confidence 0-100%:
   - 95-100%: Clear evidence, distinctive error messages
   - 80-94%: Strong indicators but some ambiguity
   - 60-79%: Multiple plausible causes
   - <60%: Insufficient evidence
4. List evidence (specific log lines that support this conclusion)
5. Explain uncertainty (what could change this diagnosis?)
6. Recommend remediation steps

Return ONLY valid JSON:
{{
  "root_cause": "...",
  "confidence": 0.95,
  "confidence_reasoning": "...",
  "evidence": ["log excerpt 1", "log excerpt 2"],
  "uncertainty": "...",
  "remediation": ["step 1", "step 2"]
}}
"""
```

**Implementation note**: After calling LLM, parse response with:
```python
def parse_rca_response(llm_text):
    """Extract JSON from LLM response, fallback to raw text."""
    try:
        import json
        json_match = re.search(r'\{.*\}', llm_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return {"raw_response": llm_text, "confidence": 0.0, "parsed": False}
```

---

## 🧪 Testing Against ByteBite Failures

Before merging features, test against all 5 ByteBite failure types:

### Test Protocol

```bash
# 1. Trigger each failure in ByteBite
curl "http://localhost:8080/bytebite/api/menu?failureType=db_leak"
curl "http://localhost:8080/bytebite/login?failureType=ldap_timeout" -d "user=admin&pass=admin"
curl "http://localhost:8080/bytebite/api/analytics?failureType=oom"
curl -X POST "http://localhost:8080/bytebite/api/kds" -d '{"failureType":"deadlock"}'
curl -X POST "http://localhost:8080/bytebite/checkout" -d '{"failureType":"ssl"}'

# 2. Export logs from each failure
docker-compose -f ../log-analysis-ai-usecase-app/docker-compose.yml logs tomcat > failure_logs.txt

# 3. Upload to toolkit and run RCA
# (Use Streamlit UI)

# 4. Verify diagnosis
# - Does it correctly identify the failure type?
# - Does confidence score reflect certainty? (high for clear failures, lower for ambiguous)
# - Does evidence point to actual log lines?
# - Are remediation steps correct?
```

### Success Criteria

| Failure Type | Accuracy Target | Notes |
|---|---|---|
| db_leak | 95%+ | HikariCP messages are clear |
| ldap_timeout | 95%+ | LDAP error messages are distinctive |
| oom | 90%+ | OOM is obvious, but may need heap context |
| deadlock | 85%+ | Requires thread dump analysis, more nuanced |
| ssl | 90%+ | Certificate errors are explicit |

---

## 📂 Key Architecture Files

Refer to or modify:

* **Entry Point**: `app.py` - Streamlit UI and main flow
* **Retrieval**: `utils/database.py` (ChromaDB operations)
* **LLM Reasoning**: `utils/llm_engines.py` (prompt execution, parsing)
* **Components**: `components/log_analysis_tab.py` (RCA workflow)
* **Knowledge Base**: `data/sample_kb/` (runbooks, patterns, remediation)

---

## 🔍 Validation & Confidence Scoring

### Target Output Format (WIP)

The RCA should output structured JSON:
```json
{
  "root_cause": "Connection pool exhaustion in HikariCP",
  "confidence": 0.95,
  "confidence_reasoning": "Clear HikariCP messages + persistent 'Available connections: 0' pattern in logs",
  "evidence": [
    "Available connections: 0 (line 2847)",
    "Connection not available, timeout after 30000ms (line 2852)",
    "MenuServlet making repeated DB calls without closing (code review)"
  ],
  "uncertainty": "Could be coincident with network latency; need to confirm connection closure code",
  "remediation": [
    "1. Restart service to reset connection pool (immediate)",
    "2. Code review: find unclosed connection in MenuServlet (urgent)",
    "3. Add try-with-resources or finally block to ensure cleanup (fix)",
    "4. Add monitoring for available connections < 5 (prevention)"
  ]
}
```

**Status**: Format defined; LLM output parsing not yet implemented (see `utils/llm_engines.py` for where to add parsing)

### When to Distrust Agent Outputs

Red flags:
- Confidence 100% (overconfident)
- Multiple plausible root causes but agent doesn't mention alternatives
- Evidence points to wrong log lines
- Remediation doesn't match the root cause

When you see these, iterate on prompts or retrieval.

---

## 📊 Evaluation Metrics

Track these metrics per failure type:

| Metric | How | Target |
|---|---|---|
| **Accuracy** | Correct root cause diagnosis | 90%+ |
| **Confidence Calibration** | High confidence = high accuracy | Spearman > 0.8 |
| **Latency** | Time to generate diagnosis | < 10 seconds |
| **Recall** | Agent finds relevant log lines | 85%+ |
| **Precision** | Retrieval doesn't include noise | 80%+ |

---

## 🔧 Development Best Practices

### 1. Modular Components
- Retrieval logic separate from prompting
- Prompting separate from parsing
- Each testable independently

### 2. Fail Gracefully
- If LLM response can't be parsed, return raw response + warning
- If retrieval finds nothing, tell user (don't hallucinate)
- If confidence is low, say so explicitly

### 3. Iterate on Evidence
- When agent gets a diagnosis wrong, collect evidence
- Did retrieval miss relevant logs? Fix retrieval.
- Did prompt mislead the LLM? Fix prompt.
- Did LLM hallucinate? Try different model or lower temperature.

### 4. Document Decisions
- Why did you choose this embedding model?
- Why this chunk size?
- Why this prompt structure?
- These decisions affect accuracy—document trade-offs.

---

## 🧪 Testing & Validation Strategy

### Unit Tests
- Test retrieval independently (does it find the right logs?)
- Test prompt formatting (are variables substituted correctly?)
- Test response parsing (does it extract confidence, evidence, remediation?)

### Integration Tests
- Run against all 5 ByteBite failure types (see Testing Against ByteBite Failures above)
- Measure accuracy per failure type
- Track confidence calibration

### Before Shipping
```
✓ All unit tests pass
✓ Integration tests pass (accuracy >= targets)
✓ Manually verified against ByteBite failures
✓ Confidence scores are calibrated (0.95 confidence ≈ 95% accuracy)
✓ Documentation updated
✓ Performance acceptable (< 10s per diagnosis)
```

---

## 🔗 Key Failure Signatures (From ByteBite)

Know these signatures so you can tune retrieval:

| Failure | Log Breadcrumb | Key Signal |
|---|---|---|
| **db_leak** | `⚠️ Connection leak scenario` | `Available connections: 0` persists |
| **ldap_timeout** | `⚠️ LDAP Failure Injection: Simulating connection timeout` | Connection timeout message after ~30 seconds |
| **oom** | `⚠️ OOM FAILURE INJECTION` | `OutOfMemoryError: Java heap space` |
| **deadlock** | `❌ DEADLOCK SCENARIO: Both threads are now BLOCKED` | Thread names + lock names in circular pattern |
| **ssl** | `❌ SSL Certificate Validation Failed` | Certificate error messages |

These breadcrumbs help retrieval—tune chunking and embedding to capture them.

---

## 📚 Knowledge Base Content

**Status**: `data/sample_kb/` is currently empty; need to create 5 KB documents.

### Required Runbooks

For each failure type, create a markdown file in `data/sample_kb/`:

**1. db_leak_runbook.md**
```markdown
# Connection Pool Exhaustion (db_leak)

## Symptom
- Applications hang waiting for database connection
- Error: "Connection not available, request timed out after 30000ms"
- HikariCP logs show: "Available connections: 0"

## Root Cause
Connections not returned to pool. Usually:
- Unclosed statement or connection
- Exception before close() in try/finally
- Long-running transaction
- Missing try-with-resources

## Log Analysis
1. Look for: "Available connections: X" entries in HikariCP logs
2. Track if X drops over time → likely leak
3. Find which endpoint was active when pool exhausted
4. Search for error stacktraces in connection handling code
5. Review servlet code for try-finally or try-with-resources

## Log Signatures
- "⚠️ Connection leak scenario" (ByteBite marker)
- "Available connections: 0" (persists across requests)
- "Connection not available, timeout after 30000ms"
- "HikariPool.getConnection()" in stacktrace

## Remediation
1. Restart service (immediate)
2. Code review - find unclosed connection
3. Add try-with-resources
4. Monitor for available connections < 5
```

**2-5. Similar structure for**:
- `ldap_timeout_runbook.md` — LDAP errors, timeout patterns
- `oom_runbook.md` — OutOfMemoryError, heap analysis
- `deadlock_runbook.md` — Thread dumps, lock cycles
- `ssl_runbook.md` — Certificate errors, trust store

### Implementation
1. Create .md files in `data/sample_kb/`
2. Open Streamlit UI → Knowledge Base tab
3. Upload all 5 runbooks
4. Verify in "Indexed Documents" section

---

## 📖 Development Context

When building the agent, remember:

1. **Readers are using this**: Book chapters show how the agent works. Make output clear and educational.
2. **Logs are from ByteBite**: Understand the log format, failure signatures, and diagnostic breadcrumbs.
3. **Accuracy matters**: 85% accuracy is not good enough. Aim for 90%+.
4. **Confidence scores save lives**: An uncertain agent is better than an overconfident wrong answer.

You are building the AI expert. Make it one you'd trust in production.

---

## 🔄 Integration with Book Chapters

- **Chapter 9**: Toolkit architecture overview
- **Chapter 10**: Embedding and semantic search strategy
- **Chapter 11**: Prompting patterns and RCA workflow
- **Chapter 12**: Knowledge base design
- **Chapter 13**: End-to-end integration (app failure → agent diagnosis)

See `../log-analysis-book/CLAUDE.md` for how your code is used in teaching.

---

## 🚀 Development Priorities (Next Steps)

### Phase 1: Foundation (Weeks 1-2)
1. **Populate sample KB** — Create 5 runbooks in `data/sample_kb/` (db_leak, ldap_timeout, oom, deadlock, ssl)
2. **Build LLM output parser** — Add JSON parsing in `utils/llm_engines.py` with fallback to raw text
3. **Enhance prompt** — Update prompt in `log_analysis_tab.py` line 168-173 to request structured JSON + confidence

### Phase 2: Testing (Weeks 3-4)
1. **Create test framework** — Add integration tests against ByteBite failures
2. **Manual verification** — Run against all 5 failure types; verify accuracy >= targets
3. **Confidence calibration** — Collect results, measure confidence vs. accuracy

### Phase 3: Optimization (Weeks 5-6)
1. **Tune retrieval** — Experiment with chunk_size, overlap, similarity_threshold per failure type
2. **Ablation studies** — Measure impact of KB, web search, log retrieval separately
3. **Performance profiling** — Ensure diagnosis latency < 10 seconds

---

## 📋 Quick Reference: What Not To Do

**Anti-patterns that violate CLAUDE.md**:
- ❌ Return confidence 1.0 (100%) — always explain uncertainty
- ❌ Ignore retrieval quality — tune retrieval before tweaking prompts
- ❌ Merge features without testing against ByteBite failures
- ❌ Use generic prompts that don't request evidence or reasoning
- ❌ Hallucinate if retrieval returns nothing — tell the user instead
- ❌ Skip knowledge base population — KB quality directly impacts accuracy

---

## 🔧 How to Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Ollama (or point OLLAMA_URL to remote)
ollama serve

# 3. Pull recommended models
ollama pull llama3:latest
ollama pull nomic-embed-text

# 4. Run Streamlit app
streamlit run app.py

# 5. Open browser
# http://localhost:8501
```

**Environment variables**:
```bash
OLLAMA_URL=http://localhost:11434  # Ollama endpoint
OPENAI_API_KEY=...                 # If using OpenAI
```

**Or use Docker Compose**:
```bash
docker-compose up -d
# Streamlit: http://localhost:8501
# Ollama: http://localhost:11434
```
