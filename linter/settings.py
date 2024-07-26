from . import tokenizer
from . import errors_checker
from . import code_analyzer
import re


class Settings:
    _have_errors = False

    def checking_for_errors(self, lines):
        errors = errors_checker.ErrorsChecker.checking_for_errors(lines)
        self._have_errors = False
        if len(errors) > 0:
            errors = ['--- ERRORS ---'] + errors
            self._have_errors = True
        return errors

    def analyze_code(self, lines):
        result = []
        unused_objects = code_analyzer.CodeAnalyzer.find_unused_objects(lines)
        if len(unused_objects) > 0:
            result += ['--- UNUSED VARIABLES ---'] + unused_objects

        result.append('--- CYCLOMATIC COMPLEXITY ---')
        if self._have_errors:
            result.append('The indentation style check cannot be performed until you fix'
                          ' all the errors in the code mentioned above')
        else:
            cyclomatic_complexity = code_analyzer.CodeAnalyzer.get_cyclomatic_complexity_by_function(lines)
            result.extend(cyclomatic_complexity)
        return result

    def max_line_length(self, max_length, lines):
        res = []
        for i in range(len(lines)):
            count_symbols = sum([len(t.value) for t in lines[i] if t.value != '\n'])
            if count_symbols > max_length:
                res.append(
                    f'Line {lines[i][0].row}: the number of characters in the line has been exceeded ({count_symbols} > {max_length})')
        return res

    def allow_trailing_whitespace(self, value, lines):
        if not value:
            return []
        res = []
        for line in lines:
            if len(line) == 1: continue
            if line[-2].token_type == tokenizer.TokenType.Space and line[-1].value == '\n':
                res.append(f"Line {line[0].row}: don't expected spaces in the end of line")
        return res

    def trim_whitespace(self, value, lines):
        if not value:
            return []
        res = []
        for line in lines:
            for token in line[1:]:
                if token.token_type == tokenizer.TokenType.Space and len(token.value) != 1:
                    res.append(f"Line {token.row}: expected \' \'. Actual: \'{token.value}\'")
        return res

    def space_after_comma(self, value, lines):
        if not value:
            return []
        res = []
        for line in lines:
            for token, next_token in zip(line, line[1:]):
                if token.value == ',' and next_token.token_type != tokenizer.TokenType.Space:
                    res.append(f"Line {token.row}: expected space after \',\'")
        return res

    def space_before_comma(self, value, lines):
        if not value:
            return []
        res = []
        for line in lines:
            for token, next_token in zip(line, line[1:]):
                if next_token.value == ',' and token.token_type != tokenizer.TokenType.Space:
                    res.append(f"Line {token.row}: expected space before \',\'")
        return res

    def space_after_colon(self, value, lines):
        if not value:
            return []
        res = []
        for line in lines:
            for token, next_token in zip(line, line[1:]):
                if token.value == ':' and next_token.token_type != tokenizer.TokenType.Space:
                    res.append(f"Line {token.row}: expected space after \':\'")
        return res

    def space_before_colon(self, value, lines):
        if not value:
            return []
        res = []
        for line in lines:
            for token, next_token in zip(line, line[1:]):
                if next_token.value == ':' and token.token_type != tokenizer.TokenType.Space:
                    res.append(f"Line {token.row}: expected space before \':\'")
        return res

    def newline_after_open_brace(self, value, lines):
        res = []
        if not value:
            return []

        for i in range(len(lines)):
            if (any(token.value == '{' for token in lines[i]) and not any(token.value == '}' for token in lines[i]) and
                    len([token for token in lines[i] if token.token_type != tokenizer.TokenType.Space]) != 1):
                res.append(f'Line {lines[i][0].row}: expected newline before \'{{\'')
        return res

    def newline_before_close_brace(self, value, lines):
        res = []
        if not value:
            return []

        for i in range(len(lines)):
            if any(token.value == '}' for token in lines[i]) and len(
                    [token for token in lines[i] if token.token_type != tokenizer.TokenType.Space]) != 1 and not any(
                token.value == '{' for token in lines[i]):
                res.append(f'Line {lines[i][0].row}: expected newline before \'}}\'')
        return res

    def indent_style_and_size(self, value, size, lines):
        if self._have_errors is True:
            return [
                'The indentation style check cannot be performed until you fix all the errors in the code mentioned above']

        options = {
            'spaces': ' ',
            'tab': '\t'
        }

        res = []
        expected_count = 0

        i = 0
        length = len(lines)
        while i < length:
            count = 0
            delta_expected_count = 0

            if lines[i][0].value == '\n' or lines[i][0].token_type == tokenizer.TokenType.StringConstant:
                i += 1
                continue

            is_prev_line_closed = True

            for t in lines[i]:
                if t.value == '{':
                    delta_expected_count += size
                if t.value == '}':
                    delta_expected_count -= size

            if delta_expected_count < 0: expected_count += delta_expected_count

            res.extend(self._check_indent_type(i, value, lines))

            if lines[i][0].token_type == tokenizer.TokenType.Space:
                count = lines[i][0].value.count(options[value])
            if count != expected_count + size * (is_prev_line_closed == 0):
                res.append(
                    f'Line {lines[i][0].row}: the number of indents ({value}) per line is different (Yours {count} > {expected_count + size * (is_prev_line_closed == 0)} in code style)')

            analysis = self._find_statements(i, lines)
            if analysis is not None:
                tmp_res, end_row = self._analyse_statement(analysis, expected_count, value, size, lines)
                res.extend(tmp_res)
                i = end_row
                if delta_expected_count > 0: expected_count += delta_expected_count
                continue

            if delta_expected_count > 0: expected_count += delta_expected_count

            i += 1

        return res

    def _find_statements(self, line_index, lines):
        statement_words = {"if", "else", "for", "foreach", "while", "do", "lock"}
        line = lines[line_index]
        if all(token.value not in statement_words for token in line):
            return None
        for i in range(len(line) - 1, -1, -1):
            if line[i].value in statement_words:
                break
        if i + 1 < len(line) and line[i + 1].value == '(':
            begin = i + 1
        elif i + 2 < len(line) and line[i + 2].value == '(':
            begin = i + 2
        else:
            return None
        begin_row, begin_index = line_index, begin
        end_row, end_index = self._find_bracket_pair(line_index, begin, lines)
        index = end_index + 1
        for row, line in enumerate(lines[end_row:]):
            while index < len(line):
                if line[index].token_type != tokenizer.TokenType.Space and \
                        line[index].token_type != tokenizer.TokenType.Comment:
                    # последние 3 - строка, индекс в строке первого токена после ')' Если этот токен == '{', то
                    # последний элемент - True, иначе False
                    # (случай, когда у у данного выражения нет тела, обрамлённого фигурными скобками)
                    #      (.row       (.column     ).row    ).column   (см выше, что за индексы)
                    return [begin_row, begin_index, end_row, end_index, row + end_row, index] + [
                        line[index].value == '{']
                index += 1
            index = 0
        return None

    def _find_bracket_pair(self, line_index, index, lines):
        # Предполагаю, что скобки в коде правильные (проверены точным алгоритмом в errors_checker)
        stack = []
        for row, line in enumerate(lines[line_index:]):
            while index < len(line):
                bracket = line[index]
                if bracket.value in '()':
                    if bracket.value == '(':
                        stack.append(bracket)
                    else:
                        if len(stack) > 0:
                            stack.pop()
                        if len(stack) == 0:
                            return row + line_index, index
                index += 1
            index = 0
        raise ValueError

    def _analyse_statement(self, data, statement_indent, value, size, lines):
        res = []
        # анализ выражения в условии
        for row in range(data[0] + 1, data[2]):
            indent = self._get_indent(row, lines)
            if indent != statement_indent + size:
                res.append(
                    f'Line {lines[row][0].row}: the number of indents ({value}) per line is different '
                    f'(Yours {indent} > {statement_indent + size} in code style)')

        if data[-1] is False:  # Если тело выражения не выделено фигурными скобками
            if data[2] != data[4]:  # если закрывающая скобка ) и начало тела находятся в разных строках
                indent = self._get_indent(data[4], lines)
                if indent != statement_indent + size:
                    res.append(
                        f'Line {lines[data[4]][0].row}: the number of indents ({value}) per line is different '
                        f'(Yours {indent} > {statement_indent + size} in code style)')
            # будем продолжать анализ со следующей строчки
            end_row = data[4] + 1
        else:
            # стандартный случай, ничего больше делать не надо
            end_row = data[4] + (1 if data[0] == data[4] else 0)
            pass
        return res, end_row

    def _get_indent(self, index, lines):
        first_token = lines[index][0]
        if first_token.value == '\n' or first_token.token_type != tokenizer.TokenType.Space:
            return 0
        return len(first_token.value)

    def _check_indent_type(self, index, indent_type, lines):
        options = {
            'spaces': ' ',
            'tab': '\t'
        }
        first_token = lines[index][0]
        if first_token.value == '\n' or first_token.token_type != tokenizer.TokenType.Space:
            return []
        if first_token.value.count(options[indent_type]) == len(first_token.value):
            return []
        return [f'Line {first_token.row}: the indentation type is incorrect. Must be {indent_type}']

    def newline_before_return(self, value, lines):
        res = []
        empty_line_count = 0

        for i in range(len(lines)):
            if all(t.token_type == tokenizer.TokenType.Space for t in lines[i]):
                empty_line_count += 1
            else:
                for t in lines[i]:
                    if (t.token_type == tokenizer.TokenType.Keyword or t.token_type == tokenizer.TokenType.Identifier) \
                            and t.value != 'return': break
                    if t.value == 'return':
                        if empty_line_count < int(value):
                            res.append(
                                f'Line {lines[i][0].row}: there must be {int(value)} empty line before the return (was: {empty_line_count})')
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
                res.append(f'Line {lines[i][0].row}: expected ;')

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
                        f'Line {lines[i][0].row}: {"do not " if not value else ""}expected space after \'{lines[i][j].value}\'')
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
                        f'Line {lines[i][0].row}: expected camelCase in \'{lines[i][j].value}\'')
        return res

    def always_use_braces(self, value, lines):
        res = []
        if not value:
            return []

        func_list = ["if", "else", "for", "foreach", "while", "do", "switch", "try", "catch", "finally", "lock"]
        for i in range(len(lines) - 1):
            if any(token.value in func_list for token in lines[i]) and all(
                    token.value != '{' for token in lines[i]) and all(token.value != '{' for token in lines[i + 1]):
                res.append(f'Line {lines[i][0].row}: expected \'{{\'')
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
                    res.append(f"Line {lines[i][0].row}: expected spaces around \'{lines[i][j].value}\'")
        return res
