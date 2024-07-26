import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))

from linter.code_analyzer import CodeAnalyzer
from linter.tokenizer import Tokenizer


class MyTestCase(unittest.TestCase):
    parser = Tokenizer()

    def test_find_unused_vars(self):
        code = """
        var variable = some_function();
        Console.WriteLine(variable);
        var unused_variable;
        GetSomeVar(int a, int unused_arg)
        {
            return a;
        }
        """
        unused_vars = [token.value
                       for token in
                       CodeAnalyzer._find_unused_vars(CodeAnalyzer._remove_excess_tokens(self.parser.get_tokens(code)))]
        self.assertListEqual(['unused_variable', 'unused_arg'], unused_vars)

    def test_find_functions_names(self):
        code = """
namespace Geometry;

public static class Geometry
{
    public static double GetLength(Vector a)
    {
        return Math.Sqrt(a.X * a.X + a.Y * a.Y);
    }

    public static Vector Add(Vector a, Vector b)
    {
        return new Vector() { X = a.X + b.X, Y = a.Y + b.Y };
    }
}
"""
        tokens = CodeAnalyzer._remove_excess_tokens(self.parser.get_tokens(code))
        function_names = [structure.name_token.value for structure in CodeAnalyzer._find_function_structures(tokens)]
        self.assertListEqual(['GetLength', 'Add'], function_names)

    def test_find_unused_functions(self):
        code = """
namespace Geometry;


public static class Geometry
{
    public static double GetLength(Vector a)
    {
        return Math.Sqrt(a.X * a.X + a.Y * a.Y);
    }
    
    public static Vector Sub(Vector a, Vector b)
    {
        return new Vector() { X = a.X - b.X, Y = a.Y - b.Y };
    }

    public static bool IsVectorInSegment(Vector a, Segment segment)
    {
        var leftHalf = Sub(segment.Begin, a);
        if (...) {
        ...
        }
        ...
        return Math.Abs(expectedLength - actualLength) < 1e-5;
    }
}"""
        tokens = CodeAnalyzer._remove_excess_tokens(self.parser.get_tokens(code))
        function_names = [function.value for function in CodeAnalyzer._find_unused_functions(tokens)]
        self.assertEqual(['GetLength', 'IsVectorInSegment'], function_names)

    def test_find_unused_objects(self):
        code = """
namespace Geometry;


public static class Geometry
{
    public static double GetLength(Vector a)
    {
        return Math.Sqrt(a.X * a.X + a.Y * a.Y);
    }

    public static Vector Sub(Vector a, Vector b)
    {
        return new Vector() { X = a.X - b.X, Y = a.Y - b.Y };
    }

    public static bool IsVectorInSegment(Vector a, Segment segment)
    {
        var leftHalf = Sub(segment.Begin, a);
        ...
    }
}"""
        lines = self.parser.get_lines(code)
        object_names = CodeAnalyzer.find_unused_objects(lines)
        expected = ["Line 19: local variable 'leftHalf' value is not used",
                    "Line 7: method 'GetLength' is not used",
                    "Line 17: method 'IsVectorInSegment' is not used"]
        self.assertEqual(expected, object_names)

    def test_get_cyclomatic_complexity(self):
        code = """
class Program
{
    static void Main(string[] args)
    {
        if (args.Length == 2)
            return;
        foreach (var arg in args.Skip(2))
            Console.WriteLine(arg);
    }
    
    static int SecondFunction()
    {
        while (true) {
            if (...) {
                abracadabra;
            } else if (...) {
                simsalavim;
            } else return 0;
        }
        if (...)
            return -1;
        return 0;
    }
}
"""
        lines = self.parser.get_lines(code)
        cyclomatic_complexity = CodeAnalyzer.get_cyclomatic_complexity_by_function(lines)
        self.assertListEqual(['Cyclomatic complexity of the entire code: 8',
                              "Function: 'Main', cyclomatic complexity: 3",
                              "Function: 'SecondFunction', cyclomatic complexity: 5"], cyclomatic_complexity)


if __name__ == '__main__':
    unittest.main()
