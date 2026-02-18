# FIS 3.1 Lite - Quick Reference

## Quick Commands (快速命令)

### Initialize Environment (初始化环境)
```bash
python3 ~/.openclaw/workspace/skills/fis-architecture/examples/init_fis31.py
```

### Run 3-Role Pipeline Demo (运行三角色流水线示例)
```bash
python3 ~/.openclaw/workspace/skills/fis-architecture/examples/subagent_pipeline.py
```

---

## Python API

### 1. Shared Memory (共享记忆)
```python
from memory_manager import write_memory, query_memory

# Write (写入)
write_memory(
    agent="pulse",
    content={"key": "value"},
    layer="short_term",  # working/short_term/long_term
    tags=["gpr", "task-001"]
)

# Query (查询)
results = query_memory(
    query="gpr",
    agent_filter=["pulse"],
    limit=10
)
```

### 2. Deadlock Detection (死锁检测)
```python
from deadlock_detector import check_and_resolve

report = check_and_resolve(auto_resolve=False)
if report["deadlock_found"]:
    print(f"Deadlocks: {report['deadlocks']}")
```

### 3. Skill Registry (技能注册)
```python
from skill_registry import register_skills, discover_skills

# Register (注册)
with open('skill_manifest.json') as f:
    manifest = json.load(f)
register_skills("pulse", manifest)

# Discover (发现)
skills = discover_skills(query="SFCW")
```

### 4. SubAgent Lifecycle (子代理生命周期)
```python
from subagent_lifecycle import SubAgentLifecycleManager, SubAgentRole

manager = SubAgentLifecycleManager("cybermao")

# Create / Issue Badge (创建/发工卡)
card = manager.spawn(
    name="Worker-001",
    role=SubAgentRole.WORKER,  # WORKER/REVIEWER/RESEARCHER/FORMATTER
    task_description="Task details...",
    timeout_minutes=120,
    resources=["file_read", "file_write"]
)

# Activate (激活)
manager.activate(card['employee_id'])

# Display Badge (显示工卡)
print(manager.generate_badge(card['employee_id']))

# Heartbeat (心跳)
manager.heartbeat(card['employee_id'])

# Terminate (终止)
manager.terminate(card['employee_id'], "completed")

# List Active (列表)
active = manager.list_active()
```

---

## Badge ID Format (工号格式)

```
{PARENT}-SA-{YYYY}-{NNNN}

Examples:
- CYBERMAO-SA-2026-0001
- PULSE-SA-2026-0001
```

---

## Directory Structure (目录结构)

```
~/.openclaw/
├── research-uav-gpr/.fis3.1/     # Shared Infrastructure (共享基础设施)
│   ├── memories/{working,short_term,long_term}/
│   ├── skills/{registry.json,manifests/}
│   ├── lib/{*.py}
│   └── subagent_registry.json
│
├── workspace/.fis3.1/            # CyberMao Extension
├── workspace-radar/.fis3.1/      # Pulse Extension
│   └── skill_manifest.json
│
└── workspace-subagent_*/         # SubAgent Workspaces (子代理工作区)
    ├── AGENTS.md
    ├── TODO.md
    └── EMPLOYEE_CARD.json
```

---

## Design Principles (设计原则)

1. **Zero Core File Pollution (零污染 Core Files)**: Never modify other agents' MEMORY.md/HEARTBEAT.md
2. **File-First Architecture (纯文件机制)**: No services/databases, JSON + Python only
3. **Layered Permissions (分层权限)**: SubAgents access external resources only through parent
4. **Badge System (工卡系统)**: Elegant identity management with permission matrix

---

## Troubleshooting (故障排查)

### Check Registries (检查注册表)
```bash
cat ~/.openclaw/research-uav-gpr/.fis3.1/skills/registry.json
cat ~/.openclaw/research-uav-gpr/.fis3.1/subagent_registry.json
```

### Check SubAgent Workspaces (检查子代理工作区)
```bash
ls ~/.openclaw/workspace-subagent_*
```

### Run Maintenance (运行维护脚本)
```bash
~/.openclaw/system/scripts/fis_maintenance.sh check
```

---

## Task Router (任务路由) - 自动判断使用 SubAgent

### Quick Check (快速判断)
```python
from task_router import should_use_subagent, classify_task

# 判断是否应使用 SubAgent
if should_use_subagent("帮我整理 downloads 文件夹"):
    # 创建 SubAgent
    card = manager.spawn(...)
else:
    # 主会话直接处理
    pass
```

### Detailed Classification (详细分类)
```python
from task_router import classify_task

result = classify_task("统计 workspace 下的代码行数")
print(result)
# {
#     "use_subagent": True,
#     "reason": "检测到长任务关键词: '统计'",
#     "estimated_time": "medium",
#     "recommended_role": "researcher"
# }
```

### Pattern Matching (模式匹配)
```python
from task_router import match_task_pattern

pattern = match_task_pattern("帮我检查代码")
print(pattern["use_subagent"])  # True/False
print(pattern["role"])          # 推荐角色
print(pattern["timeout"])       # 建议超时时间
```

### Auto-Routing Rule (自动路由规则)

**使用 SubAgent 的场景:**
- 文件整理、清理、批量处理
- 代码统计、分析、检查
- Git 操作（提交、同步）
- 调研、研究类任务
- 描述 >20 词的多步骤任务

**主会话直接处理:**
- 快速问答（是什么、为什么、怎么）
- 解释说明类
- 简单对比、推荐
- 是/否 确认

---

*FIS 3.1 Lite — Quality over Quantity (质胜于量) 🐱⚡*
