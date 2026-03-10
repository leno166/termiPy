# -*- mode: python ; coding: utf-8 -*-
"""
@文件: main.spec
@作者: 雷小鸥
@日期: 2026/3/10 16:20
@描述: 
    pyinstaller 构建配置表

    - 生成构建配置表
        pyi-makespec "<__dir__>/main.py" --onefile
        pyi-makespec "<__dir__>/main.py"

    - 构建可执行文件
    pyinstaller --clean "<__dir__>/main.spec"

@许可: MIT License
@版本: Version 1.0
"""
import os
import sys
from pathlib import Path
import tqdm

tqdm_dir = os.path.dirname(tqdm.__file__)

spec_dir = Path.cwd()

# 获取当前 spec 文件所在目录（项目根目录）
PROJECT_ROOT = spec_dir

# 主入口脚本
MAIN_SCRIPT = str(PROJECT_ROOT / 'main.py')

# 需要打包的源代码目录（src 目录）
SRC_DIR = str(PROJECT_ROOT / 'src')

a = Analysis(
    # 主脚本路径 (必需)
    [MAIN_SCRIPT],

    # 搜索路径 (建议添加自定义模块路径)
    pathex=[str(PROJECT_ROOT)],

    # 第三方二进制依赖 (DLL/SO等)
    binaries=[],

    # 非代码文件资源 (当前所在位置的绝对路径, 应用内部目录的相对路径)
    datas=[(SRC_DIR, 'src'), (tqdm_dir, 'tqdm')],

    # 隐藏导入 (解决打包后缺失模块的问题)
    hiddenimports=[
        'paramiko', 'tqdm',
        'win32pipe', 'win32file', 'win32security',  # pywin32 模块
        'sqlite3',                                   # 标准库，有时需要显式导入
        'pathlib', 'threading', 'queue', 'uuid',     # 常用标准库
        're', 'time', 'io',                           # 其他隐式依赖
        # 项目内部模块（通常自动收集，但可显式列出确保安全）
        'src.core', 'src.core.logger', 'src.core.ipc',
        'src.core.base', 'src.core.manager', 'src.core.server',
        'src.sShell', 'src.sShell.ssh', 'src.sShell.ssh_connect',
        'src.sShell.ssh_normal_tools', 'src.SqliteEditor',
    ],

    # 自定义钩子脚本目录
    hookspath=[],

    # 钩子配置 (覆盖默认钩子行为)
    hooksconfig={},

    # 运行时钩子 (在程序启动时执行的脚本)
    runtime_hooks=[],

    # 排除不需要的模块 (减小体积)
    excludes=[],

    # 是否禁用归档 (False=生成单文件)
    noarchive=False,

    # 优化级别 (0=不优化, 1=移除断言, 2=移除文档字符串)
    optimize=1,
)

# 将纯Python代码打包成ZIP归档
pyz = PYZ(a.pure)

exe = EXE(
    pyz,                               # 依赖的PYZ归档
    a.scripts,                         # 主脚本列表
    a.binaries,                        # 二进制文件列表
    a.datas,                           # 资源文件列表
    [],                                # 额外二进制文件
    name='ssh_playbook',                           # 输出可执行文件名
    debug=False,                       # 是否包含调试信息
    bootloader_ignore_signals=False,   # 是否忽略操作系统信号（例如 Ctrl+C 触发的 SIGINT 信号）。
    strip=False,                       # 是否去除符号信息（不可用于 windows）
    upx=True,                          # 使用UPX压缩可执行文件
    console=True,                      # 是否显示控制台窗口 (GUI程序设为False)
    disable_windowed_traceback=False,  # 非控制台程序（console=False）崩溃时是否显示错误窗口。
    argv_emulation=False,              # macOS参数模拟
    target_arch=None,                  # 目标架构 (x86/x64)
    codesign_identity=None,            # macOS签名标识
    entitlements_file=None,            # macOS权限配置文件
)