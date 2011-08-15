#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Script for word count.
TODO: check for mode (filetype) and adjust file accordingly.
TODO: strip dates and other strings consisting only of numerals and /
"""
import re
import sys
import os
import codecs

class PyWordCounter(object):

    LINE_SEPS = (
        "\r",
        "\n"
    )

    WORD_SEPS = (
        " ",        # space
        "\n",       # linebreak
        "\t",       # tab
        "/",        # slash
        "&",        # ampersand
        '"',        # double quotation mark, straight
        u"\u201C",  # double quotation mark, left
        u"\u201D",  # double quotation mark, right
        u"\u2018",  # single quotation mark, left
        u"\u2013",  # en dash
        u"\u2014",  # em dash
        u"\xa0",  # non-breaking space
        ">",        # greater than symbol
        "<",        # less than symbol
        "+",        # plus
        "=",        # equals
        "(",        # left parenthesis
        ")",        # right parenthesis
        "[",        # left bracket
        "]",        # right bracket
        "{",        # left curly bracket
        "}",        # right curly bracket
        "|",        # bar
        ":",        # colon; URL handling normally makes this irrelevant
        ";",        # semicolon
        #Multichar separators:
        "--",
        "--",
        "..",
        "...",
    )

    IGNORE = (
    #Not separators per se, but should not be treated as word content
        "'",        # single quotation mark, straight
        u"\u2019",  # single quotation mark, right
        "-",        # hyphen
        "#",        # hash mark
        ".",        # period
        "_",        # underscore
        "`",        # backtick
        "\\",        # backslash
    )

    def __init__(self):
        self.processes = []

    def cli_main(self):
        """
        TODO: count more than one file.
        """
        base_dir = os.path.realpath(os.path.dirname(__file__))
        self.handle_config(base_dir)
        self.handle_command_line(sys.argv)
        output = self.count_input()
        print u"\n".join(output)

    def handle_config(self, base_dir):
        """
        Here we want to:

        + Read the config file and parse it.
        + Set the list of modes where we want to run WordCount().
        + Load any modules necessary for supporting the modes.
        + Set what gets run in what order for each mode.

        """
        import ConfigParser
        plugindir = "%s/plugins/" % base_dir
        sys.path.insert(0, plugindir)
        cp = ConfigParser.ConfigParser()
        cp.read("%s/config.ini" % base_dir)

        #Parse the config data so that we end up with a list of processes for
        #each filetype, or None for those filetypes without specified processes
        types = [ft.strip() for ft in cp.get("filetypes", "types").split(",")]
        procs = dict([(t, None) for t in types] + cp.items("preprocesses"))
        def tolist(v): return v and [i.strip() for i in v.split(",")] or v
        procs = dict([(k, tolist(procs[k])) for k in procs])

        #Get a unique list of the processes and import them
        try:
            from sets import Set
            set = Set
        except ImportError:
            pass
        proc_funcs = {}
        for proc in set(sum([v for v in procs.values() if v], [])):
            proc_funcs[proc] = __import__(
                proc, globals(), locals(),
                ["pywordcountplugin"]).pywordcountplugin

        #Replace the string names with the actual functions:
        for ft in procs:
            procs[ft] = procs[ft] and [proc_funcs[p] for p in procs[ft]] or []

        self.filetypes = procs

    def handle_command_line(self, args):
        parser = self.setup_cli_parser()
        options = self.cli_options(args, parser)
        self.handle_filetypes(options.get("type", []))
        self.handle_input(options.get("file", []))

    def setup_cli_parser(self):
        """
        Sets up the parser for handling command line options.
        """
        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option(
            "-f",
            "--file",
            dest="file",
            help="read from FILE",
            metavar="FILE",
            action="store",
        )
        parser.add_option(
            "-t",
            "--type",
            dest="type",
            help="set TYPE",
            metavar="TYPE"
        )
        return parser

    def cli_options(self, args, parser):
        options, args = parser.parse_args(args)
        opts = dict(vars(options))
        #Split types by comma:
        if opts.get("type", False):
            opts["type"] = [i.strip() for i in opts["type"].split(",")]
        #Treat unparsed args as filenames:
        if opts.get("file", False):
            opts["file"] = [opts["file"]]
            if len(args) > 1:
                opts["file"] += args[1:]

        #have to eliminate the empty keys
        #See http://www.siafoo.net/article/52#dictionary-comprehensions
        #return dict([k, v] for k, v in opts.iteritems() if v != None)
        #The above doesn't work in Python 2.3, so:

        clean_opts = {}
        for k, v in opts.iteritems():
            if v != None:
                clean_opts[k] = v
        return clean_opts

    def handle_filetypes(self, filetypes):
        for filetype in filetypes:
            if filetype not in self.filetypes:
                print "%s is an unsupported filetype." % filetype
                raise Exception
            for proc in self.filetypes.get(filetype, []):
                if proc not in self.processes:
                    self.processes.append(proc)

    def handle_input(self, files):
        if not files:
            self.files = [sys.stdin.read()]
            return

        def read(f): return codecs.open(f, mode="r",encoding="utf-8").read()
        self.files = [read(f) for f in files]

    def count_text(self, text):
        chars = len(text)
        for process in self.processes:
            text = process(text)
        words, lines = self.count_words(text)
        return (chars, words, lines)

    def count_input(self):
        return ["c: %s w: %s l: %s" % self.count_text(f) for f in self.files]

    def count_words(self, text):

        def ors(l): return r"|".join([re.escape(c) for c in l])
        def retext(text, chars, sub):
            return re.compile(ors(chars)).sub(sub, text)

        lns = text and len(re.compile(ors(self.LINE_SEPS)).findall(text)) or 0

        text = retext(text, self.WORD_SEPS + self.LINE_SEPS, u" ").strip()
        text = retext(text.strip(), self.IGNORE, u"").strip()
        words = text.strip() and len(re.compile(r"[ ]+").split(text)) or 0

        return (words, lns)

if __name__ == "__main__":
    wc = PyWordCounter()
    wc.cli_main()
