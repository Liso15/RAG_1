# Context-Aware RAG System

A production-ready RAG system that enforces strict character budgets for agentic AI context windows, ensuring optimal performance under token constraints.

## Design Decisions

### 1. Budget Allocation Strategy
- **Instructions (255 chars)**: Core system behavior - kept minimal to maximize space for dynamic content
- **Goal (1,500 chars)**: Current objective - largest allocation as it drives retrieval and reasoning
- **Memory (55 chars)**: Session state compression - forces prioritization of critical user preferences
- **Retrieval (550 chars)**: External knowledge - balanced between relevance and context diversity  
- **Tool Outputs (855 chars)**: Action results - sized for 2-3 realistic tool responses

### 2. Truncation and Prioritization Rules
- **Sentence Boundary Preservation**: Never split sentences mid-way to maintain semantic coherence
- **Relevance-Based Ranking**: Retrieval chunks sorted by semantic similarity, lowest scores truncated first
- **Memory Compression**: Key-value pairs compressed with abbreviations (e.g., "user_pref:CLI")
- **Graceful Degradation**: Empty sections filled with descriptive placeholders, not left blank

### 3. Retrieval Strategy
- **Hybrid Approach**: Semantic similarity via embeddings + keyword matching for precision
- **Chunk Size**: 500 characters to balance granularity with context coherence
- **Re-ranking**: Fetch top-10 chunks, then select best-fitting content within 550-char budget
- **Fallback Logic**: Returns "[No relevant documents found]" rather than failing silently

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python main.py --query "How do I restart the server safely?"
```

### Verbose Mode (Recommended)
```bash
python main.py --query "Emergency shutdown procedure" --verbose
```

### Custom Instructions and Goal
```bash
python main.py \
  --query "Database maintenance" \
  --instructions "You are a senior DevOps engineer" \
  --goal "Guide junior engineers through complex procedures with safety checks" \
  --verbose
```

## Worked Example

**Input Query**: "How do I restart the server safely?"

**Raw Retrieval Results** (before budget enforcement):
- Chunk 1 (487 chars): "Server restart procedure: Step 1 - Check system load using 'top' command..."
- Chunk 2 (312 chars): "Critical: Never restart during peak hours (9AM-5PM EST)..."
- Chunk 3 (298 chars): "Expected downtime: 30-60 seconds. Monitor logs for 5 minutes..."

**Budget Enforcement**:
- Total available: 550 chars
- Selected: Chunk 1 (487) + partial Chunk 2 (63 chars) = 550 chars exactly
- Truncation: Chunk 2 cut at sentence boundary: "Critical: Never restart during peak hours"

**Final Context Window**:
```
INSTRUCTIONS: You are a helpful operations assistant.

GOAL: Help the user with operational procedures and troubleshooting.

MEMORY: user_pref:CLI;last_action:restart

RETRIEVAL: Server restart procedure: Step 1 - Check system load using 'top' command. If CPU usage exceeds 90%, wait for processes to complete. Step 2 - Notify team via Slack #ops channel. Step 3 - Execute 'sudo systemctl restart apache2'. Step 4 - Monitor logs for 5 minutes using 'tail -f /var/log/apache2/error.log'. Step 5 - Verify service status with 'systemctl status apache2'. Expected downtime: 30-60 seconds. Critical: Never restart during peak hours

TOOL_OUTPUTS: search_logs: Found 3 ERROR entries in last 24h | check_status: Service running, CPU 45%, Memory 67% | get_config: timeout=30s, retry=3, debug=false
```

## Budget Exceeded Scenario

When retrieval finds 1,200 characters but budget allows only 550:

1. **Ranking**: All chunks scored by semantic similarity to query
2. **Selection**: Highest-scoring chunks selected first
3. **Truncation**: When adding next chunk would exceed budget, attempt partial inclusion at sentence boundary
4. **Fallback**: If no complete sentences fit, truncate at word boundary with "..." indicator

**Example Output**:
```
RETRIEVAL: Server restart procedure: Step 1 - Check system load. Step 2 - Notify team. Step 3 - Execute restart command. Monitor logs carefully. Critical: Never restart during peak hours (9AM-5PM EST). Expected downtime varies by system load...
```

## Agent Consumption Pattern

An agentic system would parse this structured context to understand:

1. **Instruction Hierarchy**: Instructions > Goal > Retrieval > Memory > Tool Outputs
2. **Action Prioritization**: Goal drives what actions to take, Retrieval provides how-to knowledge
3. **Context Awareness**: Memory maintains user preferences across interactions
4. **Current State**: Tool Outputs show system status for informed decision-making

## Architecture

```
Query Input
    ↓
Vector Store (ChromaDB)
    ↓
Semantic Retrieval (Top-K)
    ↓
Relevance Ranking
    ↓
Budget Enforcement
    ↓
Context Assembly
    ↓
Structured Output
```

## Key Features

- **Mathematical Budget Enforcement**: Pydantic validators ensure hard character limits
- **Semantic Chunking**: Preserves sentence boundaries for coherent context
- **Session Memory**: Compressed key-value storage for user preferences
- **Rich CLI Output**: Color-coded budget usage and section breakdown
- **Graceful Degradation**: Handles empty sections and oversized content elegantly

## Testing the System

1. **Normal Operation**: `python main.py --query "server restart" --verbose`
2. **Budget Stress Test**: Use very long goal (>1500 chars) to see truncation
3. **Empty Retrieval**: Query for non-existent topic to see fallback behavior
4. **Memory Overflow**: Add many memory items to test 55-char compression

This system demonstrates production-ready constraint handling for agentic AI applications where context window management is critical for performance and cost optimization.