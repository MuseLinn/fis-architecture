# FIS 3.1 Lite - Quick Reference

## 核心命令

### 初始化环境
```bash
python3 ~/.openclaw/workspace/skills/fis-architecture/examples/init_fis31.py
```

### 运行三角色流水线示例
```bash
python3 ~/.openclaw/workspace/skills/fis-architecture/examples/subagent_pipeline.py
```

## Python API

### 1. 共享记忆
```python
from memory_manager import write_memory, query_memory

# 写入
write_memory(
    agent="pulse",
    content={"key": "value"},
    layer="short_term",  # working/short_term/long_term
    tags=["gpr", "task-001"]
)

# 查询
results = query_memory(
    query="gpr",
    agent_filter=["pulse"],
    limit=10
)
```

### 2. 死锁检测
```python
from deadlock_detector import check_and_resolve

report = check_and_resolve(auto_resolve=False)
if report["deadlock_found"]:
    print(f"Deadlocks: {report['deadlocks']}")
```

### 3. 技能注册
```python
from skill_registry import register_skills, discover_skills

# 注册
with open('skill_manifest.json') as f:
    manifest = json.load(f)
register_skills("pulse", manifest)

# 发现
skills = discover_skills(query="SFCW")
```

### 4. 子代理生命周期
```python
from subagent_lifecycle import SubAgentLifecycleManager, SubAgentRole

manager = SubAgentLifecycleManager("cybermao")

# 创建 (发工卡)
card = manager.spawn(
    name="Worker-001",
    role=SubAgentRole.WORKER,  # WORKER/REVIEWER/RESEARCHER/FORMATTER
    task_description="Task details...",
    timeout_minutes=120,
    resources=["file_read", "file_write"]
)

# 激活
manager.activate(card['employee_id'])

# 显示工卡
print(manager.generate_badge(card['employee_id']))

# 心跳
manager.heartbeat(card['employee_id'])

# 终止
manager.terminate(card['employee_id'], "completed")

# 列表
active = manager.list_active()
```

## 工号格式

```
{PARENT}-SA-{YYYY}-{NNNN}

Examples:
- CYBERMAO-SA-2026-0001
- PULSE-SA-2026-0001
```

## 目录结构

```
~/.openclaw/
├── research-uav-gpr/.fis3.1/     # 共享基础设施
│   ├── memories/{working,short_term,long_term}/
│   ├── skills/{registry.json,manifests/}
│   ├── lib/{*.py}
│   └── subagent_registry.json
│
├── workspace/.fis3.1/            # CyberMao 扩展
├── workspace-radar/.fis3.1/      # Pulse 扩展
│   └── skill_manifest.json
│
└── workspace-subagent_*/         # 子代理工作区
    ├── AGENTS.md
    ├── TODO.md
    └── EMPLOYEE_CARD.json
```

## 关键设计原则

1. **零污染 Core Files**: 绝不修改其他 Agent 的 MEMORY.md/HEARTBEAT.md
2. **纯文件机制**: 无服务/无数据库，JSON + Python
3. **分层权限**: SubAgent 只能通过父 Agent 访问外部
4. **工卡系统**: 精致的身份管理与权限控制

## 故障排查

### 检查注册表
```bash
cat ~/.openclaw/research-uav-gpr/.fis3.1/skills/registry.json
cat ~/.openclaw/research-uav-gpr/.fis3.1/subagent_registry.json
```

### 检查子代理工作区
```bash
ls ~/.openclaw/workspace-subagent_*
```

### 运行维护脚本
```bash
~/.openclaw/system/scripts/fis_maintenance.sh check
```

---
*FIS 3.1 Lite - 质胜于量 🐱⚡*
