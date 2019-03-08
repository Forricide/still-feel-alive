import re
import sys
import glob, os

IGNORED_FILES = "index.html"
OUTPUT_EXT = '.gi.html'

def get_compiled(filename):
    if filename.endswith('.py') or filename.endswith('.sh') or filename.endswith(OUTPUT_EXT):
        print('Refusing to compile script file.')
        return None
    if filename in ['.git']:
        sys.exit('You are doing something very wrong, sir. [Filename was: .git]')
    with open(filename, 'r') as file:
        d = file.read()
    d = re.sub(r'\*\*\*([^\*]*)\*\*\*', r'<b><i>\1</i></b>', d)
    d = re.sub(r'\*\*([^\*]*)\*\*', r'<b>\1</b>', d)
    d = re.sub(r'\*([^\*]*)\*', r'<i>\1</i>', d)
    d = re.sub(r'(.+?)(\r|\n|$)+', r'<p>\1</p>\n\n', d)
    return d


def write_compiled(filename, contents):
    with open(filename + OUTPUT_EXT, 'w') as file:
        file.write(contents)


def full_compile(filename):
    new_contents = get_compiled(filename)
    if new_contents is None:
        return
    write_compiled(filename, new_contents)

def html_files():
    return [f for f in glob.glob("*.html") if f not in IGNORED_FILES]

def md_files():
    return [f for f in glob.glob("*.md") if f not in IGNORED_FILES]

def sort_ch_num(d):
    return sorted(d, key=lambda x: int(x.strip("Chapter .md.gi.html")))

def dts(d):
    return ' '.join(d)

def main(filenames):
    for filename in filenames:
        print("Compiling:", filename)
        full_compile(filename)
    print('Making index.')
    index = html_files()
    print('Found', len(index), 'html files.')
    index = sort_ch_num(index) 
    index = [("<a href=\"" + x + "\">" + x.rstrip(".dgihtml") + "</a>") for x in index]
    print('Created a', len(index), 'length index.')
    itext = '<p>' + '</p>\n<p>'.join(index) + '</p>'
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

