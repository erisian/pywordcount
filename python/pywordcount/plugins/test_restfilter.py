#! /usr/bin/python
# -*- coding: utf-8 -*-

import mpage

def test_adjust_for_morning_pages():
    cases = [
        (
            u"\n".join([
                u"one",
                u"two",
                u"three"
            ]),
            u""
        ),
        (
            u"\n".join([
                u"one",
                u".. container:: main",
                u"three"
            ]),
            u"three"
        ),
        (
            u"\n".join([
                u"one",
                u".. container:: main",
                u"three",
                u"four",
            ]),
            u"three\nfour"
        ),
        (
            u"\n".join([
                u"one",
                u".. container:: main",
                u"three",
                u"four",
                u".. whatever",
                u"five",
                u".. container:: affirmations",
                u"six",
            ]),
            u"three\nfour\n.. whatever\nfive"
        ),
    ]

    for inp, outp in cases:
        assert mpage.pywordcountplugin(inp) == outp
