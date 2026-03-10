"""
@文件: server.py
@作者: 雷小鸥
@日期: 2025/12/11 16:39
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from typing import NoReturn
import paramiko
import subprocess
import time

from .logger import logger
from .base import TerminalIn, TerminalOut


class CmdServer(TerminalIn, TerminalOut):
    def __init__(self):
        self.process = subprocess.Popen(
            ["cmd.exe"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )

    @property
    def input(self) -> NoReturn:
        return super().input

    @input.setter
    def input(self, value):
        if not value.endswith('\n'):
            value += '\n'
        self.process.stdin.write(value.encode('gbk'))
        self.process.stdin.flush()

    @property
    def out(self) -> str:
        return self.process.stdout.readline().decode('gbk')

    @property
    def err(self) -> str:
        return self.process.stderr.readline().decode('gbk')


class SshServer(TerminalIn, TerminalOut):
    def __init__(self, ssh_client: paramiko.SSHClient, term: str, width: int, height: int):
        self.client = ssh_client

        self.channel = self.client.invoke_shell(term=term, width=width, height=height)
        # self.channel = self.client.invoke_shell(term='xterm', width=1000, height=1000)
        # self.channel = self.client.invoke_shell(term='xterm-256color', width=1000, height=1000)
        self.channel.setblocking(0)

        self.out_buffer = b''
        self.err_buffer = b''

    @property
    def input(self) -> NoReturn:
        return super().input

    @input.setter
    def input(self, value):
        if not self.channel:
            raise ConnectionError("SSH连接已关闭")

        match value:
            case '^C':
                self.channel.send('\x03'.encode('utf-8'))
            case '^D':
                self.channel.send('\x04'.encode('utf-8'))
            case '^Z':
                self.channel.send('\x1a'.encode('utf-8'))
            case 'is script':
                for cmd in [
                    b"export TERM=dumb",
                    b"unset PROMPT_COMMAND",  # 禁用窗口标题更新
                    b"PS1=''",  # 设置最简提示符
                    b"stty -echo"  # 可选：关闭回显（避免命令重复出现）
                ]:
                    self.channel.send(cmd + b'\n')
            case _:
                if not value.endswith('\n'):
                    value += '\n'

                logger.info(value)
                self.channel.send(value.encode('utf-8'))

        time.sleep(0.05)

    @property
    def out(self) -> str:
        if self.out_buffer and b'\n' in self.out_buffer:
            self.out_buffer = self.out_buffer.split(b'\n')
            line = self.out_buffer[0].decode('utf-8', errors='ignore')
            self.out_buffer = self.out_buffer[1:]
            self.out_buffer = b'\n'.join(self.out_buffer)
            return line

        if self.channel.recv_ready():
            self.out_buffer += self.channel.recv(4096)

        return ''

    @property
    def err(self) -> str:
        if self.err_buffer and b'\n' in self.err_buffer:
            self.err_buffer = self.err_buffer.split(b'\n')
            line = self.err_buffer[0].decode('utf-8', errors='ignore')
            self.err_buffer = self.err_buffer[1:]
            self.err_buffer = b'\n'.join(self.err_buffer)
            return line

        if self.channel.recv_stderr_ready():
            self.err_buffer += self.channel.recv_stderr(4096)

        return ''
