# FIS Architecture Skill

> **版本**: 3.1 Lite  
> **名称**: Federal Intelligence System (联邦智能系统)  
> **定位**: OpenClaw 多 Agent 协作架构  
> **设计**: 分形文件系统 + 零污染 Core Files + 纯文件机制

---

## 核心设计原则

### 1. 分形架构 (Fractal Structure)

每个 Agent 工作区是完整缩放的系统副本：

```
~/.openclaw/
├── workspace/                    # CyberMao (主控)
│   ├── AGENTS.md                # Agent 元数据
│   ├── BOOTSTRAP.md             # 首次启动指南
│   ├── HEARTBEAT.md             # 周期性任务
│   ├── IDENTITY.md              # 身份定义
│   ├── MEMORY.md                # 长久记忆
│   ├── SOUL.md                  # 行为准则
│   ├── TODO.md                  # 当前任务
│   ├── TOOLS.md                 # 本地工具配置
│   ├── USER.md                  # 用户信息
│   ├── README.md                # 工作区说明
│   ├── skills/                  # 本地技能库
│   ├── memory/                  # 每日记忆 (YYYY-MM-DD.md)
│   ├── output/                  # 产出物
│   ├── logs/                    # 日志
│   └── .fis3.1/                 # ⭐ FIS 3.1 扩展
│       └── local_cache/
│
├── workspace-radar/              # Pulse (雷达专家)
│   ├── [同上 8 Core Files]
│   ├── skills/
│   ├── output/
│   └── .fis3.1/
│       ├── local_cache/
│       └── skill_manifest.json  # ⭐ 技能清单
│
├── workspace-painter/            # Painter (视觉专家)
│   ├── [同上 8 Core Files]
│   └── .fis3.1/
│
├── workspace-formatter/          # Formatter (格式化专家)
│   └── [同上结构]
│
├── workspace-hardware/           # Hardware (硬件专家)
│   └── [同上结构]
│
└── workspace-subagent_*/         # ⭐ 动态创建的子代理
    ├── AGENTS.md
    ├── TODO.md
    └── EMPLOYEE_CARD.json       # 工卡信息

共享中心 (Shared Hub):
research-uav-gpr/
├── .fis3.1/                      # ⭐ FIS 3.1 共享基础设施
│   ├── memories/                 # 分层共享记忆
│   │   ├── working/              # 工作记忆 (1h TTL)
│   │   ├── short_term/           # 短期记忆 (24h TTL)
│   │   └── long_term/            # 长期记忆 (永久)
│   ├── skills/
│   │   ├── registry.json         # 技能注册表
│   │   └── manifests/            # Agent技能清单
│   ├── lib/                      # Python库
│   │   ├── memory_manager.py
│   │   ├── deadlock_detector.py
│   │   ├── skill_registry.py
│   │   ├── subagent_lifecycle.py
│   │   ├── badge_image_pil.py
│   │   └── badge_generator.py
│   ├── heartbeat/                # 心跳文件
│   └── subagent_registry.json    # 子代理注册表
│
├── tickets/                      # 任务票据
│   ├── active/                   # 进行中
│   ├── completed/                # 已完成
│   └── archive/                  # 归档
│
├── knowledge/                    # 共享知识库
├── results/                      # 实验结果
└── README.md
```

**Core Files (8个必备)**: AGENTS.md, BOOTSTRAP.md, HEARTBEAT.md, IDENTITY.md, MEMORY.md, SOUL.md, TODO.md, TOOLS.md, USER.md

### 2. 零污染 Core Files

```
❌ 绝对禁止修改:
   - workspace/MEMORY.md, HEARTBEAT.md (其他 Agent)
   - openclaw.json (主配置)

✅ 只允许新增:
   - research-uav-gpr/.fis3.1/ (共享基础设施)
   - workspace/.fis3.1/ (本 Agent 扩展)
```

### 3. 三层隔离层级

| 层级 | 范围 | 访问规则 |
|------|------|----------|
| L1 Core Files | `*/MEMORY.md`, `*/HEARTBEAT.md` | 仅本 Agent 读写 |
| L2 Agent 工作区 | `workspace-*/` | 仅本 Agent，通过 Shared Hub 间接共享 |
| L3 Shared Hub | `research-uav-gpr/` | 全 Agent 受控读写 |
| L4 FIS 扩展 | `*/.fis3.1/` | 各 Agent 独立扩展 |

---

## FIS 3.1 Lite 新增功能

### 3.1 共享记忆 (Shared Memory)

分层存储解决 Agent 间信息传递：

```
research-uav-gpr/.fis3.1/memories/
├── working/           # 工作记忆 (TTL: 1小时)
├── short_term/        # 短期记忆 (TTL: 24小时)
└── long_term/         # 长期记忆 (永久)
```

**使用方式**:
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

### 3.2 死锁检测 (Deadlock Detection)

DFS 算法检测任务依赖循环：

```python
from deadlock_detector import check_and_resolve

# 定期检查
report = check_and_resolve()
if report["deadlock_found"]:
    print(f"发现死锁: {report['deadlocks']}")
    print(f"已解决: {report['resolved']}")
```

### 3.3 技能注册 (Skill Registry)

Agent 能力发现与调用：

