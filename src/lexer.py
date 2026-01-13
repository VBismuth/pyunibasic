# -*- coding: utf-8 -*-
""" Tokenizer for unibasic v0.01 """

from enum import Enum
from typing import Tuple

from textdata import TextData, EOF
from textdata import TextPointer as Pointer
from errors import IllegalCharacterErr, SyntaxErr, Error


# TODO: Need semicolon to do something
class TokenType(Enum):
    """ Token types """
    NIL        = 0
    INT        = 1
    FLOAT      = 2
    STR        = 3

    KEYWORD    = 4
    FUNCTION   = 5
    COMMENT    = 6

    DOT        = 7
    COLON      = 8
    SEMICOLON  = 9
    TILDE      = 10
    LBRACE     = 11
    RBRACE     = 12
    LPAREN     = 13
    RPAREN     = 14

    OP_PLUS    = 15
    OP_MINUS   = 16
    OP_MULT    = 17
    OP_DIV     = 18
    OP_ASSIGN  = 19
    OP_POW     = 20
    OP_MOD     = 21
    OP_GREATER = 22
    OP_LESSER  = 23
    OP_EQUAL   = 24
    OP_NOT     = 25
    OP_GE      = 26
    OP_LE      = 27
    OP_NE      = 28

    NEWLINE    = 29
    MAX        = 30


class Token:
    """ Token class """
    # pylint: disable=too-few-public-methods

    def __init__(self, token_type: TokenType, pos_data: Pointer, value=None):
        self.value = value
        self.token_type = token_type if token_type else TokenType.NIL
        self.pos_data = pos_data if isinstance(pos_data, Pointer) else None

    def __repr__(self) -> str:
        if self.value:
            return str(self.token_type.name) + ':' + str(self.value)[:20] +\
                '...' * (len(self.value) >= 20)
        return str(self.token_type.name)


class Lexer(TextData):
    """ Tokenizing text """

    def tokenize(self, other: TextData | None = None
                 ) -> Tuple[list[Token], Error]:
        """ Token generator
            If argument is ommited, tokenizes self
            Returns list of Tokens and no_error bool """
        this = self
        error: Error | None = None
        if isinstance(other, TextData):
            this = other
        result: list[Token] = []
        while this.get_char() != EOF and not error:
            char: str = this.get_char()
            TT: type[TokenType] = TokenType
            if char in ' \t':
                this.next()
                continue
            match char:
                # TODO finish
                case '+': result.append(Token(TT.OP_PLUS, this.get_pointer()))
                case '-': result.append(Token(TT.OP_MINUS, this.get_pointer()))
                case '*': result.append(Token(TT.OP_MULT, this.get_pointer()))
                case '/': result.append(Token(TT.OP_DIV, this.get_pointer()))
                case '~': result.append(Token(TT.TILDE, this.get_pointer()))
                case '=': result.append(Token(TT.OP_ASSIGN,
                                              this.get_pointer()))
                case '#': result.append(Token(TT.COMMENT, this.get_pointer(),
                                              self.process_comment(this)))
                case '%': result.append(Token(TT.OP_MOD, this.get_pointer()))
                case '^': result.append(Token(TT.OP_POW, this.get_pointer()))
                case '(': result.append(Token(TT.LPAREN, this.get_pointer()))
                case ')': result.append(Token(TT.RPAREN, this.get_pointer()))
                case '{': result.append(Token(TT.RBRACE, this.get_pointer()))
                case '}': result.append(Token(TT.LBRACE, this.get_pointer()))
                case '\n': result.append(Token(TT.NEWLINE, this.get_pointer()))
                case '"' | '\'':
                    string, error = self.process_as_string(this)
                    result.append(Token(TT.STR, this.get_pointer(), string))

                case ch:
                    if str(ch).isdigit():
                        num, error = self.process_as_number(this)
                        result.append(num)
                    elif str(ch).isalpha():
                        keyword, error = self.process_as_keyword(this)
                        result.append(keyword)
                    else:
                        error = IllegalCharacterErr(f'got ({ch.encode().hex()}'
                                                    f") {ch}'",
                                                    self.get_pointer(),
                                                    self.get_pointer(),
                                                    self.get_filename())
            this.next()
        return result, error

    # TODO: implement interpreter error handling
    @staticmethod
    def process_comment(this: TextData) -> str:
        """ Process text as unibasic comment string """
        res: str = ''
        while this.next() not in ('\n', EOF):
            res += this.get_char()
        return res

    @staticmethod
    def process_as_string(this: TextData) -> (str, Error | None):
        """ Process text as string """
        quote: str = this.get_char()
        res: str = quote or ''
        pos_start = this.get_pointer()
        while this.next() != quote or res[-1] == '\\':
            if this.get_char() == EOF:
                return res, SyntaxErr('unterminated string literal', pos_start,
                                      this.get_pointer(), this.get_filename())
            res += this.get_char()
        return res + quote, None

    @staticmethod
    def process_as_keyword(this: TextData) -> (Token, Error | None):
        """ Process text as keyword """
        res: str = ""
        error: Error | None = None
        start_pos: Pointer = this.get_pointer()
        while this.get_char() not in ' \n':
            if this.get_char() == EOF:
                break
            if not this.get_char().isalnum():
                error = IllegalCharacterErr(f"'{this.get_char()}'",
                                            start_pos, this.get_pointer(),
                                            this.get_filename())
                break
            res += this.get_char()
            this.next()
        return Token(TokenType.KEYWORD, start_pos, res), error

    @staticmethod
    def process_as_number(this: TextData) -> (Token, Error | None):
        """ Process text as int or float """
        res: str = ""
        dots: int = 0
        error: Error | None = None
        start_pos: Pointer = this.get_pointer()
        while this.get_char() not in ' \n':
            if this.get_char() == EOF:
                break
            if this.get_char() == '.':
                dots += 1
            elif not this.get_char().isdigit():
                break
            res += this.get_char()
            this.next()
        this.previous()
        if dots > 1:
            error = SyntaxErr("too many dots for number",
                              start_pos, this.get_pointer(),
                              this.get_filename())
        token_type = TokenType.FLOAT if dots else TokenType.INT
        return Token(token_type, start_pos, res), error


def run(text: str) -> (Token, Error | None):
    """ Run tokenizer """
    lex = Lexer(text)
    return lex.tokenize()
