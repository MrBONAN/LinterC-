import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))

from linter.tokenizer import Tokenizer, TokenType


class MyTestCase(unittest.TestCase):
    def get_tokens(self, csharp_code):
        parser = Tokenizer(csharp_code)
        return parser.get_tokens()

    def get_lines(self, csharp_code):
        parser = Tokenizer(csharp_code)
        return parser.get_lines()

    def print_tokens(self, tokens):
        for token in tokens:
            if token.token_type is not TokenType.Space:
                print(f'{token.value} - {token.token_type}')

    def print_lines(self, lines):
        for line in lines:
            print(f"row: {line[0].row}")
            self.print_tokens(line)

    def _filter_space_tokens(self, tokens):
        return [token for token in tokens if token.token_type is not TokenType.Space]

    def test_string_constant(self):
        string_constant = '"hello, how are you?"'
        result = self.get_tokens(string_constant)
        self.assertEqual(1, len(result))
        self.assertEqual(TokenType.StringConstant, result[0].token_type)
        self.assertEqual('hello, how are you?', result[0].value)

    def test_large_csharp_code(self):
        if __name__ != "__main__":
            return
        large_csharp_code = """
                using System;

                namespace HelloWorld
                {
                    class Program
                    {
                        static void Main(string[] args)
                        {
                            string message = "Hello, world!";
                            Console.WriteLine(message);
                        }
                    }
                }
                """
        result = self.get_lines(large_csharp_code)
        self.print_lines(result)

    def test_space_tokens(self):
        code = """some_code 
        eight_spaces"""
        result = self.get_tokens(code)
        self.assertEqual(5, len(result))

        self.assertEqual(TokenType.Space, result[1].token_type)
        self.assertEqual(' ', result[1].value)

        self.assertEqual(TokenType.Space, result[2].token_type)
        self.assertEqual('\n', result[2].value)

        self.assertEqual(TokenType.Space, result[3].token_type)
        self.assertEqual(' ' * 8, result[3].value)

    OPERATIONS = ['=', '+', '-', '*', '/', '%',
                  '++', '--', '+=', '-=', '*=', '/=', '%=',
                  '&&', '^', '||', '==', '!=', '>', '<', '>=', '<=',
                  '<<', '>>', '&', '|', '^', '~', '?', '=>']

    def test_connected_operations(self):
        result = self.get_tokens(''.join(self.OPERATIONS))
        self.assertEqual(len(result), len(self.OPERATIONS))
        for token, op in zip(result, self.OPERATIONS):
            self.assertEqual(op, token.value)

    def test_separated_operations(self):
        result = [token for token in self.get_tokens(' '.join(self.OPERATIONS)) if
                  token.token_type != TokenType.Space]
        self.assertEqual(len(result), len(self.OPERATIONS))
        for token, op in zip(result, self.OPERATIONS):
            self.assertEqual(op, token.value)

    def test_dont_delete_newline_character(self):
        string = """some_string
with_newline_character"""
        result = self.get_tokens(string)
        self.assertEqual(3, len(result))
        self.assertEqual('\n', result[1].value)

    def test_dont_delete_newline_character_in_string(self):
        string = '''"some_string
with_newline_character"'''
        result = self.get_tokens(string)
        self.assertEqual(1, len(result))
        self.assertEqual('\n', result[0].value[11])

    def test_without_closing_quotation_mark(self):
        string = "'very big string without closing quotation mark"
        result = self.get_tokens(string)
        self.assertEqual(13, len(result))

    def test_oneline_comment(self):
        code = """// this code do nothing
var v = 0;"""
        result = self.get_tokens(code)
        self.assertEqual(10, len(result))
        self.assertEqual(TokenType.Comment, result[0].token_type)
        self.assertEqual(' this code do nothing', result[0].value)

    def test_multiline_comment_1(self):
        code = """/*- WOW, is this multiline comment?
- Yes, it is!*/
var v = 0;"""
        result = self.get_tokens(code)
        self.assertEqual(10, len(result))
        self.assertEqual(TokenType.Comment, result[0].token_type)
        self.assertEqual("""- WOW, is this multiline comment?
- Yes, it is!""", result[0].value)

    def test_multiline_comment_2(self):
        code = "var message = 2 * /*WOW*/ + 5;"
        result = self.get_tokens(code)
        self.assertEqual(16, len(result))
        self.assertEqual(TokenType.Comment, result[10].token_type)
        self.assertEqual('WOW', result[10].value)

    def test_multiline_comment_3_empty_comment(self):
        code = "var message = 2 * /**/ + 5;"
        result = self.get_tokens(code)
        self.assertEqual(16, len(result))
        self.assertEqual(TokenType.Comment, result[10].token_type)
        self.assertEqual('', result[10].value)

    def test_multiline_comment_without_closing_symbols(self):
        code = "var message = 2 * /*WOW + 5;"
        result = self.get_tokens(code)
        self.assertEqual(16, len(result))
        self.assertEqual(TokenType.Comment, result[10].token_type)
        self.assertEqual('WOW', result[10].value)

    def test_integer_numbers_1(self):
        code = """var n = 5;"""
        result = self.get_tokens(code)
        self.assertEqual(8, len(result))
        self.assertEqual('5', result[6].value)

    def test_integer_numbers_2_literals(self):
        literals = "u U l L UL Ul uL ul LU Lu lU lu".split()
        numbers = " ".join(["5" + lit for lit in literals])
        result = self._filter_space_tokens(self.get_tokens(numbers))
        self.assertEqual(len(literals), len(result))
        for expected, actual in zip(literals, result):
            self.assertEqual(TokenType.NumberConstant, actual.token_type)
            self.assertEqual("5" + expected, actual.value)

    def test_double_numbers_1(self):
        code = """var n = 5.;"""
        result = self._filter_space_tokens(self.get_tokens(code))
        self.assertEqual(5, len(result))
        self.assertEqual('5.', result[3].value)

    def test_double_numbers_2(self):
        code = """var n = 5.5242;"""
        result = self._filter_space_tokens(self.get_tokens(code))
        self.assertEqual(5, len(result))
        self.assertEqual('5.5242', result[3].value)

    def test_double_numbers_3_begin_with_dot(self):
        code = """var n = .42;"""
        result = self._filter_space_tokens(self.get_tokens(code))
        self.assertEqual(5, len(result))
        self.assertEqual('.42', result[3].value)

    def test_double_numbers_4_with_literal(self):
        literals = "f F d D m M".split()
        numbers = " ".join(["4.2" + lit for lit in literals])
        result = self._filter_space_tokens(self.get_tokens(numbers))
        self.assertEqual(len(literals), len(result))
        for expected, actual in zip(literals, result):
            self.assertEqual(TokenType.NumberConstant, actual.token_type)
            self.assertEqual("4.2" + expected, actual.value)

    def test_all_numbers_type(self):
        code = """var n=.42+5D+5.f+1.0F+3U+2l;"""
        result = self._filter_space_tokens(self.get_tokens(code))
        self.assertEqual(15, len(result))
        expected = '.42 5D 5.f 1.0F 3U 2l'.split()
        for i in range(3, 14, 2):
            self.assertEqual(TokenType.NumberConstant, result[i].token_type)
            self.assertEqual(expected[i // 2 - 1], result[i].value)

    def test_check_negative_numbers(self):
        code = """var n = -.42f;"""
        result = self._filter_space_tokens(self.get_tokens(code))
        self.assertEqual(6, len(result))
        self.assertEqual('.42f', result[4].value)

    def test_if_statement(self):
        if_statement = """
        if (true) {
            identifier += value * 5;
        }
        """

        result = self.get_tokens(if_statement)

    def test_while_statement(self):
        while_statement = """
        while (5 > 4) {
            Console.WriteLine("Wow, StringConstant");
        }
        """

        self.get_tokens(while_statement)


if __name__ == '__main__':
    unittest.main()
