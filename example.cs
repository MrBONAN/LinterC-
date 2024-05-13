using System;
using System.Collections.Generic;

namespace StylisticExample
{
    public static class Example
    {
        №public static List<string> Calculate(List<string> first, List<string> second)
        {
            var a = DoSomething(first, second);
            return new List<string>();
        }

        private static double[] DoSomething => new [] { 0.0 };
    }

    class Program
    {
        static void Main(string[] args)
        {
            int num1 = 10;
            int num2 = 20;

            if (num1 > num2)
            {
                Console.WriteLine("num1 больше num2.");
            }
            else if (num1 < num2)
            {
                Console.WriteLine("num1 меньше num2.");
            }
            else Console.WriteLine("num1 равен num2.");

            for (int i = 0; i < 5; i++)
            {
                Console.WriteLine($"Итерация номер {i}");
            }

            switch (num1)
            {
                case 5:
                    Console.WriteLine("num1 равно 5");
                    break;
                case 10:
                    Console.WriteLine("num1 равно 10");
                    break;
                default:
                    Console.WriteLine("num1 не равно ни 5, ни 10");
                    break;
            }

            try
            {
                int result = num2 / 0;
                Console.WriteLine($"Результат деления: {result}");
            }
            catch (DivideByZeroException ex)
            {
                Console.WriteLine("Деление на ноль!");
                Console.WriteLine($"Ошибка: {ex.Message}");
            }

            int[] numbers = { 1, 2, 3, 4, 5 };
            foreach (int number in numbers)
            {
                Console.WriteLine($"Элемент массива: {number}");
            }

            string str = "Пример строки";
            Console.WriteLine($"Длина строки: {str.Length}");

            int x = 10;
            int y = 20;
            int z = x + y;
            Console.WriteLine($"Сумма {x} и {y} равна {z}");

            string multilineString = @"Это
            многострочная
            строка";
            Console.WriteLine(multilineString);

            // Пример комментария в одну строку
            /*
             * Пример многострочного
             * комментария
             */

            int camelCaseVariable = 0;
            const int PascalCaseConstant = 100;
            var variable = 10;
            int longVariableNameForExample = 10;
        }
    }
}