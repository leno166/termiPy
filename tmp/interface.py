from pathlib import Path
import sys
from collections.abc import Awaitable, Callable, Iterable, Sequence, Set as AbstractSet, Sized
from dataclasses import Field
from os import PathLike
from typing import (
    Any,
    AnyStr,
    ClassVar,
    Final,
    Generic,
    Literal,
    Protocol,
    SupportsFloat,
    SupportsIndex,
    SupportsInt,
    TypeVar,
    final,
    overload,
)

from typing_extensions import Buffer, LiteralString, TypeAlias
import paramiko
import paramiko
import types
from _typeshed import Incomplete
from pathlib import Path

class Ipc:
    ENCODING: str
    BUFFER_SIZE: int
    TIMEOUT: int
    pipe_name: str
    sa: Incomplete
    pipe: Incomplete
    pipe_mode: str
    connected: bool
    lock: Incomplete
    r_lock: Incomplete
    def __init__(self, pipe_name=None) -> None: ...
    def create_master_pipe(self) -> None: ...
    def create_slave_pipe(self) -> None: ...
    def write(self, msg: str): ...
    @property
    def read(self) -> str: ...
    def clear(self) -> None: ...
    def close(self) -> None: ...


class SshExecutor:
    ssh_server: Incomplete
    terminal_manager: Incomplete
    def __init__(self, ssh_client: paramiko.SSHClient) -> None: ...
    def __enter__(self): ...
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: types.TracebackType | None) -> None: ...
    @property
    def input(self) -> None: ...
    @input.setter
    def input(self, value: str): ...
    def user_interaction(self, cmd: str, timeout: float = 20, is_generator: bool = False, ipc: Ipc = None): ...

class SshSession:
    terminal_in: Incomplete
    def __init__(self, ssh_executor: SshExecutor) -> None: ...
    def __enter__(self): ...
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: types.TracebackType | None) -> None: ...
    def cmd(self, cmd: str, timeout: float = 20): ...
    def download(self, local: Path, remote: str, timeout: float = 600): ...
    def upload(self, local: Path, remote: str, timeout: float = 600): ...
    def close(self) -> None: ...

    def ping(self, ip: str, count: int = 5, timeout: int = 3, debug: bool = False) -> tuple | bool: ...

    def easy_cmd(self, cmds) -> None: ...

class App:
    def auto_connect_from_db(self, db_path: str | Path = None, **kwargs): ...


app = App()

__all__ = ['SshSession', 'app']
