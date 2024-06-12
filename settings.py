import tokenizer
import re


class Settings:
    def max_line_length(self, value, lines):
        res = []
        for i in range(len(lines)):
            count_sym = sum([len(t.value) for t in lines[i]])
            if count_sym > value:
                res.append(
                    f'Line {i + 1}: the number of characters in the line has been exceeded ({count_sym} > {value})')
        return res

    def indent_style_and_size(self, value, size, lines):
        options = {
            'spaces': ' ',
            'tab': '\t'
        }
        res = []
        expected_count = 0
        last_expected_count = 0

        for i in range(len(lines)):
            count = 0
            if len(lines[i]) == 0 or lines[i][0].value == '\n': continue

            if lines[i][0].token_type == tokenizer.TokenType.Space: count = lines[i][0].value.count(options[value])
            if count != expected_count:
                res.append(
                    f'Line {i + 1}: the number of indents ({value}) per line is different (Yours {count} > {expected_count} in code style)')
            # TODO: сделать проверку отступов для перенесенных строк и однострочных конструкций

            for t in lines[i]:
                if t.value == '{': expected_count += size
                if t.value == '}': expected_count -= size
        # if (index - 1 > 0 and tokens[index + 1].value != '}' and options[value]):
        #     tokens[index]
        return res

    def newline_before_return(self, value, lines):  # TODO: проверить работоспособность
        res = []
        empty_line_count = 0
        is_prev_line_empty = False

        for i in range(len(lines)):
            if all(t.token_type == tokenizer.TokenType.Space for t in lines[i]):
                empty_line_count += 1
            else:
                for t in lines[i]:
                    if t.value == 'return':
                        if empty_line_count != int(value):
                            res.append(
                                f'Line {i + 1}: there must be {int(value)} empty line before the return (expected: {empty_line_count})')
        return res

    def require_semicolons(self, value, lines):
        if not value:
            return []

        res = []
        # Ключевые слова, после которых обычно не идет ;
        block_keywords = {"if", "else", "for", "foreach", "while", "do", "switch", "try", "catch", "finally", "lock",
                          "using", "namespace"}

        for i in range(len(lines)):
            if any(token.value in block_keywords for token in lines[i] if
                   token.token_type == tokenizer.TokenType.Keyword) or len(lines[i]) or len(lines[i]) == 1 or lines[i][
                -2].value in {"{", "}",
                              "else", "do", "catch", "finally"} or any(
                token.token_type == tokenizer.TokenType.Comment for token in lines[i]):
                continue

            if lines[i][-2].value != ';':
                res.append(f'Line {i + 1}: expected ;')

        return res

    def space_after_keywords(self, value, lines):
        res = []
        for i in range(len(lines)):
            for j in range(len(lines[i]) - 1):
                if lines[i][j + 1].token_type == tokenizer.TokenType.Symbol or lines[i][j + 1].value in ['>', '>>']:
                    continue
                if lines[i][j].token_type == tokenizer.TokenType.Keyword and (
                        (lines[i][j + 1].token_type == tokenizer.TokenType.Space) != value):
                    res.append(
                        f'Line {i + 1}: {'don\'t ' if not value else ''}expected space after \'{lines[i][j].value}\'')
        return res

    def camel_case(self, value, lines):
        res = []
        camel_case_pattern = re.compile(r'^[a-zA-Z]+([A-Z0-9][a-z]*)*$')
        if not value:
            return []

        for i in range(len(lines)):
            for j in range(len(lines[i])):
                if lines[i][j].token_type == tokenizer.TokenType.Identifier and not camel_case_pattern.match(
                        lines[i][j].value):
                    print(lines[i][j].value, lines[i][j].token_type)
                    res.append(
                        f'Line {i + 1}: expected camelCase in \'{lines[i][j].value}\'')
        return res

    def always_use_braces(self, value, lines):
        res = []
        if not value:
            return []
        func_list = ["if", "else", "for", "foreach", "while", "do", "switch", "try", "catch", "finally", "lock",
                     "using"]
        for i in range(len(lines)):
            if any(token in func_list for token in lines[i]) and any(token.value == '{' for token in lines[i]):
                res.append(f'Line {i + 1}: expected \'{{\'')
        return res

    def newline_after_open_brace(self, value, lines):
        res = []
        if not value:
            return []
        for i in range(len(lines)):
            if (any(token.value == '{' for token in lines[i]) and not any(token.value == '}' for token in lines[i]) and
                    len([token for token in lines[i] if token.token_type != tokenizer.TokenType.Space]) != 1):
                res.append(f'Line {i + 1}: expected newline before \'{{\'')
        return res

    def newline_before_close_brace(self, value, lines):
        res = []
        if not value:
            return []
        for i in range(len(lines)):
            if any(token.value == '}' for token in lines[i]) and len(
                    [token for token in lines[i] if token.token_type != tokenizer.TokenType.Space]) != 1 and not any(
                token.value == '{' for token in lines[i]):
                res.append(f'Line {i + 1}: expected newline before \'}}\'')
        return res

    def space_after_comma(self, value, lines):
        res = []
        if not value:
            return []
        for i in range(len(lines)):
            for j in range(len(lines[i]) - 1):
                if lines[i][j].value == ',' and lines[i][j + 1].token_type != tokenizer.TokenType.Space:
                    res.append(f"Line {i + 1}: expected space after \',\'")
        return res

    def space_before_comma(self, value, lines):
        res = []
        if not value:
            return []
        for i in range(len(lines)):
            for j in range(1, len(lines[i])):
                if lines[i][j].value == ',' and lines[i][j - 1].token_type != tokenizer.TokenType.Space:
                    res.append(f"Line {i + 1}: expected space before \',\'")
        return res

    def space_after_colon(self, value, lines):
        res = []
        if not value:
            return []
        for i in range(len(lines)):
            for j in range(len(lines[i]) - 1):
                if lines[i][j].value == ':' and lines[i][j + 1].token_type != tokenizer.TokenType.Space:
                    res.append(f"Line {i + 1}: expected space after \':\'")
        return res

    def space_before_colon(self, value, lines):
        res = []
        if not value:
            return []
        for i in range(len(lines)):
            for j in range(1, len(lines[i])):
                if lines[i][j].value == ':' and lines[i][j - 1].token_type != tokenizer.TokenType.Space:
                    res.append(f"Line {i + 1}: expected space before \':\'")
        return res

    def space_around_operators(self, value, lines):
        res = []
        if not value:
            return []
        for i in range(len(lines)):
            for j in range(1, len(lines[i]) - 1):
                if lines[i][j].token_type == tokenizer.TokenType.Operation and (
                        lines[i][j - 1].token_type != tokenizer.TokenType.Space or lines[i][
                    j - 1].token_type != tokenizer.TokenType.Space):
                    res.append(f"Line {i + 1}: expected spaces around \'{lines[i][j].value}\'")
        return res

    def remove_trailing_whitespace(self, value, lines):
        res = []
        if not value:
            return []
        for i in range(len(lines)):
            if len(lines[i]) == 1: continue
            if lines[i][-2].token_type == tokenizer.TokenType.Space:
                res.append(f"Line {i + 1}: don't expected spaces in the end of line")
        return res

    def trim_whitespace(self, value, lines):
        res = []
        if not value:
            return []
        for i in range(len(lines)):
            for j in range(1, len(lines[i])):
                if lines[i][j].token_type == tokenizer.TokenType.Space and len(lines[i][j].value) != 1:
                    res.append(f"Line {i + 1}: expected \' \'. Actual: \'{lines[i][j].value}\'")
        return res
