from . import tokenizer

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

        statement_words = {"if", "else", "for", "foreach", "while", "do", "lock"}

        res = []
        expected_count = 0
        last_delta = 0

        for i in range(len(lines)):
            count = 0
            delta_expected_count = 0

            if lines[i][0].value == '\n' or lines[i][0].token_type == tokenizer.TokenType.StringConstant: continue

            is_prev_line_closed = True

            for t in lines[i]:
                if t.value == '{':
                    delta_expected_count += size
                if t.value == '}':
                    delta_expected_count -= size

            if last_delta == 0 and any(token.value in statement_words for token in lines[i - 1]) and not any(
                    token.value == '{' for token in lines[i - 1]) and not any(
                token.value == '{' for token in lines[i]) and lines[i - 1][-2].value != ';':
                is_prev_line_closed = False

            if delta_expected_count < 0: expected_count += delta_expected_count

            if lines[i][0].token_type == tokenizer.TokenType.Space: count = lines[i][0].value.count(options[value])
            if count != expected_count + size * (is_prev_line_closed == 0):
                res.append(
                    f'Line {i + 1}: the number of indents ({value}) per line is different (Yours {count} > {expected_count + size * (is_prev_line_closed == 0)} in code style)')
            if delta_expected_count > 0: expected_count += delta_expected_count
            last_delta = delta_expected_count

        return res

    def newline_before_return(self, value, lines):
        res = []
        empty_line_count = 0

        for i in range(len(lines)):
            if all(t.token_type == tokenizer.TokenType.Space for t in lines[i]):
                empty_line_count += 1
            else:
                for t in lines[i]:
                    if t.token_type == tokenizer.TokenType.Keyword and t.value != 'return': break
                    if t.value == 'return':
                        if empty_line_count != int(value):
                            res.append(
                                f'Line {i + 1}: there must be {int(value)} empty line before the return (expected: {empty_line_count})')
                empty_line_count = 0
        return res

    def require_semicolons(self, value, lines):
        if not value:
            return []

        res = []
        # Ключевые слова, после которых обычно не идет ;
        block_keywords = {"if", "else", "for", "foreach", "while", "do", "switch", "try", "catch", "finally", "lock",
                          "class", "static", "case", "default"}

        for i in range(len(lines) - 1):
            if any(token.value in block_keywords for token in lines[i] if
                    token.token_type == tokenizer.TokenType.Keyword) or len(lines[i]) <= 1 or lines[i][
                    -2].value in ["{", "}", "else", "do", "catch", "finally"] or any(
                    token.token_type == tokenizer.TokenType.Comment for token in lines[i]) or lines[i][
                    -2].token_type == tokenizer.TokenType.Space:
                continue

            tokens_without_spaces = [token for token in lines[i + 1] if token.token_type != tokenizer.TokenType.Space]
            if len(tokens_without_spaces) != 0 and tokens_without_spaces[0].value == '{':
                continue

            if lines[i][-2].value != ';':
                res.append(f'Line {i + 1}: expected ;')

        return res

    def space_after_keywords(self, value, lines):
        res = []
        for i in range(len(lines)):
            for j in range(len(lines[i]) - 1):
                if lines[i][j + 1].token_type != tokenizer.TokenType.Symbol or lines[i][j + 1].value in ['>', '>>', '[',
                                                                                                         ']', ';', ',',
                                                                                                         '.', ')']:
                    continue
                if lines[i][j].token_type == tokenizer.TokenType.Keyword and (
                        (lines[i][j + 1].token_type == tokenizer.TokenType.Space) != value):
                    res.append(
                        f'Line {i + 1}: {'don\'t ' if not value else ''}expected space after \'{lines[i][j].value}\'')
        return res

    def camel_case(self, value, lines):
        res = []
        camel_case_pattern = re.compile(r'^[a-zA-Z]+([A-Z0-9a-z]*)*$')
        if not value:
            return []

        for i in range(len(lines)):
            for j in range(len(lines[i])):
                if lines[i][j].token_type == tokenizer.TokenType.Identifier and not camel_case_pattern.match(
                        lines[i][j].value):
                    res.append(
                        f'Line {i + 1}: expected camelCase in \'{lines[i][j].value}\'')
        return res

    def always_use_braces(self, value, lines):
        res = []
        if not value:
            return []

        func_list = ["if", "else", "for", "foreach", "while", "do", "switch", "try", "catch", "finally", "lock"]
        for i in range(len(lines) - 1):
            if any(token.value in func_list for token in lines[i]) and all(
                    token.value != '{' for token in lines[i]) and all(token.value != '{' for token in lines[i + 1]):
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
            close_generic_indexes = []
            values = [token.value for token in lines[i]]
            for j in range(1, len(lines[i]) - 1):
                if (lines[i][j - 1].token_type in [tokenizer.TokenType.Identifier, tokenizer.TokenType.Keyword] and
                        lines[i][j + 1].token_type in [tokenizer.TokenType.Identifier, tokenizer.TokenType.Keyword] and
                        values[j] == '<'):
                    close_generic_index = values[j:].index('>')
                    if close_generic_index != -1 and values[j + 1:j + close_generic_index].count('<') == 0:
                        close_generic_indexes.append(close_generic_index + j)
                        continue

                if (lines[i][j].token_type == tokenizer.TokenType.Operation and lines[i][j].value not in ['++',
                                                                                                          '--'] and (
                            lines[i][j - 1].token_type != tokenizer.TokenType.Space or lines[i][
                        j - 1].token_type != tokenizer.TokenType.Space)) and j not in close_generic_indexes:
                    res.append(f"Line {i + 1}: expected spaces around \'{lines[i][j].value}\'")
        return res

    def allow_trailing_whitespace(self, value, lines):
        res = []
        if not value:
            return []
        for i in range(len(lines)):
            if len(lines[i]) == 1: continue
            if lines[i][-2].token_type == tokenizer.TokenType.Space and lines[i][-1].value == '\n':
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
