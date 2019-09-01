#!/usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    raise Exception("Python 2 is unsupported.")

from enum import Enum
import re, json, glob, os
import hashlib

IGNORED_FILES = "index.html"
OUTPUT_EXT = '.gi.html'

class Mode(Enum):
    HTML = 1
    BBCode = 2
    BAD = 3

class ModeInfo():
    def __init__(self, config):
        # Defaults
        self.ext = OUTPUT_EXT
        self.mode_str = 'HTML'
        self.mode = Mode.HTML
        if 'mode' in config:
            self.parse_mode(str(config['mode']).strip(' \r\n').lower())

    def parse_mode(self, mode):
        if mode in ['b', 'bb', 'bbcode']:
            self.ext = '.bbcode'
            self.mode_str = 'BBCode'
            self.mode = Mode.BBCode
        elif mode in ['h', 'html']:
            return
        else:
            warn('Mode', mode, 'is not supported.')
            self.mode = Mode.BAD

    def __str__(self):
        return self.mode_str

def file_guard(filename):
    """
    Takes a filename and checks to see if it 
    is something we shouldn't be compiling.
    Returns true if we shouldn't compile,
    exits if the filename indicates an error.
    """
    if filename.endswith('.py') or filename.endswith('.sh') or filename.endswith(OUTPUT_EXT):
        print('Refusing to compile script file.')
        return True
    if filename in ['.git', '.vscode']:
        sys.exit('You are doing something very wrong, sir. [Filename was: ' + filename + ']')
    return False

def write(*args, **kwargs):
    print(*args, **kwargs)

def vwrite(config, *args, **kwargs):
    if 'v' in config and is_true(config['v']):
        write('(Info)', *args, **kwargs)

def warn(*args, **kwargs):
    write("Warning:") 
    write(*args, **kwargs)

def get_def(k, d, default):
    return d[k] if k in d else default

def is_true(v):
    # This is pretty mediocre at best, but that's okay.
    return (v==True or str(v).lower()=='true' or str(v).lower()=='t')

def get_f(k, d):
    return (k in d and is_true(d[k]))

def get_compiled(filename, config):
    if file_guard(filename):
        return None # We should not compile this!
    with open(filename, 'r') as file:
        d = file.read()
    mode = ModeInfo(config)
    if mode.mode == Mode.HTML:
        d = re.sub(r'\*\*\*([^\*]*)\*\*\*', r'<b><i>\1</i></b>', d)
        d = re.sub(r'\*\*([^\*]*)\*\*', r'<b>\1</b>', d)
        d = re.sub(r'\*([^\*]*)\*', r'<i>\1</i>', d)
        d = re.sub(r'(.+?)(\r|\n|$)+', r'<p>\1</p>\n\n', d)
    elif mode.mode == Mode.BBCode:
        d = re.sub(r'\*\*\*([^\*]*)\*\*\*', r'[b][i]\1[/i][/b]', d)
        d = re.sub(r'\*\*([^\*]*)\*\*', r'[b]\1[/b]', d)
        d = re.sub(r'\*([^\*]*)\*', r'[i]\1[/i]', d)
        d = re.sub(r'(.+?)(\r|\n|$)+', r'\1\n\n', d)
    else:
        pass
    return d

def get_file_as_json(filename):
    if not os.path.isfile(filename):
        return {}
    with open(filename, "r") as file:
        return json.load(file)
        
def write_file_as_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=2) 

def fh(filename):
    if not os.path.isfile(filename):
        return None
    with open(filename, 'r') as file:
        return hashlib.sha1(file.read().encode('utf-8')).hexdigest()

def should_compile(filename, config):
    hashresult = fh(filename)
    if hashresult is not None:
        # File exists
        status = get_file_as_json("status.json") 
        if filename in status:
            status = status[filename]
            if config['output'] in status:
                if status[config['output']] == hashresult:
                    return False
        return True
    else:
        print(filename, "does not exist.")
        ### todo - allow user to delete corresponding generated file
        ### something like if isfile(get_output_path(filename)) etc
        return False

def write_compiled(filename, contents, config):
    mode = ModeInfo(config)
    output_path = os.path.join(os.path.normpath(config['output']), filename + mode.ext)
    vwrite(config, "Compiling", filename, "in mode", mode, "to output filename:\n", output_path)
    with open(output_path, 'w') as file:
        file.write(contents)

