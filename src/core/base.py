"""
@文件: base.py
@作者: 雷小鸥
@日期: 2025/12/11 16:36
@许可: MIT License
@描述: 
@版本: Version 1.0
"""
from abc import ABC, abstractmethod
from typing import NoReturn


class TerminalIn(ABC):
    """
    命令输入处理抽象基类，定义输入接口规范。

    子类必须实现 input 属性的读写方法，
    其中读取操作应抛出错误（因为该属性设计为只写）。
    """

    @property
    @abstractmethod
    def input(self) -> NoReturn:
        """
        获取输入内容（设计为只写属性，直接访问会抛出错误）

        :raises AttributeError: 当尝试读取该属性时抛出
        """
        raise AttributeError('input 属性是只写的，不能读取')

    @input.setter
    @abstractmethod
    def input(self, value: str) -> NoReturn:
        """
        设置输入内容

        :param value: 要输入的字符串内容
        """
        pass


class TerminalOut(ABC):
    """
    命令输出处理抽象基类，定义输出接口规范。

    子类必须实现 out 和 err 两个只读属性，
    分别用于获取标准输出和错误输出。
    """

    @property
    @abstractmethod
    def out(self) -> str:
        """
        获取标准输出内容

        :return: 标准输出的字符串内容
        """
        return ''

    @property
    @abstractmethod
    def err(self) -> str:
        """
        获取错误输出内容

        :return: 错误输出的字符串内容
        """
        return ''
