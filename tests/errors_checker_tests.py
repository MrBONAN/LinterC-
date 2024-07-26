import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))

from linter.tokenizer import Tokenizer
from linter.errors_checker import ErrorsChecker


class MyTestCase(unittest.TestCase):
    parser = Tokenizer()
    def test_wrong_string_constant(self):
        code = """
"this string has has a closing quotation mark"
"but this does not have a closing quotation mark
"""
        lines = self.parser.get_lines(code)
        errors = ErrorsChecker.checking_for_errors(lines)
        self.assertEqual(1, len(errors), msg="The number of errors does not match")
        self.assertEqual('Line 3: the string does not have a closing quotation mark', errors[0])

    def test_wrong_multiline_comment(self):
        code = """
/*This multiline comment is good*/
/*This multiline comments does not have a closing symbols
"""
        lines = self.parser.get_lines(code)
        errors = ErrorsChecker.checking_for_errors(lines)
        self.assertEqual(1, len(errors), msg="The number of errors does not match")
        self.assertEqual('Line 3: the multiline comment has no closing characters', errors[0])

    def test_correct_brackets(self):
        code = '({[]})'
        lines = self.parser.get_lines(code)
        errors = ErrorsChecker._checking_brackets_by_dp(lines)[1]
        self.assertEqual(0, len(errors))

    def test_incorrect_brackets(self):
        code = '({[' * 100
        lines = self.parser.get_lines(code)
        errors = ErrorsChecker._checking_brackets_by_dp(lines)[1]
        self.assertEqual(300, len(errors))

    def test_difference_between_dp_and_stack(self):
        """Иллюстрация в разнице работы двух отличающихся подходов"""
        code = '({)}'
        lines = self.parser.get_lines(code)
        errors = ErrorsChecker._checking_brackets_by_dp(lines)[1]
        # Нашло 2 ошибки: нужно убрать одну из пар скобок, чтобы последовательность стала правильной
        self.assertEqual(2, len(errors))

        errors = ErrorsChecker._checking_brackets_by_stack(lines, '(', ')')
        errors.extend(ErrorsChecker._checking_brackets_by_stack(lines, '{', '}'))
        # Нашло 0 ошибок: разные типы скобок проверяются отдельно друг от друга. На данном примере ошибок "нет"
        self.assertEqual(0, len(errors))

if __name__ == '__main__':
    unittest.main()
