"""
@文件: helper.py
@作者: 雷小鸥
@日期: 2026/3/10 15:18
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):  # 打包
    ROOT = Path(sys._MEIPASS)
    APP_DIR = Path(sys.executable).parent
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(APP_DIR))
else:
    ROOT = Path(__file__).parents[2]
    APP_DIR = ROOT / 'tmp'
    sys.path.insert(0, str(ROOT))

# print(APP_DIR, ROOT)
