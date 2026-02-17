#!/usr/bin/env python3
"""
FIS 3.1 Lite - 初始化脚本
一键部署 FIS 3.1 环境
"""

import sys
from pathlib import Path

# Add skill lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

def init_fis31():
    """Initialize FIS 3.1 Lite environment"""
    
    print("🚀 FIS 3.1 Lite Initialization")
    print("=" * 50)
    
    # Check directories
    openclaw_dir = Path.home() / ".openclaw"
    fis31_dir = openclaw_dir / "research-uav-gpr" / ".fis3.1"
    
    print(f"\n📁 OpenClaw directory: {openclaw_dir}")
    print(f"📁 FIS 3.1 directory: {fis31_dir}")
    
    # Create structure
    dirs = [
        fis31_dir / "memories" / "working",
        fis31_dir / "memories" / "short_term", 
        fis31_dir / "memories" / "long_term",
        fis31_dir / "skills" / "manifests",
        fis31_dir / "lib",
        fis31_dir / "heartbeat"
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {d.relative_to(openclaw_dir)}")
    
    # Create initial registry
    registry_file = fis31_dir / "skills" / "registry.json"
    if not registry_file.exists():
        import json
        registry = {
            "version": "3.1.0-lite",
            "agents": [],
            "skills": [],
            "last_updated": "2026-02-17T20:00:00+08:00"
        }
        with open(registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        print(f"  ✅ Created registry.json")
    
    # Create subagent registry
    subagent_file = fis31_dir / "subagent_registry.json"
    if not subagent_file.exists():
        import json
        registry = {
            "version": "3.1.0-lite",
            "subagents": [],
            "id_counter": 0
        }
        with open(subagent_file, 'w') as f:
            json.dump(registry, f, indent=2)
        print(f"  ✅ Created subagent_registry.json")
    
    print("\n" + "=" * 50)
    print("✅ FIS 3.1 Lite initialized successfully!")
    print("\nNext steps:")
    print("  1. Create Agent extensions: mkdir workspace/.fis3.1")
    print("  2. Register skills: python3 -m skill_registry")
    print("  3. Spawn subagents: python3 subagent_pipeline.py")

if __name__ == "__main__":
    init_fis31()
