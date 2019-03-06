import re
import sys
import glob, os

IGNORED_FILES = "index.html"

def get_compiled(filename):
    with open(filename, 'r') as file:
        d = file.read()
    d = re.sub(r'\*\*\*([^\*]*)\*\*\*', r'<b><i>\1</i></b>', d)
    d = re.sub(r'\*\*([^\*]*)\*\*', r'<b>\1</b>', d)
    d = re.sub(r'\*([^\*]*)\*', r'<i>\1</i>', d)
    d = re.sub(r'(.+?)(\r|\n|$)+', r'<p>\1</p>\n\n', d)
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
    index = [f for f in glob.glob("*.html") if f not in IGNORED_FILES]
    index = sorted(index, key=lambda x: int(x.strip("Chapter .md.html")))
    index = [("<a href=\"" + x + "\">" + x.rstrip(".dhtml") + "</a>") for x in index]
    itext = '\n'.join(index)
    with open("index.template", "r") as ti:
        it = ti.read()
    it = it.replace("${ALL_FILES}", itext)
    with open("index.html", "w") as inf:
        inf.write(it)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        main([])

