from enum import Enum

TokenType = Enum('TokenType', ['Symbol', 'Keyword', 'NumberConstant',
                               'StringConstant', 'Character', 'Identifier',
                               'Operation'])


class Token:
    def __init__(self, value, token_type, right_space='', row=0, column=0):
        self.value = value
        self.token_type = token_type
        self.row = row
        self.column = column
        self.right_space = right_space


class Tokenizer:
    def __init__(self, code):
        self._code = code
        self._index = 0
        self._tokens = []

    def get_tokens(self):
        self._tokens = []
        self._read_spaces()
        while self._index < len(self._code):
            for i in [self._try_read_token_word,
                      self._try_read_string_constant,
                      self._try_read_operator,
                      self._read_symbol]:
                if i():
                    break
        return self._tokens

    def _try_read_token_word(self):
        char = self._code[self._index]
        if not (char.isalnum() or char == '_'):
            return False
        current_token = self._read_word()
        spaces = self._read_spaces()
        if current_token in self.KEYWORDS:
            self._tokens.append(Token(current_token, TokenType.Keyword, spaces))
        else:
            self._tokens.append(Token(current_token, TokenType.Identifier, spaces))
        return True

    def _try_read_string_constant(self):
        char = self._code[self._index]
        if char != '"':
            return False
        current_token = self._read_string_constant()
        spaces = self._read_spaces()
        self._tokens.append(Token(current_token, TokenType.StringConstant, spaces))
        return True

    def _try_read_operator(self):
        index = self._index
        if index >= len(self._code):
            return False
        op1 = self._code[index]
        op2 = self._code[index:index + 2] if index + 1 < len(self._code) else None
        if op2 in self.OPERATIONS:
            self._index += 2
            spaces = self._read_spaces()
            self._tokens.append(Token(op2, TokenType.Operation, spaces))
        elif op1 in self.OPERATIONS:
            self._index += 1
            spaces = self._read_spaces()
            self._tokens.append(Token(op1, TokenType.Operation, spaces))
        else:
            return False
        return True

    def _read_symbol(self):
        self._index += 1
        char = self._code[self._index - 1]
        self._tokens.append(
            Token(char, TokenType.Symbol, self._read_spaces()))
        return True

    def _read_spaces(self):
        spaces = ''
        while self._index < len(self._code) and self._code[self._index].isspace():
            spaces += self._code[self._index]
            self._index += 1
        return spaces

    def _read_word(self):
        current_token = ''
        start = self._index
        for char in self._code[start:]:
            if char.isalnum() or char == '_':
                current_token += char
                self._index += 1
            else:
                break
        return current_token

    def _read_string_constant(self):
        string = ''
        self._index += 1
        start = self._index
        for char in self._code[start:]:
            if char != '"':
                string += char
                self._index += 1
            else:
                break
        self._index += 1
        return string

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
                  '<<', '>>', '&', '|', '^', '~', '?']
