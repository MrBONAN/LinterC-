from stylecheck import Stylecheck
from settings import Settings
from tokenizer import Tokenizer

if __name__ == '__main__':
    with open('example.cs', encoding='utf-8') as file:
        code = file.read()

    stylecheck = Stylecheck()
    tokenizer = Tokenizer(code)

    lines = tokenizer.get_lines()
    result = stylecheck.check(lines, 'default.style')
    for line in result:
        print(line)
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
    print(args)


if __name__ == '__main__':
    main()
