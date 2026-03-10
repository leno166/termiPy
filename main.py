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
import re
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

def normal_play(path: Path, app: App):
    with open(path, 'r', encoding='utf-8') as f:
        script = f.read()

    exec_globals = {
        '__name__'  : '__main__',
        '__file__'  : str(path),
        'app'       : app,
        'SshSession': SshSession,
        'Path'      : Path,
        'time'      : __import__('time'),
        're'        : __import__('re'),
        'os'        : os,
    }

    try:
        exec(script, exec_globals)
    except Exception as e:
        print("❌ 执行剧本出错:")
        raise e

def easy_play(path: Path, app: App):
    try:
        with app.auto_connect_from_db() as session:
            lines = path.read_text(encoding='utf-8').splitlines()
            for raw_line in lines:
                line = raw_line.strip()
                if not line:
                    continue

                # 处理特殊指令（以 # 开头，后跟特定关键字）
                if line.startswith('#download '):
                    parts = line.split(maxsplit=2)
                    if len(parts) >= 3:
                        _, remote, local = parts
                        session.download(Path(local), remote)
                    else:
                        print(f"⚠️ 格式错误: {line}")
                elif line.startswith('#upload '):
                    parts = line.split(maxsplit=2)
                    if len(parts) >= 3:
                        _, local, remote = parts
                        session.upload(Path(local), remote)
                    else:
                        print(f"⚠️ 格式错误: {line}")
                elif line.startswith('#'):
                    # 其他注释直接忽略
                    continue
                else:
                    # 普通 Shell 命令，通过 easy_cmd 执行
                    # easy_cmd 内部会打印命令输出
                    session.easy_cmd(line)
    except Exception as e:
        print("❌ easy 模式执行失败")
        print(e)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="SSH 剧本执行器")

    parser.add_argument('--easy', '-e', action='store_true', help='启用 easy 模式，直接执行 Shell 脚本')

    args = parser.parse_args()

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
        if args.easy:
            easy_play(path, app)
        else:
            normal_play(path, app)




if __name__ == "__main__":
    main()
