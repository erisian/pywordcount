#! /usr/bin/python
# -*- coding: utf-8 -*-

import uris

def test_adjust_for_uris():
    cases = [
        (
            u"\n".join([
                u"http://tadhg.com/wp/ ",
                u"two",
                u"three"
            ]),
            u"url \ntwo\nthree"
        ),
    ]

    for inp, outp in cases:
        assert uris.pywordcountplugin(inp) == outp
