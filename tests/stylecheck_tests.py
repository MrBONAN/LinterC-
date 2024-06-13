import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))

from linter.stylecheck import Stylecheck
from linter.settings import Settings



class TestSettings(unittest.TestCase):
    def test_max_line_length_exceeded(self):
        settings = Settings()
        lines = [
            ['token1', 'token2', 'token3'],  # Список токенов для строки 1
            ['token1' * 50],                 # Строка 2 с длинным токеном
            ['token1', 'token2'],            # Список токенов для строки 3
        ]
        max_length = 10  # Максимальная длина строки
        expected_result = ['Line 2: the number of characters in the line has been exceeded (50 > 10)']
        self.assertEqual(settings.max_line_length(max_length, lines), expected_result)

    # Напишите другие тесты для остальных методов класса Settings

class TestStylecheck(unittest.TestCase):
    def test_check(self):
        stylecheck = Stylecheck()
        lines = [
            [['{'], ['token1', 'token2'], ['}']],  # Один токен между фигурными скобками
            [['{'], ['token1', 'token2'], ['token3'], ['}']],  # Три токена между фигурными скобками
            [['{'], ['token1', 'token2'], ['\t'], ['token3'], ['}']]  # С табуляцией внутри
        ]
        settings = Settings()
        expected_result = [
            "Line 1: the number of indents (spaces) per line is different (Yours 2 > 0 in code style)",
            "Line 2: the number of indents (spaces) per line is different (Yours 2 > 0 in code style)"
        ]
        self.assertEqual(stylecheck.check(lines, settings), expected_result)

    # Напишите другие тесты для остальных методов класса Stylecheck

if __name__ == '__main__':
    unittest.main()