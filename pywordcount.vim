" WordCount Function
let current_dir = expand("<sfile>:h")
exe 'python cdir = u"' . current_dir . '"'
python << EOP
import sys
#sys.path.insert(0, cdir)
if "/Users/tadhg/subversion/code/python/vim_scripts" not in sys.path:
    sys.path.append("/Users/tadhg/subversion/code/python/vim_scripts")
#import pywordcount_vim
from pywordcount import pywordcount_vim
import vim

vwc = pywordcount_vim.VimWordCounter(vim, cdir)
EOP
function! WordCount()
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
" /WordCount Function
set statusline=%F%m%r%h%w\ [FORMAT=%{&ff}]\ [TYPE=%Y]\ [POS=%04l,%04v][%p%%]\ wc:%{WordCount()}
