===========
PyWordCount
===========

PyWordCount is an accurate, Unicode-aware [1]_, configurable word counting script. It is also a plugin for Vim that provides a "live" word count if added to the Vim statusline.

It's aimed at people who want precise word counts, not approximations. It's also aimed at Vim users.

Why
===
``wc`` doesn't count Unicode characters properly; it also only splits on spaces, and that was insufficient for my purposes. For example:

    This is five words—only.

``wc`` counts that as four words.

In addition, ``wc`` doesn't easily let you filter content. PyWordCount can support filters, for example to strip quoted lines out of emails, so that the following would count as five words:

    > This is from the email being replied to

    This is five words—only

How
===
To run it on the command line, 

To run it from Vim,

    - put it in plugins
    - map PyWordCount to something
    - to put it in the statusline, do:

