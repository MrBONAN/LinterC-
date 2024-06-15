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
        '-s', '--source', type=str, default='tests/example.cs',
        help='the source file for checking the style (default: "tests/example.cs")'
    )

    return parser.parse_args()


def main():
    args = parse_args()
    config_file = args.config
    source_file = args.source

    print(f'Your file: "{source_file}"')
    print(f'Your style: "{config_file}"')
    print()

    with open(source_file, encoding='utf-8') as file:
        code = file.read()

    print(f'"{source_file}" has been loaded successfully.\n')

    stylecheck = Stylecheck()
    tokenizer = Tokenizer(code)
    lines = tokenizer.get_lines()
    result = stylecheck.check(lines, config_file)

    for line in result:
        print(line)

    with open('result.txt', 'w', encoding='utf-8') as file:
        file.write(f'Your file: "{source_file}"\n')
        file.write(f'Your style: "{config_file}"\n\n')
        file.write('\n'.join(result))

    print('\nResult has been recorded into "result.txt"')
    input("\nPress Enter to quit...")

if __name__ == '__main__':
    main()
