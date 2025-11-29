# -*- coding: utf-8 -*-
""" UniBasic Markup Language """

import re
from typing import Any, IO


def _get_from_subscr(source_sub: list | tuple | str, idx: int) -> Any:
    if not isinstance(source_sub, list | tuple | str) or\
            idx >= len(source_sub):
        return None
    return source_sub[idx]


class ParenthesisMismatch(Exception):
    """ Error for failing the hash check """


class InvalidNumberError(Exception):
    """ Error for invalid words in ubml """


class InvalidSymbolError(Exception):
    """ Error for invalid symbols in ubml,
        like using : or = in lists """


class UBMLParser:
    """ Main class for parsing ubml files
    """

    def __init__(self, text: str, filename: str):
        self._pos: int = 0
        self._ln: int = 1
        self._col: int = 1
        self._filename: str = filename or '<stdin>'
        self._text: str = text or '{}'
        self._textsize: int = len(text)

    @staticmethod
    def _detect_object_type(text: str) -> type[dict, list]:
        if text.startswith('{'):  # }
            return dict
        if text.startswith('['):  # ]
            return list

        # Looking for less obvious dict pattern
        skip_ch: bool = False
        skip_str: bool = False
        for ch in text[:text.find(',' if ',' in text else '\n')]:
            if ch == '\\':
                skip_ch = True
            elif skip_ch:
                skip_ch = False
            elif ch in '"\'' and not skip_str:
                skip_str = True
            elif ch in '"\'' and skip_str:
                skip_str = False
            elif ch in ':=' and not skip_str and not skip_ch:
                break  # found
        else:
            return list  # pattern not found
        return dict  # if cycle breaks (pattern found)

    @staticmethod
    def _append_to_obj(obj: dict | list, item: Any):
        if not isinstance(obj, dict | list):
            return
        if isinstance(obj, dict) and isinstance(item, dict):
            obj.update(item)
        elif isinstance(obj, list):
            obj.append(item)
        else:
            raise TypeError(f'cannot add {type(item)} to {type(obj)}')

    def _check_text(self) -> bool:
        if not self._text:
            return False
        if self._text.count('[') != self._text.count(']'):
            raise ParenthesisMismatch(f'brackets mismatch in {self._filename}')
        if self._text.count('{') != self._text.count('}'):
            raise ParenthesisMismatch(f'braces mismatch in {self._filename}')
        return True

    def _skip_first(self):
        if self._text[self._pos] in '{[':  # ]}
            self._pos += 1
            self._col += 1

    def _process_text(self) -> dict | list | None:
        if not self._check_text() or\
                self._detect_object_type(self._text) is None:
            return None
        obj = self._detect_object_type(self._text[self._pos:])
        self._skip_first()
        parsed: dict | list = obj()
        add_key: Any = ''

        while self._pos < self._textsize:
            ch: str = self._text[self._pos]
            if ch == '\n':
                self._ln += 1
                self._col = 1
                self._pos += 1
            elif ch in '\r\t, ' or\
                    (ch in ':=' and obj is dict):
                self._col += 1
                self._pos += 1
            elif ch in ':=' and obj is not dict:
                raise InvalidSymbolError(f"unexpected '{ch}' for object of "
                                         f"type {obj.__name__} in "
                                         f"{self._filename}"
                                         f":{self._ln}:{self._col} "
                                         f"(pos: {self._pos})")
            elif ch == '#':
                self._cut_text_part(end='\n')
            elif ch.isalpha() or ch in '\'"\\':
                add_key = self._process_word(parsed, add_key)
            elif ch in '+-0123456789':
                add_key = self._process_num(parsed, add_key)
            elif ch in '[{':  # }]
                add_key = self._process_new_obj(parsed, add_key)
            elif (ch == ']' and obj is list) or\
                    (ch == '}' and obj is dict):
                self._col += 1
                self._pos += 1
                break
            else:
                raise InvalidSymbolError(f"invalid symbol in {self._filename}"
                                         f":{self._ln}:{self._col} - '{ch}' "
                                         f"(pos: {self._pos})")
        return parsed

    def _process_new_obj(self, parsed: dict | list, add_key: Any) -> Any:
        is_dict: bool = isinstance(parsed, dict)
        new_obj: dict | list = self._process_text()
        if is_dict and add_key:
            self._append_to_obj(parsed, {add_key: new_obj})
            add_key = ''
        elif is_dict:
            raise TypeError(f'unhashable type: \'{type(new_obj)}\'')
        else:
            self._append_to_obj(parsed, new_obj)
        return add_key

    def _collect_string(self) -> str:
        res: str = ''
        first_ch: str = self._text[self._pos]
        first_posdata: tuple[int] = (self._pos, self._ln, self._col)
        while self._pos < self._textsize:
            ch: str = self._text[self._pos]
            next_ch: str | None = _get_from_subscr(self._text, self._pos + 1)
            if ch == '\\' and next_ch:
                res += f'\\{next_ch}' if next_ch not in '\'",:=}]' else next_ch
                self._pos += 1
                self._col += 1
            elif self._pos > first_posdata[0] and\
                    first_ch in '\'"' and ch == first_ch:
                res += ch
                self._pos += 1
                self._col += 1
                break
            elif ch in '}],:=' and first_ch not in '\'"':
                self._pos += 1
                self._col += 1
                break
            else:
                res += ch
            self._pos += 1
            self._col += 1
        if first_ch in '\'"' and first_ch != _get_from_subscr(res, -1):
            errpos, errln, errcol = first_posdata
            raise ParenthesisMismatch(f'unterminated string literal {first_ch}'
                                      f' in {self._filename}:{errln}'
                                      f':{errcol} (pos: {errpos})')
        return res

    def _process_word(self, parsed: dict | list, add_key: Any) -> Any:
        word: str = self._collect_string()
        res = self._process_str(word)
        match word:
            case None | 'nil' | 'null' | '':
                res = None
            case 'true':
                res = True
            case 'false':
                res = False
        if isinstance(parsed, dict) and add_key:
            self._append_to_obj(parsed, {add_key: res})
            add_key = ''
        elif isinstance(parsed, dict):
            add_key = res
        else:
            self._append_to_obj(parsed, res)
        return add_key

    def _process_num(self, parsed: dict | list, add_key: str) -> str:
        obj: type = type(parsed)
        num = self._cut_text_part()
        try:
            converted_num: float | int = UBMLParser._convert_num(num)
        except ValueError:
            raise InvalidNumberError(f'got invalid number "{num}"'
                                     f' in file {self._filename}'
                                     f':{self._ln}:{self._col}') from None
        if not add_key and obj is dict:
            add_key = converted_num
        elif obj is dict:
            UBMLParser._append_to_obj(parsed, {add_key: converted_num})
            add_key = ''
        else:
            UBMLParser._append_to_obj(parsed, converted_num)
        return add_key

    def _cut_text_part(self, end='\n\r\t ,]}:=') -> str:
        word: str = ''
        while self._pos < self._textsize:
            ch: str = self._text[self._pos]
            if ch == '\n':
                self._ln += 1
                self._col = 1
                self._pos += 1
            elif ch in '\r\t ':
                self._col += 1
                self._pos += 1
            if ch in end:
                break
            word += ch
            self._pos += 1
            self._col += 1
        return word

    @staticmethod
    def _convert_num(text: str) -> int | float | str:
        if not text:
            return ''
        match_float = re.match(r'[+-]?\d+\.\d+', text)
        match_int = re.match(r'[+-]?\d+', text)
        if match_float and match_float.group() == text:
            return float(text)
        if match_int and match_int.group() == text:
            return int(text)
        raise ValueError

    @staticmethod
    def _process_str(text: str) -> str:
        res: str = text.strip()
        if res and res[0] in '"\'' and res[0] == res[-1]:
            res = res[1:-1]  # manual strip only if double ' or "
        to_replace: dict = {'\\n': '\n', '\\t': '\t',
                            '\\"': '"', '\\\\': '\\'}
        for old, new in to_replace.items():
            res = res.replace(old, new)
        return res

    def result(self) -> Any:
        """ Result of parsing """
        return self._process_text()

    def get_pos_data(self) -> tuple[int]:
        """ Returns tuple of pos data"""
        return self._pos, self._ln, self._col


########################################################
# Main functions
########################################################
def loads(text: str) -> Any:
    """ Load object from string of UBML format """
    return UBMLParser(text, '').result()


def load(fd: IO) -> Any:
    """ Load object from UBML file """
    text: str = fd.read()
    return UBMLParser(text, fd.name).result()


def dumps(obj: Any, ident: int = 0, mark_str: str = '',
          first_parens: bool = False, as_json: bool = False) -> str:
    """ Serialize object into a string in UBML format """
    if not isinstance(obj, dict | list):
        return str(obj) if not as_json else\
            f'["{str(obj).replace('"', '\\"')}"]'
    if as_json:
        mark_str = '"'
        first_parens = True
    nil: str = 'null' if as_json else 'nil'
    res: str = ''
    return res
