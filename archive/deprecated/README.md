# Deprecated Components (FIS 3.1)

These components were part of FIS 3.1 but have been **deprecated in FIS 3.2**.

## Why Deprecated?

FIS 3.2 adopts a simplified architecture where **QMD (Query Model Direct)** handles content management:

| Deprecated Component | Replacement | Reason |
|---------------------|-------------|--------|
| `memory_manager.py` | **QMD semantic search** | QMD provides native memory/retrieval |
| `skill_registry.py` | **SKILL.md + QMD** | QMD indexes SKILL.md files |
| `deadlock_detector.py` | **Simple conventions** | Rarely needed; conventions suffice |
| `subagent_lifecycle.py` | **Ticket files (JSON)** | Simpler, more transparent |

## Core Principle: FIS Manages Workflow, QMD Manages Content

```
FIS 3.2:               FIS 3.1 (deprecated):
tickets/               memories/ + skill_registry/
(JSON files)           (Python classes)
     ↓                        ↓
  Workflow               Workflow + Content
```

## What to Use Instead

### Instead of memory_manager.py

```bash
# Use QMD semantic search
mcporter call 'exa.web_search_exa(query: "your query", numResults: 5)'
```

Or use OpenClaw's native memory search:
```
Let me search my memory for that information...
```

### Instead of skill_registry.py

```bash
# QMD automatically indexes SKILL.md files
mcporter call 'exa.web_search_exa(query: "SKILL.md image processing", numResults: 5)'
```

### Instead of deadlock_detector.py

Follow these conventions:
1. Always set `timeout_minutes` in tickets
2. Archive completed tickets promptly
3. Use simple parent-child relationships (avoid complex graphs)

### Instead of subagent_lifecycle.py

Use ticket files directly:

```bash
# Create ticket
cat > tickets/active/TASK_001.json << 'EOF'
{
  "ticket_id": "TASK_001",
  "agent_id": "worker-001",
  "role": "worker",
  "task": "Description",
  "status": "active",
  "created_at": "2026-02-19T21:00:00",
  "timeout_minutes": 60
}
EOF

# Archive when done
mv tickets/active/TASK_001.json tickets/completed/
```

## Preserved for Reference

These files are kept for:
- Historical reference
- Migration guidance
- Understanding 3.1 → 3.2 evolution

**Do not use in new projects.**

---

*FIS 3.2.0-lite — Simplified architecture*
