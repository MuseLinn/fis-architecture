# FIS (Federal Intelligence System) Architecture Skill

> **Version**: 3.2.0-lite  
> **Name**: Federal Intelligence System (联邦智能系统)  
> **Description**: OpenClaw lightweight multi-agent collaboration framework — FIS manages workflow, QMD manages content  
> **Status**: ✅ Stable — Simplified architecture with QMD integration

---

## Core Principle: FIS Manages Workflow, QMD Manages Content

**FIS 3.2** is a radical simplification of FIS 3.1. We removed components that overlapped with QMD (Query Model Direct) semantic search capabilities:

| Component | FIS 3.1 | FIS 3.2 | Reason |
|-----------|---------|---------|--------|
| Task Management | Python classes + memory_manager | Ticket files (JSON) | Simpler, audit-friendly |
| Memory/Retrieval | memory_manager.py | **QMD** | QMD has native semantic search |
| Skill Discovery | skill_registry.py | **SKILL.md + QMD** | QMD indexes SKILL.md files |
| Knowledge Graph | experimental/kg/ | **QMD** | QMD covers knowledge discovery |
| Deadlock Detection | deadlock_detector.py | Simple conventions | Rarely needed in practice |

**What's Kept**: Only the unique workflow capabilities that FIS provides.

---

## What's New in 3.2.0

### Simplified Architecture
- **No Python dependencies** for core functionality — pure file-based workflow
- **Ticket system only** — JSON files for task tracking
- **QMD integration** — semantic search replaces custom registries
- **Badge generator** — beautiful visual identity for subagents (v7+)

### Directory Structure

```
research-uav-gpr/                    # Your shared hub
├── 📁 tickets/                      # Task workflow (FIS core)
│   ├── active/                      # Active tasks (JSON files)
│   └── completed/                   # Archived tasks
├── 📁 knowledge/                    # Shared knowledge (QMD-indexed)
│   ├── cybermao/                    # System knowledge
│   ├── fis/                         # FIS documentation
│   └── your-domain/                 # Your domain knowledge
├── 📁 results/                      # Research outputs
├── 📁 archive/                      # Archived old versions
│   ├── fis3.1-full/                 # Complete 3.1 backup
│   └── fis3.1-legacy/               # Legacy files
└── 📁 .fis3.1/                      # Light configuration
    └── notifications.json           # Event notifications
```

---

## Quick Start

### 1. Create a Task Ticket

```bash
# Create ticket manually or use helper
cat > ~/.openclaw/research-uav-gpr/tickets/active/TASK_EXAMPLE_001.json << 'EOF'
{
  "ticket_id": "TASK_EXAMPLE_001",
  "agent_id": "worker-001",
  "parent": "cybermao",
  "role": "worker",
  "task": "Analyze GPR signal patterns",
  "status": "active",
  "created_at": "2026-02-19T21:00:00",
  "timeout_minutes": 60,
  "resources": ["file_read", "code_execute"]
}
EOF
```

### 2. Generate Badge Image

```bash
cd ~/.openclaw/workspace/skills/fis-architecture/lib
python3 badge_generator_v7.py

# Output: ~/.openclaw/output/badges/TASK_*.png
```

### 3. Complete and Archive

```bash
# Move from active to completed
mv ~/.openclaw/research-uav-gpr/tickets/active/TASK_EXAMPLE_001.json \
   ~/.openclaw/research-uav-gpr/tickets/completed/
```

---

## Ticket Format

```json
{
  "ticket_id": "TASK_CYBERMAO_20260219_001",
  "agent_id": "worker-001",
  "parent": "cybermao",
  "role": "worker|reviewer|researcher|formatter",
  "task": "Task description",
  "status": "active|completed|timeout",
  "created_at": "2026-02-19T21:00:00",
  "completed_at": null,
  "timeout_minutes": 60,
  "resources": ["file_read", "file_write", "web_search"],
  "output_dir": "results/TASK_001/"
}
```

---

## Workflow Patterns

### Pattern 1: Worker → Reviewer Pipeline

```
CyberMao (Coordinator)
    ↓ spawn
Worker (Task execution)
    ↓ complete
Reviewer (Quality check)
    ↓ approve
Archive
```

**Tickets**:
1. `TASK_001_worker.json` → active → completed
2. `TASK_002_reviewer.json` → active → completed

### Pattern 2: Parallel Workers

```
CyberMao
    ↓ spawn 4x
Worker-A (chunk 1)
Worker-B (chunk 2)
Worker-C (chunk 3)
Worker-D (chunk 4)
    ↓ all complete
Aggregator (combine results)
```

### Pattern 3: Research → Execute

