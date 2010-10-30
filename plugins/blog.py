#! /usr/bin/python
# -*- coding: utf-8 -*-

def pywordcountplugin(text):
    """
    We want to start on the third line, and end at ..container:: date.
    """
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
        text = u"\n".join(newlines)
    return text
