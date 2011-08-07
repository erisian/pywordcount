" WordCount Function
let current_dir = expand("<sfile>:h:h") . "/python"
exe 'python cdir = u"' . current_dir . '"'
python << EOP
import sys
#sys.path.insert(0, cdir)
if cdir not in sys.path:
    sys.path.append(cdir)
#import pywordcount_vim
from pywordcount import pywordcount_vim
import vim

vwc = pywordcount_vim.VimWordCounter(vim, cdir)
EOP
function! WordCount() " {{{ WordCount
    python << EOF
fts = [ft for ft in vim.eval("&ft").split(".") if ft]
validft = bool([ft for ft in vwc.wc.filetypes if ft in fts])
if validft:
    vwc.vim_fast()
EOF
if exists("b:TotalWordCount")
    return b:TotalWordCount
endif
if !exists("b:TotalWordCount")
    return "-"
endif
endfunction
" }}} WordCount
" Example: set statusline=wc:%{WordCount()}
