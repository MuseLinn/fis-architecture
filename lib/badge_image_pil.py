"""
FIS 3.1 Lite - Badge Image Generator (PIL Version)
工卡图片生成器 - 纯 Python 实现
"""

from PIL import Image, ImageDraw, ImageFont
import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path.home() / ".openclaw" / "output" / "badges"

def get_font(size: int) -> ImageFont.FreeTypeFont:
    """Get font with fallbacks"""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    
    for path in font_paths:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    
    return ImageFont.load_default()

def get_font_bold(size: int) -> ImageFont.FreeTypeFont:
    """Get bold font with fallbacks"""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    ]
    
    for path in font_paths:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    
    return get_font(size)

def draw_rounded_rect(draw: ImageDraw.Draw, xy: tuple, radius: int, fill: tuple, outline: tuple = None):
    """Draw rounded rectangle"""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)

def generate_single_badge(card: dict, output_path: Path = None) -> Path:
    """Generate a single badge image"""
    # Image dimensions
    WIDTH, HEIGHT = 800, 500
    
    # Create image
    img = Image.new('RGB', (WIDTH, HEIGHT), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # Card background with shadow effect
    card_margin = 40
    card_w = WIDTH - 2 * card_margin
    card_h = HEIGHT - 2 * card_margin
    
    # Shadow
    draw.rounded_rectangle(
        [card_margin + 5, card_margin + 5, card_margin + card_w + 5, card_margin + card_h + 5],
        radius=20,
        fill='#0f0f1a'
    )
    
    # Card background
    draw.rounded_rectangle(
        [card_margin, card_margin, card_margin + card_w, card_margin + card_h],
        radius=20,
        fill='#ffffff'
    )
    
    # Header gradient bar
    header_h = 80
    # Draw gradient manually
    for y in range(header_h):
        ratio = y / header_h
        r = int(102 + (118 - 102) * ratio)  # #667eea to #764ba2
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)
        draw.line(
            [(card_margin + 20, card_margin + y), (card_margin + card_w - 20, card_margin + y)],
            fill=(r, g, b)
        )
    
    # Header text
    font_title = get_font_bold(28)
    font_subtitle = get_font(18)
    
    draw.text((card_margin + 40, card_margin + 15), "FIS 3.1 LITE", fill='white', font=font_title)
    draw.text((card_margin + 40, card_margin + 48), "联邦智能系统 · 子代理工卡", fill='#e0e0ff', font=font_subtitle)
    
    # Photo placeholder (circle)
    photo_x = card_margin + 60
    photo_y = card_margin + header_h + 40
    photo_size = 120
    
    # Photo background
    draw.ellipse(
        [photo_x, photo_y, photo_x + photo_size, photo_y + photo_size],
        fill='#f0f0f0',
        outline='#667eea',
        width=4
    )
    
    # Emoji/Icon
    font_emoji = get_font(60)
    emoji_map = {
        'worker': '🔧',
        'reviewer': '👁️',
        'researcher': '🔬',
        'formatter': '🎨'
    }
    emoji = emoji_map.get(card['role'], '🤖')
    draw.text((photo_x + 35, photo_y + 25), emoji, font=font_emoji)
    
    # Info section
    info_x = card_margin + 220
    info_y = card_margin + header_h + 40
    
    font_label = get_font(16)
    font_value = get_font_bold(24)
    font_mono = get_font(20)
    
    # Employee ID
    draw.text((info_x, info_y), "Employee ID", fill='#888888', font=font_label)
    draw.rounded_rectangle(
        [info_x, info_y + 25, info_x + 320, info_y + 60],
        radius=8,
        fill='#f0f0f0'
    )
    draw.text((info_x + 15, info_y + 28), card['employee_id'], fill='#333333', font=font_mono)
    
    # Name
    draw.text((info_x, info_y + 75), "Name", fill='#888888', font=font_label)
    draw.text((info_x, info_y + 100), card['name'], fill='#333333', font=font_value)
    
    # Role badge
    draw.text((info_x, info_y + 150), "Role", fill='#888888', font=font_label)
    
    role_colors = {
        'worker': ('#e3f2fd', '#1976d2'),
        'reviewer': ('#f3e5f5', '#7b1fa2'),
        'researcher': ('#e8f5e9', '#388e3c'),
        'formatter': ('#fff3e0', '#f57c00')
    }
    bg_color, text_color = role_colors.get(card['role'], ('#e0e0e0', '#333333'))
    
    badge_w = 160
    badge_h = 40
    draw.rounded_rectangle(
        [info_x, info_y + 175, info_x + badge_w, info_y + 175 + badge_h],
        radius=20,
        fill=bg_color
    )
    draw.text((info_x + 20, info_y + 180), card['role'].upper(), fill=text_color, font=get_font_bold(18))
    
    # Status
    draw.text((info_x + 200, info_y + 150), "Status", fill='#888888', font=font_label)
    
    status_colors = {
        'active': '#4caf50',
        'pending': '#ff9800',
        'terminated': '#f44336'
    }
    status_color = status_colors.get(card['status'], '#888888')
    
    # Status dot
    draw.ellipse([info_x + 200, info_y + 180, info_x + 220, info_y + 200], fill=status_color)
    draw.text((info_x + 230, info_y + 178), card['status'].upper(), fill=status_color, font=get_font_bold(18))
    
    # Permissions section
    perm_y = card_margin + card_h - 100
    draw.line([(card_margin + 40, perm_y), (card_margin + card_w - 40, perm_y)], fill='#e0e0e0', width=2)
    
    draw.text((card_margin + 40, perm_y + 15), "Permissions", fill='#888888', font=font_label)
    
    perms = card['permissions']
    perm_items = [
        (perms.get('can_read_shared_hub', False), "Read Shared"),
        (perms.get('can_write_shared_hub', False), "Write (via Parent)"),
        (perms.get('can_call_other_agents', False), "Call Agents"),
        (perms.get('can_modify_tickets', False), "Modify Tickets")
    ]
    
    perm_x = card_margin + 40
    for i, (allowed, label) in enumerate(perm_items):
        x = perm_x + (i % 2) * 250
        y = perm_y + 45 + (i // 2) * 30
        
        icon = "✓" if allowed else "✗"
        color = '#4caf50' if allowed else '#f44336'
        
        draw.text((x, y), icon, fill=color, font=get_font(18))
        draw.text((x + 25, y), label, fill='#666666', font=font_label)
    
    # Footer
    footer_y = card_margin + card_h - 35
    font_footer = get_font(16)
    
    draw.text((card_margin + 40, footer_y), f"Dept: {card['parent']}", fill='#667eea', font=get_font_bold(16))
    
    deadline = card['task']['deadline'][:16].replace('T', ' ')
    draw.text((card_margin + card_w - 280, footer_y), f"Valid until: {deadline}", fill='#999999', font=font_footer)
    
    # Save
    if output_path is None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / f"badge_{card['employee_id']}.png"
    
    img.save(output_path, 'PNG', quality=95)
    return output_path

def generate_multi_badge_image(cards: list, output_name: str = None) -> Path:
    """Generate multiple badges in one image (grid layout)"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if output_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"badges_multi_{timestamp}.png"
    
    output_path = OUTPUT_DIR / output_name
    
    # Calculate grid
    num_cards = len(cards)
    cols = min(2, num_cards)
    rows = (num_cards + cols - 1) // cols
    
    # Single badge size
    badge_w, badge_h = 800, 500
    padding = 40
    
    # Canvas size
    canvas_w = cols * (badge_w + padding) + padding
    canvas_h = rows * (badge_h + padding) + padding
    
    # Create canvas
    canvas = Image.new('RGB', (canvas_w, canvas_h), color='#1a1a2e')
    
    for i, card in enumerate(cards):
        # Generate single badge
        single = generate_single_badge(card)
        badge_img = Image.open(single)
        
        # Calculate position
        row = i // cols
        col = i % cols
        x = padding + col * (badge_w + padding)
        y = padding + row * (badge_h + padding)
        
        # Paste
        canvas.paste(badge_img, (x, y))
    
    canvas.save(output_path, 'PNG', quality=95)
    return output_path

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    
    print("🎫 FIS 3.1 Badge Image Generator (PIL)")
    print("=" * 50)
    
    # Load subagents
    from fis_config import get_shared_hub_path
    registry_file = get_shared_hub_path() / ".fis3.1" / "subagent_registry.json"
    
    if registry_file.exists():
        with open(registry_file) as f:
            registry = json.load(f)
        
        subagents = registry.get("subagents", [])
        
        if subagents:
            print(f"\nFound {len(subagents)} subagent(s)")
            
            # Generate multi-badge image
            multi_path = generate_multi_badge_image(subagents)
            print(f"✅ Multi-badge image: {multi_path}")
            
            # Generate individual badges
            for card in subagents:
                single_path = generate_single_badge(card)
                print(f"✅ {card['employee_id']}: {single_path.name}")
            
            print(f"\n📁 All images saved to: {OUTPUT_DIR}")
        else:
            print("\n⚠️  No subagents found")
    else:
        print("\n⚠️  Registry not found")
