import unittest
import tokenizer


class MyTestCase(unittest.TestCase):
    def test_something(self):
        csharp_code = """
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

        parser = tokenizer.Tokenizer(csharp_code)
        for token in parser.get_tokens():
            print((f'{token.value} - {token.token_type}'))


if __name__ == '__main__':
    unittest.main()
