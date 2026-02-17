"""
FIS 3.1 Lite - SubAgent Lifecycle Manager
子代理生命周期管理与工卡系统
"""

import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum

SHARED_HUB = Path.home() / ".openclaw" / "research-uav-gpr" / ".fis3.1"
SUBAGENT_REGISTRY = SHARED_HUB / "subagent_registry.json"

class SubAgentStatus(Enum):
    PENDING = "pending"      # 已创建，等待激活
    ACTIVE = "active"        # 运行中
    PAUSED = "paused"        # 暂停
    COMPLETED = "completed"  # 正常完成
    TERMINATED = "terminated" # 被终止

class SubAgentRole(Enum):
    WORKER = "worker"        # 执行具体任务
    REVIEWER = "reviewer"    # 审查/验证
    RESEARCHER = "researcher" # 调研分析
    FORMATTER = "formatter"  # 格式化输出

class SubAgentLifecycleManager:
    """子代理生命周期管理器"""
    
    def __init__(self, parent_agent: str):
        self.parent = parent_agent
        self.registry = self._load_registry()
        
    def _load_registry(self) -> dict:
        """加载注册表"""
        if SUBAGENT_REGISTRY.exists():
            with open(SUBAGENT_REGISTRY) as f:
                return json.load(f)
        return {
            "version": "3.1.0-lite",
            "subagents": [],
            "id_counter": 0
        }
    
    def _save_registry(self):
        """保存注册表"""
        SUBAGENT_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        with open(SUBAGENT_REGISTRY, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def _generate_id(self) -> str:
        """生成工号: PARENT-SA-YYYY-NNNN"""
        self.registry["id_counter"] += 1
        counter = str(self.registry["id_counter"]).zfill(4)
        year = datetime.now().year
        return f"{self.parent.upper()}-SA-{year}-{counter}"
    
    def spawn(self, 
              name: str,
              role: SubAgentRole,
              task_description: str,
              timeout_minutes: int = 60,
              resources: list = None) -> dict:
        """
        创建子代理（发工卡）
        
        Returns:
            工卡信息 dict
        """
        employee_id = self._generate_id()
        
        # 生成专属工作区路径
        workspace_name = f"subagent_{employee_id.lower().replace('-', '_')}"
        workspace_path = Path.home() / ".openclaw" / f"workspace-{workspace_name}"
        
        subagent_card = {
            "employee_id": employee_id,
            "name": name,
            "role": role.value,
            "parent": self.parent,
            "status": SubAgentStatus.PENDING.value,
            
            # 任务信息
            "task": {
                "description": task_description,
                "created_at": datetime.now().isoformat(),
                "deadline": (datetime.now() + timedelta(minutes=timeout_minutes)).isoformat(),
                "resources_granted": resources or ["file_read", "file_write"]
            },
            
            # 工作区配置
            "workspace": {
                "path": str(workspace_path),
                "allowed_dirs": [
                    str(workspace_path),  # 自己的工作区
                    str(SHARED_HUB.parent)  # 只读访问 research-uav-gpr
                ],
                "forbidden_dirs": [
                    str(Path.home() / ".openclaw" / "workspace"),  # CyberMao核心
                    str(Path.home() / ".openclaw" / "workspace-radar")  # Pulse核心
                ]
            },
            
            # 权限矩阵
            "permissions": {
                "can_read_shared_hub": True,
                "can_write_shared_hub": False,  # 只能通过父代理
                "can_create_subagent": False,   # 子代理不能再创建子代理
                "can_modify_tickets": False,    # 不能修改票据
                "can_call_other_agents": False  # 不能调用其他Agent
            },
            
            # 生命周期记录
            "lifecycle": {
                "spawned_at": datetime.now().isoformat(),
                "activated_at": None,
                "completed_at": None,
                "heartbeat_count": 0,
                "last_heartbeat": None
            }
        }
        
        # 注册到系统
        self.registry["subagents"].append(subagent_card)
        self._save_registry()
        
        # 创建工作区目录
        self._init_workspace(workspace_path, subagent_card)
        
        return subagent_card
    
    def _init_workspace(self, workspace_path: Path, card: dict):
        """初始化子代理工作区"""
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # 创建标准文件
        (workspace_path / "AGENTS.md").write_text(f"""# AGENTS.md - {card['name']}

## Identity
- **Name**: {card['name']}
- **Employee ID**: {card['employee_id']}
- **Role**: {card['role']}
- **Parent**: {card['parent']}

## Constraints
- Workspace only: {card['workspace']['path']}
- Cannot modify tickets directly
- Cannot call other agents directly
- All external communication through parent

## Task
{card['task']['description']}
""")
        
        (workspace_path / "TODO.md").write_text(f"""# TODO - {card['name']}

## Current Task
{card['task']['description']}

## Deadline
{card['task']['deadline']}

## Progress
- [ ] Task started
- [ ] In progress
- [ ] Completed
""")
        
        # 工卡文件
        (workspace_path / "EMPLOYEE_CARD.json").write_text(json.dumps(card, indent=2))
    
    def activate(self, employee_id: str) -> bool:
        """激活子代理"""
        for sa in self.registry["subagents"]:
            if sa["employee_id"] == employee_id:
                sa["status"] = SubAgentStatus.ACTIVE.value
                sa["lifecycle"]["activated_at"] = datetime.now().isoformat()
                self._save_registry()
                return True
        return False
    
    def heartbeat(self, employee_id: str) -> bool:
        """记录心跳"""
        for sa in self.registry["subagents"]:
            if sa["employee_id"] == employee_id:
                sa["lifecycle"]["heartbeat_count"] += 1
                sa["lifecycle"]["last_heartbeat"] = datetime.now().isoformat()
                self._save_registry()
                return True
        return False
    
    def terminate(self, employee_id: str, reason: str = "completed") -> bool:
        """终止子代理"""
        for sa in self.registry["subagents"]:
            if sa["employee_id"] == employee_id:
                sa["status"] = SubAgentStatus.TERMINATED.value
                sa["lifecycle"]["completed_at"] = datetime.now().isoformat()
                sa["termination_reason"] = reason
                self._save_registry()
                return True
        return False
    
    def list_active(self) -> list:
        """列出所有活跃子代理"""
        return [sa for sa in self.registry["subagents"] 
                if sa["status"] in [SubAgentStatus.PENDING.value, SubAgentStatus.ACTIVE.value]]
    
    def get_card(self, employee_id: str) -> dict:
        """获取工卡信息"""
        for sa in self.registry["subagents"]:
            if sa["employee_id"] == employee_id:
                return sa
        return None
    
    def generate_badge(self, employee_id: str) -> str:
        """生成 ASCII 工卡（用于展示）"""
        card = self.get_card(employee_id)
        if not card:
            return "工卡不存在"
        
        badge = f"""
╔══════════════════════════════════════════════════════════════╗
║                     FIS 3.1 LITE                             ║
║              联邦智能系统 · 子代理工卡                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ┌──────────────────────────────────────────────────────┐  ║
║  │  照                                                  │  ║
║  │  片    🤖                                           │  ║
║  │  位                                                  │  ║
║  │  置                                                  │  ║
║  └──────────────────────────────────────────────────────┘  ║
║                                                              ║
║  工号: {card['employee_id']:<45}║
║  姓名: {card['name']:<45}║
║  角色: {card['role'].upper():<45}║
║  部门: {card['parent']:<45}║
║                                                              ║
║  状态: {'🟢 ' + card['status'].upper() if card['status'] == 'active' else '🟡 ' + card['status'].upper():<45}║
║  有效期至: {card['task']['deadline'][:19]:<42}║
║                                                              ║
║  ┌──────────────────────────────────────────────────────┐  ║
║  │ 权限:                                                 │  ║
║  │  {'✓' if card['permissions']['can_read_shared_hub'] else '✗'} 读共享中心          │  ║
║  │  {'✓' if card['permissions']['can_write_shared_hub'] else '✗'} 写共享中心 (需父代)│  ║
║  │  {'✓' if card['permissions']['can_call_other_agents'] else '✗'} 调用其他Agent     │  ║
║  │  {'✓' if card['permissions']['can_modify_tickets'] else '✗'} 修改票据           │  ║
║  └──────────────────────────────────────────────────────┘  ║
║                                                              ║
║         签发: CyberMao    日期: {datetime.now().strftime('%Y-%m-%d'):<25}║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        return badge

    def generate_badge_image(self, employee_id: str, output_path: Path = None) -> Path:
        """Generate badge image using PIL"""
        from badge_image_pil import generate_single_badge
        
        card = self.get_card(employee_id)
        if not card:
            raise ValueError(f"Employee {employee_id} not found")
        
        return generate_single_badge(card, output_path)
    
    def generate_multi_badge_image(self, employee_ids: list = None, output_path: Path = None) -> Path:
        """Generate multi-badge image for multiple subagents"""
        from badge_image_pil import generate_multi_badge_image
        
        if employee_ids is None:
            # Use all active subagents
            cards = self.list_active()
        else:
            cards = [self.get_card(eid) for eid in employee_ids]
            cards = [c for c in cards if c]
        
        if not cards:
            raise ValueError("No subagents to generate badges for")
        
        return generate_multi_badge_image(cards, output_path.name if output_path else None)

if __name__ == "__main__":
    print("FIS 3.1 SubAgent Lifecycle Manager loaded")
