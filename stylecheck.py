import json
import tokenizer


class Settings:
    def max_line_length(self, lines, value):
        res = []
        for i in range(len(lines)):
            count_sym = sum([len(t.value) for t in lines[i]])
            if count_sym > value:
                res.append(f'Line {i+1}: the number of characters in the line has been exceeded ({count_sym} > {value})')
        return res

    def indent_style(self, value, lines, size):
        options = {
            'spaces': ' ',
            'tab': '\t'
        }
        res = []
        expected_count = 0
        for i in range(len(lines)):
            count = 0

            for t in lines[i]:
                if t.value != options[value]: break
                else: count += 1

            if count != expected_count:
                res.append(f'Line {i+1}: the number of indents ({value}) per line is different (Yours {count} > {expected_count} in code style)')

            for t in lines[i]:
                if t.value == '{': expected_count += size
                if t.value == '}': expected_count -= size
        #TODO: сделать проверку отступов для перенесенных строк и однострочных конструкций

        # if (index - 1 > 0 and tokens[index + 1].value != '}' and options[value]):
        #     tokens[index]

    def newline_before_return(self, value, lines):
        res = []
        empty_line_count = 0
        is_prev_line_empty = False

        for i in range(len(lines)):
            if all(t.token_type == tokenizer.TokenType.Space for t in lines[i]):
                is_prev_line_empty = True
                empty_line_count += 1
            elif is_prev_line_empty:
                for t in lines[i]:
                    if t.token_type == tokenizer.TokenType.Space:
                        continue
                    elif t.value == 'return':
                        if empty_line_count != int(value):
                            res.append(f'Line {i+1}: there must be {int(value)} empty line before the return (expected: {empty_line_count})')
                        is_prev_line_empty = False
        return res


class Stylecheck:
    def check(self, lines, settings):  # lines[tokens[Token]], Dict
        raise Exception

