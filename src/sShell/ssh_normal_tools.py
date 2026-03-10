"""
@文件: ssh_normal_tools.py
@作者: 雷小鸥
@日期: 2026/3/9 16:01
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from .ssh import SshSession, SshExecutor
import re


class SshTool(SshSession):
    def __init__(self, ssh_executor: SshExecutor):
        super().__init__(ssh_executor)



    def ping(self, ip: str, count: int = 5, timeout: int = 3, debug: bool = False) -> tuple | bool:
        with self:
            lines = []
            with self.cmd(f'ping -c {count} {ip}', timeout=timeout) as iterator:
                for line in iterator:
                    lines.append(line)

            success = False
            loss_percent = 100
            pattern = re.compile(r'(\d+)% packet loss')

            for line in lines:
                if 'packet loss' not in line:
                    continue

                match = pattern.search(line)
                if match:
                    loss_percent = int(match.group(1))
                    success = loss_percent < 100
                    break

            return (success, loss_percent, lines) if debug else success

    def easy_cmd(self, cmds):
        with self.cmd(cmds) as iterator:
            for line in iterator:
                print(line)




