" An thesaurus query & replacing framework written in python.
" Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
"
" part of the code and idea of using online resources for thesaurus query:
"       Anton Beloglazov <http://beloglazov.info/>

if exists("g:loaded_thesaurus_query")
    finish
endif
let g:loaded_thesaurus_query = 1

let s:save_cpo = &cpo
set cpo&vim

" --------------------------------
"  Expose our commands to the user
" --------------------------------
command! ThesaurusQueryReplaceCurrentWord :call thesaurus_query#Thesaurus_Query_Lookup(expand('<cword>'), 1)
command! ThesaurusQueryLookupCurrentWord :call thesaurus_query#Thesaurus_Query_Lookup(expand('<cword>'), 0)
command! ThesaurusQueryReset :call thesaurus_query#Thesaurus_Query_Restore_Handler()

command! -nargs=1 Thesaurus :call thesaurus_query#Thesaurus_Query_Lookup(<q-args>, 0)


" --------------------------------
"  Map keys
" --------------------------------
if g:thesaurus_query#map_keys
    nnoremap <unique><silent> <LocalLeader>cs :ThesaurusQueryReplaceCurrentWord<CR>
    vnoremap <unique><silent> <LocalLeader>cs y:Thesaurus <C-r>"<CR>
endif

let &cpo = s:save_cpo
