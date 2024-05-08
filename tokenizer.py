from enum import Enum

TokenType = Enum('TokenType', ['Symbol', 'Keyword', 'IntegerConstant',
                               'StringConstant', 'Identifier'])


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
    def tokenize(self):
        tokens = []
        current_token = ''
        while self.index < len(self.code):
            char = self.code[self.index]
            if char.isalnum() or char == '_':
                current_token = self.read_word()
            elif char == '"':
                current_token = self.read_string_constant()
            elif current_token is not '':
                tokens.append(Token(current_token, TokenType.Keyword if current_token in keywords else TokenType.Identifier))
                current_token = ''
                tokens.append(Token(char, TokenType.Symbol))
            else:
                tokens.append(Token(char, TokenType.Symbol))
                self.index += 1

        if current_token:
            tokens.append(Token(current_token,
                                TokenType.Identifier if current_token not in keywords else TokenType.Keyword, right_space))

        return tokens

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
        start = self.index
        for char in self.code[start:]:
            if char != '"':
                string += char
                self.index += 1
            else:
                self.index += 1
                break
        return string



keywords = ["abstract", "as", "base", "bool", "break", "byte", "case",
            "catch", "char", "checked", "class", "const", "continue",
            "decimal", "default", "delegate", "do", "double", "else",
            "enum", "event", "explicit", "extern", "false",
            "finally", "fixed", "float", "for", "foreach", "goto", "if",
            "implicit", "in", "int", "interface", "internal", "is",
            "lock", "long", "namespace", "new", "null", "object",
            "operator", "out", "override", "params", "private",
            "protected", "public", "readonly", "ref", "return", "sbyte",
            "sealed", "short", "sizeof", "stackalloc", "static",
            "string", "struct", "switch", "this", "throw", "true", "try",
            "typeof", "uint", "ulong", "unchecked", "unsafe", "ushort",
            "using", "virtual", "void", "volatile", "while"]
