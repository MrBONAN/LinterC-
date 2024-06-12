""" Модуль для токенизации и разбора исходного кода """

from enum import Enum
from re import search

TokenType = Enum('TokenType', ['Symbol', 'Keyword', 'NumberConstant',
                               'StringConstant', 'Character', 'Identifier',
                               'Operation', 'Comment', 'Space'])


class Token:
    def __init__(self, value, token_type, row=0, column=0):
        self.value = value
        self.token_type = token_type
        self.row = row
        self.column = column


class Tokenizer:
    def __init__(self, code):
        self._code = code
        self._index = 0
        self._tokens = []
        self._row = 1

    def get_tokens(self):
        """Получение кода в виде токенов"""
        self._index = 0
        self._tokens = []
        self._row = 1
        while self._index < len(self._code):
            for i in [self._try_read_space_token,
                      self._try_read_number,
                      self._try_read_token_word,
                      self._try_read_comment,
                      self._try_read_string_constant,
                      self._try_read_operator,
                      self._read_symbol]:
                if i():
                    break
        return self._tokens

    def get_lines(self):
        """Группировка токенов по строкам как в исходном коде"""
        tokens = self.get_tokens()
        prev_line = tokens[0].row
        lines = [[]]
        for token in tokens:
            if token.row == prev_line:
                lines[-1].append(token)
            else:
                prev_line = token.row
                lines.append([token])
        return lines

    def _try_read_space_token(self):
        space = self._read_spaces()
        if space == '':
            return False
        start = 0
        end = 0
        for end in range(len(space)):
            char = space[end]
            if char == '\n':
                if start != end:
                    self._tokens.append(Token(space[start:end], TokenType.Space, self._row))
                self._tokens.append(Token('\n', TokenType.Space, self._row))
                self._row += 1
                start = end + 1
        if space[-1] != '\n':
            self._tokens.append(Token(space[start:end + 1], TokenType.Space, self._row))

    def _try_read_token_word(self):
        if self._index >= len(self._code):
            return False
        char = self._code[self._index]
        if not (char.isalnum() or char == '_'):
            return False
        current_token = self._read_word()
        if current_token in self.KEYWORDS:
            self._tokens.append(Token(current_token, TokenType.Keyword, self._row))
        else:
            self._tokens.append(Token(current_token, TokenType.Identifier, self._row))
        return True

    def _try_read_string_constant(self):
        if self._index >= len(self._code):
            return False
        char = self._code[self._index]
        if char != '\"' and char != '\'':
            return False
        current_token = self._read_string_constant()
        self._tokens.append(Token(current_token, TokenType.StringConstant, self._row))
        return True

    def _try_read_operator(self):
        index = self._index
        if index >= len(self._code):
            return False
        op1 = self._code[index]
        op2 = self._code[index:index + 2] if index + 1 < len(self._code) else None
        if op2 in self.OPERATIONS:
            self._index += 2
            self._tokens.append(Token(op2, TokenType.Operation, self._row))
        elif op1 in self.OPERATIONS:
            self._index += 1
            self._tokens.append(Token(op1, TokenType.Operation, self._row))
        else:
            return False
        return True

    def _read_symbol(self):
        if self._index >= len(self._code):
            return False
        self._index += 1
        char = self._code[self._index - 1]
        self._tokens.append(
            Token(char, TokenType.Symbol, self._row))
        return True

    def _read_spaces(self):
        spaces = ''
        while self._index < len(self._code) and self._code[self._index].isspace():
            spaces += self._code[self._index]
            self._index += 1
        return spaces

    def _read_word(self):
        word = ''
        start = self._index
        for char in self._code[start:]:
            if char.isalnum() or char == '_':
                word += char
                self._index += 1
            else:
                break
        return word

    def _read_string_constant(self):
        string = ''
        open_quotation_mark = self._code[self._index]
        self._index += 1
        start = self._index
        for char in self._code[start:]:
            if char == '\n':
                self._row += 1
            if char != open_quotation_mark:
                string += char
                self._index += 1
            else:
                break
        # если не нашли закрывающую кавычку (неправильно написанный код)
        else:
            self._index = start
            return self._read_word()
        self._index += 1
        return string

    def _try_read_comment(self):
        return self._read_oneline_comment() or self._read_multiline_comment()

    def _read_oneline_comment(self):
        regx_oneline_comment = r'(?<=^\/\/).*?(?=\n|$)'
        result = search(regx_oneline_comment, self._code[self._index:])
        if not result:
            return False
        number = result.group(0)
        self._tokens.append(Token(number, TokenType.Comment, self._row))
        self._index += len(number) + 2
        return True

    def _read_multiline_comment(self):
        regx_multiline_comment = r'(?<=^\/\*)([\w\W]*?)(?=\*\/)'
        regx_without_closing_symbols = r'(?<=^\/\*)(.*?)(?= )'
        result = search(regx_multiline_comment, self._code[self._index:])
        complete_multiline_comment = True
        if not result:
            result = search(regx_without_closing_symbols, self._code[self._index:])
            complete_multiline_comment = False
            if not result:
                return False
        number = result.group(0)
        self._tokens.append(Token(number, TokenType.Comment, self._row))
        self._index += len(number) + 2
        if complete_multiline_comment:
            self._index += 2
        return True

    def _try_read_number(self):
        regx_real_numbers = r'((([0-9]*\.[0-9]+)|([0-9]+\.[0-9]*)|([0-9]+))[fFdDmM]{0})'
        regx_integer_numbers = r'([0-9]+((UL)|(Ul)|(uL)|(ul)|(LU)|(Lu)|(lU)|(lu)|[uUlL]{0}))'
        regx_numbers = rf'^({regx_real_numbers.format("")}|{regx_integer_numbers.format("")}' + \
                       rf'|{regx_real_numbers.format("?")}|{regx_integer_numbers.format("?")})'
        result = search(regx_numbers, self._code[self._index:])
        if not result:
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
                'using', 'virtual', 'void', 'volatile', 'while']

    OPERATIONS = ['+', '-', '*', '/', '%', '=',
                  '++', '--', '+=', '-=', '*=', '/=', '%=',
                  '&&', '^', '||', '==', '!=', '>', '<', '<=', '>=',
                  '<<', '>>', '&', '|', '^', '~', '?', '=>']
