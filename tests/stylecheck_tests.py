import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))

from linter.tokenizer import Tokenizer
from linter.stylecheck import Stylecheck


class MyTestCase(unittest.TestCase):
    def test_all(self):
        # Костыль
        example_code = 'example.cs'
        if __name__ == "__main__":
            example_code = 'tests/' + example_code
        with open(example_code, encoding='utf-8') as file:
            code = file.read()

        tokenizer = Tokenizer()
        lines = tokenizer.get_lines(code)
        stylecheck = Stylecheck()
        result = stylecheck.check(lines, 'default.style')
        expected = """####################################################
                 CHECKING THE STYLE                 
####################################################
--- always_use_braces ---
Line 26: expected '{'
Line 33: expected '{'
Line 40: expected '{'

Total errors: 3
####################################################
               ADDITIONAL INFORMATION               
####################################################
--- UNUSED VARIABLES ---
Line 10: local variable 'a' value is not used
Line 80: local variable 'variable' value is not used
Line 20: local variable 'args' value is not used
Line 8: method 'Calculate' is not used
Line 20: method 'Main' is not used
--- CYCLOMATIC COMPLEXITY ---
Cyclomatic complexity of the entire code: 7
Function: 'Calculate', cyclomatic complexity: 1
Function: 'Main', cyclomatic complexity: 6""".split('\n')
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
