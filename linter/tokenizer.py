""" Модуль для токенизации и разбора исходного кода """
import re
from enum import Enum
from collections import defaultdict

TokenType = Enum('TokenType', ['Symbol', 'Keyword', 'NumberConstant',
                               'StringConstant', 'Character', 'Identifier',
                               'Operation', 'Comment', 'Space'])


class Token:
    def __init__(self, value, token_type, row=0, column=0):
        self.value = value
        self.token_type = token_type
        self.row = row
        self.column = column

    def __str__(self):
        return ', '.join(f'{k}:=\'{v}\''
                         for k, v in vars(self).items()
                         if k[0] != '_')


class Tokenizer:
    def __init__(self):
        self.__compile_regular_expressions()

        # К сожалению, эта красивая конструкция не нужна, так как методы нужно вызывать в определённом порядке :(
        # self.__read_methods = [getattr(Tokenizer, m)
        #                       for m in dir(Tokenizer)
        #                       if re.match(r'^_try_read_', m)] + [getattr(Tokenizer, '_read_symbol')]
        self.__read_methods = \
            [self._try_read_space_token,
             self._try_read_number,
             self._try_read_token_word,
             self._try_read_comment,
             self._try_read_string_constant,
             self._try_read_operator,
             self._read_symbol]

    def __compile_regular_expressions(self):
        """Предварительная компиляция регулярных выражений"""
        self.__regx_read_spaces = re.compile(r'\s+')
        self.__regx_read_token_word = re.compile(r'\w+')
        ops = ("#".join(self.OPERATIONS)
               .replace('+', r'\+')
               .replace('*', r'\*')
               .replace('?', r'\?')
               .replace('^', r'\^')
               .replace('/', r'\/')
               .replace('|', r'\|')
               .replace('#', r'|'))
        self.__regx_read_operator = re.compile(ops)

        regx_string_constant = r"""(?:(?:\$@)|(?:@\$)|(?:@)|(?:\$))?(["'])[\W\w]*?(?<!\\)(?:\\\\)*\1"""
        regx_string_constant_without_end_quote = r"""(?:(?:\$@)|(?:@\$)|(?:@)|(?:\$))?(["'])[\W\w]*?(?=\n|$| )"""
        self.__regx_read_string_constant = \
            re.compile(f'(?:{regx_string_constant})|(?:{regx_string_constant_without_end_quote})')
        self.__regx_read_oneline_comment = re.compile(r'//.*?(?=\n|$)')

        regx_multiline_comment = r'\/\*[\w\W]*?(?<!\\)(?:\\\\)*\*\/'
        regx_multiline_comment_without_closing_symbols = r'/\*.*?(?=\n|$| )'
        self.__regx_read_multiline_comment = (
            re.compile(f'(?:{regx_multiline_comment})|(?:{regx_multiline_comment_without_closing_symbols})'))

        self.__regx_read_real_numbers = re.compile(r'(([0-9]*[.,][0-9]+)|([0-9]+[.,]?))(?:[eE][-+]?[0-9]+)?[fFdDmM]?')
        self.__regx_read_integer_numbers = re.compile(r'([0-9]+((UL)|(Ul)|(uL)|(ul)|(LU)|(Lu)|(lU)|(lu)|[uUlL]?))')

    def get_tokens(self, code):
        """Получение кода в виде токенов"""
        self._index = 0
        self._tokens = []
        self._row = 1
        self._code = code

        while self._index < len(self._code):
            for method in self.__read_methods:
                if method():
                    break
        self._calculate_token_positions()
        return self._tokens

    def _calculate_token_positions(self):
        row, column = 1, 1
        prev_token = None
        for token in self._tokens:
            token.row = row
            token.column = column
            if prev_token is not None and \
                    prev_token.token_type == TokenType.StringConstant and \
                    prev_token.value == token.value:
                continue
            row += token.value.count('\n')
            if '\n' in token.value:
                column = len(token.value) - token.value.rfind('\n')
            else:
                column += len(token.value)
            prev_token = token

    def get_lines(self, code):
        """Группировка токенов по строкам как в исходном коде"""
        lines = defaultdict(list)
        for token in self.get_tokens(code):
            lines[token.row].append(token)
        return [sorted(line[1], key=lambda t: t.column) for line in sorted(lines.items())]

    def _try_read_space_token(self):
        space = self._read_spaces()
        if space == None:
            return False
        spaces = filter(None, space.replace('\n', '#\n#').split('#'))
        for s in spaces:
            self._tokens.append(Token(s, TokenType.Space))
        self._index += len(space)
        return True

    def _read_spaces(self):
        spaces = self.__regx_read_spaces.match(self._code, self._index)
        return spaces.group(0) if spaces else None

    def _try_read_token_word(self):
        char = self._code[self._index]
        if not (char.isalnum() or char == '_'):
            return False
        current_token = self._read_word()
        self._tokens.append(Token(current_token,
                                  TokenType.Keyword if current_token in self.KEYWORDS else TokenType.Identifier))
        return True

    def _read_word(self):
        word = self.__regx_read_token_word.match(self._code, self._index).group(0)
        self._index += len(word)
        return word

    def _try_read_string_constant(self):
        current_token = self._read_string_constant()
        if current_token is None:
            return False
        self._tokens.append(Token(current_token, TokenType.StringConstant))
        if current_token.count('\n') > 0:
            self._tokens.append(Token(current_token, TokenType.StringConstant))
        return True

    def _read_string_constant(self):
        string = self.__regx_read_string_constant.match(self._code, self._index)
        if string is None:
            return None
        string = string.group(0)
        self._index += len(string)
        return string

    def _try_read_operator(self):
        op = self.__regx_read_operator.match(self._code, self._index)
        if op is None:
            return False
        op = op.group(0)
        self._tokens.append(Token(op, TokenType.Operation))
        self._index += len(op)
        return True

    def _read_symbol(self):
        char = self._code[self._index]
        self._tokens.append(Token(char, TokenType.Symbol))
        self._index += 1
        return True

    def _try_read_comment(self):
        return self._read_oneline_comment() or self._read_multiline_comment()

    def _read_oneline_comment(self):
        result = self.__regx_read_oneline_comment.match(self._code, self._index)
        if result is None:
            return False
        comment = result.group(0)
        self._tokens.append(Token(comment, TokenType.Comment, self._row))
        self._index += len(comment)
        return True

    def _read_multiline_comment(self):
        result = self.__regx_read_multiline_comment.match(self._code, self._index)
        if result is None:
            return False
        comment = result.group(0)
        self._tokens.append(Token(comment, TokenType.Comment, self._row))
        self._index += len(comment)
        return True

    def _try_read_number(self):
        real_number = self.__regx_read_real_numbers.match(self._code, self._index)
        integer_number = self.__regx_read_integer_numbers.match(self._code, self._index)
        result = max(filter(None, [real_number, integer_number]), key=lambda res: len(res.group(0)), default=None)
        if result is None:
            return False
        number = result.group(0)
        self._tokens.append(Token(number, TokenType.NumberConstant, self._row))
        self._index += len(number)
        return True

    KEYWORDS = ['abstract', 'as', 'base', 'bool', 'break', 'byte', 'case',
                'catch', 'char', 'checked', 'class', 'const', 'continue',
                'decimal', 'default', 'delegate', 'do', 'double', 'else',
                'enum', 'event', 'explicit', 'extern', 'false',
                'finally', 'fixed', 'float', 'for', 'foreach', 'goto', 'if',
                'implicit', 'in', 'int', 'interface', 'internal', 'is',
                'lock', 'long', 'namespace', 'new', 'null', 'object',
                'operator', 'out', 'override', 'params', 'private',
                'protected', 'public', 'readonly', 'ref', 'return', 'sbyte',
                'sealed', 'short', 'sizeof', 'stackalloc', 'static',
                'string', 'struct', 'switch', 'this', 'throw', 'true', 'try',
                'typeof', 'uint', 'ulong', 'unchecked', 'unsafe', 'ushort',
                'using', 'virtual', 'void', 'volatile', 'while', 'var']

    OPERATIONS = ['++', '--', '+=', '-=', '*=', '/=', '%=',
                  '&&', '||', '==', '!=', '<=', '>=',
                  '<<', '>>', '=>',
                  '&', '|', '~', '?', '+', '-', '*', '/', '%', '=', '^', '>', '<']
