# FIS Architecture Skill

> **版本**: 3.1.0-lite  
> **名称**: Federal Intelligence System (联邦智能系统)  
> **定位**: OpenClaw 多 Agent 协作架构  
> **状态**: P0 核心功能已部署，Phase 2/3 功能预览中

---

## 当前架构状态

### P0 核心功能 (已部署)
```
research-uav-gpr/.fis3.1/
├── lib/                          # 核心 Python 库
│   ├── memory_manager.py         ✅ 共享记忆管理
│   ├── deadlock_detector.py      ✅ 死锁检测 (DFS)
│   ├── skill_registry.py         ✅ 技能注册发现
│   └── subagent_lifecycle.py     ✅ 子代理生命周期 + 工卡系统
├── memories/                     # 三层记忆存储
│   ├── working/                  # TTL: 1小时
│   ├── short_term/               # TTL: 24小时
│   └── long_term/                # 永久
├── skills/
│   ├── registry.json             # 技能索引 (Pulse 4项技能已注册)
│   └── manifests/                # Agent 技能清单
└── heartbeat/                    # 心跳状态

验证状态: ✅ 健康运行，零 Core File 污染
```

### Phase 2/3 预览 (experimental/)
```
research-uav-gpr/.fis3.1/experimental/
├── knowledge_graph/              # 知识图谱原型 (9 nodes)
├── lib/
│   ├── kg_manager.py             # 图谱管理
│   ├── gating_controller.py      # 访问控制
│   ├── retrieval_orchestrator.py # 多源检索
│   └── emb_spawn_wrapper.py      # 向量化子代理
└── POLICY_GATING.md              # 门控策略文档

状态: 📦 功能完整，待 Phase 2 正式激活
```

---

## 快速命令

```bash
# 初始化 FIS 3.1 环境
python3 ~/.openclaw/workspace/skills/fis-architecture/examples/init_fis31.py

# 检查架构健康
~/.openclaw/system/scripts/fis_maintenance.sh check

# 清理冗余 (dry-run)
~/.openclaw/system/scripts/fis_cleanup_redundancy.sh

# 子代理清理
python3 ~/.openclaw/system/scripts/fis_subagent_cleanup.py

# 自动生成工卡图片
python3 ~/.openclaw/workspace/skills/fis-architecture/examples/generate_badges.py
```

---

## Python API 参考

### 共享记忆
```python
from memory_manager import write_memory, query_memory

# Pulse 写入分析结果
write_memory(
    agent="pulse",
    content={"spectrum": data, "snr": 15.5},
    layer="short_term",
    tags=["gpr", "fis-uav-001"]
)

# CyberMao 查询
results = query_memory(
    query="gpr fis-uav-001",
    agent_filter=["pulse"],
    limit=5
)
```

### 死锁检测
```python
from deadlock_detector import check_and_resolve

report = check_and_resolve()
if report["deadlock_found"]:
    print(f"发现死锁: {report['deadlocks']}")
    print(f"已解决: {report['resolved']}")
```

### 技能注册
```python
from skill_registry import register_skills, discover_skills

# 注册技能
register_skills("pulse", manifest)

# 发现技能
skills = discover_skills(query="SFCW")
```

### 子代理生命周期
```python
from subagent_lifecycle import SubAgentLifecycleManager, SubAgentRole

manager = SubAgentLifecycleManager("cybermao")

# 发放工卡
worker = manager.spawn(
    name="Worker-001",
    role=SubAgentRole.WORKER,
    task_description="实现 PTVF 滤波算法"
)

# 生成工卡图片 (WhatsApp/Feishu 适配)
image_path = manager.generate_badge_image(worker['employee_id'])

# 批量生成
multi_image = manager.generate_multi_badge_image([id1, id2, id3, id4])

# 终止 (自动清理工作区)
manager.terminate(worker['employee_id'], "completed")
```

---

## 目录结构规范

