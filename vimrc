:set exrc
:set secure

:set tabstop=4
:set softtabstop=4
:set shiftwidth=4
:set autoindent

set colorcolumn=110
highlight ColorColumn ctermbg=darkgray

:set bg=dark
"let &path.="src/include,/usr/include/AL,"
:set makeprg=cmake\ .\ &&\ make\ ../build\ -j
nnoremap <F4> :make!<cr>

function! s:c_header_skel()
    let gatename = substitute(toupper(expand("%:t")), "\\.", "_", "g")
    execute "normal i/**"
    execute "normal o * Description:"
    execute "normal o * Author: Igor Diakonov"
    execute "normal o * Date: " . strftime("%d.%m.%y %H:%M:%S")
    execute "normal o */"
    execute "normal o#ifndef " . gatename
    execute "normal o#define " . gatename . "   "
    execute "normal Go#endif"
    normal k3o
    normal k
endfunction

au BufNewFile *.{h,hpp} call <SID>c_header_skel()

filetype on
filetype plugin on
