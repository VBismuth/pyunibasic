# -*- coding: utf-8 -*-
""" Working with text (filename, pos, etc)"""
# pylint: disable=too-many-positional-arguments, too-many-arguments,

from textpointer import TextPointer


DEFAULT_FILENAME = '<stdin>'
EOF = '<EOF>'


class TextData:
    """ Processing text """

    def __init__(self, text: str, pos=0, line=1, col=1, filename=None):
        self._text: str = text if isinstance(text, str) else str(text) or ''
        self._txtsize: int = len(self._text)
        self._filename: str = str(filename)

        _pos: int = max(pos, 0) if isinstance(pos, int) else 0
        _line: int = max(line, 1) if isinstance(line, int) else 1
        _col: int = max(col, 1) if isinstance(col, int) else 1
        self._pointer = TextPointer(self._txtsize, pos=_pos,
                                    line=_line, column=_col)

    def copy(self):
        """ Returns copy of self """
        res = TextData(text=self._text, pos=0, line=1, col=1,
                       filename=self._filename)
        # pylint: disable = protected-access
        res._pointer = self._pointer.copy()
        return res

    def reset(self, text=None, pos=0, line=1, col=1, filename=None):
        """ Reset to initial values, or change certain parameters """
        self._text = text if isinstance(text, str) else self._text
        self._txtsize = len(self._text)
        self._pointer.reset(self._txtsize, pos, col, line)
        self._filename = self._filename if not filename else str(filename)

    def reset_pos(self):
        """ Move pointer to the beginning """
        self._pointer.reset()

    def get_char(self, pos=None) -> str:
        """ Return char at current position
            Returns EOF at the end of text """
        text_pos: int = self._pointer.pos
        if pos and isinstance(pos, int):
            text_pos = max(0, pos)
        if text_pos >= self._txtsize:
            return EOF
        return self._text[text_pos]

    def get_pos(self) -> int:
        """ Returns pos """
        return self._pointer.pos

    def get_line(self) -> int:
        """ Returns line """
        return self._pointer.ln

    def get_col(self) -> int:
        """ Returns col """
        return self._pointer.col

    def get_pointer(self) -> TextPointer:
        """ Returns data of pos, line, col """
        return self._pointer.copy()

    def get_filename(self) -> str:
        """ Get filename """
        if not self._filename or self._filename == 'None':
            return '<stdin>'
        return self._filename

    def get_textsize(self) -> int:
        """ Get size of text in bytes """
        return self._txtsize

    def get_text(self, start=None, step=None, end=None) -> str:
        """ Get text whole or from start to end by step """
        if start and not isinstance(start, int):
            start = None
        if step and not isinstance(step, int):
            step = None
        if end and not isinstance(end, int):
            end = None
        return self._text[start:end:step]

    def next(self) -> str:
        """ Move pointer to the next char
        in text and returns this char """
        newline = self.get_char() == '\n'
        self._pointer.advance(newline)
        return self.get_char()

    def previous(self) -> str:
        """ Move pointer to the previous char
        in text and returns this char """
        newline = self.get_char(self.get_pos() - 1) == '\n'
        prev_col = self.get_pos() -\
            max(self._text.rfind('\n', 0, self.get_pos() - 1), 0)
        self._pointer.recede(newline, prev_col)
        return self.get_char()

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other) and self._text == other.get_text()

    def __ne__(self, other: object) -> bool:
        return type(self) is not type(other) or not self == other

    def __add__(self, other: object) -> object:
        if type(self) is not type(other):
            err = TypeError("unsupported operand type(s) for +: "
                            f"'{type(self).__name__}' and "
                            f"'{type(other).__name__}'")
            raise err
        res = self.copy()
        if other.get_textsize() > 0:
            res._text += str(other.get_text())
        return res
