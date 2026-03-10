"""
@文件: ipc.py
@作者: 雷小鸥
@日期: 2025/12/11 16:24
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
import win32pipe
import win32security
import win32file
import uuid
import threading

from .logger import logger


class Ipc:
    ENCODING = 'utf-8'
    BUFFER_SIZE = 65536
    TIMEOUT = 0

    def __init__(self, pipe_name=None):
        self.pipe_name: str = pipe_name or uuid.uuid4().hex
        if not self.pipe_name.startswith(r'\\.'):
            self.pipe_name = r'\\.\pipe\ipc_pipe_' + self.pipe_name

        self.sa = win32security.SECURITY_ATTRIBUTES()  # 创建默认安全属性
        self.sa.bInheritHandle = True  # 可选：是否可继承

        self.pipe = None
        self.pipe_mode = ''
        self.connected = False

        self.lock = threading.Lock()
        self.r_lock = threading.RLock()

    def create_master_pipe(self):
        self.pipe = win32pipe.CreateNamedPipe(
            self.pipe_name,
            win32pipe.PIPE_ACCESS_DUPLEX,  # 双向通信（可读可写）
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            win32pipe.PIPE_UNLIMITED_INSTANCES,
            self.BUFFER_SIZE,  # 输出缓冲区大小
            self.BUFFER_SIZE,  # 输入缓冲区大小
            self.TIMEOUT,  # 默认超时时间
            self.sa  # 默认安全属性
        )
        self.pipe_mode = 'master'

    def create_slave_pipe(self):
        self.pipe = (win32file.CreateFile(
            self.pipe_name,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,  # 读 / 写 权限
            0,
            None,
            win32file.OPEN_EXISTING,  # 关键！ 表示只打开已存在的文件/管道，不会创建新管道
            0,
            None
        ))
        self.pipe_mode = 'slave'

    def write(self, msg: str):
        if not self.pipe:
            raise AttributeError("Pipe not initialized. Call create_master_pipe() or create_slave_pipe() first.")

        if self.pipe_mode == 'master' and self.connected == False:
            win32pipe.ConnectNamedPipe(self.pipe, None)
            self.connected = True

        with self.lock:
            win32file.WriteFile(self.pipe, (msg.strip() + '\n').encode(self.ENCODING))

    @property
    def read(self) -> str:
        if not self.pipe:
            raise AttributeError("Pipe not initialized. Call create_master_pipe() or create_slave_pipe() first.")

        if self.pipe_mode == 'master' and self.connected == False:
            win32pipe.ConnectNamedPipe(self.pipe, None)
            self.connected = True

        # 这里非常奇怪. 我只能理解到: 会返回换行符截至的字符(\n \r). 一定是写入消息的截至.
        # 比如写入 xxx\n, xx\nxx\r. 那么一定返回  xxx\n 或者 xxx\nxx\nxx\r, 一定不会返回 xxx\nxx\n
        # 每次写入之后默认加了\n
        # PeekNamedPipe 只返回换行符之前的值, \r \n 都会.
        peek_data: bytes
        peek_data, available, hr = win32pipe.PeekNamedPipe(self.pipe, self.BUFFER_SIZE)
        if peek_data:
            logger.info('hr: %s, available: %s, peek_data: %s', hr, available, peek_data)

        if not peek_data:  # 没有数据
            return ''

        # 找到行结束符位置
        # 只走一次，用生成器找最小非 -1 的 index
        line_end = min(
            (i for i in (peek_data.find(b'\n'), peek_data.find(b'\r')) if i != -1),
            default=-1
        )

        if line_end < 0:
            return ''  # 没有完整的一行

        buffer_size = line_end + 1

        data: bytes
        with self.r_lock:
            result, data = win32file.ReadFile(self.pipe, buffer_size)

        data = data.strip()
        if data:
            return data.decode(self.ENCODING)
        return ''

    def clear(self):
        data: str = 'none'
        while data:
            data = self.read

    def close(self):
        if self.pipe:
            win32file.CloseHandle(self.pipe)
            self.pipe = None