```
~/.openclaw/
├── workspace/                    # CyberMao (主控)
│   ├── MEMORY.md                 # Core File (不变)
│   ├── HEARTBEAT.md              # Core File (不变)
│   └── .fis3.1/                  # FIS 3.1 扩展
│       └── local_cache/
│
├── workspace-radar/              # Pulse (雷达专家)
│   ├── MEMORY.md
│   ├── HEARTBEAT.md
│   └── .fis3.1/
│       ├── skill_manifest.json   # 技能清单
│       └── local_cache/
│
├── workspace-[agent]/            # 其他专家 Agent
│   └── ...
│
└── research-uav-gpr/             # 共享中心
    ├── .fis3.1/                  # FIS 3.1 共享基础设施
    │   ├── lib/                  # Python 库
    │   ├── memories/             # 共享记忆
    │   ├── skills/               # 技能注册表
    │   ├── heartbeat/            # 心跳状态
    │   └── experimental/         # Phase 2/3 预览
    │       ├── knowledge_graph/
    │       ├── lib/
    │       └── POLICY_GATING.md
    │
    └── tickets/                  # 任务票据
        ├── active/
        ├── completed/
        └── archive/
```

---

## 设计原则

### 1. 零污染 Core Files
```
❌ 禁止修改:
   - workspace/MEMORY.md, HEARTBEAT.md (其他 Agent)
   - openclaw.json (主配置)

✅ 只允许新增:
   - research-uav-gpr/.fis3.1/ (共享基础设施)
   - workspace/.fis3.1/ (本 Agent 扩展)
```

### 2. 分层隔离
| 层级 | 范围 | 访问规则 |
|------|------|----------|
| L1 Core Files | `*/MEMORY.md` | 仅本 Agent |
| L2 Agent 工作区 | `workspace-*/` | 仅本 Agent |
| L3 Shared Hub | `research-uav-gpr/` | 全 Agent 受控读写 |
| L4 FIS 扩展 | `*/.fis3.1/` | 各 Agent 独立 |

### 3. 纯文件机制
- 无新增服务/进程
- 100% 文件系统操作
- 可审计、可恢复

---

## 与 FIS 3.0 对比

| 特性 | FIS 3.0 | FIS 3.1 Lite |
|------|---------|--------------|
| 任务票据 | ✅ 基础格式 | ✅ 增强格式 (兼容) |
| 记忆共享 | ❌ 无 | ✅ Shared Hub 分层 |
| 死锁检测 | ❌ 无 | ✅ DFS 检测 |
| 技能发现 | ❌ 硬编码 | ✅ 动态注册表 |
| 子代理 | ❌ 无 | ✅ 工卡系统 |
| Core Files 污染 | - | ✅ 零污染 |
| 新增服务 | - | 无 (纯文件) |

---

## 更新记录

### 2026-02-18: Phase 2/3 预览归档
- 知识图谱和门控移至 `experimental/`
- 保持 P0 核心简洁
- 添加 TOOLS.md 快速参考

### 2026-02-17: FIS 3.1 Lite 初始部署
- 部署 memory_manager, deadlock_detector, skill_registry
- 部署 subagent_lifecycle + 工卡系统
- Pulse 4 项技能注册完成

### 2026-02-17: 工卡图片生成
- 添加 `generate_badge_image()` PNG 生成
- 支持批量 `generate_multi_badge_image()`
- 适配 WhatsApp/Feishu

### 2026-02-17: 子代理自动清理
- `terminate()` 自动删除工作区
- 新增 `cleanup_all_terminated()` 批量清理

---

## 文件位置

```
~/.openclaw/workspace/skills/fis-architecture/
├── SKILL.md                    # 本文件
├── QUICK_REFERENCE.md          # 速查手册
├── lib/                        # Python 库 (已部署到 shared hub)
│   ├── memory_manager.py
│   ├── deadlock_detector.py
│   ├── skill_registry.py
│   ├── subagent_lifecycle.py
│   ├── badge_image_pil.py
│   └── badge_generator.py
├── examples/                   # 使用示例
│   ├── init_fis31.py
│   ├── subagent_pipeline.py
│   └── generate_badges.py
└── system/                     # 系统脚本
    ├── fis_maintenance.sh
    ├── fis_cleanup_redundancy.sh
    └── fis_subagent_cleanup.py
```

---

*FIS 3.1 Lite - 质胜于量*  
*Designed by CyberMao 🐱⚡*
