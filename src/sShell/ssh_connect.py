"""
@文件: ipd.py
@作者: 雷小鸥
@日期: 2025/12/15 09:50
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from typing import TypedDict, Optional
from paramiko.ssh_exception import AuthenticationException
from pathlib import Path
import sqlite3

from ..core import logger
from .ssh import SshConnect, SshExecutor, SshSession as _SshSession
from .ssh_normal_tools import SshTool as SshSession


class AuthInfo(TypedDict):
    method: str
    ip: str
    port: int
    username: str
    authentication: str


class HostInfo(TypedDict):
    id: int
    name: str
    ip: str
    port: int
    remark: str


# noinspection DuplicatedCode
class KeyLoginInfo(TypedDict):
    id: int
    username: str
    date: str
    private_key: str
    passphrase: str
    key_fmt: str
    key_type: str


class PasswordLoginInfo(TypedDict):
    id: int
    username: str
    password: str


class DbIpdBridge:
    def __init__(self, db_path: Path = None):
        self.db_path = db_path

        if not self.db_path.exists():
            raise FileNotFoundError(f"数据库文件不存在: {self.db_path}")

    def fetch_hosts(self, **filters) -> list[HostInfo]:
        query = "SELECT id, name, ip, port, remark FROM host_info"
        conditions = []
        params = []
        for key, value in filters.items():
            if value is None:
                continue
            # 只允许新表字段作为筛选条件
            if key in ('name', 'ip', 'port', 'remark'):
                conditions.append(f"{key} = ?")
                params.append(value)
            else:
                logger.warning(f"忽略不支持的筛选字段: {key}")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        host_infos = []
        for row in rows:
            host_infos.append({
                'id'    : row[0],
                'name'  : row[1],
                'ip'    : row[2],
                'port'  : row[3],
                'remark': row[4],
            })
        return host_infos

    def fetch_keys(self):
        query = "SELECT id, username, private_key, passphrase, key_type, remark FROM key_login"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        key_infos = []
        for row in rows:
            key_infos.append({
                'id'         : row[0],
                'username'   : row[1],
                'private_key': row[2],
                'passphrase' : row[3] if row[3] else None,
                'key_fmt'    : 'STR',
                'key_type'   : row[4],
                'remark'     : row[5],  # 如果需要，可在 KeyLoginInfo 中添加 remark 字段
            })
        return key_infos

    def fetch_passwords(self):
        query = "SELECT id, username, password, remark FROM password_login"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        password_infos = []
        for row in rows:
            password_infos.append({
                'id'      : row[0],
                'username': row[1],
                'password': row[2],
                'remark'  : row[3],  # 可以添加，如果不需要则省略
            })
        return password_infos


class AutoConnect:
    def __init__(self, db_path: Path = None):
        self.db_path = db_path

    def auto_connect(
            self,
            host_infos: list[HostInfo] = None,
            key_login_infos: list[KeyLoginInfo] = None, password_login_infos: list[PasswordLoginInfo] = None,
            auth_info: Optional[AuthInfo] = None
    ):
        logger.info("正在自动连接 ipd 中...")

        if auth_info:
            ssh = SshConnect(auth_info['ip'], auth_info['port'], auth_info['username'])

            try:
                ssh.reconnect(auth_info['method'], auth_info['authentication'])
            except TimeoutError:
                logger.warning(
                    '重连: %s@%s:%s, method: %s, 连接超时. ',
                    auth_info['username'], auth_info['ip'], auth_info['port'], auth_info['method']
                )
                raise ConnectionError('未连接成功')
            except AuthenticationException:
                logger.warning(
                    '重连: %s@%s:%s, method: %s, 连接被拒绝. ',
                    auth_info['username'], auth_info['ip'], auth_info['port'], auth_info['method']
                )
                raise ConnectionError('未连接成功')

            logger.info(
                '重连成功: %s:%s, 用户: %s, 认证方式: %s',
                auth_info['ip'], auth_info['port'], auth_info['username'], auth_info['method']
            )

            ssh_executor = SshExecutor(ssh.ssh_client)
            session = SshSession(ssh_executor)
            return session, ssh_executor, auth_info

        if not host_infos:
            raise ConnectionError('未连接成功')

        for host_info in host_infos:
            logger.info(
                '尝试连接: 名称=%s, IP=%s, 端口=%s, 备注=%s',
                host_info['name'], host_info['ip'], host_info['port'], host_info['remark']
            )

            if key_login_infos:
                logger.info('尝试密钥登录...')
                for key_login_info in key_login_infos:
                    ssh = SshConnect(
                        host_info['ip'], host_info['port'], key_login_info['username']
                    )
                    logger.info(
                        '尝试登录: %s@%s:%s',
                        key_login_info['username'], host_info['ip'], host_info['port']
                    )

                    try:
                        key = ssh.private_key_connect(
                            key_login_info['private_key'], key_login_info['key_type'],
                            key_login_info['key_fmt'], key_login_info['passphrase']
                        )

                        auth_info: AuthInfo = {
                            'method'        : 'key',
                            'ip'            : host_info['ip'],
                            'port'          : host_info['port'],
                            'username'      : key_login_info['username'],
                            'authentication': key,
                        }

                        ssh_executor = SshExecutor(ssh.ssh_client)
                        session = SshSession(ssh_executor)
                        return session, ssh_executor, auth_info
                    except TimeoutError:
                        logger.warning(
                            '密钥登录超时: %s | %s',
                            key_login_info['key_type'], key_login_info['key_fmt']
                        )
                    except AuthenticationException:
                        logger.warning(
                            '密钥被拒绝: %s | %s',
                            key_login_info['key_type'], key_login_info['key_fmt']
                        )

            if password_login_infos:
                logger.info('尝试密码登录...')
                for password_login_info in password_login_infos:
                    logger.info('密码登录, 用户名: %s', password_login_info['username'])
                    ssh = SshConnect(
                        host_info['ip'], host_info['port'], password_login_info['username']
                    )
                    try:
                        ssh.password_connect(password_login_info['password'])
                        auth_info: AuthInfo = {
                            'method'        : 'password',
                            'ip'            : host_info['ip'],
                            'port'          : host_info['port'],
                            'username'      : password_login_info['username'],
                            'authentication': (password_login_info['password'])
                        }

                        ssh_executor = SshExecutor(ssh.ssh_client)
                        session = SshSession(ssh_executor)
                        return session, ssh_executor, auth_info
                    except TimeoutError:
                        logger.warning('密码登录超时!')
                    except AuthenticationException:
                        logger.warning('密码登录被拒绝')

        raise ConnectionError('未连接成功')

    def auto_connect_from_db(self, db_path: str | Path = None, **kwargs):
        """
        从数据库自动连接。
        :param db_path: 数据库路径，若为 None 则使用初始化时传入的 db_path
        :param kwargs: 主机筛选条件，支持 name, ip, port, remark
        """
        if not db_path:
            db_path = self.db_path

        db_path = Path(db_path)

        db_ipd_bridge = DbIpdBridge(db_path)

        return self.auto_connect(db_ipd_bridge.fetch_hosts(**kwargs), db_ipd_bridge.fetch_keys(),
                                 db_ipd_bridge.fetch_passwords())
