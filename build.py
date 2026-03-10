"""
@文件: build.py
@作者: 雷小鸥
@日期: 2026/3/10 18:58
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
import subprocess
import shutil
import sys
from pathlib import Path

from src.core import APP_DIR as _tmp

# 1. 执行打包
print("正在打包...")
subprocess.run(['pyinstaller', '--clean', 'main.spec'], check=True)

# 2. 确定可执行文件名
project_root = Path.cwd()
exe_name = 'ssh_playbook.exe' if sys.platform.startswith('win') else 'ssh_playbook'
src_exe = project_root / 'dist' / exe_name

# 3. 移动到临时目录
dst_exe = _tmp / exe_name

if src_exe.exists():
    shutil.move(str(src_exe), str(dst_exe))
    print(f"✅ 可执行文件已移动到: {dst_exe}")
else:
    print(f"❌ 未找到可执行文件: {src_exe}")
    sys.exit(1)
