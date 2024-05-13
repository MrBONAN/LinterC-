import unittest
import tokenizer


class MyTestCase(unittest.TestCase):
    def get_tokens(self, csharp_code):
        parser = tokenizer.Tokenizer(csharp_code)
        return parser.get_tokens()

    def print_tokens(self, tokens):
        for token in tokens:
            print((f'{token.value} - {token.token_type}'))

    def test_string_constant(self):
        string_constant = '"hello, how are you?"'
        result = self.get_tokens(string_constant)
        self.assertEqual(1, len(result))
        string_token = result[0]
        self.assertEqual('hello, how are you?', string_token.value)
        self.assertEqual('', string_token.right_space)

    def tests_large_csharp_code(self):
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
        result = self.get_tokens(large_csharp_code)
        self.print_tokens(result)

    OPERATIONS = ['=', '+', '-', '*', '/', '%',
                  '++', '--', '+=', '-=', '*=', '/=', '%=',
                  '&&', '^', '||', '==', '!=', '>', '<', '>=', '<=',
                  '<<', '>>', '&', '|', '^', '~', '?']

    def test_connected_operations(self):
        result = self.get_tokens(''.join(self.OPERATIONS))
        self.assertEqual(len(result), len(self.OPERATIONS))
        for token, op in zip(result, self.OPERATIONS):
            self.assertEqual(op, token.value)

    def test_separated_operations(self):
        result = self.get_tokens(' '.join(self.OPERATIONS))
        self.assertEqual(len(result), len(self.OPERATIONS))
        for token, op in zip(result, self.OPERATIONS):
            self.assertEqual(op, token.value)

    def test_dont_delete_newline_character(self):
        string = """some_string
with_newline_character"""
        result = self.get_tokens(string)
        self.assertEqual(2, len(result))
        self.assertEqual('\n', result[0].right_space)

    def test_dont_delete_newline_character_in_string(self):
        string = '''"some_string
with_newline_character"'''
        result = self.get_tokens(string)
        self.assertEqual(1, len(result))
        self.assertEqual('\n', result[0].value[11])

    def test_without_closing_quotation_mark(self):
        string = "'very big string without closing quotation mark"
        result = self.get_tokens(string)
        self.assertEqual(7, len(result))

    def test_oneline_comment(self):
        code = """// this code do nothing
var v = 0;"""
        result = self.get_tokens(code)
        self.assertEqual(6, len(result))
        self.assertEqual(result[0].token_type, tokenizer.TokenType.Comment)
        self.assertEqual(result[0].value, ' this code do nothing')

    def test_multiline_comment_1(self):
        code = """/*- WOW, this is multiline comment?
- Yes, it is!*/
var v = 0;"""
        result = self.get_tokens(code)
        self.assertEqual(6, len(result))
        self.assertEqual(result[0].token_type, tokenizer.TokenType.Comment)
        self.assertEqual(result[0].value, """- WOW, this is multiline comment?
- Yes, it is!""")

    def test_multiline_comment_2(self):
        code = "var message = 2 * /*WOW*/ + 5;"
        result = self.get_tokens(code)
        self.assertEqual(9, len(result))
        self.assertEqual(result[5].token_type, tokenizer.TokenType.Comment)
        self.assertEqual(result[5].value, 'WOW')

    def test_multiline_comment_3_empty_comment(self):
        code = "var message = 2 * /**/ + 5;"
        result = self.get_tokens(code)
        self.assertEqual(9, len(result))
        self.assertEqual(result[5].token_type, tokenizer.TokenType.Comment)
        self.assertEqual(result[5].value, '')

    def test_multiline_comment_without_closing_symbols(self):
        code = "var message = 2 * /*WOW + 5;"
        result = self.get_tokens(code)
        self.assertEqual(9, len(result))
        self.assertEqual(result[5].token_type, tokenizer.TokenType.Comment)
        self.assertEqual(result[5].value, 'WOW')

    def test_numbers(self):
        code = """var message = 2 * /*WOW*/ + 5;"""
        result = self.get_tokens(code)

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
