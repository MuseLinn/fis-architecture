#!/usr/bin/env python3
"""
FIS 3.1 工卡生成器 v7.0 - 优化版

改进内容：
- 动态获取工作区路径，避免硬编码
- 增加高度，预留更多文本空间
- 输出要求分行显示，包含具体任务要求
- 缩减宽度，优化布局
- 右侧添加倾斜像素工牌装饰
- 动态获取 OpenClaw 版本号
- 修复中文显示支持

Author: CyberMao
Version: 3.1.4
"""

from PIL import Image, ImageDraw, ImageFont
import random
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class BadgeGenerator:
    """FIS 3.1 SubAgent Badge Generator - Optimized Layout"""
    
    # 优化后的尺寸
    WIDTH = 900          # 缩减宽度 (原1200)
    HEIGHT = 520         # 增加高度 (原400)
    
    # 配色方案
    COLORS = {
        'primary': '#ff4d00',      # Orange
        'background': '#f5f5f0',   # Off-white paper
        'border': '#1a1a1a',       # Black
        'text': '#1a1a1a',         # Black text
        'secondary': '#666666',    # Gray
        'muted': '#999999',        # Light gray
        'divider': '#dddddd',      # Divider line
        'paper_line': '#e8e8e3',   # Paper texture
        'active': '#00c853',       # Green active
        'translucent': (26, 26, 26, 128),  # 半透明黑色
    }
    
    def __init__(self, output_dir=None):
        self.width = self.WIDTH
        self.height = self.HEIGHT
        
        # 动态获取输出目录 - 优先使用环境变量或标准路径
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # 尝试多个可能的路径
            possible_paths = [
                Path(os.environ.get('OPENCLAW_WORKSPACE', '')) / 'output' / 'badges',
                Path.home() / '.openclaw' / 'output' / 'badges',
                Path.home() / '.openclaw' / 'workspace' / 'output' / 'badges',
                Path.cwd() / 'output' / 'badges',
            ]
            
            for path in possible_paths:
                if path.parent.exists():
                    self.output_dir = path
                    break
            else:
                # 回退到当前目录
                self.output_dir = Path.cwd() / 'badges'
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载字体 - 支持中文
        self.fonts = self._load_fonts()
        
        # 获取 OpenClaw 版本
        self.openclaw_version = self._get_openclaw_version()
    
    def _get_openclaw_version(self):
        """动态获取 OpenClaw 版本号 - 格式: vYYYY.MM.DD"""
        try:
            result = subprocess.run(
                ['openclaw', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # 提取版本号 - 处理 "openclaw version 2026.2.17" 或 "2026.2.17" 格式
                import re
                match = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', version_str)
                if match:
                    year, month, day = match.groups()
                    return f"v{year}.{month.zfill(1)}.{day.zfill(1)}"  # 保持原始数字，不添加前导零
                return version_str
        except Exception as e:
            pass
        
        # 回退到默认版本
        return 'v2026.2.17'
    
    def _load_fonts(self):
        """加载支持中文的字体 - 修复 .ttc 文件索引问题"""
        # 中文字体配置: (路径, index) - 对于 .ttc 文件需要正确的索引
        # uming.ttc: index 0 = AR PL UMing (Latin), index 1 = AR PL UMing TW (中文)
        # wqy-zenhei.ttc: index 0 = 文泉驿正黑 (中文), index 1 = 文泉驿等宽正黑
        chinese_font_configs = [
            ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 0),  # 优先使用文泉驿，index 0 是中文
            ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
            ("/usr/share/fonts/truetype/arphic/uming.ttc", 1),    # index 1 是中文 (TW)
            ("/usr/share/fonts/truetype/arphic/ukai.ttc", 1),     # index 1 是中文 (TW)
            ("/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf", None),
            ("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", None),
        ]
        
        # 等宽英文字体
        mono_font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        ]
        
        fonts = {}
        default_font = ImageFont.load_default()
        
        # 尝试加载中文字体
        chinese_font = None
        chinese_font_index = None
        
        for path, index in chinese_font_configs:
            if os.path.exists(path):
                try:
                    # 测试字体是否可用 - ttc文件需要指定index
                    if index is not None:
                        test_font = ImageFont.truetype(path, 12, index=index)
                    else:
                        test_font = ImageFont.truetype(path, 12)
                    
                    # 测试是否能渲染中文
                    test_text = "中文测试"
                    bbox = test_font.getbbox(test_text)
                    if bbox and bbox[2] > bbox[0]:  # 宽度大于0说明能渲染
                        chinese_font = path
                        chinese_font_index = index
                        print(f"  Loaded Chinese font: {path} (index={index})")
                        break
                except Exception as e:
                    print(f"  Failed to load {path} (index={index}): {e}")
                    continue
        
        if not chinese_font:
            print("  Warning: No Chinese font found, using default")
        
        # 尝试加载等宽字体
        mono_font = None
        for path in mono_font_paths:
            if os.path.exists(path):
                try:
                    mono_font = path
                    break
                except:
                    continue
        
        # 创建字体变体
        try:
            if chinese_font:
                # 为 ttc 文件传递 index 参数
                font_kwargs = {'index': chinese_font_index} if chinese_font_index is not None else {}
                fonts['title'] = ImageFont.truetype(chinese_font, 18, **font_kwargs)
                fonts['header'] = ImageFont.truetype(chinese_font, 13, **font_kwargs)
                fonts['text'] = ImageFont.truetype(chinese_font, 11, **font_kwargs)
                fonts['small'] = ImageFont.truetype(chinese_font, 9, **font_kwargs)
            else:
                fonts['title'] = ImageFont.truetype(mono_font, 18) if mono_font else default_font
                fonts['header'] = ImageFont.truetype(mono_font, 13) if mono_font else default_font
                fonts['text'] = ImageFont.truetype(mono_font, 11) if mono_font else default_font
                fonts['small'] = ImageFont.truetype(mono_font, 9) if mono_font else default_font
            
            fonts['pixel'] = ImageFont.truetype(mono_font, 9) if mono_font else default_font
        except Exception as e:
            print(f"  Font loading error: {e}")
            fonts = {k: default_font for k in ['title', 'header', 'text', 'small', 'pixel']}
        
        return fonts
    
    def create_badge(self, agent_data, output_path=None):
        """Create optimized badge layout"""
        # 创建画布
        card = Image.new('RGB', (self.width, self.height), self.COLORS['background'])
        draw = ImageDraw.Draw(card)
        
        # 添加纸质纹理
        self._add_paper_texture(draw)
        
        # 添加边框
        self._add_border(draw)
        
        # 添加头部
        self._add_header(draw, agent_data)
        
        # 添加左侧区域（头像 + 身份信息）
        self._add_left_section(draw, agent_data)
        
        # 添加右侧区域（职责 + 详细任务要求）
        self._add_right_section(draw, agent_data)
        
        # 添加右侧倾斜像素装饰
        self._add_tilted_pixel_badge(draw, agent_data)
        
        # 添加底部
        self._add_footer(draw, agent_data)
        
        # 保存
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            agent_id = agent_data.get('id', 'UNKNOWN').replace('/', '-')
            output_path = self.output_dir / f"badge_v7_{agent_id}_{timestamp}.png"
        
        card.save(output_path)
        return str(output_path)
    
    def _add_paper_texture(self, draw):
        """添加纸质纹理线条"""
        for y in range(0, self.height, 2):
            if y % 4 == 0:
                draw.line([(0, y), (self.width, y)], fill=self.COLORS['paper_line'], width=1)
    
    def _add_border(self, draw):
        """添加黑色边框"""
        draw.rectangle([3, 12, self.width - 3, self.height - 12], 
                      outline=self.COLORS['border'], width=3)
    
    def _add_header(self, draw, agent_data):
        """添加头部区域"""
        header_y = 30
        
        # Logo 和标题
        draw.text((30, header_y), "⚡", fill=self.COLORS['primary'], font=self.fonts['title'])
        draw.text((60, header_y), f"OPENCLAW {self.openclaw_version}", 
                 fill=self.COLORS['border'], font=self.fonts['header'])
        draw.text((60, header_y + 18), "FEDERAL INTELLIGENCE SYSTEM", 
                 fill=self.COLORS['secondary'], font=self.fonts['small'])
        
        # 右侧任务ID
        task_id = agent_data.get('task_id', '#UNKNOWN')
        # 计算文本宽度以便右对齐
        draw.text((self.width - 120, header_y), task_id, 
                 fill=self.COLORS['primary'], font=self.fonts['title'])
        
        # 虚线分隔线
        for x in range(30, self.width - 30, 8):
            draw.line([(x, header_y + 45), (x + 4, header_y + 45)], fill='#333333', width=1)
    
    def _add_left_section(self, draw, agent_data):
        """添加左侧区域"""
        left_x = 40
        avatar_y = 90
        
        # 头像框架（橙色圆圈）
        draw.ellipse([left_x, avatar_y, left_x + 70, avatar_y + 70],
                    outline=self.COLORS['primary'], width=4)
        
        # CryptoPunks 风格随机像素头像
        self._draw_cryptopunk_avatar(draw, left_x, avatar_y)
        
        # 角色标签（固定宽度）
        role = agent_data.get('role', 'AGENT').upper()
        badge_y = avatar_y + 85
        badge_width = 100
        draw.rectangle([left_x, badge_y, left_x + badge_width, badge_y + 22],
                      fill=self.COLORS['border'], outline=self.COLORS['primary'], width=2)
        
        # 居中文字
        bbox = draw.textbbox((0, 0), role, font=self.fonts['pixel'])
        text_width = bbox[2] - bbox[0]
        text_x = left_x + (badge_width - text_width) // 2
        draw.text((text_x, badge_y + 5), role, fill='#ffffff', font=self.fonts['pixel'])
        
        # Agent 元数据
        draw.text((left_x, badge_y + 35), "AGENT NAME", fill=self.COLORS['muted'], font=self.fonts['small'])
        name = agent_data.get('name', 'Unknown Agent')
        draw.text((left_x, badge_y + 50), name[:18], fill=self.COLORS['border'], font=self.fonts['header'])
        
        agent_id = agent_data.get('id', 'UNKNOWN')
        draw.text((left_x, badge_y + 72), f"ID: {agent_id}", fill=self.COLORS['secondary'], font=self.fonts['small'])
    
    def _draw_cryptopunk_avatar(self, draw, left_x, avatar_y):
        """绘制 CryptoPunks 风格随机像素头像"""
        colors = {
            'skin': ['#f5d0b0', '#e8c4a0', '#d4a574', '#8d5524', '#523418', '#f8e8d8'],
            'hair': ['#ff6b00', '#4a4a4a', '#8b4513', '#ffd700', '#ff0000', '#000000'],
            'eyes': ['#000000', '#4169e1', '#228b22', '#8b4513', '#9370db'],
            'accessory': ['#ff6b00', '#ffd700', '#c0c0c0', '#4169e1'],
            'bg': ['#1a1a1a', '#ff4d00', '#4169e1', '#228b22'],
        }
        
        random.seed(left_x + avatar_y)
        
        center_x = left_x + 35
        center_y = avatar_y + 35
        pixel_size = 7
        
        # 背景
        bg_color = random.choice(colors['bg'])
        for y in range(avatar_y + 6, avatar_y + 64, pixel_size):
            for x in range(left_x + 6, left_x + 64, pixel_size):
                dist = ((x + pixel_size//2 - center_x) ** 2 + 
                       (y + pixel_size//2 - center_y) ** 2) ** 0.5
                if dist < 28:
                    draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill=bg_color)
        
        # 脸部
        skin_color = random.choice(colors['skin'])
        face_x = center_x - 21
        face_y = center_y - 14
        for y in range(face_y, face_y + 42, pixel_size):
            for x in range(face_x, face_x + 42, pixel_size):
                dist = ((x + pixel_size//2 - center_x) ** 2 + 
                       (y + pixel_size//2 - center_y) ** 2) ** 0.5
                if dist < 24:
                    draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill=skin_color)
        
        # 眼睛
        eye_color = random.choice(colors['eyes'])
        draw.rectangle([face_x + 7, face_y + 14, face_x + 14, face_y + 21], fill=eye_color)
        draw.rectangle([face_x + 28, face_y + 14, face_x + 35, face_y + 21], fill=eye_color)
        
        # 嘴巴
        draw.rectangle([face_x + 14, face_y + 32, face_x + 28, face_y + 36], fill='#000000')
        
        random.seed()
    
    def _add_right_section(self, draw, agent_data):
        """添加右侧区域 - 包含详细任务要求"""
        right_x = 220
        section_y = 90
        
        # SOUL 标签（橙色）
        soul = agent_data.get('soul', '"Digital familiar navigating the void"')
        draw.rectangle([right_x, section_y, right_x + 70, section_y + 22],
                      fill=self.COLORS['primary'], outline=self.COLORS['border'], width=2)
        draw.text((right_x + 8, section_y + 5), "SOUL", fill='#ffffff', font=self.fonts['pixel'])
        draw.text((right_x + 80, section_y + 3), soul[:40], fill=self.COLORS['primary'], font=self.fonts['text'])
        
        # RESPONSIBILITIES 标签（黑色）
        resp_y = section_y + 40
        draw.rectangle([right_x, resp_y, right_x + 140, resp_y + 22],
                      fill=self.COLORS['border'], outline=self.COLORS['border'], width=2)
        draw.text((right_x + 8, resp_y + 5), "RESPONSIBILITIES", fill='#ffffff', font=self.fonts['pixel'])
        
        # 职责列表
        responsibilities = agent_data.get('responsibilities', [
            "Execute assigned tasks with precision",
            "Maintain communication with parent agent",
            "Report progress and blockers promptly",
        ])
        
        for i, bullet in enumerate(responsibilities[:3]):
            y = resp_y + 28 + (i * 18)
            text = bullet[:55]  # 截断长文本
            draw.text((right_x + 8, y), f"▸ {text}", fill=self.COLORS['border'], font=self.fonts['small'])
        
        # 输出要求 - 第一行：格式标签
        out_y = resp_y + 95
        draw.rectangle([right_x, out_y, right_x + 100, out_y + 22],
                      fill='#666666', outline=self.COLORS['border'], width=2)
        draw.text((right_x + 8, out_y + 5), "OUTPUT REQ", fill='#ffffff', font=self.fonts['pixel'])
        
        output_formats = agent_data.get('output_formats', 'MARKDOWN | JSON | TXT')
        draw.text((right_x + 108, out_y + 5), output_formats, 
                 fill=self.COLORS['border'], font=self.fonts['small'])
        
        # 输出要求 - 第二行：具体任务要求（新增）
        task_req_y = out_y + 28
        task_requirements = agent_data.get('task_requirements', [
            "1. Analyze code structure and dependencies",
            "2. Provide detailed line count statistics",
            "3. Report top 5 largest files",
        ])
        
        draw.text((right_x, task_req_y), "任务输出要求:", 
                 fill=self.COLORS['primary'], font=self.fonts['small'])
        
        for i, req in enumerate(task_requirements[:3]):
            y = task_req_y + 18 + (i * 16)
            text = req[:50]
            draw.text((right_x + 8, y), f"• {text}", fill=self.COLORS['secondary'], font=self.fonts['small'])
        
        # 垂直分隔线
        draw.line([(210, 80), (210, self.height - 80)], fill=self.COLORS['divider'], width=2)
    
    def _add_tilted_pixel_badge(self, draw, agent_data):
        """添加右侧倾斜像素工牌装饰"""
        # 在右侧空白区域绘制一个倾斜的像素风格小工牌
        badge_x = self.width - 140
        badge_y = 200
        
        # 创建半透明层
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # 倾斜角度模拟 - 通过绘制偏移的矩形
        # 外框
        for offset in range(3):
            overlay_draw.rectangle(
                [badge_x + offset, badge_y - offset, badge_x + 80 + offset, badge_y + 100 - offset],
                outline=(255, 77, 0, 100),  # 半透明橙色
                width=2
            )
        
        # 内部像素头像简化版
        pixel_size = 4
        for row in range(12):
            for col in range(12):
                if random.random() > 0.3:  # 70% 填充率
                    color = random.choice([
                        (255, 77, 0, 150),   # 橙色
                        (26, 26, 26, 150),   # 黑色
                        (102, 102, 102, 100), # 灰色
                    ])
                    x = badge_x + 10 + col * pixel_size
                    y = badge_y + 10 + row * pixel_size
                    overlay_draw.rectangle(
                        [x, y, x + pixel_size, y + pixel_size],
                        fill=color
                    )
        
        # 工号文字
        agent_id = agent_data.get('id', 'ID')[4:8] if len(agent_data.get('id', '')) > 8 else '0001'
        overlay_draw.text((badge_x + 15, badge_y + 70), f"#{agent_id}", 
                         fill=(255, 77, 0, 200), font=self.fonts['small'])
        
        # 将半透明层合并到主画布
        # 由于 PIL Draw 不支持直接混合，我们使用简单方法
        # 在 draw 上直接绘制低饱和度的颜色来模拟透明效果
        badge_color = '#ff4d00'
        for offset in range(2):
            draw.rectangle(
                [badge_x + offset, badge_y - offset, badge_x + 70 + offset, badge_y + 90 - offset],
                outline='#ffaa80',  # 浅橙色模拟透明
                width=1
            )
    
    def _add_footer(self, draw, agent_data):
        """添加底部区域"""
        footer_y = self.height - 65
        
        # 黑色背景底栏
        draw.rectangle([3, footer_y, self.width - 3, self.height - 12],
                      fill=self.COLORS['border'])
        
        # 条形码
        bar_x = 30
        bar_width = 2
        bar_spacing = 2
        for i in range(35):
            draw.rectangle([bar_x, footer_y + 8, bar_x + bar_width, footer_y + 30], fill='#ffffff')
            bar_x += bar_width + bar_spacing
        
        # 条形码ID
        barcode_id = agent_data.get('barcode_id', f"OC-2025-{agent_data.get('role', 'AGENT')[:4].upper()}-001")
        draw.text((30, footer_y + 35), barcode_id, fill='#666666', font=self.fonts['small'])
        
        # 状态指示器
        status = agent_data.get('status', 'PENDING')
        status_color = self.COLORS['active'] if status == 'ACTIVE' else '#ff4d00'
        status_x = 280
        draw.ellipse([status_x, footer_y + 12, status_x + 12, footer_y + 24], 
                    fill=status_color, outline='#ffffff', width=1)
        draw.text((status_x + 18, footer_y + 12), status, fill='#ffffff', font=self.fonts['pixel'])
        
        # 有效期
        valid_until = agent_data.get('valid_until', 
                                     (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'))
        draw.text((self.width - 200, footer_y + 12), f"VALID UNTIL: {valid_until}", 
                 fill='#666666', font=self.fonts['small'])
        
        # 右下角像素二维码占位
        qr_x, qr_y = self.width - 60, footer_y + 8
        for i in range(5):
            for j in range(5):
                if (i + j) % 2 == 0:
                    draw.rectangle([qr_x + i * 8, qr_y + j * 8, qr_x + i * 8 + 6, qr_y + j * 8 + 6], 
                                  fill='#ffffff')


def generate_badge_with_task(agent_name, role, task_desc, task_requirements, output_dir=None):
    """
    便捷函数：生成带详细任务要求的工卡
    
    Args:
        agent_name: 子代理名称
        role: 角色 (WORKER/RESEARCHER/REVIEWER/FORMATTER)
        task_desc: 任务描述
        task_requirements: 任务输出要求列表
        output_dir: 输出目录
    """
    generator = BadgeGenerator(output_dir)
    
    # 生成唯一ID
    timestamp = datetime.now()
    agent_id = f"CYBERMAO-SA-{timestamp.year}-{timestamp.strftime('%m%d%H%M')}"
    
    agent_data = {
        'name': agent_name,
        'id': agent_id,
        'role': role,
        'task_id': f"#{role[:4].upper()}-{timestamp.strftime('%m%d')}",
        'soul': f'"{task_desc[:30]}..."' if len(task_desc) > 30 else f'"{task_desc}"',
        'responsibilities': [
            "Execute task with precision and quality",
            "Report progress within deadline",
            "Follow FIS 3.1 protocol standards",
        ],
        'output_formats': 'MARKDOWN | JSON | TXT',
        'task_requirements': task_requirements,
        'barcode_id': f"OC-{timestamp.year}-{role[:4].upper()}-{timestamp.strftime('%m%d')}",
        'status': 'PENDING',
    }
    
    return generator.create_badge(agent_data)


if __name__ == "__main__":
    # 测试生成工卡
    print("=== FIS 3.1 Badge Generator v7.0 ===")
    
    # 示例：统计代码行数任务
    badge_path = generate_badge_with_task(
        agent_name="CodeStats-001",
        role="RESEARCHER",
        task_desc="统计 workspace 下所有 Python 文件的行数",
        task_requirements=[
            "1. Find all .py files recursively",
            "2. Count lines for each file",
            "3. Report top 5 largest files",
            "4. Calculate total line count",
        ]
    )
    
    print(f"✅ Badge generated: {badge_path}")
