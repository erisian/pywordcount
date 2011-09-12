"""
Vim plugin for configurable live word count.
"""
import re
import os
import pywordcount_core as pywordcount

class VimWordCounter(object):

    def __init__(self, vim, base_dir=None):

        base_dir = base_dir or os.path.dirname(__file__)
        self.vim = vim
        self.wc = pywordcount.PyWordCounter()
        self.wc.handle_config(base_dir)
        self.fast = False

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

        self.vim_get_filetypes()
        self.fast = True
        buff, cmd = self.vim.current.buffer, self.vim.command
        current_line_num = self.vim.current.range.start

        def uc(text): return unicode(text, "utf-8")

        def ev(var): return int(self.vim.eval(var))

        def get_count(text):
            self.handle_filetypes()
            return self.wc.count_text(text)[1]

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

    def vim_get_filetypes(self):
        self.filetypes = [ft for ft in self.vim.eval("&ft").split(".") if ft]

    def handle_filetypes(self):
        """
        Sets the WordCounter processes to match those specified in the config
        for the current Vim filetype(s).
        """
        preprocs = []
        for ft in set(self.filetypes).intersection(self.wc.filetypes.keys()):
            for process in self.wc.filetypes[ft]:
                if process not in preprocs:
                    preprocs.append(process)
        self.wc.processes = preprocs
