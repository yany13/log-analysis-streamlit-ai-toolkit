# System Directive: Log Analysis AI Toolkit (CLAUDE.md)

**Role**: AI Agent & RAG System Developer  
**Target Audience**: Backend Engineers, ML Engineers, DevOps (building AI-assisted diagnostics)  
**User Persona**: ML/Backend architect (Prefers architecture-first, robust validation, measurable accuracy)  
**Current Date Context**: June 2026  

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

### Prompting Strategy

Prompts must:
1. **Include actual log excerpts** (not descriptions)
2. **Ask for structured reasoning** (symptoms → hypothesis → validation)
3. **Request confidence scores** (0-100%, with uncertainty explanation)
4. **Demand evidence** (which log lines support this conclusion?)

**Example**:
```
Given these log excerpts:
[LOGS HERE]

And this context from the knowledge base:
[KB CONTEXT HERE]

Diagnose the root cause. For each hypothesis:
1. State the symptom you observe
2. Explain why this indicates root cause X
3. Point to specific log evidence
4. Rate confidence 0-100%
5. Explain any uncertainty
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

### How Agents Report Confidence

Agents must output:
```json
{
  "root_cause": "Connection pool exhaustion in HikariCP",
  "confidence": 0.95,
  "uncertainty_explanation": "Clear evidence in logs, but could be coincident with network issue",
  "evidence": [
    "Log line 42: 'Available connections: 0'",
    "Log line 67: 'Connection not available, timeout after 30s'"
  ],
  "remediation": [
    "1. Restart service to reset connection pool",
    "2. Code review: find unclosed connection in MenuServlet",
    "3. Add try-with-resources to ensure cleanup"
  ]
}
```

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

Populate knowledge base with:

**For each failure type:**
1. **Symptom description** - What users see
2. **Root cause explanation** - Why it happens
3. **Log analysis steps** - How to diagnose manually
4. **Common patterns** - Log patterns to look for
5. **Remediation steps** - How to fix
6. **Prevention** - How to avoid in future

**Example (db_leak)**:
```
## Connection Pool Exhaustion

### Symptom
Applications hang waiting for database connection. 
Error: "Connection not available, request timed out after 30000ms"

### Root Cause
Connections not returned to pool. Usually: unclosed statement, exception before close(), 
or long-running transaction.

### Log Analysis
1. Look for: "Available connections: X" entries
2. Track if X drops over time → likely leak
3. Check which endpoint was active when pool exhausted
4. Review servlet code for try-finally or try-with-resources

### Remediation
1. Restart service (short-term)
2. Code review for connection handling (long-term)
3. Add monitoring for available connections < 5

### Prevention
- Always use try-with-resources or try-finally
- Never hold connections longer than necessary
- Load test to catch leaks before production
```

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
