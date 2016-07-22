set exrc
set secure

set tabstop=4
set softtabstop=4
set shiftwidth=4

set colorcolumn=110
highlight ColorColumn ctermbg=darkgray

set bg=dark
"let &path.="src/include,/usr/include/AL,"
set makeprg=cmake\ .\ &&\ make\ ../build\ -j
nnoremap <F4> :make!<cr>

function! s:insert_gates()
  let gatename = substitute(toupper(expand("%:t")), "\\.", "_", "g")
  execute "normal! i#ifndef " . gatename
  execute "normal! o#define " . gatename . " "
  normal! o
  normal! o
  normal! o
  execute "normal! Go#endif /* " . gatename . " */"
  normal! kk
endfunction
au BufNewFile *.{h,hpp} call <SID>insert_gates()
filetype on
filetype plugin on
