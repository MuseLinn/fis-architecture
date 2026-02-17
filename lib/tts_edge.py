#!/usr/bin/env python3
"""
OpenClaw TTS Integration - Edge-TTS
CosyVoice 备选方案 - 无需 GPU，完全免费
"""

import asyncio
import edge_tts
import tempfile
from pathlib import Path
from typing import Optional

# Voice presets
VOICES = {
    # 女声
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",      # 晓晓 - 活泼俏皮
    "xiaoyi": "zh-CN-XiaoyiNeural",          # 小艺 - 温柔知性
    "yunxi": "zh-CN-YunxiNeural",            # 云希 - 专业稳重
    
    # 男声
    "yunjian": "zh-CN-YunjianNeural",        # 云健 - 稳重成熟
    "yunyang": "zh-CN-YunyangNeural",        # 云扬 - 年轻活力
    
    # 方言
    "xiaoxuan": "zh-CN-XiaoxuanNeural",      # 晓萱 - 东北话
    "xiaomeng": "zh-CN-XiaomengNeural",      # 晓梦 - 陕西话
    "xiaobei": "zh-CN-XiaobeiNeural",        # 晓北 - 粤语
}

DEFAULT_VOICE = "xiaoxiao"

def get_voice_id(voice_name: str) -> str:
    """Get voice ID from name"""
    return VOICES.get(voice_name, VOICES[DEFAULT_VOICE])

async def text_to_speech(
    text: str,
    output_path: Optional[str] = None,
    voice: str = DEFAULT_VOICE,
    rate: str = "+0%",
    volume: str = "+0%"
) -> str:
    """
    Convert text to speech using Edge-TTS
    
    Args:
        text: Text to synthesize
        output_path: Output file path (auto-generated if None)
        voice: Voice name (xiaoxiao, yunjian, etc.)
        rate: Speech rate (-50% to +100%)
        volume: Volume (-100% to +100%)
    
    Returns:
        output_path: Path to generated audio file
    """
    voice_id = get_voice_id(voice)
    
    if output_path is None:
        output_file = tempfile.NamedTemporaryFile(
            suffix=".mp3", delete=False
        )
        output_path = output_file.name
    
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice_id,
        rate=rate,
        volume=volume
    )
    
    await communicate.save(output_path)
    return output_path

def synthesize(
    text: str,
    output_path: Optional[str] = None,
    voice: str = DEFAULT_VOICE,
    **kwargs
) -> str:
    """
    Synchronous wrapper for text_to_speech
    
    Usage:
        output = synthesize("你好，这是测试")
        output = synthesize("你好", voice="yunjian")
    """
    return asyncio.run(text_to_speech(text, output_path, voice, **kwargs))

def list_voices():
    """List available voices"""
    print("🎙️  Available Voices (Edge-TTS)")
    print("=" * 50)
    
    categories = {
        "女声": ["xiaoxiao", "xiaoyi", "yunxi"],
        "男声": ["yunjian", "yunyang"],
        "方言": ["xiaoxuan", "xiaomeng", "xiaobei"]
    }
    
    for category, voices in categories.items():
        print(f"\n{category}:")
        for v in voices:
            print(f"  - {v}: {VOICES[v]}")
    
    print(f"\nDefault: {DEFAULT_VOICE}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list-voices":
        list_voices()
        sys.exit(0)
    
    # Test synthesis
    text = sys.argv[1] if len(sys.argv) > 1 else "你好，这是赛博毛毛的语音测试。"
    voice = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_VOICE
    
    output = synthesize(text, voice=voice)
    print(f"✅ Generated: {output}")
