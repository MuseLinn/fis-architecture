# FIS Architecture 3.1 Lite

[![Version](https://img.shields.io/badge/version-3.1.3-blue.svg)](./package.json)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

> **Federal Intelligence System (FIS) 3.1 Lite**
> 
> OpenClaw Multi-Agent Collaboration Framework - File-First Architecture + Zero Core File Pollution

## 🌟 Core Features

- **Zero Core File Pollution** - Never modify other agents' `MEMORY.md` / `HEARTBEAT.md`
- **File-First Architecture** - No services/databases, pure JSON + Python
- **Three-Tier Shared Memory** - working (1h) / short_term (24h) / long_term (permanent)
- **Deadlock Detection** - DFS-based cycle detection for task dependencies
- **Skill Registry** - Dynamic capability discovery across agents
- **SubAgent Lifecycle** - Badge system with automatic cleanup
- **Phase 2/3 Framework** - Knowledge graph and access control (optional activation)

## 📦 Installation

### From ClawHub (Recommended)
```bash
clawhub install fis-architecture@3.1.3
```

### From Source
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/MuseLinn/fis-architecture.git
```

### Initialize
```bash
python3 ~/.openclaw/workspace/skills/fis-architecture/examples/init_fis31.py
```

## 🚀 Quick Start

### 1. Create SubAgent

```python
from subagent_lifecycle import SubAgentLifecycleManager, SubAgentRole

manager = SubAgentLifecycleManager("coordinator")  # Your coordinator name

# Issue badge
card = manager.spawn(
    name="Worker-001",
    role=SubAgentRole.WORKER,
    task_description="Your task here",
    timeout_minutes=120
)

print(f"Badge ID: {card['employee_id']}")
# Output: COORDINATOR-SA-2026-0001
```

### 2. Generate Badge Image

```python
# Single badge
image_path = manager.generate_badge_image(card['employee_id'])

# Batch badges (2x2 grid)
multi_image = manager.generate_multi_badge_image([id1, id2, id3, id4])
```

### 3. Terminate (Auto-Cleanup)

```python
# Terminate SubAgent (auto-deletes workspace)
manager.terminate(card['employee_id'], "completed")
# ✅ Workspace folder automatically cleaned
```

### 4. Shared Memory

```python
from memory_manager import write_memory, query_memory

# Write
write_memory(
    agent="worker",                    # Your agent name
    content={"result": data, "score": 0.95},
    layer="short_term",
    tags=["project", "task-001"]       # Your tags
)

# Query
results = query_memory(
    query="project task",              # Your query
    agent_filter=["worker"],           # Your agents
    limit=5
)
```

## 📚 Documentation

- **[SKILL.md](./SKILL.md)** - Full architecture documentation
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Quick reference guide
- **[examples/](./examples/)** - Usage examples

## 🏗️ Architecture

```
~/.openclaw/
├── workspace/                    # Your coordinator workspace
│   ├── MEMORY.md                 # Core File
│   ├── HEARTBEAT.md              # Core File
│   └── .fis3.1/                 # FIS 3.1 extension
│
├── workspace-agent1/             # Your agent 1 workspace
│   └── .fis3.1/
│       └── skill_manifest.json  # Your skill manifest
│
└── research-shared-hub/          # Your Shared Hub
    ├── .fis3.1/                 # FIS 3.1 shared infrastructure
    │   ├── lib/                 # Python libraries
    │   ├── memories/            # Shared memory
    │   ├── skills/              # Skill registry
    │   ├── heartbeat/           # Heartbeat status
    │   └── experimental/        # Phase 2/3 framework
    └── tickets/                 # Task tickets
```

## 🔒 Privacy-First Design

**This skill provides framework tools only. Your data stays in your workspace.**

- Framework code deploys to shared hub
- Knowledge graph nodes, memories, and agent configs are created in YOUR local workspace
- Your data is never shared or uploaded

## 🔄 Changelog

### 3.1.3 (2026-02-18)
- ✅ Complete generalization - removed personal config examples
- ✅ Removed unrelated utilities
- ✅ All examples now use generic placeholders
- ✅ Privacy-first design

### 3.1.0 (2026-02-17)
- 🎉 FIS 3.1 Lite initial release
- File-first architecture
- SubAgent badge system
- Three-tier shared memory
- Deadlock detection
- Skill registry

## 🤝 Contributing

Issues and PRs welcome!

## 📄 License

[MIT](./LICENSE)

---

*FIS 3.1 Lite — Quality over Quantity 🐱⚡*
