import re, json, sys, glob, os

def write(*args, **kwargs):
    print(*args, **kwargs)

def warn(*args, **kwargs):
    write("Warning:") 
    write(*args, **kwargs)

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


def write_compiled(filename, contents, config):
    with open(os.path.join(os.path.normpath(config['output']), filename + OUTPUT_EXT), 'w') as file:
        file.write(contents)


def full_compile(filename, config):
    new_contents = get_compiled(filename)
    if new_contents is None:
        return
    write_compiled(filename, new_contents, config)

def html_files():
    return [f for f in glob.glob("*.html") if f not in IGNORED_FILES]

def md_files():
    return [f for f in glob.glob("*.md") if f not in IGNORED_FILES]

def sort_ch_num(d):
    return sorted(d, key=lambda x: int(x.strip("Chapter .md.gi.html")))

def dts(d):
    return ' '.join(d)

def main(filenames, config):
    for filename in filenames:
        print("Compiling:", filename)
        full_compile(filename, config)
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

def get_def(k, d, default):
    return d[k] if k in d else default

def is_true(v):
    # This is pretty mediocre at best, but that's okay.
    return (v==True or str(v).lower()=='true' or str(v).lower()=='t')
        
def get_f(k, d):
    return (k in d and is_true(d[k]))

def dmerge(a, b):
    for k in b:
        if k not in a:
            a[k] = b[k]
    return a

def get_config(args):
    config = {'loaded': False}
    filenames = []
    debug = False
    for arg in args:
        if arg in ['-v', '--verbose']:
            config['v'] = True
            args.remove(arg)
        elif re.match(r'--?c(onfig)?=.+', arg) is not None:
            cfilename = re.match(r'-{0,2}c(onfig)?=(.+)', arg).group(2)
            with open(cfilename, 'r') as cfile:
                lconf = json.load(cfile)
            config = dmerge(config, lconf)
            config['loaded'] = True
            args.remove(arg)
        elif arg in ['--debug']:
            print(json.dumps(config, indent=2))
            debug = True
            args.remove(arg)

    if not config['loaded']:
        write("Attempting to load from default config.")
        # Try to load our default
        if os.path.isfile("config.json"):
            with open("config.json", 'r') as cfile:
                lconf = json.load(cfile)
            config = dmerge(config, lconf)
            config['loaded'] = True
        else:
            warn("Could not find any configuration options.")

    if debug:
        print(json.dumps(config, indent=2))

    filenames = args
    return [filenames, config]

if __name__ == '__main__':
    # Attempt to get configuration options
    args = sys.argv[1:]
    if len(args) == 0:
        warn("No arguments passed. Working on defaults.")
    conf = get_config(args)
    main(conf[0], conf[1])

