"""
@文件: __init__.py
@作者: 雷小鸥
@日期: 2025/12/11 16:34
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from .helper import ROOT, APP_DIR
from .logger import logger
from .ipc import Ipc
from .base import TerminalIn, TerminalOut
from .manager import TerminalManager, TerminalCommand
from .server import CmdServer, SshServer

import paramiko as _paramiko


def main(ssh_client: _paramiko.SSHClient):
    import time
    from src.core.ipc import Ipc

    cmd_server = CmdServer()
    ssh_server = SshServer(ssh_client, 'xterm', 1000, 1000)

    terminal_manager = TerminalManager(ssh_server, ssh_server)
    terminal_manager.start()

    _ipc = Ipc(terminal_manager.pipe_name)
    _ipc.create_slave_pipe()

    while True:
        out_line = _ipc.read
        if out_line:
            print(out_line.strip())
        time.sleep(0.01)


__all__ = [
    'logger', 'Ipc', 'main', 'APP_DIR', 'ROOT',
    'TerminalIn', 'TerminalOut', 'TerminalManager', 'CmdServer', 'SshServer', 'TerminalCommand',
]
