import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))

from linter.tokenizer import Token, Tokenizer
from linter.settings import Settings
from linter.stylecheck import Stylecheck


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()
        self.parser = Tokenizer()

    def create_token(self, value, token_type):
        return Token(value, token_type)

    def test_max_line_length(self):
        with open('settings_test_code/test_max_line_length.txt', 'r') as f:
            lines = f.read()
        result = self.settings.max_line_length(20, self.parser.get_lines(lines))
        self.assertEqual(["Line 1: the number of characters in the line has been exceeded (55 > 20)"], result)

    def test_indent_style_and_size(self):
        lines = "\t\tif (true) { return; }"
        result = self.settings.indent_style_and_size('spaces', 4, self.parser.get_lines(lines))
        self.assertEqual(['Line 1: the indentation type is incorrect. Must be spaces'], result)

        result = self.settings.indent_style_and_size('tab', 4, self.parser.get_lines(lines))
        self.assertIn("Line 1: the number of indents (tab) per line is different (Yours 2 > 0 in code style)", result)

    def test_newline_before_return(self):
        lines = "\n\nreturn"
        result = self.settings.newline_before_return(1, self.parser.get_lines(lines))
        self.assertEqual([], result)

        lines = "return"
        result = self.settings.newline_before_return(1, self.parser.get_lines(lines))
        self.assertEqual(["Line 1: there must be 1 empty line before the return (was: 0)"], result)

    def test_require_semicolons(self):
        with open('settings_test_code/test_require_semicolons.txt', 'r') as f:
            lines = f.read()
        result = self.settings.require_semicolons(True, self.parser.get_lines(lines))
        self.assertEqual(["Line 1: expected ;"], result)

        result = self.settings.require_semicolons(False, self.parser.get_lines(lines))
        self.assertEqual([], result)

    def test_space_after_keywords(self):
        lines = "if(true)"
        result = self.settings.space_after_keywords(True, self.parser.get_lines(lines))
        self.assertEqual(["Line 1: expected space after 'if'"], result)

        result = self.settings.space_after_keywords(False, self.parser.get_lines(lines))
        self.assertEqual([], result)

    def test_camel_case(self):
        with open('settings_test_code/test_camel_case.txt', 'r') as f:
            lines = f.read()
        result = self.settings.camel_case(True, self.parser.get_lines(lines))
        self.assertEqual([], result)

        lines = "snake_case"
        result = self.settings.camel_case(True, self.parser.get_lines(lines))
        self.assertEqual(["Line 1: expected camelCase in 'snake_case'"], result)

        result = self.settings.camel_case(False, self.parser.get_lines(lines))
        self.assertEqual([], result)

    def test_always_use_braces(self):
        with open('settings_test_code/test_always_use_braces.txt', 'r') as f:
            lines = f.read()
        result = self.settings.always_use_braces(True, self.parser.get_lines(lines))
        self.assertEqual(["Line 1: expected '{'"], result)

        result = self.settings.always_use_braces(False, self.parser.get_lines(lines))
        self.assertEqual([], result)

    def test_newline_after_open_brace(self):
        lines = "{return;"
        result = self.settings.newline_after_open_brace(True, self.parser.get_lines(lines))
        self.assertEqual(["Line 1: expected newline before '{'"], result)

        result = self.settings.newline_after_open_brace(False, self.parser.get_lines(lines))
        self.assertEqual([], result)

    def test_newline_before_close_brace(self):
        lines = "return;}"
        result = self.settings.newline_before_close_brace(True, self.parser.get_lines(lines))
        self.assertEqual(["Line 1: expected newline before '}'"], result)

        result = self.settings.newline_before_close_brace(False, self.parser.get_lines(lines))
        self.assertEqual([], result)

    def test_space_after_comma(self):
        lines = "a,b"
        result = self.settings.space_after_comma(True, self.parser.get_lines(lines))
        self.assertEqual(["Line 1: expected space after ','"], result)

        result = self.settings.space_after_comma(False, self.parser.get_lines(lines))
        self.assertEqual([], result)

    def test_space_before_comma(self):
        lines = "a,b"
        result = self.settings.space_before_comma(True, self.parser.get_lines(lines))
        self.assertEqual(["Line 1: expected space before ','"], result)

        result = self.settings.space_before_comma(False, self.parser.get_lines(lines))
        self.assertEqual([], result)

    def test_space_after_colon(self):
        lines = "a:b"
        result = self.settings.space_after_colon(True, self.parser.get_lines(lines))
        self.assertEqual(["Line 1: expected space after ':'"], result)

        result = self.settings.space_after_colon(False, self.parser.get_lines(lines))
        self.assertEqual([], result)

    def test_space_before_colon(self):
        lines = "a:b"
        result = self.settings.space_before_colon(True, self.parser.get_lines(lines))
        self.assertEqual(["Line 1: expected space before ':'"], result)

        result = self.settings.space_before_colon(False, self.parser.get_lines(lines))
        self.assertEqual([], result)

    def test_space_around_operators(self):
        with open('settings_test_code/test_space_around_operators.txt', 'r') as f:
            lines = f.read()
        result = self.settings.space_around_operators(True, self.parser.get_lines(lines))
        self.assertEqual(result, ["Line 1: expected spaces around '+'", "Line 2: expected spaces around '='"])

        result = self.settings.space_around_operators(False, self.parser.get_lines(lines))
        self.assertEqual(result, [])

    def test_allow_trailing_whitespace(self):
        lines = "a + b;     \n"
        result = self.settings.allow_trailing_whitespace(True, self.parser.get_lines(lines))
        self.assertEqual(result, ["Line 1: don't expected spaces in the end of line"])

        result = self.settings.allow_trailing_whitespace(False, self.parser.get_lines(lines))
        self.assertEqual(result, [])

    def test_trim_whitespace(self):
        lines = "a  + b;\n"
        result = self.settings.trim_whitespace(True, self.parser.get_lines(lines))
        self.assertEqual(result, ["Line 1: expected ' '. Actual: '  '"])

        result = self.settings.trim_whitespace(False, self.parser.get_lines(lines))
        self.assertEqual(result, [])

    def test_file(self):
        example_code = 'example.cs'
        with open(example_code, encoding='utf-8') as file:
            code = file.read()

        tokenizer = Tokenizer()
        lines = tokenizer.get_lines(code)
        stylecheck = Stylecheck()
        result = stylecheck._check_style(lines, 'default.style')
        self.assertEqual(result, ['--- always_use_braces ---', "Line 26: expected '{'", "Line 33: expected '{'",
                                  "Line 40: expected '{'", '', 'Total errors: 3'])


if __name__ == '__main__':
    unittest.main()
