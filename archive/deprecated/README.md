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
| `init_fis31.py` | **Manual directory creation** | No init needed in 3.2 |
| `setup_agent_extension.py` | **Not needed** | 3.2 has no extension system |
| `subagent_pipeline.py` | **Native sessions_spawn** | Use OpenClaw's native spawning |

## Core Principle: FIS Manages Workflow, QMD Manages Content

```
FIS 3.2:               FIS 3.1 (deprecated):
tickets/               memories/ + skill_registry/
(JSON files)           (Python classes + registries)
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

### Instead of init_fis31.py

```bash
# 3.2 needs no initialization — just create directories
mkdir -p ~/.openclaw/my-project/{tickets/active,tickets/completed,knowledge}
```

### Instead of subagent_pipeline.py

Use OpenClaw's native `sessions_spawn`:
```python
# OpenClaw native tool
sessions_spawn(task="Your task", agentId="worker")
```

Or FIS 3.2 tickets:
```bash
# Create a ticket to track the spawned session
echo '{"ticket_id":"TASK_001","openclaw_session":"sess_xxx","status":"active"}' > tickets/active/TASK_001.json
```

## File Manifest

### Core Libraries (lib/)
- `memory_manager.py` — Tiered memory system
- `skill_registry.py` — Skill discovery & registration
- `deadlock_detector.py` — DFS cycle detection
- `subagent_lifecycle.py` — SubAgent lifecycle management

### Examples (examples/)
- `init_fis31.py` — Initialization script
- `setup_agent_extension.py` — Agent extension setup
- `subagent_pipeline.py` — 3-role pipeline demo

## Preserved for Reference

These files are kept for:
- Historical reference
- Migration guidance
- Understanding 3.1 → 3.2 evolution

**Do not use in new projects.**

---

*FIS 3.2.0-lite — Simplified architecture*
