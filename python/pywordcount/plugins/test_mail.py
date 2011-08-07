#! /usr/bin/python
# -*- coding: utf-8 -*-

import mail

def test_adjust_for_mail():
    cases = [
        (
            u"\n".join([
                u"Subject: one",
                u"To: two",
                u"From: three"
            ]),
            u""
        ),
        (
            u"\n".join([
                u"Subject: one",
                u"From: main",
                u"three",
            ]),
            u"three"
        ),
        (
            u"\n".join([
                u"Subject: one",
                u"From: main",
                u"three",
                u"four",
            ]),
            u"three\nfour"
        ),
        (
            u"\n".join([
                u"Subject: one",
                u"From: main",
                u"three",
                u"four",
                u".. whatever",
                u"five",
                u"> container:: affirmations",
                u">six",
            ]),
            u"three\nfour\n.. whatever\nfive"
        ),
        (
            u"\n".join([
                u"Subject: one",
                u"From: main",
                u"three",
                u"four",
                u".. whatever",
                u"five",
                u"> container:: affirmations",
                u">six",
                u"",
                u"Furthermore: ",

            ]),
            u"\n".join([
                u"three",
                u"four",
                u".. whatever",
                u"five",
                u"",
                u"Furthermore: ",
            ]),
        ),
    ]

    for inp, outp in cases:
        assert mail.pywordcountplugin(inp) == outp
