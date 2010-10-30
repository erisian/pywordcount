#! /usr/bin/python
# -*- coding: utf-8 -*-

import blog

def test_adjust_for_blog():
    cases = [
        (
            u"\n".join([
                u"one",
                u"two",
                u"three"
            ]),
            u"three"
        ),
        (
            u"\n".join([
                u"TITLE",
                u"-----",
                u"three"
            ]),
            u"three"
        ),
        (
            u"\n".join([
                u"TITLE",
                u"-----",
                u"three",
                u"four",
            ]),
            u"three\nfour"
        ),
        (
            u"\n".join([
                u"TITLE",
                u"-----",
                u"three",
                u"four",
                u".. whatever",
                u"five",
                u".. container:: date",
                u"six",
            ]),
            u"three\nfour\n.. whatever\nfive"
        ),
    ]

    for inp, outp in cases:
        assert blog.pywordcountplugin(inp) == outp
