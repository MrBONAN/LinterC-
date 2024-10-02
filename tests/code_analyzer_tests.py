import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))

from linter.code_analyzer import CodeAnalyzer
from linter.tokenizer import Tokenizer


class MyTestCase(unittest.TestCase):
    parser = Tokenizer()

    def test_find_unused_vars(self):
        with open("code_analyzer_test_code/test_find_unused_vars.txt") as f:
            code = f.read()
        unused_vars = [token.value
                       for token in
                       CodeAnalyzer._find_unused_vars(CodeAnalyzer._remove_excess_tokens(self.parser.get_tokens(code)))]
        self.assertListEqual(['unused_variable', 'unused_arg'], unused_vars)

    def test_find_functions_names(self):
        with open("code_analyzer_test_code/test_find_functions_names.txt") as f:
            code = f.read()
        tokens = CodeAnalyzer._remove_excess_tokens(self.parser.get_tokens(code))
        function_names = [structure.name_token.value for structure in CodeAnalyzer._find_function_structures(tokens)]
        self.assertListEqual(['GetLength', 'Add'], function_names)

    def test_find_unused_functions(self):
        with open("code_analyzer_test_code/test_find_unused_functions.txt") as f:
            code = f.read()
        tokens = CodeAnalyzer._remove_excess_tokens(self.parser.get_tokens(code))
        function_names = [function.value for function in CodeAnalyzer._find_unused_functions(tokens)]
        self.assertEqual(['GetLength', 'IsVectorInSegment'], function_names)

    def test_find_unused_objects(self):
        with open("code_analyzer_test_code/test_find_unused_objects.txt") as f:
            code = f.read()
        lines = self.parser.get_lines(code)
        object_names = CodeAnalyzer.find_unused_objects(lines)
        expected = ["Line 19: local variable 'leftHalf' value is not used",
                    "Line 7: method 'GetLength' is not used",
                    "Line 17: method 'IsVectorInSegment' is not used"]
        self.assertEqual(expected, object_names)

    def test_get_cyclomatic_complexity(self):
        with open("code_analyzer_test_code/test_get_cyclomatic_complexity.txt") as f:
            code = f.read()
        lines = self.parser.get_lines(code)
        cyclomatic_complexity = CodeAnalyzer.get_cyclomatic_complexity_by_function(lines)
        self.assertListEqual(['Cyclomatic complexity of the entire code: 8',
                              "Function: 'Main', cyclomatic complexity: 3",
                              "Function: 'SecondFunction', cyclomatic complexity: 5"], cyclomatic_complexity)


if __name__ == '__main__':
    unittest.main()
