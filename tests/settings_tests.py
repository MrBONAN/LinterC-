import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))

from linter.tokenizer import TokenType, Token, Tokenizer
from linter.settings import Settings
from linter.stylecheck import Stylecheck


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()

    def create_token(self, value, token_type):
        return Token(value, token_type)

    def test_max_line_length(self):
        lines = [
            [self.create_token("This is a very long line of text that exceeds the limit", TokenType.Identifier)],
            [self.create_token("Short line", TokenType.Identifier)]
        ]
        result = self.settings.max_line_length(20, lines)
        self.assertEqual(result, ["Line 1: the number of characters in the line has been exceeded (55 > 20)"])

    def test_indent_style_and_size(self):
        lines = [
            [self.create_token("\t\t", TokenType.Space), self.create_token("if", TokenType.Keyword),
             self.create_token("(", TokenType.Symbol), self.create_token("true", TokenType.Identifier),
             self.create_token(")", TokenType.Symbol)],
            [self.create_token("{", TokenType.Symbol)],
            [self.create_token("    ", TokenType.Space), self.create_token("return", TokenType.Keyword),
             self.create_token(";", TokenType.Symbol)],
            [self.create_token("}", TokenType.Symbol)]
        ]
        result = self.settings.indent_style_and_size('spaces', 4, lines)
        self.assertEqual(result, [])

        result = self.settings.indent_style_and_size('tab', 4, lines)
        self.assertIn("Line 1: the number of indents (tab) per line is different (Yours 2 > 0 in code style)", result)

    def test_newline_before_return(self):
        lines = [
            [self.create_token("\n", TokenType.Space)],
            [self.create_token("return", TokenType.Keyword)]
        ]
        result = self.settings.newline_before_return(1, lines)
        self.assertEqual(result, [])

        lines = [
            [self.create_token("return", TokenType.Keyword)]
        ]
        result = self.settings.newline_before_return(1, lines)
        self.assertEqual(result, ["Line 1: there must be 1 empty line before the return (expected: 0)"])

    def test_require_semicolons(self):
        lines = [
            [self.create_token("int", TokenType.Keyword), self.create_token("a", TokenType.Identifier),
             self.create_token("=", TokenType.Operation), self.create_token("5", TokenType.NumberConstant),
             self.create_token("\n", TokenType.Space)]
        ]
        result = self.settings.require_semicolons(True, lines)
        self.assertEqual(result, ["Line 1: expected ;"])

    def test_space_after_keywords(self):
        lines = [
            [self.create_token("if", TokenType.Keyword), self.create_token("(", TokenType.Symbol),
             self.create_token("true", TokenType.Identifier), self.create_token(")", TokenType.Symbol)]
        ]
        result = self.settings.space_after_keywords(True, lines)
        self.assertEqual(result, ["Line 1: expected space after 'if'"])

        result = self.settings.space_after_keywords(False, lines)
        self.assertEqual(result, [])

    def test_camel_case(self):
        lines = [
            [self.create_token("camelCase", TokenType.Identifier)],
            [self.create_token("PascalCase", TokenType.Identifier)]
        ]
        result = self.settings.camel_case(True, lines)
        self.assertEqual(result, [])

        lines = [
            [self.create_token("snake_case", TokenType.Identifier)]
        ]
        result = self.settings.camel_case(True, lines)
        self.assertEqual(result, ["Line 1: expected camelCase in 'snake_case'"])

    def test_always_use_braces(self):
        lines = [
            [self.create_token("if", TokenType.Keyword), self.create_token("(", TokenType.Symbol),
             self.create_token("true", TokenType.Identifier), self.create_token(")", TokenType.Symbol)],
            [self.create_token("return", TokenType.Keyword), self.create_token(";", TokenType.Symbol)]
        ]
        result = self.settings.always_use_braces(True, lines)
        self.assertEqual(result, ["Line 1: expected '{'"])

    def test_newline_after_open_brace(self):
        lines = [
            [self.create_token("{", TokenType.Symbol), self.create_token("return", TokenType.Keyword),
             self.create_token(";", TokenType.Symbol)]
        ]
        result = self.settings.newline_after_open_brace(True, lines)
        self.assertEqual(result, ["Line 1: expected newline before '{'"])

    def test_newline_before_close_brace(self):
        lines = [
            [self.create_token("return", TokenType.Keyword), self.create_token(";", TokenType.Symbol),
             self.create_token("}", TokenType.Symbol)]
        ]
        result = self.settings.newline_before_close_brace(True, lines)
        self.assertEqual(result, ["Line 1: expected newline before '}'"])

    def test_space_after_comma(self):
        lines = [
            [self.create_token("a", TokenType.Identifier), self.create_token(",", TokenType.Symbol),
             self.create_token("b", TokenType.Identifier)]
        ]
        result = self.settings.space_after_comma(True, lines)
        self.assertEqual(result, ["Line 1: expected space after ','"])

    def test_space_before_comma(self):
        lines = [
            [self.create_token("a", TokenType.Identifier), self.create_token(",", TokenType.Symbol),
             self.create_token("b", TokenType.Identifier)]
        ]
        result = self.settings.space_before_comma(True, lines)
        self.assertEqual(result, ["Line 1: expected space before ','"])

    def test_space_after_colon(self):
        lines = [
            [self.create_token("a", TokenType.Identifier), self.create_token(":", TokenType.Symbol),
             self.create_token("b", TokenType.Identifier)]
        ]
        result = self.settings.space_after_colon(True, lines)
        self.assertEqual(result, ["Line 1: expected space after ':'"])

    def test_space_before_colon(self):
        lines = [
            [self.create_token("a", TokenType.Identifier), self.create_token(":", TokenType.Symbol),
             self.create_token("b", TokenType.Identifier)]
        ]
        result = self.settings.space_before_colon(True, lines)
        self.assertEqual(result, ["Line 1: expected space before ':'"])

    def test_space_around_operators(self):
        lines = [
            [self.create_token("a", TokenType.Identifier), self.create_token("+", TokenType.Operation),
             self.create_token("b", TokenType.Identifier)]
        ]
        result = self.settings.space_around_operators(True, lines)
        self.assertEqual(result, ["Line 1: expected spaces around '+'"])

    def test_file(self):
        with open('example.cs', encoding='utf-8') as file:
            code = file.read()
        tokenizer = Tokenizer(code)
        lines = tokenizer.get_lines()
        stylecheck = Stylecheck()
        result = stylecheck.check(lines, 'default.style')
        self.assertEqual(result, ['--- always_use_braces ---', "Line 26: expected '{'", "Line 33: expected '{'",
                                  "Line 40: expected '{'"])


if __name__ == '__main__':
    unittest.main()
