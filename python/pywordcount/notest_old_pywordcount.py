#! /usr/bin/python2.6
# -*- coding: utf-8 -*-
from pywordcount.old_pywordcount import *
from mockvim import *
class TestWordCount(object):

    def __init__(self):

        self.wc = WordCounter()

    def test_count_words(self):
        oneline_cases = [
            ("This should be five words.", 5),
            ("This shouldn't be six words.", 5),
            (u"This should be—five words", 5),
            (u"This should be\u2014five words", 5),
            (u"This should be--five words", 5),
            (u"Six–four Federer means six words.", 6)
        ]

        for text, wordcount in oneline_cases:
            assert self.wc.count_words(text)[0] == wordcount

        single_char_separators = (
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
        )

        for char in single_char_separators:
            text = "one%stwo" % char
            assert self.wc.count_words(text)[0] == 2

        ignore_list = (
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

        for char in ignore_list:
            text = "one%sone" % char
            assert self.wc.count_words(text)[0] == 1

        repeaters = (
        #These are only separators if they're present consecutively, e.g. -- or ..
            "-",
            "."
        )

        for char in repeaters:
            nonrepeat = "one%sone" % char
            repeat = "one%stwo" % (char * 2)
            assert self.wc.count_words(nonrepeat)[0] == 1
            assert self.wc.count_words(repeat)[0] == 2

        line_endings = (
            "\r",
            "\n"
        )

        for char in line_endings:
            text = "one%stwo" % char
            assert self.wc.count_words(text)[0] == 2

    def test_word_count(self):
        cases = [
            (u"\n".join([
                "The quick brown fox",
                "jumped over the lazy",
                "dog"
            ]), (44, 9, 3)),
            (u"\n".join([
                u"The quick brown “fox”",
                u"jumped over the lazy",
                u"dog"
            ]), (46, 9, 3)),
            (u"\n".join([
                u"The quick brown “fox”",
                u"didn’t jump over the lazy",
                u"dog"
            ]), (46, 10, 3)),
            (u"\n", (0, 0, 2)),
            (u"", (0, 0, 0)),
            (u"one two three five words", (24, 5, 1)),
            (u"one\two\three five words", (24, 5, 1)),
            (u"one/two/three five words", (24, 5, 1)),
            (u"one&two&three five words", (24, 5, 1)),
            (u"one\"two\"three five words", (24, 5, 1)),
            (u"one“two“three five words", (24, 5, 1)),
            (u"one“two”three five words", (24, 5, 1)),
            (u"one‘two‘three five words", (24, 5, 1)),
            (u"one–two–three five words", (24, 5, 1)),
            (u"one—two—three five words", (24, 5, 1)),
            (u"one\xa0two\xa0three five words", (24, 5, 1)),
            (u"one>two>three five words", (24, 5, 1)),
            (u"one<two<three five words", (24, 5, 1)),
            (u"one+two+three five words", (24, 5, 1)),
            (u"one=two=three five words", (24, 5, 1)),
            (u"one(two)three five words", (24, 5, 1)),
            (u"one (two) three five words", (26, 5, 1)),
            (u"one ( two ) three five words", (28, 5, 1)),
            (u"one[two]three five words", (24, 5, 1)),
            (u"one [two] three five words", (26, 5, 1)),
            (u"one [ two ] three five words", (28, 5, 1)),
            (u"one\{two\}three five words", (24, 5, 1)),
            (u"one \{two\} three five words", (26, 5, 1)),
            (u"one { two } three five words", (28, 5, 1)),
            (u"one|two|three five words", (24, 5, 1)),
            (u"one |two| three five words", (26, 5, 1)),
            (u"one | two | three five words", (28, 5, 1)),
            (u"one--two--three five words", (24, 5, 1)),
            (u"one...two..three five words", (24, 5, 1)),
            (u"one: two three five words", (24, 5, 1)),
            (u"one;two three five words", (24, 5, 1)),
        ]

        for text, cwl in cases:
            self.wc.text = text
            self.wc.word_count()
            assert (cwl[0], self.wc.wordcount, self.wc.linecount) == cwl

    def test_vim_get_modes(self):
        modes = [
            ("",[]),
            ("rest", ["rest"]),
            ("rest.html", ["rest", "html"])
        ]

        for rawmode, mode in modes:
            self.wc.vim = MockVim()
            #self.wc.vim.rawmodes = rawmode
            self.wc.vim.eval_list["&ft"] = lambda: rawmode
            self.wc.vim_get_modes()
            assert self.wc.modes == mode

    def test_handle_modes(self):
        modes = [
            ([], [self.wc.word_count]),
            (["rest"], [self.wc.adjust_for_rest, self.wc.word_count]),
            (["rest", "mpage"],
                [self.wc.adjust_for_morning_pages,
                    self.wc.adjust_for_rest, self.wc.word_count]),
            (["mpage"], [self.wc.adjust_for_morning_pages,
                    self.wc.adjust_for_rest, self.wc.word_count]),
        ]

        for mode, processes in modes:
            self.wc.modes = mode
            self.wc.handle_modes()
            assert self.wc.processes == processes

    def test_vim(self):
        #set up a mock object
        #give the mock object a buffer
        #give the mock object rawmodes values
        #check that the char, word, and line counts are correct.

        cases = [
            (
                u"\n".join([
                    "The quick brown fox",
                    "jumped over the lazy",
                    "dog"
                ]),
                "",
                (44, 9, 3),
            ),
            (
                u"\n".join([
                    u"The quick brown “fox”",
                    u"jumped over the lazy",
                    u"dog"
                ]),
                "rest",
                (46, 9, 3),
            ),
            (
                u"\n".join([
                    u"The quick brown “fox”",
                    u".. jumped over the lazy",
                    u"dog"
                ]),
                "rest",
                (49, 5, 2),
            ),
            (
                u"\n".join([
                    u"|Incinerate|\ s |Hypnotic Specter|\ —|Hypnotic Specter|\ s",
                    u".. jumped over the lazy",
                    u"dog"
                ]),
                "rest",
                (86, 6, 2),
            ),
            (
                u"\n".join([
                    u"|Incinerate|\ s |Hypnotic Specter|\ —|Hypnotic Specter|\ s",
                    u".. jumped over the lazy",
                    u"dog"
                ]),
                "rest",
                (86, 6, 2),
            ),
        ]

        for text, mode, cwl in cases:
            self.wc.vim = MockVim()
            self.wc.vim.current.buffer = [
                line.encode("utf-8") for line in text.split("\n")
            ]
            self.wc.vim.eval_list["&ft"] = lambda: mode
            self.wc.vim_main(self.wc.vim)
            assert (
                self.wc.charcount, self.wc.wordcount, self.wc.linecount) == cwl

    def test_vim_fast(self):
        def mock_cmd(myvim, cmd):
            if cmd.startswith("let"):
                #myvim.varlist.update(dict([cmd[4:].split(u" = ")]))
                var, val = cmd[4:].split(u" = ")
                myvim.varlist[var] = val
            myvim.commands.append(cmd)
        def mock_eval(myvim, cmd):
            if cmd.startswith("b:"):
                return myvim.varlist.get(cmd, "")

            return myvim.eval_list.get(cmd, lambda: "")()

        self.wc.vim = MockVim()
        self.wc.vim.eval = lambda c: mock_eval(self.wc.vim, c)
        self.wc.vim.command = lambda c: mock_cmd(self.wc.vim, c)
        self.wc.vim.varlist = {}
        self.wc.vim.current.buffer = [
            u"the quick brown fox".encode("utf-8"),
            u"jumped over the lazy".encode("utf-8"),
            u".. dog".encode("utf-8"),
            u".. dog".encode("utf-8"),
            u".. dog".encode("utf-8"),
            u".. dog".encode("utf-8"),
        ]
        self.wc.vim.current.range = EmptyObject()
        self.wc.vim.current.range.start = 1
        #self.wc.vim.rawmodes = "rest"
        self.wc.vim.eval_list["&ft"] = lambda: "rest"
        self.wc.vim.eval_list["exists('b:TotalDirty')"] = lambda: 0

        assert self.wc.vim_fast(self.wc.vim) == 8

"""
TODO: test handle_urls and test end-to-end
            (u"one...two http://test.com/ five words", (24, 5, 1)),
            (u"one...two tadhg@tadhg.com five words", (24, 5, 1)),
            (u"one...two <http://test.com/> five words", (24, 5, 1)),
            (u"one...two “http://test.com/” five words", (24, 5, 1)),
"""
