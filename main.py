from linter.stylecheck import Stylecheck
from linter.tokenizer import Tokenizer
import argparse

def parse_args():
    """Разбор аргументов запуска"""
    parser = argparse.ArgumentParser(
        usage='%(prog)s [OPTIONS]',
        description='Linter for C#')

    parser.add_argument(
        '-c', '--config', type=str,
        default='default.style', help='style settings file (default: "default.style")')

    parser.add_argument(
        '-s', '--source', type=str,
        help='the source file for checking the style'
    )

    return parser.parse_args()


def main():
    args = parse_args()
    config_file = args.config
    source_file = args.source

    with open('example.cs', encoding='utf-8') as file:
        code = file.read()

    stylecheck = Stylecheck()
    tokenizer = Tokenizer(code)

    lines = tokenizer.get_lines()
    result = stylecheck.check(lines, 'default.style')
    for line in result:
        print(line)

if __name__ == '__main__':
    main()
