from .tokenizer import TokenType
import re


class ErrorsChecker:
    @staticmethod
    def checking_for_errors(lines):
        """Проверка анализируемого кода на корректность"""
        errors = []
        regx_string_constant = re.compile(r"""(?:(?:\$@)|(?:@\$)|(?:@)|(?:\$))?(["'])[\W\w]*?(?<!\\)(?:\\\\)*\1""")
        regx_multiline_comment = re.compile(r'\/\*[\w\W]*?(?<!\\)(?:\\\\)*\*\/')
        regx_oneline_comment = re.compile(r'//.*?(?=\n|$)')
        for token in (token for line in lines for token in line):
            if token.token_type is TokenType.StringConstant and \
                    regx_string_constant.match(token.value) is None:
                errors.append((TokenType.StringConstant,
                               f'Line {token.row}: the string does not have a closing quotation mark'))
            if token.token_type is TokenType.Comment and \
                    regx_multiline_comment.match(token.value) is None and \
                    regx_oneline_comment.match(token.value) is None:
                errors.append((TokenType.Comment,
                               f'Line {token.row}: the multiline comment has no closing characters'))

        # Упорядочивание ошибок
        errors = [error[1] for error in sorted(errors, key=lambda pair: pair[0])]

        wrong_brackets = ErrorsChecker._checking_brackets_by_dp(lines)[1]
        # если анализ работает слишком медленно, следует использовать _checking_brackets_by_stack
        # for open, close in [('(', ')'), ('[', ']'), ('{', '}')]:
        #     wrong_brackets.extend(ErrorsChecker._checking_brackets_by_stack(lines, open, close))
        for bracket in wrong_brackets[::-1]:
            errors.append(
                f"""Line {bracket.row}, column {bracket.column}: it looks like this bracket doesn't have a pair""")

        return errors

    @staticmethod
    def _checking_brackets_by_dp(lines):
        """Более общее решение проверки скобочных последовательностей, но за время O(N^3)"""
        # Решение тут (большое спасибо этому человеку) https://qna.habr.com/q/934791
        pairs = {')': '(', ']': '[', '}': '{'}
        close = ')]}'
        brackets = [token
                    for line in lines
                    for token in line
                    if token.token_type is TokenType.Symbol and token.value in '()[]{}']

        dp = [[0] * len(brackets) for _ in range(len(brackets))]
        wrong_brackets = [[[] for _ in range(len(dp))] for _ in range(len(dp))]
        for r in range(len(dp)):
            for l in range(r, -1, -1):
                # Первый случай: рассматриваем случай, когда просто удаляем текущую скобку: dp[l][r] = 1 + dp[l][r-1]
                ans = 1
                wrong_brackets[l][r].append(brackets[r])
                if l <= r - 1:
                    ans += dp[l][r - 1]
                    wrong_brackets[l][r].extend(wrong_brackets[l][r - 1])
                # если она была закрывающей, то пытаемся найти ей пару (вдруг можно не удалять данную скобку)
                # Второй случай: dp[l][r] = dp[l][i-1] + dp[i+1][r-1], где i - индекс найденной перебором парной скобки
                if brackets[r].value in close:
                    for i in range(l, r + 1):
                        if brackets[i].value != pairs[brackets[r].value]: continue
                        prev2 = 0
                        tmp_brackets = []
                        if l <= i - 1:
                            prev2 += dp[l][i - 1]
                            tmp_brackets.extend(wrong_brackets[l][i - 1])
                        if i + 1 <= r - 1:
                            prev2 += dp[i + 1][r - 1]
                            tmp_brackets.extend(wrong_brackets[i + 1][r - 1])
                        if prev2 < ans:
                            ans = prev2
                            wrong_brackets[l][r] = tmp_brackets
                dp[l][r] = ans
        if len(dp) == 0:
            return 0, []
        return dp[0][-1], wrong_brackets[0][-1]

    @staticmethod
    def _checking_brackets_by_stack(lines, open, close):
        """Простое решение проверки скобочных последовательностей реализованное на stack за O(N)"""
        wrong_brackets = []
        brackets = [token
                    for line in lines
                    for token in line
                    if token.token_type is TokenType.Symbol and token.value in open + close]
        stack = []
        for bracket in brackets:
            if bracket.value == open:
                stack.append(bracket)
            else:
                if len(stack) > 0:
                    stack.pop()
                else:
                    wrong_brackets.append(bracket)
        wrong_brackets.extend(stack)
        return wrong_brackets
