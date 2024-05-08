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
        self.code = code
        self.index = 0
        self.tokens = []

    def get_tokens(self):
        self.tokens = []
        while self.index < len(self.code):
            # any([self.try_read_token_word(),
            #     self.try_read_string_constant(),
            #     self.try_read_operator(),
            #     self.skip_spaces()])
            # continue
            char = self.code[self.index]
            if char.isalnum() or char == '_':
                current_token = self.read_word()
                spaces = self.read_spaces()
                if current_token in Tokenizer.KEYWORDS:
                    self.tokens.append(Token(current_token, TokenType.Keyword, spaces))
                else:
                    self.tokens.append(Token(current_token, TokenType.Identifier, spaces))
            elif char == '"':
                current_token = self.read_string_constant()
                spaces = self.read_spaces()
                if current_token != '':
                    self.tokens.append(Token(current_token, TokenType.StringConstant, spaces))
            elif char.isspace():
                self.read_spaces()
            else:
                isOperator = self.try_read_operator()
                if isOperator:
                    self.tokens.append(Token(char, TokenType.Symbol, self.read_spaces()))
                else:
                    self.index += 1
                    self.tokens.append(
                        Token(char, TokenType.Symbol, self.read_spaces()))
        return self.tokens

    def try_read_token_word(self):
        char = self.code[self.index]
        if not (char.isalnum() or char == '_'):
            return False
        current_token = self.read_word()
        spaces = self.read_spaces()
        if current_token in Tokenizer.KEYWORDS:
            self.tokens.append(Token(current_token, TokenType.Keyword, spaces))
        else:
            self.tokens.append(Token(current_token, TokenType.Identifier, spaces))
        return True

    def try_read_string_constant(self):
        char = self.code[self.index]
        if char != '"':
            return False
        current_token = self.read_string_constant()
        spaces = self.read_spaces()
        if current_token != '':
            self.tokens.append(Token(current_token, TokenType.StringConstant, spaces))
        return True

    def try_read_operator(self):
        return False

    def read_symbol(self):
        self.index += 1
        char = self.code[self.index - 1]
        self.tokens.append(
            Token(char, TokenType.Symbol, self.read_spaces()))
        return True

    def skip_spaces(self):
        self.read_spaces()
        return False

    def read_spaces(self):
        spaces = ''
        while self.index < len(self.code) and self.code[self.index].isspace():
            spaces += self.code[self.index]
            self.index += 1
        return spaces

    def read_word(self):
        current_token = ''
        start = self.index
        for char in self.code[start:]:
            if char.isalnum() or char == '_':
                current_token += char
                self.index += 1
            else:
                break
        return current_token

    def read_string_constant(self):
        string = ''
        self.index += 1
        start = self.index
        for char in self.code[start:]:
            if char != '"':
                string += char
                self.index += 1
            else:
                break
        self.index += 1
        return string

    def try_read_operator(self):
        pass

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