```python
from skill_registry import register_skills, discover_skills

# Pulse 注册技能
register_skills("pulse", manifest)

# CyberMao 发现
skills = discover_skills(query="SFCW")
```

### 3.4 子代理生命周期 (SubAgent Lifecycle)

**工卡系统** - 精致的身份管理：

```python
from subagent_lifecycle import SubAgentLifecycleManager, SubAgentRole

# 创建管理器
manager = SubAgentLifecycleManager("cybermao")

# 发放工卡
worker_card = manager.spawn(
    name="小毛-Worker-001",
    role=SubAgentRole.WORKER,
    task_description="实现 PTVF 滤波算法",
    timeout_minutes=120
)

# 显示工卡
print(manager.generate_badge(worker_card['employee_id']))
```

**工号格式**: `{PARENT}-SA-{YYYY}-{NNNN}`  
**示例**: `CYBERMAO-SA-2026-0001`

**工卡图片生成** (适配 WhatsApp/Feishu):

```python
from subagent_lifecycle import SubAgentLifecycleManager, SubAgentRole

manager = SubAgentLifecycleManager("cybermao")

# 发放工卡
worker = manager.spawn(name="Worker-001", role=SubAgentRole.WORKER, task_description="...")

# 生成单张工卡图片
image_path = manager.generate_badge_image(worker['employee_id'])
# Output: ~/.openclaw/output/badges/badge_CYBERMAO-SA-2026-0001.png

# 批量生成多张工卡（平铺布局，避免消息轰炸）
multi_image = manager.generate_multi_badge_image([worker1['employee_id'], worker2['employee_id']])
# Output: 2x2 工卡网格图片
```

**工卡图片特性**:
- 渐变色标题栏 (FIS 3.1 Lite 品牌)
- 头像 emoji 标识角色 (🔧 Worker / 👁️ Reviewer / 🔬 Researcher / 🎨 Formatter)
- 彩色角色徽章 (蓝/紫/绿/橙)
- 状态指示灯 (🟢 ACTIVE / 🟡 PENDING / 🔴 TERMINATED)
- 权限矩阵可视化
- 有效期显示
- **批量布局**: 2x2 网格，一张图片包含最多4张工卡

---

## 快速开始

### 1. 初始化 FIS 3.1 环境

```bash
# 运行初始化脚本
python3 ~/.openclaw/workspace/skills/fis-architecture/examples/init_fis31.py
```

### 2. 使用子代理三角色流水线

```bash
# 示例: PTVF 滤波器开发
python3 ~/.openclaw/workspace/skills/fis-architecture/examples/subagent_pipeline.py
```

---

## 目录结构

```
workspace/skills/fis-architecture/
├── SKILL.md                    # 本文件
├── QUICK_REFERENCE.md          # 速查手册
├── lib/                        # Python 库
│   ├── memory_manager.py       # 共享记忆管理
│   ├── deadlock_detector.py    # 死锁检测
│   ├── skill_registry.py       # 技能注册
│   ├── subagent_lifecycle.py   # 子代理生命周期
│   ├── badge_template.html     # 工卡 HTML 模板
│   ├── badge_generator.py      # 工卡 HTML 生成器
│   └── badge_image_pil.py      # 工卡图片生成器 (PIL)
└── examples/                   # 使用示例
    ├── init_fis31.py           # 初始化脚本
    ├── subagent_pipeline.py    # 子代理流水线
    └── generate_badges.py      # 生成工卡图片示例
```

---

## 与 FIS 3.0 对比

| 特性 | FIS 3.0 | FIS 3.1 Lite |
|------|---------|--------------|
| 任务票据 | ✅ 基础格式 | ✅ 增强格式 (兼容) |
| 记忆共享 | ❌ 无 | ✅ Shared Hub 分层 |
| 死锁检测 | ❌ 无 | ✅ DFS 检测 |
| 技能发现 | ❌ 硬编码 | ✅ 动态注册表 |
| 子代理 | ❌ 无 | ✅ 工卡系统 |
| 通信 | ❌ 轮询 | ✅ 文件心跳 |
| Core Files | ✅ 保留 | ✅ 绝不修改 |
| 新增服务 | - | 无 (纯文件) |

---

## 最佳实践

1. **保持简单**: 不要为了用而用，文件系统能解决 95% 的问题
2. **增量演进**: 先跑起来，再逐步添加 FIS 3.1 功能
3. **记录决策**: 所有架构变更写入 MEMORY.md
4. **定期归档**: 使用自动归档脚本清理过期文件
5. **SubAgent 清理**: 终止时自动清理工作区，避免文件夹堆积

---

## 更新记录

### 2026-02-17: SubAgent 自动清理
- `terminate()` 现在自动删除 `workspace-subagent_{id}/` 文件夹
- 新增 `cleanup_all_terminated()` 批量清理方法
- 新增清理脚本 `fis_subagent_cleanup.py`
- 测试：从 10 个文件夹清理到 6 个

### 2026-02-17: 工卡图片生成
- 添加 `generate_badge_image()` 生成 PNG 工卡
- 支持批量生成 `generate_multi_badge_image()`
- 适配 WhatsApp/Feishu 发送

---

*FIS 3.1 Lite - 质胜于量*  
*Designed by CyberMao 🐱⚡*
