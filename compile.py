import re
import sys

def get_compiled(filename):
    with open(filename, 'r') as file:
        d = file.read()
    d = re.sub(r'\*\*\*([^\*]*)\*\*\*', r'<b><i>\1</i></b>', d)
    d = re.sub(r'\*\*([^\*]*)\*\*', r'<b>\1</b>', d)
    d = re.sub(r'\*([^\*]*)\*', r'<i>\1</i>', d)
    return d


def write_compiled(filename, contents):
    with open(filename + '.html', 'w') as file:
        file.write(contents)


def full_compile(filename):
    new_contents = get_compiled(filename)
    write_compiled(filename, new_contents)

def main(filenames):
    for filename in filenames:
        print("Compiling:", filename)
        full_compile(filename)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1:])

