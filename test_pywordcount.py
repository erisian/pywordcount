#! /usr/bin/python2.6
# -*- coding: utf-8 -*-
from pywordcount.pywordcount_core import *

class TestWordCount(object):

    def __init__(self):

        self.wc = PyWordCounter()

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
            ]), (44, 9, 2)),
            (u"\n".join([
                u"The quick brown “fox”",
                u"jumped over the lazy",
                u"dog"
            ]), (46, 9, 2)),
            (u"\n".join([
                u"The quick brown “fox”",
                u"didn’t jump over the lazy",
                u"dog"
            ]), (46, 10, 2)),
            (u"\n", (0, 0, 1)),
            (u"", (0, 0, 0)),
            (u"one two three five words\n", (24, 5, 1)),
            (u"one\two\three five words\n", (24, 5, 1)),
            (u"one/two/three five words\n", (24, 5, 1)),
            (u"one&two&three five words\n", (24, 5, 1)),
            (u"one\"two\"three five words\n", (24, 5, 1)),
            (u"one“two“three five words\n", (24, 5, 1)),
            (u"one“two”three five words\n", (24, 5, 1)),
            (u"one‘two‘three five words\n", (24, 5, 1)),
            (u"one–two–three five words\n", (24, 5, 1)),
            (u"one—two—three five words\n", (24, 5, 1)),
            (u"one\xa0two\xa0three five words\n", (24, 5, 1)),
            (u"one>two>three five words\n", (24, 5, 1)),
            (u"one<two<three five words\n", (24, 5, 1)),
            (u"one+two+three five words\n", (24, 5, 1)),
            (u"one=two=three five words\n", (24, 5, 1)),
            (u"one(two)three five words\n", (24, 5, 1)),
            (u"one (two) three five words\n", (26, 5, 1)),
            (u"one ( two ) three five words\n", (28, 5, 1)),
            (u"one[two]three five words\n", (24, 5, 1)),
            (u"one [two] three five words\n", (26, 5, 1)),
            (u"one [ two ] three five words\n", (28, 5, 1)),
            (u"one\{two\}three five words\n", (24, 5, 1)),
            (u"one \{two\} three five words\n", (26, 5, 1)),
            (u"one { two } three five words\n", (28, 5, 1)),
            (u"one|two|three five words\n", (24, 5, 1)),
            (u"one |two| three five words\n", (26, 5, 1)),
            (u"one | two | three five words\n", (28, 5, 1)),
            (u"one--two--three five words\n", (24, 5, 1)),
            (u"one...two..three five words\n", (24, 5, 1)),
            (u"one: two three five words\n", (24, 5, 1)),
            (u"one;two three five words\n", (24, 5, 1)),
            (u"one two three five (words).\n", (24, 5, 1)),
            (u"one two . . .     . three five (words).\n", (24, 5, 1)),
        ]

        for text, cwl in cases:
            counts = self.wc.count_text(text)
            assert (counts[1], counts[2]) == (cwl[1], cwl[2])