def full_compile(filename, config):
    if not get_f("force", config) and not should_compile(filename, config):
        vwrite(config, "Decided not to compile the file:", filename)
        return False
    print("Compiling:", filename)
    new_contents = get_compiled(filename, config)
    if new_contents is None:
        print("Compilation failed for", filename)
        return False
    write_compiled(filename, new_contents, config)
    # Update the hash
    sj = get_file_as_json("status.json")
    if filename not in sj:
        sj[filename] = {}
    sj[filename][config['output']] = fh(filename)
    write_file_as_json("status.json", sj)
    return True

def html_files(config):
    glob_path = get_def("output", config, "") + "*.html"
    vwrite(config, "Globbing HTML files at:", glob_path)
    return [f for f in glob.glob(glob_path) if os.path.basename(f) not in IGNORED_FILES]

def md_files():
    return [f for f in glob.glob("*.md") if f not in IGNORED_FILES]

def sort_ch_num(d):
    return sorted(d, key=lambda x: int(x.strip("Chapter .md.gi.html")))

def dts(d):
    return ' '.join(d)

def BuildIndex(config):
    print('Building index:')
    index = [os.path.basename(x) for x in html_files(config)]
    print('> Found', len(index), 'html files.')
    index = sort_ch_num(index) 
    # Removes .md.gi.html line endings. Could cause issues if a filename
    # had one of the characters being stripped here at the end of the actual
    # name. Probably would be better to just do split('.')[0], really.
    index = [("<a href=\"" + x + "\">" + x.rstrip(".dgihtml") + "</a>") for x in index]
    print('> Created a', len(index), 'length index.')
    itext = '<p>' + '</p>\n<p>'.join(index) + '</p>'
    with open(get_def("index-template-path", config, "index.template"), "r") as ti:
        it = ti.read()
    it = it.replace("${ALL_FILES}", itext)
    output_path = get_def("index-path", config, "index.html")
    vwrite(config, 'Using template to create index at path:')
    vwrite(config, output_path)
    with open(output_path, "w") as inf:
        inf.write(it)

def main(filenames, config):
    if len(filenames) == 0:
        warn('No filenames provided for compilation.')
    else:
        print('Starting compilation of', len(filenames), 'file' + ('s' if
            len(filenames) > 1 else ''), 'to', ModeInfo(config).mode_str)
        nc = 0
        tot = len(filenames)
        for filename in filenames:
            nc += int(full_compile(filename, config))
        if nc > 0:
            print('Successfully compiled', nc, 'file' + ('s.' if
            nc > 1 else '.'))
        if tot > nc:
            print('Decided not to compile', tot - nc, 'file' + ('s.' if tot -
                nc > 1 else '.'))
    # Still build the index
    mode = ModeInfo(config)
    if mode.mode == Mode.HTML:
        BuildIndex(config)
        
def dmerge(a, b):
    for k in b:
        if k not in a:
            a[k] = b[k]
    return a

def validate(config):
    return config

def get_config(args):
    config = {'loaded': False}
    filenames = []
    debug = False
    toremove = []
    for arg in args:
        if re.match(r'--?v(erbose)?', arg) is not None:
            config['v'] = True
            toremove.append(arg)
            write("Enabled verbose mode.")
        elif re.match(r'--?h(elp)?', arg) is not None:
            print('Simple Markdown Compiler', 
                    '\n\tUsage: python3 compile.py [-f, -v] -c=<config file> <filename>...')
            toremove.append(arg)
        elif re.match(r'--?c(onfig)?=.+', arg) is not None:
            cfilename = re.match(r'-{0,2}c(onfig)?=(.+)', arg).group(2)
            with open(cfilename, 'r') as cfile:
                lconf = json.load(cfile)
            config = dmerge(config, lconf)
            config['loaded'] = True
            toremove.append(arg)
        elif arg in ['--debug']:
            print(json.dumps(config, indent=2))
            debug = True
            toremove.append(arg)
        elif re.match(r'--?f(orce)?', arg) is not None:
            config['force'] = True
            toremove.append(arg)

    for arg in toremove:
        args.remove(arg)

    if not config['loaded']:
        vwrite(config, "Attempting to load from default config file.")
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

    config = validate(config)

    filenames = args
    return [filenames, config]

if __name__ == '__main__':
    # Attempt to get configuration options
    args = sys.argv[1:]
    conf = get_config(args)
    main(conf[0], conf[1])

