# -*- coding: utf-8 -*-
""" Errors for unibasic"""

from textpointer import TextPointer as Pointer
from textdata import DEFAULT_FILENAME


class Error:
    """ Standart error """
    # pylint: disable=too-few-public-methods, too-many-arguments,
    # pylint: disable=too-many-positional-arguments

    def __init__(self, name: str, msg: str,
                 pos_start: Pointer, pos_end: Pointer,
                 filename: str):
        self.name = name if isinstance(name, str) else type(self).__name__
        self.msg = msg if isinstance(msg, str) else ''
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.filename = filename if isinstance(filename, str)\
            else DEFAULT_FILENAME

    def as_str(self) -> str:
        """ Error message """
        message: str = f'File {self.filename}, line {self.pos_start.ln}'
        message += f', column {self.pos_start.col}\n'
        message += f'{self.name}: {self.msg}'
        return message


class IllegalCharacterErr(Error):
    """ Illegal character error"""
    # pylint: disable=too-few-public-methods, too-many-arguments,
    # pylint: disable=too-many-positional-arguments

    def __init__(self, msg: str, pos_start: Pointer,
                 pos_end: Pointer, filename: str):
        super().__init__('Illegal Character', msg,
                         pos_start, pos_end, filename)


class SyntaxErr(Error):
    """ Syntax error """
    # pylint: disable=too-few-public-methods

    def __init__(self, msg: str, pos_start: Pointer,
                 pos_end: Pointer, filename: str):
        super().__init__('Syntax Error', msg,
                         pos_start, pos_end, filename)
