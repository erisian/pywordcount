#! /usr/bin/python
# -*- coding: utf-8 -*-
import re
def pywordcountplugin(text):
    """
    replace URLs; regexes copied from Docutils (parsers/rst/states.py)
    """
    date=re.compile(
        r"""([0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4})
        |
        ([0-9]{4}\-[0-9]{2}\-[0-9]{1,2})
        |
        ([0-9]{1,2}\/[0-9]{1,2}\/[0-9]{2})
        |
        ([0-9]{1,2}\/[0-9]{1,2})
        """, re.VERBOSE
    )
    return date.sub("date", text)
