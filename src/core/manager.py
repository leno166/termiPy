"""
@文件: manager.py
@作者: 雷小鸥
@日期: 2025/12/11 16:37
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
import threading
import time

from ..core.ipc import Ipc
from .base import TerminalIn, TerminalOut


class TerminalManager:
    def __init__(self, terminal_in: TerminalIn, terminal_out: TerminalOut, is_script: bool = True):
        self.terminal_in = terminal_in
        self.terminal_out = terminal_out

        self.ipc = Ipc()
        self.pipe_name = self.ipc.pipe_name

        self.running = False
        self.threads: list[threading.Thread] = []

        self.ipc.create_master_pipe()

        if is_script:
            self.terminal_in.input = 'is script'

    def start(self, no_in: bool = False):
        if self.running:
            return

        self.running = True

        thread_func_list = [self.in_loop, self.out_loop, self.err_loop] if not no_in else [self.out_loop, self.err_loop]

        for fn in thread_func_list:
            thread = threading.Thread(target=fn, daemon=True)
            self.threads.append(thread)

        for thread in self.threads:
            thread.start()

    def stop(self):
        self.running = False

        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1.0)

        self.ipc.close()

    def in_loop(self):
        while self.running:
            print('请输入: ')
            self.terminal_in.input = input()

    def out_loop(self):
        while self.running:
            line = self.terminal_out.out

            if line:
                self.ipc.write('[OUT] ' + line)
            time.sleep(0.01)

    def err_loop(self):
        while self.running:
            line = self.terminal_out.err
            if line:
                self.ipc.write('[ERR] ' + line)
            time.sleep(0.01)

    def user_interaction(self, ipc: Ipc, cmd: str, timeout: float = 20, is_generator: bool = False):
        """
        一个示例
        """
        self.terminal_in.input = f'echo [USER_START]; {cmd}; echo [USER_END]'

        start_time = time.time()
        in_block = False

        def _process_lines():
            nonlocal in_block

            while True:
                if time.time() - start_time > timeout:
                    self.terminal_in.input = '^C'
                    # 清空 IPC buffer
                    ipc.clear()
                    raise TimeoutError(f"Command execution timed out after {timeout} seconds")

                line = ipc.read
                if not line:
                    continue

                if '[USER_START]' in line:
                    in_block = True
                    continue

                if '[USER_END]' in line:
                    break

                if in_block:
                    yield line.replace('[OUT]', '').strip()

        try:
            return _process_lines() if is_generator else '\n'.join(_process_lines())

        except TimeoutError:
            return '[TIMEOUT ERROR]' if not is_generator else iter(())


class TerminalCommand:
    def __init__(self, manager: TerminalManager, ipc_slave: Ipc, cmd: str, timeout: float = 20):
        self.manager = manager
        self.ipc = ipc_slave
        self.cmd = cmd
        self.timeout = timeout

        self.terminal_in = manager.terminal_in

        self._exhausted = False
        self._start_time = None
        self._in_block = False

    def __enter__(self):
        self.terminal_in.input = f'echo [USER_START]; {self.cmd}; echo [USER_END]'
        self._start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._exhausted:
            self.terminal_in.input = '^C'
            self.ipc.clear()
            time.sleep(0.05)
            self.ipc.clear()

    def __iter__(self):
        return self

    def __next__(self):
        def check_timeout():
            if time.time() - self._start_time > self.timeout:
                self.terminal_in.input = '^C'
                # self._exhausted = True
                # raise StopIteration

        check_timeout()

        while True:
            line = self.ipc.read
            if line:
                if '[USER_START]' in line:
                    self._in_block = True
                    continue
                if '[USER_END]' in line:
                    self._exhausted = True
                    raise StopIteration
                if self._in_block:
                    return line.replace('[OUT]', '').strip()
                else:
                    continue
            else:
                check_timeout()
                time.sleep(0.05)