```
Researcher (investigate options)
    ↓ deliver report
Worker (implement chosen option)
    ↓ deliver code
Reviewer (verify quality)
```

---

## When to Use SubAgents

**Use SubAgent when**:
- Task needs multiple specialized roles
- Expected duration > 10 minutes
- Failure has significant consequences
- Batch processing of many files

**Direct handling when**:
- Quick Q&A (< 5 minutes)
- Simple explanation or lookup
- One-step operations

### Decision Tree

```
User Request
    ↓
┌─────────────────────────────────────────┐
│ 1. Needs multiple specialist roles?     │
│ 2. Duration > 10 minutes?               │
│ 3. Failure impact is high?              │
│ 4. Batch processing needed?             │
└─────────────────────────────────────────┘
    ↓ Any YES
Delegate to SubAgent
    ↓ All NO
Handle directly
```

---

## QMD Integration (Content Management)

**QMD (Query Model Direct)** provides semantic search across all content:

```bash
# Search knowledge base
mcporter call 'exa.web_search_exa(query: "GPR signal processing", numResults: 5)'

# Search for skills
mcporter call 'exa.web_search_exa(query: "SKILL.md image processing", numResults: 5)'
```

**Knowledge placement**:
- Drop Markdown files into `knowledge/` subdirectories
- QMD automatically indexes them
- No manual registration needed

---

## Tool Reference

### Badge Generator v7

**Location**: `lib/badge_generator_v7.py`

**Features**:
- Retro pixel-art avatar generation
- Full Chinese/English support
- Dynamic OpenClaw version display
- Task details with QR code + barcode
- Beautiful gradient design

**Usage**:
```bash
cd ~/.openclaw/workspace/skills/fis-architecture/lib
python3 badge_generator_v7.py

# Interactive prompts for task details
# Output: ~/.openclaw/output/badges/Badge_{TICKET_ID}_{TIMESTAMP}.png
```

### CLI Helper (Optional)

```bash
# Create ticket with helper
python3 fis_subagent_tool.py full \
  --agent "Worker-001" \
  --task "Task description" \
  --role "worker"

# Complete ticket
python3 fis_subagent_tool.py complete \
  --ticket-id "TASK_CYBERMAO_20260219_001"
```

---

## Migration from FIS 3.1

If you have FIS 3.1 components:

1. **Archived components** are in `archive/fis3.1-full/` and `archive/fis3.1-legacy/`
2. **Ticket files** remain compatible (JSON format unchanged)
3. **Skill discovery** — use QMD instead of `skill_registry.py`
4. **Memory queries** — use QMD instead of `memory_manager.py`

---

## Design Principles

1. **FIS Manages Workflow, QMD Manages Content**
   - Tickets for process state
   - QMD for knowledge retrieval

2. **File-First Architecture**
   - No services or databases
   - 100% file-based
   - Git-friendly

3. **Zero Core File Pollution**
   - Never modify other agents' MEMORY.md/HEARTBEAT.md
   - Extensions isolated to `.fis3.1/`

4. **Quality over Quantity**
   - Fewer, better components
   - Remove what QMD already provides

---

## Changelog

### 2026-02-19: v3.2.0-lite Simplification
- Removed: `memory_manager.py` → use QMD
- Removed: `skill_registry.py` → use SKILL.md + QMD
- Removed: `deadlock_detector.py` → simple conventions
- Removed: `experimental/kg/` → QMD covers this
- Kept: Ticket system, badge generator
- New: Simplified architecture documentation

### 2026-02-18: v3.1.3 Generalization
- Removed personal configuration examples
- GitHub public repository created

### 2026-02-17: v3.1 Lite Initial Deploy
- Shared memory, deadlock detection, skill registry
- SubAgent lifecycle + badge system

---

## File Locations

```
~/.openclaw/workspace/skills/fis-architecture/
├── SKILL.md                    # This file
├── README.md                   # Repository readme
├── QUICK_REFERENCE.md          # Quick command reference
├── AGENT_GUIDE.md              # Agent usage guide
├── lib/                        # Tools (not core)
│   ├── badge_generator_v7.py   # ✅ Kept: Badge generation
│   ├── fis_lifecycle.py        # ✅ Kept: Lifecycle helpers
│   ├── fis_subagent_tool.py    # ✅ Kept: CLI helper
│   ├── memory_manager.py       # ❌ Deprecated (QMD replaces)
│   ├── skill_registry.py       # ❌ Deprecated (QMD replaces)
│   └── deadlock_detector.py    # ❌ Deprecated
└── examples/                   # Usage examples
```

---

*FIS 3.2.0-lite — Minimal workflow, maximal clarity*  
*Designed by CyberMao 🐱⚡*
