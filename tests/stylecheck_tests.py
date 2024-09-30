import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))

from linter.tokenizer import Tokenizer
from linter.stylecheck import Stylecheck


class MyTestCase(unittest.TestCase):
    def test_all(self):
        example_code = 'example.cs'

        with open(example_code, encoding='utf-8') as file:
            code = file.read()
        with open('test_all_expected.txt', encoding='utf-8') as file:
            expected = file.read().split('\n')

        tokenizer = Tokenizer()
        lines = tokenizer.get_lines(code)
        stylecheck = Stylecheck()
        result = stylecheck.check(lines, 'default.style')
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
