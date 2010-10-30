#! /usr/bin/python2.6
# -*- coding: utf-8 -*-

"""
Sript for word count.
TODO: check for mode (filetype) and adjust file accordingly.
"""
import re

class WordCounter(object):

    LINE_SEPS = (
        "\r",
        "\n"
    )

    WORD_SEPS = (
        " ",        # space
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

    VALID_FILETYPES = (
        #The filetypes I actually want word count in
        "rest",
        "mpage",
        "blog",
    )
    def __init__(self):
        self.fast = False
        self.setup_processes()

    def vim_init(self, vim, base_dir):
        """
        Here we want to:

        + Read the config file and parse it.
        + Set the list of modes where we want to run WordCount().
        + Load any modules necessary for supporting the modes.
        + Set what gets run in what order for each mode.

        """
        import sys
        import ConfigParser

        self.vim = vim
        self.base_dir = base_dir

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

        self.VALID_FILETYPES = procs

    def setup_processes(self):
        self.processes = [
        ]

    def vim_main(self, vim, statusline=None):
        """"
        The primary starting point for the script when run from Vim.
        """
        self.vim = vim
        ulines = [unicode(line, "utf-8") for line in vim.current.buffer]
        self.text = u"\n".join(ulines)
        self.charcount = len(self.text)
        self.vim_get_modes()
        self.handle_modes()
        if statusline:
            self.processes.append(self.vim_statusline_output)
        else:
            self.processes.append(self.print_output)
        self.run_processes()
        self.word_count()
        self.vim.command("let b:TotalWordCount = %s" % self.wordcount)
        self.vim.command("let b:TotalDirty = 1")

    def vim_fast(self, forcerecount=False):
        """
            Use Vim variables to store the count for lines other than the
            current line, so that only the current line needs to be recounted
            every time.
            Uses the variables:

            * b:TotalWordCount for the total.
            * b:CurrentLineNumber
            * b:OtherLineWordCount for the total words on other lines
            * b:TotalLines to track the number of lines in the buffer

            If b:TotalWordCount doesn't exist, counts the whole buffer and sets
            the rest of the variables.
            If it does exist, checks for line changes.
            If there's no line change, counts the current line and adds that
            total to b:OtherLineWordCount to set the new number for
            b:TotalWordCount.
            If there has been a line change, checks whether or not the buffer's
            total lines has remained the same, increased by one, or has changed
            in some other way.
            If it's remained the same or increased by one, removes the total of
            the previous line from the total and adds the total of the current
            line.
            If it's changed by more than that, recounts the whole buffer.

            TODO: display wc of range when range is selected
        """

        self.vim_get_modes()
        self.fast = True
        buff, cmd = self.vim.current.buffer, self.vim.command
        current_line_num = self.vim.current.range.start

        def uc(text): return unicode(text, "utf-8")

        def ev(var): return int(self.vim.eval(var))

        def get_count(text):
            self.text = text
            self.handle_modes()
            self.run_processes()
            self.word_count()
            return self.wordcount

        def count_all():
            #count all the lines in the buffer
            ulines = [uc(line) for line in buff[:]]
            total_lines = len(ulines)
            current_line = ulines.pop(current_line_num)
            current_line_count = get_count(current_line)
            otherline_count = get_count(u"\n".join(ulines))
            total = otherline_count + current_line_count
            return (total, otherline_count, total_lines)

        def set_all(total, current_line_num, otherline_count, total_lines):
            #set the Vim buffer variables
            buffer_variables = [
                ("TotalWordCount", total),
                ("CurrentLineNumber", current_line_num),
                ("OtherLineWordCount", otherline_count),
                ("TotalLines", total_lines),
                ("TotalDirty", 0)
            ]
            for b, v in buffer_variables:
                cmd("let b:%s = %s" % (b, v))

        def get_total():
            prev_line_num = ev("b:CurrentLineNumber")
            prev_total_lines = ev("b:TotalLines")
            otherline_count = ev("b:OtherLineWordCount")
            total_lines = len(self.vim.current.buffer)
            current_line_count = get_count(uc(self.vim.current.line))

            on_same_line = current_line_num == prev_line_num
            same_total_lines = total_lines == prev_total_lines

            if on_same_line and same_total_lines:
                total = otherline_count + current_line_count
                cmd("let b:TotalWordCount = %s" % total)
                return total

            #If we're not on the same line and/or total lines have changed,
            #try to figure out what's happened:
            on_next_line = current_line_num == prev_line_num + 1
            one_more_line = total_lines == prev_total_lines + 1
            pasted_one_line = one_more_line and (on_same_line or on_next_line)

            if not same_total_lines and not pasted_one_line:
            #We don't have a good guess for what the change was, so count all:
                total, otherline_count, total_lines = count_all()
                set_all(total, current_line_num, otherline_count, total_lines)
                return total

            prev_line_count = get_count(uc(buff[prev_line_num]))
            #Subtract the current line if we've moved lines, and don't if a
            #line was inserted:
            current_line_sub = same_total_lines and current_line_count or 0
            otherline_count += (prev_line_count - current_line_sub)

            total = otherline_count + current_line_count
            set_all(total, current_line_num, otherline_count, total_lines)
            return total


        """
        If this is called with forcerecount as true at some point, to push it
        to recount in case something's gone wrong, the flow is as follows:

        + vim_fast() with forcerecount is called
        + Since that can only happen manually, vim counts it as a user action,
          which means that WordCount() is called from the statusline (since
          something might have changed), so vim_fast() without forcerecount is
          called immediately following.
        + "TotalDirty" really means "the total was just recounted the slow and
          accurate way". The logic below avoids running any counting functions
          if ``b:TotalDirty`` is 1 and instead returns ``b:TotalWordCount``.

        """
        if bool(ev("exists('b:TotalDirty')")) and bool(ev("b:TotalDirty")):
            cmd("let b:TotalDirty = 0")
            return ev("b:TotalWordCount")

        if bool(ev("exists('b:TotalWordCount')")) and not forcerecount:
            #Do it the quick way if possible:
            total = get_total()
        else:
            total, otherline_count, total_lines = count_all()
            set_all(total, current_line_num, otherline_count, total_lines)
            if forcerecount:
                cmd("let b:TotalDirty = 1")
                print "w: %s l: %s" % (total, total_lines)
        #TODO: insert conditional to handle case where count < 0
        return total

    def vim_get_modes(self):
        self.modes = [mode for mode in self.vim.eval("&ft").split(".") if mode]

    def cli_main(self):
        """
        The primary starting point for the script when run from the command
        line.
        The only argument we're expecting from the command line is the name of
        the file to be counted.
        TODO: count more than one file.
        """

        import sys
        self.handle_command_line(sys.argv[1])
        self.handle_modes()
        self.processes.append(self.print_output)
        self.run_processes()
        self.word_count()

    def handle_command_line(filename):
        import codecs
        f = codecs.open(
            filename,
            mode="r",
            encoding="utf-8"
        )
        self.text = f.read()
        self.charcount = len(self.text)

    def handle_modes(self):
        """
        from sets import Set
        set = Set
        if self.fast:
            modes = {
                "rest": [self.adjust_for_rest],
                "mpage": [self.adjust_for_morning_pages, self.adjust_for_rest],
                "blog": [self.adjust_for_blog, self.adjust_for_rest]
            }
        else:
            modes = {
                "rest": [self.adjust_for_rest],
                "mpage": [self.adjust_for_morning_pages, self.adjust_for_rest],
                "blog": [self.adjust_for_blog, self.adjust_for_rest]
            }
        preprocs = []
        for mode in set(self.modes).intersection(modes.keys()):
            for process in modes[mode]:
                if process not in self.processes and process not in preprocs:
                    preprocs.append(process)
        """
        try:
            from sets import Set
            set = Set
        except ImportError:
            pass
        preprocs = []
        for mode in set(self.modes).intersection(self.VALID_FILETYPES):
            for process in self.VALID_FILETYPES[mode]:
                #if process not in self.processes and process not in preprocs:
                if process not in preprocs:
                    preprocs.append(process)

        #self.processes = preprocs + self.processes
        self.processes = preprocs

    def run_processes(self):
        for process in self.processes:
            self.text = process(self.text)

    def word_count(self):
        self.wordcount, self.linecount = self.count_words(self.text)

    def adjust_for_morning_pages(self):
        """
        Try to make this work by having the only "buffer" that vim_fast deals
        with be the lines between .. container:: main and either the
        affirmations or metadata lines.
        """
        text = self.text

        nothing_above = [".. container:: main"]
        nothing_below = [
            ".. container:: affirmations",
            ".. container:: metadata",
        ]

        lines = text.split(u"\n")
        if len(lines) > 1:
            newlines, include = [], False
            for line in lines:
                for start in nothing_below:
                    if line == start:
                        include = False
                if include:
                    newlines.append(line)
                for start in nothing_above:
                    if line == start:
                        include = True
            self.text = u"\n".join(newlines)

    def adjust_for_blog(self):
        """
        We want to start on the third line, and end at ..container:: date.
        """
        text = self.text
        nothing_below = u".. container:: date"
        lines = text.split(u"\n")
        if len(lines) > 2:
            lines = lines[2:]
        if len(lines):
            newlines, include = [], True
            for line in lines:
                if line == nothing_below:
                    include = False
                if include:
                    newlines.append(line)
            self.text = u"\n".join(newlines)

    def remove_directives(self, text):
        textlines = text.split("\n")
        newlines = []
        comment = re.compile(r"[ ]*\.\. [a-zA-Z0-9_\|]")
        argument = re.compile(r"    :[^\:]*:")
        for line in textlines:
            if not comment.match(line) and not argument.match(line):
                newlines.append(line)
        return u"\n".join(newlines)

    def adjust_for_rest(self):
        """
            Go through each of the special cases for reST.
        """
        rest_cases = [
            self.remove_directives,
            self.rest_adjust_pipe_space,
            self.handle_urls,
        ]

        for case in rest_cases:
            self.text = case(self.text)

    def rest_adjust_pipe_space(self, text):
        """
            Special-case "|\ " to make sure e.g. "|Hypnotic Specter|\ s"
            doesn't get counted as three words.

            |Incinerate|\ s |Hypnotic Specter|\ —|Hypnotic Specter|\ s
            The above line should be counted as five words.
        """
        spacere = re.compile(r"\|\\ ([^ ]{1})")
        finds = spacere.findall(text)
        text = spacere.sub("\g<1>", text)
        return text

    def handle_urls(self, text):
        """
        replace URLs; regexes copied from Docutils (parsers/rst/states.py)
        """
        openers = u'\'"([{<\u2018\u201c\xab\u00a1\u00bf' # see quoted_start below
        closers = u'\'")]}>\u2019\u201d\xbb!?'
        unicode_delimiters = u'\u2010\u2011\u2012\u2013\u2014\u00a0'
        start_string_prefix = (u'((?<=^)|(?<=[-/: \\n\u2019%s%s]))'
                               % (re.escape(unicode_delimiters),
                                  re.escape(openers)))
        end_string_suffix = (r'((?=$)|(?=[-/:.,; \n\x00%s%s]))'
                             % (re.escape(unicode_delimiters),
                                re.escape(closers)))
        # Valid URI characters (see RFC 2396 & RFC 2732);
        # final \x00 allows backslash escapes in URIs:
        uric = r"""[-_.!~*'()[\];/:@&=+$,%a-zA-Z0-9\x00]"""
        # Delimiter indicating the end of a URI (not part of the URI):
        uri_end_delim = r"""[>]"""
        # Last URI character; same as uric but no punctuation:
        urilast = r"""[_~*/=+a-zA-Z0-9]"""
        # End of a URI (either 'urilast' or 'uric followed by a
        # uri_end_delim'):
        uri_end = r"""(?:%(urilast)s|%(uric)s(?=%(uri_end_delim)s))""" % locals()
        emailc = r"""[-_!~*'{|}/#?^`&=+$%a-zA-Z0-9\x00]"""
        email_pattern = r"""
              %(emailc)s+(?:\.%(emailc)s+)*   # name
              (?<!\x00)@                      # at
              %(emailc)s+(?:\.%(emailc)s*)*   # host
              %(uri_end)s                     # final URI char
              """
        email=re.compile(email_pattern % locals() + '$', re.VERBOSE),
        uri=re.compile(
            (r"""
            %(start_string_prefix)s
            (?P<whole>
              (?P<absolute>           # absolute URI
                (?P<scheme>             # scheme (http, ftp, mailto)
                  [a-zA-Z][a-zA-Z0-9.+-]*
                )
                :
                (
                  (                       # either:
                    (//?)?                  # hierarchical URI
                    %(uric)s*               # URI characters
                    %(uri_end)s             # final URI char
                  )
                  (                       # optional query
                    \?%(uric)s*
                    %(uri_end)s
                  )?
                  (                       # optional fragment
                    \#%(uric)s*
                    %(uri_end)s
                  )?
                )
              )
            |                       # *OR*
              (?P<email>              # email address
                """ + email_pattern + r"""
              )
            )
            %(end_string_suffix)s
            """) % locals(), re.VERBOSE)
        return uri.sub("url", text)

    def count_words(self, text):

        def ors(l): return r"|".join([re.escape(c) for c in l])
        def retext(text, chars, sub):
            return re.compile(ors(chars)).sub(sub, text)

        lines = text and len(re.compile(ors(self.LINE_SEPS)).split(text)) or 0

        text = retext(text, self.WORD_SEPS + self.LINE_SEPS, u" ")
        text = retext(text.strip(), self.IGNORE, u"")
        words = text and len(re.compile(r"[ ]+").split(text)) or 0

        return (words, lines)

    def print_output(self, *args):
        print "chars: %s, words: %s, lines: %s" % (
            self.charcount, self.wordcount, self.linecount)
        self.cwl = (self.charcount, self.wordcount, self.linecount)

    def vim_statusline_output(self):
        #return self.wordcount
        self.vim.command("let b:Word_Count = %s" % self.wordcount)

