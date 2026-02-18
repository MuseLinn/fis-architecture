"""
FIS 3.1 Lite - SubAgent Lifecycle Manager
子代理生命周期管理与工卡系统
"""

import json
import os
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum
from fis_config import get_shared_hub_path

SHARED_HUB = get_shared_hub_path() / ".fis3.1"
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
              resources: list = None,
              badge_format: str = "auto") -> dict:
        """
        创建子代理（发工卡）
        
        Args:
            name: 子代理名称
            role: 角色 (WORKER/REVIEWER/RESEARCHER/FORMATTER)
            task_description: 任务描述
            timeout_minutes: 超时时间
            resources: 授权资源列表
            badge_format: 工卡格式 ("text", "image", "both", "auto")
                         "auto" - 根据环境自动选择 (默认image if available)
        
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
                    str(SHARED_HUB.parent)  # 只读访问共享中心
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
        
        # 生成工卡 (根据 badge_format 选择格式)
        badge_result = self._generate_badge_for_spawn(subagent_card, badge_format)
        subagent_card["badge"] = badge_result
        
        # 发送即时通知 (如果启用)
        notification = self._notify_badge_created(subagent_card)
        subagent_card["notification"] = notification
        
        return subagent_card
    
    def _notify_badge_created(self, card: dict) -> dict:
        """
        准备子代理创建通知
        
        将工卡临时复制到可访问目录，便于主会话通过 message 工具发送
        
        Returns:
            dict: 通知信息，包含 message 和 sendable_badge_path
                  主会话应使用这些信息调用 message 工具发送
        """
        try:
            # 构建通知消息
            role_emoji = {
                "architect": "🏗️",
                "worker": "🔧", 
                "reviewer": "✅",
                "researcher": "🔬",
                "formatter": "📝"
            }.get(card['role'].lower(), "🤖")
            
            message_text = f"""🎫 新子代理工卡已发放

{role_emoji} 工号: {card['employee_id']}
📋 角色: {card['role'].upper()}
📝 任务: {card['task']['description'][:60]}{'...' if len(card['task']['description']) > 60 else ''}
⏱️ 截止时间: {card['task']['deadline'][:16].replace('T', ' ')}

任务执行中，完成后将自动汇报结果。"""
            
            badge_image = card.get('badge', {}).get('image')
            sendable_badge_path = None
            
            # 将工卡复制到可访问目录（如果需要发送）
            if badge_image and os.path.exists(badge_image):
                try:
                    import shutil
                    from pathlib import Path
                    
                    # 找到当前 Agent 的 workspace
                    # 尝试多个可能的位置
                    possible_workspace_paths = [
                        Path.home() / '.openclaw' / 'workspace' / 'temp_badges',
                        Path.home() / '.openclaw' / 'temp_badges',
                        Path.cwd() / 'temp_badges',
                    ]
                    
                    # 使用第一个可用的路径
                    temp_dir = None
                    for path in possible_workspace_paths:
                        try:
                            path.mkdir(parents=True, exist_ok=True)
                            # 测试是否可写
                            test_file = path / '.test_write'
                            test_file.touch()
                            test_file.unlink()
                            temp_dir = path
                            break
                        except:
                            continue
                    
                    if temp_dir:
                        # 复制工卡到临时目录
                        badge_filename = Path(badge_image).name
                        sendable_path = temp_dir / badge_filename
                        shutil.copy2(badge_image, sendable_path)
                        sendable_badge_path = str(sendable_path)
                        print(f"  工卡已复制到可发送路径: {sendable_badge_path}")
                    else:
                        print(f"  警告: 未找到可写的临时目录")
                        sendable_badge_path = badge_image
                        
                except Exception as e:
                    print(f"  复制工卡失败: {e}")
                    sendable_badge_path = badge_image
            
            notification = {
                "timestamp": datetime.now().isoformat(),
                "employee_id": card['employee_id'],
                "message": message_text,
                "badge_image": badge_image,  # 原始路径（在工作区内，会随 terminate 清理）
                "sendable_badge_path": sendable_badge_path,  # 可发送的临时路径
                "status": "ready_to_send"
            }
            
            # 保存到通知记录
            self._save_notification(notification)
            
            print(f"✅ 工卡已生成: {card['employee_id']}")
            
            return notification
            
        except Exception as e:
            print(f"⚠️ 通知准备失败: {e}")
            return {"status": "error", "error": str(e)}
                
        except Exception as e:
            print(f"⚠️ 通知准备失败: {e}")
    
    def _notify_group_badges_created(self, group_name: str, cards: list, image_path: str):
        """
        发送分组工牌创建通知
        
        Args:
            group_name: 分组名称 (如 'worker', 'reviewer')
            cards: 该组的子代理列表
            image_path: 拼接后的工牌图片路径
        """
        try:
            role_emoji = {
                "architect": "🏗️",
                "worker": "🔧", 
                "reviewer": "✅",
                "researcher": "🔬",
                "formatter": "📝"
            }.get(group_name.lower(), "🤖")
            
            # 构建消息
            if len(cards) == 1:
                # 单个子代理
                card = cards[0]
                message_text = f"""⚡ 子代理已创建

