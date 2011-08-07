#! /usr/bin/python
# -*- coding: utf-8 -*-
import re

def pywordcountplugin(text):
    return adjust_for_rest(text)

def remove_directives(text):
    textlines = text.split("\n")
    newlines = []
    comment = re.compile(r"[ ]*\.\. [a-zA-Z0-9_\|]")
    argument = re.compile(r"    :[^\:]*:")
    for line in textlines:
        if not comment.match(line) and not argument.match(line):
            newlines.append(line)
    return u"\n".join(newlines)

def adjust_for_rest(text):
    """
        Go through each of the special cases for reST.
    """
    rest_cases = [
        remove_directives,
        rest_adjust_pipe_space,
    ]

    for case in rest_cases:
        text = case(text)

    return text

def rest_adjust_pipe_space(text):
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
