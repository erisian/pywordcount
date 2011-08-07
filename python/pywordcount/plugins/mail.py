#! /usr/bin/python
# -*- coding: utf-8 -*-
import re
import itertools

def pywordcountplugin(text):
    return adjust_for_mail(text)

def adjust_for_mail(text):
    """
        Go through each of the special cases for email.
    """
    rest_cases = [
        remove_headers,
        remove_quoted,
    ]

    for case in rest_cases:
        text = case(text)

    return text

def remove_headers(text):
    """
    Remove any lines from the start of the file that look like header lines,
    until any non-header line is reached (as headers should only be at the
    start).
    """
    lines = text.split("\n")
    header = re.compile(r"^[^:]+: ")
    return u"\n".join([l for l in itertools.dropwhile(header.match, lines)])

def remove_quoted(text):
    """
    Remove any lines with > at the start of them.
    """
    lines = text.split("\n")
    quote = re.compile(r"^>")
    return u"\n".join([l for l in lines if not quote.match(l)])
