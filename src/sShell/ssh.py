"""
@文件: ssh.py
@作者: 雷小鸥
@日期: 2025/12/11 16:04
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
import os

# noinspection PyPackageRequirements
import paramiko
import io
import time
from pathlib import Path
from tqdm import tqdm
from pathlib import PurePosixPath

from ..core import Ipc, TerminalManager, SshServer, TerminalCommand, logger


class SshConnect:
    def __init__(self, ip: str, port: int = 22, username: str = 'root'):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.ip = ip
        self.port = port
        self.username = username

        logger.info('创建 ssh 连接: %s:%s, 用户: %s', ip, port, username)

    def password_connect(self, password: str):
        self.ssh_client.connect(
            hostname=self.ip,
            port=self.port,
            username=self.username,
            password=password,
            timeout=1
        )

        logger.info('密码连接成功: %s:%s, 用户: %s', self.ip, self.port, self.username)

    def private_key_connect(self, key_info: str, key_type: str, key_fmt: str, passphrase: str = None):
        """
        密钥连接 ssh

        :param key_info: 密钥路径, 密钥字符串内容, 解析好的密钥
        :param key_type: 密钥加密类型, RSA, ECDSA, ED25519
        :param key_fmt: 密钥格式, 文件, 字符串, 解析好的密钥
        :param passphrase: 密钥密码
        :return: 解析好的密钥
        """
        match (key_type, key_fmt):
            case ('RSA', 'FILE'):
                key = paramiko.RSAKey.from_private_key_file(key_info, password=passphrase)
            case ('ECDSA', 'FILE'):
                key = paramiko.ECDSAKey.from_private_key_file(key_info, password=passphrase)
            case ('ED25519', 'FILE'):
                key = paramiko.Ed25519Key.from_private_key_file(key_info, password=passphrase)
            case ('RSA', 'STR'):
                key = paramiko.RSAKey.from_private_key(io.StringIO(key_info), password=passphrase)
            case ('ECDSA', 'STR'):
                key = paramiko.ECDSAKey.from_private_key(io.StringIO(key_info), password=passphrase)
            case ('ED25519', 'STR'):
                key = paramiko.Ed25519Key.from_private_key(io.StringIO(key_info), password=passphrase)
            case ('KEY', 'KEY'):
                key = key_info
            case _:
                raise ValueError(f'Invalid key format: {key_type} and key type: {key_fmt}')

        # noinspection PyUnboundLocalVariable
        self.ssh_client.connect(
            hostname=self.ip,
            port=self.port,
            username=self.username,
            pkey=key,
            timeout=1
        )

        logger.info('密钥连接成功: %s:%s, 用户: %s, 密钥类型: %s, 密钥格式: %s', self.ip, self.port, self.username,
                    key_type, key_fmt)

        return key

    def reconnect(self, method, authentication):
        match method:
            case 'password':
                self.password_connect(authentication)

            case 'key':
                self.private_key_connect(authentication, 'KEY', 'KEY')

            case _:
                raise ValueError(f'无效的认证方式: {method}')


class SshExecutor:
    def __init__(self, ssh_client: paramiko.SSHClient):
        self.ssh_server = SshServer(ssh_client, 'xterm', 1000, 1000)
        self.terminal_manager = TerminalManager(self.ssh_server, self.ssh_server, False)

    def __enter__(self):
        self.terminal_manager.start(True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminal_manager.stop()

    @property
    def input(self):
        raise AttributeError("input is write-only")

    @input.setter
    def input(self, value: str):
        self.terminal_manager.terminal_in.input = value

    def user_interaction(self, cmd: str, timeout: float = 20, is_generator: bool = False, ipc: Ipc = None):
        if not ipc:
            ipc = self.terminal_manager.ipc

        self.terminal_manager.user_interaction(ipc, cmd, timeout, is_generator)


class SshSession:
    def __init__(self, ssh_executor: SshExecutor):
        self.terminal_in = ssh_executor.terminal_manager.terminal_in

        self._ssh_executor = ssh_executor
        self._manager = ssh_executor.terminal_manager
        self._ipc_slave = None

    def __enter__(self):
        if not self._manager.running:
            self._manager.start(no_in=True)

        if not self._ipc_slave:
            self._ipc_slave = Ipc(self._manager.ipc.pipe_name)
            self._ipc_slave.create_slave_pipe()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._manager.terminal_in.input = '^C'
        if self._ipc_slave:
            self._ipc_slave.clear()
        time.sleep(0.1)

    def cmd(self, cmd: str, timeout: float = 20):
        return TerminalCommand(self._manager, self._ipc_slave, cmd, timeout)

    def pwd(self):
        path = None
        with self.cmd('pwd') as iterator:
            for line in iterator:
                if line:
                    path = line.strip()

        return path

    def _resolve_path(self, path: str):
        if path.startswith('/'):
            return path

        full_path = str((PurePosixPath(self.pwd()) / path).as_posix())
        logger.info(f'完整路径：{full_path}')
        return full_path

    def download(self, local: Path, remote: str, timeout: float = 600):
        local.parent.mkdir(parents=True, exist_ok=True)

        # 获取 SFTP 客户端
        sftp = self._ssh_executor.ssh_server.client.open_sftp()

        remote_path = self._resolve_path(remote)

        try:
            # 获取远程文件大小（用于进度条）
            remote_size = sftp.stat(remote_path).st_size
            with tqdm(total=remote_size, unit='B', unit_scale=True,
                      desc=f"下载 {remote_path}") as pbar:

                # 进度回调：更新进度条
                def callback(transferred, total):
                    pbar.update(transferred - pbar.n)

                sftp.get(remote_path, str(local), callback=callback)
        except Exception as e:
            logger.error('下载失败：')
            print('下载失败：')
            logger.error(e)
            print(e)
        finally:
            sftp.close()

        logger.info(f"✅ 下载完成: {remote_path} -> {local}")

    def upload(self, local: Path, remote: str, timeout: float = 600):
        # 获取本地文件大小
        local_size = local.stat().st_size

        remote_path = self._resolve_path(remote)

        # 获取 SFTP 客户端
        sftp = self._ssh_executor.ssh_server.client.open_sftp()

        try:
            with tqdm(total=local_size, unit='B', unit_scale=True,
                      desc=f"上传 {local.name}") as pbar:
                def callback(transferred, total):
                    pbar.update(transferred - pbar.n)

                sftp.put(str(local), remote_path, callback=callback)
        except Exception as e:
            logger.error(f"上传失败: {e}")
            raise
        finally:
            sftp.close()

        logger.info(f"✅ 上传完成: {local} -> {remote_path}")

    def close(self):
        if self._ipc_slave:
            self._ipc_slave.close()
            self._ipc_slave = None
        self._manager.stop()