{role_emoji} 工号: {card['employee_id']}
📋 角色: {card['role'].upper()}
📝 任务: {card['task']['description'][:60]}{'...' if len(card['task']['description']) > 60 else ''}
⏱️ 截止时间: {card['task']['deadline'][:16].replace('T', ' ')}"""
            else:
                # 多个子代理
                agent_list = "\n".join([f"  • {c['employee_id']} - {c['name']}" for c in cards])
                message_text = f"""⚡ {len(cards)} 个子代理已创建 [{group_name.upper()} 组]

{role_emoji} 角色: {group_name.upper()}
👥 成员:
{agent_list}

📝 任务: {cards[0]['task']['description'][:40]}..."""
            
            # 保存通知
            notification = {
                "timestamp": datetime.now().isoformat(),
                "group": group_name,
                "count": len(cards),
                "agent_ids": [c['employee_id'] for c in cards],
                "message": message_text,
                "badge_image": image_path,
                "status": "pending"
            }
            
            self._save_notification(notification)
            
            print(f"📱 分组通知已准备: {group_name} ({len(cards)} 个代理)")
            print(f"   图片: {image_path}")
            
        except Exception as e:
            print(f"⚠️ 分组通知准备失败: {e}")
    
    def spawn_batch(self, agent_configs: list, group_by_role=True) -> dict:
        """
        批量创建子代理并生成分组工牌
        
        Args:
            agent_configs: 子代理配置列表，每项为 dict:
                {
                    'name': 'Agent-Name',
                    'role': SubAgentRole.WORKER,
                    'task_description': 'Task desc',
                    'timeout_minutes': 60
                }
            group_by_role: 是否按角色分组生成工牌图片
        
        Returns:
            dict: {
                'agents': [card1, card2, ...],
                'group_images': {role: image_path} (如果 group_by_role=True)
            }
        
        示例:
            configs = [
                {'name': 'Worker-1', 'role': SubAgentRole.WORKER, 'task_description': 'Task 1'},
                {'name': 'Worker-2', 'role': SubAgentRole.WORKER, 'task_description': 'Task 2'},
                {'name': 'Reviewer-1', 'role': SubAgentRole.REVIEWER, 'task_description': 'Review'},
            ]
            result = manager.spawn_batch(configs, group_by_role=True)
            # 会生成: workers 一张拼接图, reviewer 一张单独图
        """
        created_cards = []
        
        # 逐个创建子代理
        for config in agent_configs:
            card = self.spawn(
                name=config['name'],
                role=config['role'],
                task_description=config.get('task_description', 'No description'),
                timeout_minutes=config.get('timeout_minutes', 60),
                badge_format='image'
            )
            created_cards.append(card)
            print(f"✅ Created: {card['employee_id']} - {card['role']}")
        
        result = {'agents': created_cards}
        
        # 生成分组工牌
        if group_by_role and created_cards:
            employee_ids = [c['employee_id'] for c in created_cards]
            group_images = self.generate_multi_badge_image(
                employee_ids=employee_ids,
                group_by_role=True
            )
            result['group_images'] = group_images
            
            print("\n📸 分组工牌已生成:")
            for role, path in group_images.items():
                print(f"   {role}: {path}")
        
        return result
    
    def _save_notification(self, notification: dict):
        """保存通知记录"""
        notify_file = SHARED_HUB / "notifications.json"
        notifications = []
        if notify_file.exists():
            with open(notify_file) as f:
                notifications = json.load(f)
        notifications.append(notification)
        with open(notify_file, 'w') as f:
            json.dump(notifications, f, indent=2)
    
    def _generate_badge_for_spawn(self, card: dict, badge_format: str) -> dict:
        """
        根据格式生成工卡
        
        Returns:
            dict with 'text', 'image', or both
        """
        result = {}
        
        # Determine format
        if badge_format == "auto":
            # Check if PIL is available for image generation
            try:
                from PIL import Image
                badge_format = "image"  # Default to image if PIL available
            except ImportError:
                badge_format = "text"
        
        # Generate text badge
        if badge_format in ["text", "both"]:
            result["text"] = self.generate_badge(card['employee_id'])
        
        # Generate image badge
        if badge_format in ["image", "both"]:
            try:
                # Use v7 generator with SubAgent-specific output dir
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent))
                from badge_generator_v7 import BadgeGenerator
                
                # 工卡生成在工作区内的 badges/ 目录，便于清理
                workspace_path = Path(card['workspace']['path'])
                badge_output_dir = workspace_path / 'badges'
                
                generator = BadgeGenerator(output_dir=badge_output_dir)
                image_path = generator.create_badge({
                    'name': card['name'],
                    'id': card['employee_id'],
                    'role': card['role'].upper(),
                    'task_id': f"#{card['role'][:4].upper()}-{card['employee_id'][-4:]}",
                    'soul': f'"{card["task"]["description"][:40]}..."' if len(card["task"]["description"]) > 40 else f'"{card["task"]["description"]}"',
                    'responsibilities': [
                        f"Execute {card['role']} tasks",
                        "Report to parent agent",
                        "Maintain workspace integrity",
                        "Complete before deadline"
                    ],
                    'output_formats': 'MARKDOWN | JSON | TXT',
                    'barcode_id': card['employee_id'],
                    'status': card['status'].upper(),
                })
                result["image"] = image_path
            except Exception as e:
                result["image_error"] = f"Failed to generate image badge: {e}"
        
        return result
    
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
        """终止子代理并清理工作区"""
        for sa in self.registry["subagents"]:
            if sa["employee_id"] == employee_id:
                sa["status"] = SubAgentStatus.TERMINATED.value
                sa["lifecycle"]["completed_at"] = datetime.now().isoformat()
                sa["termination_reason"] = reason
                self._save_registry()
                
                # 自动清理工作区文件夹
                self._cleanup_workspace(sa)
                return True
        return False
    
    def _cleanup_workspace(self, card: dict):
        """清理子代理工作区文件夹"""
        import shutil
        workspace_path = Path(card.get("workspace", {}).get("path", ""))
        
        if workspace_path.exists() and "subagent" in workspace_path.name:
            try:
                shutil.rmtree(workspace_path)
                print(f"✅ Cleaned up workspace: {workspace_path.name}")
            except Exception as e:
                print(f"⚠️ Failed to cleanup {workspace_path}: {e}")
    
    def cleanup_all_terminated(self, dry_run: bool = False) -> list:
        """
        清理所有已终止的子代理工作区
        
        Args:
            dry_run: 如果 True，只返回将要清理的列表，不实际删除
        
        Returns:
            list: 被清理的 subagent 工号列表
        """
        import shutil
        
        terminated = [sa for sa in self.registry["subagents"] 
                      if sa["status"] == SubAgentStatus.TERMINATED.value]
        
        cleaned = []
        for sa in terminated:
            emp_id = sa["employee_id"]
            workspace_path = Path(sa.get("workspace", {}).get("path", ""))
            
            if workspace_path.exists():
                if not dry_run:
                    try:
                        shutil.rmtree(workspace_path)
                        cleaned.append(emp_id)
                        print(f"✅ Cleaned: {emp_id}")
                    except Exception as e:
                        print(f"❌ Failed to clean {emp_id}: {e}")
                else:
                    cleaned.append(emp_id)
                    print(f"[DRY-RUN] Would clean: {emp_id}")
        
        return cleaned
    
    def archive_completed(self, days_old: int = 7) -> list:
        """
        归档已完成超过 N 天的子代理
        
        Args:
            days_old: 多少天前的 terminated 子代理需要归档
        """
        from datetime import datetime, timedelta
        import shutil
        
        cutoff = datetime.now() - timedelta(days=days_old)
        archive_dir = Path.home() / ".openclaw" / "archive" / "subagents"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        archived = []
        for sa in self.registry["subagents"]:
            if sa["status"] == SubAgentStatus.TERMINATED.value:
                completed_at = sa.get("lifecycle", {}).get("completed_at")
                if completed_at:
                    completed = datetime.fromisoformat(completed_at)
                    if completed < cutoff:
                        # 移动到归档
                        emp_id = sa["employee_id"]
                        workspace_path = Path(sa.get("workspace", {}).get("path", ""))
                        
                        if workspace_path.exists():
                            dest = archive_dir / workspace_path.name
                            try:
                                shutil.move(str(workspace_path), str(dest))
                                archived.append(emp_id)
                                print(f"📦 Archived: {emp_id}")
                            except Exception as e:
                                print(f"❌ Failed to archive {emp_id}: {e}")
        
        return archived
    
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

    def generate_badge_image(self, employee_id: str, output_path=None):
        """Generate badge image using v7 (optimized layout)"""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from badge_generator_v7 import BadgeGenerator
        
        card = self.get_card(employee_id)
        if not card:
            raise ValueError(f"Employee {employee_id} not found")
        
        generator = BadgeGenerator()
        return generator.create_badge({
            'name': card['name'],
            'id': card['employee_id'],
            'role': card['role'].upper(),
            'task_id': f"#{card['role'][:4].upper()}-{card['employee_id'][-4:]}",
            'soul': '"Digital agent"',
            'responsibilities': [f"Execute {card['role']} tasks"],
            'output_formats': 'MARKDOWN | JSON | TXT',
            'barcode_id': card['employee_id'],
            'status': card['status'].upper(),
        }, output_path)
    
    def generate_multi_badge_image(self, employee_ids=None, output_path=None, layout='horizontal', group_by_role=False):
        """
        生成多工牌拼接图片 (使用 v7 生成器)
        
        Args:
            employee_ids: 工号列表，None 表示所有活跃子代理
            output_path: 输出路径
            layout: 'horizontal'(水平), 'vertical'(垂直), 'grid'(网格)
            group_by_role: 是否按角色分组（workers 一起，reviewer 单独）
        
        Returns:
            dict: {group_name: image_path} 或单个路径
        """
        import sys
        from pathlib import Path
        from PIL import Image
        sys.path.insert(0, str(Path(__file__).parent))
        from badge_generator_v7 import BadgeGenerator
        
        if employee_ids is None:
            cards = self.list_active()
        else:
            cards = [self.get_card(eid) for eid in employee_ids]
            cards = [c for c in cards if c]
        
        if not cards:
            raise ValueError("No subagents to generate badges for")
        
        # 使用 v7 生成器
        generator = BadgeGenerator()
        
        def create_badge_data(card):
            return {
                'name': card['name'],
                'id': card['employee_id'],
                'role': card['role'].upper(),
                'task_id': f"#{card['role'][:4].upper()}-{card['employee_id'][-4:]}",
                'soul': '"Digital agent"',
                'responsibilities': [f"Execute {card['role']} tasks"],
                'output_formats': 'MARKDOWN | JSON | TXT',
                'barcode_id': card['employee_id'],
                'status': card['status'].upper(),
            }
        
        def combine_badges(badge_paths, layout='horizontal'):
            """拼接多个工卡图片"""
            images = [Image.open(p) for p in badge_paths]
            
            if layout == 'horizontal':
                total_width = sum(img.width for img in images)
                max_height = max(img.height for img in images)
                combined = Image.new('RGB', (total_width, max_height), '#f5f5f0')
                x_offset = 0
                for img in images:
                    combined.paste(img, (x_offset, 0))
                    x_offset += img.width
            elif layout == 'vertical':
                max_width = max(img.width for img in images)
                total_height = sum(img.height for img in images)
                combined = Image.new('RGB', (max_width, total_height), '#f5f5f0')
                y_offset = 0
                for img in images:
                    combined.paste(img, (0, y_offset))
                    y_offset += img.height
            elif layout == 'grid':
                n = len(images)
                cols = 2 if n <= 4 else 3
                rows = (n + cols - 1) // cols
                max_width = max(img.width for img in images)
                max_height = max(img.height for img in images)
                combined = Image.new('RGB', (max_width * cols, max_height * rows), '#f5f5f0')
                for idx, img in enumerate(images):
                    row = idx // cols
                    col = idx % cols
                    x = col * max_width
                    y = row * max_height
                    combined.paste(img, (x, y))
            
            return combined
        
        if group_by_role:
            # 按角色分组
            groups = {}
            for card in cards:
                role = card['role'].lower()
                if role not in groups:
                    groups[role] = []
                groups[role].append(card)
            
            # 为每组生成拼接图片
            results = {}
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for role, role_cards in groups.items():
                # 生成单个工卡
                badge_paths = []
                for card in role_cards:
                    badge_data = create_badge_data(card)
                    path = generator.create_badge(badge_data)
                    badge_paths.append(path)
                
                # 确定布局
                group_layout = 'horizontal' if len(role_cards) <= 3 else 'grid'
                
                # 拼接
                combined = combine_badges(badge_paths, group_layout)
                output_file = generator.output_dir / f"badges_{role}_{timestamp}.png"
                combined.save(output_file)
                
                results[role] = str(output_file)
                
                # 发送分组通知
                self._notify_group_badges_created(role, role_cards, str(output_file))
            
            return results
        else:
            # 不分组，全部一起
            badge_paths = []
            for card in cards:
                badge_data = create_badge_data(card)
                path = generator.create_badge(badge_data)
                badge_paths.append(path)
            
            combined = combine_badges(badge_paths, layout)
            
            if output_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = generator.output_dir / f"badges_multi_{layout}_{timestamp}.png"
            
            combined.save(output_path)
            return str(output_path)


    def check_expired(self, auto_terminate: bool = True) -> list:
        """
        检查并处理超时的 SubAgent
        
        Args:
            auto_terminate: 如果 True，自动终止超时的 SubAgent
        
        Returns:
            list: 超时的 subagent 工号列表
        """
        now = datetime.now()
        expired = []
        
        for sa in self.registry["subagents"]:
            if sa["status"] in [SubAgentStatus.PENDING.value, SubAgentStatus.ACTIVE.value]:
                deadline_str = sa.get("task", {}).get("deadline")
                if deadline_str:
                    try:
                        deadline = datetime.fromisoformat(deadline_str)
                        if now > deadline:
                            emp_id = sa["employee_id"]
                            expired.append(emp_id)
                            if auto_terminate:
                                print(f"⏰ Auto-terminating expired SubAgent: {emp_id}")
                                self.terminate(emp_id, "timeout_expired")
                    except ValueError:
                        pass  # Invalid deadline format
        
        return expired

if __name__ == "__main__":
    print("FIS 3.1 SubAgent Lifecycle Manager loaded")
