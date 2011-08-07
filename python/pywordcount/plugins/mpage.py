#! /usr/bin/python
# -*- coding: utf-8 -*-

def pywordcountplugin(text):
    """
    Try to make this work by having the only "buffer" that vim_fast deals
    with be the lines between .. container:: main and either the
    affirmations or metadata lines.
    """
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
        text = u"\n".join(newlines)

    return text
