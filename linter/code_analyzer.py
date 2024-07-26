from . import tokenizer
from dataclasses import dataclass


class CodeAnalyzer:
    @staticmethod
    def find_unused_objects(lines):
        tokens = [token
                  for line in lines
                  for token in CodeAnalyzer._remove_excess_tokens(line)]
        warnings = [f"""Line {token.row}: local variable '{token.value}' value is not used"""
                    for token in CodeAnalyzer._find_unused_vars(tokens)]

        warnings.extend([f"""Line {token.row}: method '{token.value}' is not used"""
                         for token in CodeAnalyzer._find_unused_functions(tokens)
                         ])
        return warnings

    @staticmethod
    def get_cyclomatic_complexity_by_function(lines):
        tokens = [token
                  for line in lines
                  for token in CodeAnalyzer._remove_excess_tokens(line)]
        cyclomatic_complexity = CodeAnalyzer._calculate_cyclomatic_complexity_by_function(tokens)
        cyclomatic_sum = sum(complexity for function_token, complexity in cyclomatic_complexity)
        return [f'Cyclomatic complexity of the entire code: {cyclomatic_sum}'] + \
            [f"""Function: '{function_token.value}', cyclomatic complexity: {complexity}"""
             for function_token, complexity in cyclomatic_complexity]

    @staticmethod
    def _find_unused_vars(tokens):
        vars = []
        stack = [{}]
        nesting_level = 0
        for i, token in enumerate(tokens):
            if token.value == '{':
                stack.append({**stack[-1]})
                nesting_level += 1
            elif token.value == '}':
                vars.extend(token for used_count, token, nest_lvl in stack[-1].values()
                            if used_count <= 1 and nest_lvl == nesting_level)
                stack.pop()
                nesting_level -= 1
            var_token = CodeAnalyzer._check_if_variable(i, tokens)
            if var_token is not None:
                stack[-1][var_token.value] = [0, var_token, nesting_level]
            elif token.value in stack[-1].keys():
                stack[-1][token.value][0] += 1
        vars.extend(token for used_count, token, nest_lvl in stack[-1].values() if used_count <= 1)
        vars.extend(CodeAnalyzer._find_unused_function_arguments(tokens))
        return vars

    @staticmethod
    def _check_if_variable(i, tokens):
        if tokens[i].value == 'var':
            if i + 1 < len(tokens):
                return tokens[i + 1]
            return None
        # TODO в теории, можно ещё написать поиск для переменных, у которых явно указан тип, но это сложнее
        return None

    @staticmethod
    def _find_unused_function_arguments(tokens):
        function_structures = CodeAnalyzer._find_function_structures(tokens)
        unused_arguments = []
        for function in function_structures:
            arguments = [tokens[i]
                         for i in range(function.begin_arguments_pos, function.end_arguments_pos - 1)
                         if tokens[i + 1].value == ',']
            # добавление последнего аргумента (так как за ним нет ',')
            if function.end_arguments_pos - function.begin_arguments_pos - 1 > 0:
                arguments.append(tokens[function.end_arguments_pos - 1])
            end = CodeAnalyzer._find_pair_bracket_position(function.begin_arguments_pos, '{', '}', tokens)
            for token in tokens[function.end_arguments_pos:end]:
                for i, argument in enumerate(arguments):
                    if argument.value == token.value:
                        arguments.pop(i)
                        break
            unused_arguments.extend(arguments)
        return unused_arguments

    @staticmethod
    def _find_unused_functions(tokens):
        function_names = [structure.name_token for structure in CodeAnalyzer._find_function_structures(tokens)]
        all_token_values = [token.value for token in tokens]
        return [function for function in function_names if all_token_values.count(function.value) == 1]

    @staticmethod
    def _find_function_structures(tokens):
        function_names = []
        skip_until = -1
        for i, token in enumerate(tokens):
            if i <= skip_until:
                continue
            if token.value == '(':
                end_bracket_pos = CodeAnalyzer._find_pair_bracket_position(i, '(', ')', tokens)
                if tokens[end_bracket_pos + 1].value != '{':
                    continue
                possible_name_token = tokens[i - 1]
                if possible_name_token.value not in tokenizer.Tokenizer.KEYWORDS:
                    begin_body = end_bracket_pos + 1
                    end_body = CodeAnalyzer._find_pair_bracket_position(end_bracket_pos + 1, '{', '}', tokens)
                    function_names.append(
                        FunctionStructure(possible_name_token, i + 1, end_bracket_pos, begin_body, end_body))
                    skip_until = end_body
        return function_names

    @staticmethod
    def _find_pair_bracket_position(start, open, close, tokens):
        stack = 0
        for end, token in enumerate(tokens[start:]):
            if token.value not in open + close:
                continue
            if token.value == open:
                stack += 1
            else:
                if stack == 1:
                    return end + start
                else:
                    stack -= 1

    @staticmethod
    def _calculate_cyclomatic_complexity_by_function(tokens):
        # Рассчитывал по формуле CC = π − s + 2 из википедии, где s = 1 всегда
        # Решил сделать так, как реализовано в Visual Studio (там можно посчитать СС)
        # Узнал эмпирически, анализируя несколько программ
        cyclomatic_complexity = []
        decision_tokens = ['if', 'for', 'while', 'foreach']
        for function in CodeAnalyzer._find_function_structures(tokens):
            count = 1
            for token in tokens[function.begin_body_pos:function.end_body_pos]:
                count += 1 if token.value in decision_tokens else 0
            cyclomatic_complexity.append((function.name_token, count))
        return cyclomatic_complexity

    @staticmethod
    def _get_line(i, tokens):
        return [token for token in tokens if token.row == tokens[i].row]

    @staticmethod
    def _remove_excess_tokens(tokens):
        return [token
                for token in tokens
                if token.token_type != tokenizer.TokenType.Comment and
                token.token_type != tokenizer.TokenType.Space]


@dataclass
class FunctionStructure:
    name_token: tokenizer.Token
    begin_arguments_pos: int
    end_arguments_pos: int
    begin_body_pos: int
    end_body_pos: int
