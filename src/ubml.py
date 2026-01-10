# -*- coding: utf-8 -*-
""" UniBasic Markup Language """

import re
from typing import Any, IO


def _get_from_subscr(source_sub: list | tuple | str, idx: int) -> Any:
    if not isinstance(source_sub, list | tuple | str) or\
            idx >= len(source_sub):
        return None
    return source_sub[idx]


class NotSupported(Exception):
    """ Error for unsupported types """


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
        self._text: str = text.strip() or '{}'
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
            raise TypeError(f'cannot add {type(item).__name__} to '
                            f'{type(obj).__name__}')

    def _check_text(self) -> bool:
        if not self._text:
            return False
        return True

    def _skip_first_br(self):
        if self._text[self._pos] in '{[':  # ]}
            self._pos += 1
            self._col += 1

    def _process_text(self) -> dict | list | None:
        if not self._check_text() or\
                self._detect_object_type(self._text[self._pos:]) is None:
            return None
        obj = self._detect_object_type(self._text[self._pos:])
        self._skip_first_br()
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
            raise TypeError(f'unhashable type: \'{type(new_obj).__name__}\'')
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
                break
            else:
                res += ch
            self._pos += 1
            self._col += 1
        if first_ch in '\'"' and first_ch != _get_from_subscr(res, -1):
            errpos, errln, errcol = first_posdata
            raise SyntaxError(f'unterminated string literal {first_ch}'
                              f' in {self._filename}:{errln}'
                              f':{errcol} (pos: {errpos})')
        return res

    def _process_word(self, parsed: dict | list, add_key: Any) -> Any:
        word: str = self._collect_string()
        res = self._process_str(word)
        if res is None:
            return None
        match word.strip().strip('\n'):
            case 'nil' | 'null' | '':
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


class UBMLDumper:
    """ Used to serialize objects """

    # pylint: disable=too-many-arguments, disable=too-many-positional-arguments
    def __init__(self, ident: int = 0, mark_str: str = '',
                 ident_str: str = ' ', setter: str = '=',
                 as_json: bool = False):
        self.ident = ident
        self.setter = ':' if as_json else setter if setter in ':=' else '='
        self.ident_str = ident_str or ' '
        self.mark_str = '"' if as_json else mark_str\
            if mark_str in '"\'' else ''
        self.as_json = as_json

    def _process(self, obj: Any, level: int = 1) -> str:
        if isinstance(obj, tuple | set):
            raise NotSupported(f"type '{type(obj).__name__}' is not supported")
        ident: str = self.ident_str * (self.ident * max(level, 1))
        space: str = ' ' if ident or self.as_json else ''
        nil: str = 'null' if self.as_json else 'nil'
        newline: str = '\n' if ident else ''
        res: str = ''
        if isinstance(obj, dict) and obj:
            res = '{' + newline if self.as_json or level > 1 else ''
            items = tuple(obj.items())
            k, v = items[0]
            res += ident
            res += self._process(k)
            res += f'{self.setter}{space}'
            res += self._process(v, level + 1)
            for key, val in items[1:]:
                res += ',' + newline + ident if ident else ',' + space
                res += self._process(key)
                res += f'{self.setter}{space}'
                res += self._process(val, level + 1)
            res += newline + ident[:self.ident * max(level - 1, 0)] + '}'\
                if self.as_json or level > 1 else ''
        elif isinstance(obj, list) and obj:
            res = '[' + newline if self.as_json or level > 1 else ''
            res += ident
            res += self._process(obj[0], level + 1)
            for val in obj[1:]:
                res += ',' + newline + ident if ident else ',' + space
                res += self._process(val, level + 1)
            res += newline + ident[:self.ident * max(level - 1, 0)] + ']'\
                if self.as_json or level > 1 else ''
        elif isinstance(obj, int | float) and not isinstance(obj, bool):
            res = str(obj)
        else:
            res = self._to_processed_str(obj, self.mark_str, nil)
        return res

    @staticmethod
    def _to_processed_str(obj: Any, mark_str: str = '',
                          nil: str = 'null') -> str:
        if obj is None:
            return nil
        if isinstance(obj, bool):
            return str(obj).lower()
        to_replace: dict = {'\\': '\\\\', '\n': '\\n', '\t': '\\t'}
        if mark_str and mark_str in '"\'':
            to_replace[mark_str] = f'\\{mark_str}'
        res = str(obj)
        for orig, new in to_replace.items():
            res = res.replace(orig, new)
        if obj and obj[0] in '+-0123456789':
            return '"' + res + '"'
        return mark_str + res + mark_str

    def set_ident(self, new_ident: int):
        """ Set ident """
        self.ident = new_ident or self.ident

    def result(self, obj: Any) -> str:
        """ Serialize object """
        return self._process(obj)


########################################################
# Main functions
########################################################
def loads(text: str) -> Any:
    """ Loads object from the string of UBML format and returns it """
    return UBMLParser(text, '').result()


def load(fd: IO) -> Any:
    """ Loads object from UBML file and returns it """
    text: str = fd.read()
    return UBMLParser(text, fd.name).result()


# pylint: disable=too-many-arguments, disable=too-many-positional-arguments
def dumps(obj: Any, ident: int = 0, mark_str: str = '',
          ident_str: str = ' ', setter: str = '=',
          as_json: bool = False) -> str:
    """ Dumps object into the string of UBML format and returns it """
    return UBMLDumper(ident, mark_str, ident_str, setter, as_json).result(obj)


def dump(obj: Any, fd: IO, ident: int = 0, mark_str: str = '',
         ident_str: str = ' ', setter: str = '=',
         as_json: bool = False) -> int:
    """ Dumps object into UBML file and returns number of bytes written """
    text: str = UBMLDumper(ident, mark_str, ident_str,
                           setter, as_json).result(obj)
    return fd.write(text)
