from enum import Enum

TokenType = Enum('TokenType', ['Symbol', 'Keyword', 'NumberConstant',
                               'StringConstant', 'Character', 'Identifier',
                               'Operation', 'Comment', 'Space'])


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
            for i in [self._try_read_number,
                      self._try_read_token_word,
                      self._try_read_comment,
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
        if char != '\"' and char != '\'':
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
        if self._index + 1 >= len(self._code) or self._code[self._index] != '/' or self._code[
            self._index + 1] not in '/*':
            return
        self._index += 2
        if self._code[self._index - 1] == '*':
            return self._read_multiline_comment()
        return self._read_oneline_comment()

    def _read_oneline_comment(self):
        index = self._index
        for index in range(self._index, len(self._code)):
            if self._code[index] == '\n':
                break
        start = self._index
        self._index = index
        self._tokens.append(Token(self._code[start:index], TokenType.Comment, self._read_spaces()))
        return True

    def _read_multiline_comment(self):
        for index in range(self._index, len(self._code)):
            if index + 1 < len(self._code) and self._code[index:index + 2] == '*/':
                start = self._index
                self._index = index + 2
                self._tokens.append(Token(self._code[start:index], TokenType.Comment, self._read_spaces()))
                return True
        else:
            comment = self._read_word()
            self._tokens.append(Token(comment, TokenType.Comment, self._read_spaces()))
            return True

    def _try_read_number(self):
        if not self._code[self._index].isdigit() and not self._code[self._index] == '.':
            return False
        fraction_literals = 'fFdDmM'
        integer_literals = 'ulUL'
        was_dot = False
        number = ''
        for index in range(self._index, len(self._code)):
            char = self._code[index]
            if char.isdigit():
                number += char
            elif char == '.':
                if was_dot:
                    self._index = index + 1
                    self._get_number_token(number)
                    return True
                else:
                    was_dot = True
                    number += char
            # если не цифра и не точка, но, возможно, литерал
            else:
                self._index = index
                if char in fraction_literals:
                    number += char
                    self._index += 1
                elif char in integer_literals:
                    number += char
                    self._index += 1
                    # если есть вторая часть литерала, такая как Lu
                    if index + 1 < len(self._code) and \
                            self._code[index + 1].lower() != char.lower and \
                            self._code[index + 1] in integer_literals:
                        number += self._code[index + 1]
                        self._index += 1
                self._get_number_token(number)
                return True

    def _get_number_token(self, number):
        self._tokens.append(Token(number, TokenType.NumberConstant, self._read_spaces()))

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
