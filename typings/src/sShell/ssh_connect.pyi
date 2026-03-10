from ..core import logger as logger
from .ssh import SshConnect as SshConnect, SshExecutor as SshExecutor
from _typeshed import Incomplete
from pathlib import Path
from typing import TypedDict

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
    db_path: Incomplete
    def __init__(self, db_path: Path = None) -> None: ...
    def fetch_hosts(self, **filters) -> list[HostInfo]: ...
    def fetch_keys(self): ...
    def fetch_passwords(self): ...

class AutoConnect:
    db_path: Incomplete
    def __init__(self, db_path: Path = None) -> None: ...
    def auto_connect(self, host_infos: list[HostInfo] = None, key_login_infos: list[KeyLoginInfo] = None, password_login_infos: list[PasswordLoginInfo] = None, auth_info: AuthInfo | None = None): ...
    def auto_connect_from_db(self, db_path: str | Path = None, **kwargs): ...
