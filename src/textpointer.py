# -*- coding: utf-8 -*-
""" Pointer for the text in a format: pos, line, column """


class TextPointer:
    """ Work with position in text
        Is able to advance() and recede() the pointer """

    def __init__(self, pos_lim, pos: int = -1, column: int = 0, line: int = 0):
        self.pos_lim = max(pos_lim, 0)
        self.pos = min(max(pos, 0), pos_lim)
        self.col = max(column, 1)
        self.ln = max(line, 1)

    def copy(self):
        """ Copy to a new instance """
        return TextPointer(self.pos_lim, pos=self.pos,
                           column=self.col, line=self.ln)

    def advance(self, newline: bool = False):
        """ Move pointer forward """
        self.pos = min(self.pos_lim, self.pos + 1)
        self.col += 1
        if newline:
            self.col = 1
            self.ln += 1

    def recede(self, newline: bool = False, prev_col: int = 0):
        """ Move pointer backwards """
        self.pos = max(0, self.pos - 1)
        self.col = max(1, self.col - 1)
        if newline:
            self.col = max(prev_col, 1)
            self.ln = max(0, self.ln - 1)

    def reset(self, pos_lim: int = 0, pos: int = 0,
              column: int = 0, line: int = 0):
        """ Reset pointer """
        self.pos_lim = max(pos_lim, self.pos_lim)
        self.pos = min(max(pos, 0), pos_lim)
        self.col = max(column, 1)
        self.ln = max(line, 1)

    def as_dict(self) -> dict:
        """ Returns TextPointer dict """
        return self.__dict__.copy()
