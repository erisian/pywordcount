#! /usr/bin/python
# -*- coding: utf-8 -*-
import re
def pywordcountplugin(text):
    """
    replace URLs; regexes copied from Docutils (parsers/rst/states.py)
    """
    openers = u'\'"([{<\u2018\u201c\xab\u00a1\u00bf' # see quoted_start below
    closers = u'\'")]}>\u2019\u201d\xbb!?'
    unicode_delimiters = u'\u2010\u2011\u2012\u2013\u2014\u00a0'
    start_string_prefix = (u'((?<=^)|(?<=[-/: \\n\u2019%s%s]))'
                           % (re.escape(unicode_delimiters),
                              re.escape(openers)))
    end_string_suffix = (r'((?=$)|(?=[-/:.,; \n\x00%s%s]))'
                         % (re.escape(unicode_delimiters),
                            re.escape(closers)))
    # Valid URI characters (see RFC 2396 & RFC 2732);
    # final \x00 allows backslash escapes in URIs:
    uric = r"""[-_.!~*'()[\];/:@&=+$,%a-zA-Z0-9\x00]"""
    # Delimiter indicating the end of a URI (not part of the URI):
    uri_end_delim = r"""[>]"""
    # Last URI character; same as uric but no punctuation:
    urilast = r"""[_~*/=+a-zA-Z0-9]"""
    # End of a URI (either 'urilast' or 'uric followed by a
    # uri_end_delim'):
    uri_end = r"""(?:%(urilast)s|%(uric)s(?=%(uri_end_delim)s))""" % locals()
    emailc = r"""[-_!~*'{|}/#?^`&=+$%a-zA-Z0-9\x00]"""
    email_pattern = r"""
          %(emailc)s+(?:\.%(emailc)s+)*   # name
          (?<!\x00)@                      # at
          %(emailc)s+(?:\.%(emailc)s*)*   # host
          %(uri_end)s                     # final URI char
          """
    email=re.compile(email_pattern % locals() + '$', re.VERBOSE),
    uri=re.compile(
        (r"""
        %(start_string_prefix)s
        (?P<whole>
          (?P<absolute>           # absolute URI
            (?P<scheme>             # scheme (http, ftp, mailto)
              [a-zA-Z][a-zA-Z0-9.+-]*
            )
            :
            (
              (                       # either:
                (//?)?                  # hierarchical URI
                %(uric)s*               # URI characters
                %(uri_end)s             # final URI char
              )
              (                       # optional query
                \?%(uric)s*
                %(uri_end)s
              )?
              (                       # optional fragment
                \#%(uric)s*
                %(uri_end)s
              )?
            )
          )
        |                       # *OR*
          (?P<email>              # email address
            """ + email_pattern + r"""
          )
        )
        %(end_string_suffix)s
        """) % locals(), re.VERBOSE)
    return uri.sub("url", text)
