from stylecheck import Stylecheck
from settings import Settings
from tokenizer import Tokenizer

if __name__ == '__main__':
    with open('example.cs', encoding='utf-8') as file:
        code = file.read()

    stylecheck = Stylecheck()
    settings = Settings()
    tokenizer = Tokenizer(code)

    lines = tokenizer.get_lines()
    result = stylecheck.check(lines, 'default.style')
    for line in result:
        print(line)
