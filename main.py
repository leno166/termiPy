"""
@文件: main.py
@作者: 雷小鸥
@日期: 2026/3/10 08:47
@许可: MIT License
@描述:
    stubgen -p src -o ./typings

    用法：
        app

@版本: Version 1.0
"""
import argparse
import sys
import os
from pathlib import Path
import importlib.util

from src.core import ROOT, APP_DIR
from src.sShell import AutoConnect as App, SshSession
from src.SqliteEditor import init_database

DATABASE_PATH = ROOT / 'release' / 'ssh.db'
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_config(config_path: Path):
    spec = importlib.util.spec_from_file_location("config", config_path)
    mod = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(mod)

    user_path = APP_DIR / '.ssh'
    user_path.mkdir(parents=True, exist_ok=True)

    setattr(mod, 'USER_PATH', user_path.resolve())

    return mod

def main():
    parser = argparse.ArgumentParser(description="SSH 剧本执行器")

    config_path = APP_DIR / "config.py"
    config_mod = load_config(config_path)

    init_database(DATABASE_PATH, config_mod)

    script_path_list = [
        f for f in APP_DIR.glob('*.py')
        if f.name not in ['config.py', 'interface.py'] and not f.name.startswith('_')
    ]

    if not script_path_list:
        raise FileNotFoundError("未找到符合条件的剧本")

    database_path = (ROOT / 'release' / 'ssh.db').resolve()

    app = App(database_path)

    for path in script_path_list:
        with open(path, 'r', encoding='utf-8') as f:
            script = f.read()

        exec_globals = {
            '__name__': '__main__',
            '__file__': str(path),
            'app': app,
            'SshSession': SshSession,
            'Path': Path,
            'time': __import__('time'),
            're': __import__('re'),
            'os': os,
        }

        try:
            exec(script, exec_globals)
        except Exception as e:
            print("❌ 执行剧本出错:")
            raise e

if __name__ == "__main__":
    main()




