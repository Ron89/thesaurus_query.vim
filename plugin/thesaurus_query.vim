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
"  Basic settings
" --------------------------------
"
if !exists("g:tq_map_keys")
    let g:tq_map_keys = 1
endif

if !exists("g:tq_use_vim_autocomplete")
    let g:tq_use_vim_autocomplete = 1
endif


" --------------------------------
"  Expose our commands to the user
" --------------------------------
"
command! ThesaurusQueryReplaceCurrentWord :call thesaurus_query#Thesaurus_Query_Lookup(expand('<cword>'), 1)
command! ThesaurusQueryLookupCurrentWord :call thesaurus_query#Thesaurus_Query_Lookup(expand('<cword>'), 0)
command! ThesaurusQueryReset :call thesaurus_query#Thesaurus_Query_Restore_Handler()

command! -nargs=1 Thesaurus :call thesaurus_query#Thesaurus_Query_Lookup(<q-args>, 0)

command! -nargs=1 ThesaurusQueryReplace :call thesaurus_query#Thesaurus_Query_Lookup(<q-args>, 1)


" --------------------------------
"  Map keys
" --------------------------------

if g:tq_map_keys
    nnoremap <unique><silent> <Leader>cs :ThesaurusQueryReplaceCurrentWord<CR>
    vnoremap <unique><silent> <Leader>cs "ky:ThesaurusQueryReplace <C-r>k<CR>
    nnoremap <silent> <LocalLeader>cs :ThesaurusQueryReplaceCurrentWord<CR>
    vnoremap <silent> <LocalLeader>cs "ky:ThesaurusQueryReplace <C-r>k<CR>
endif

if g:tq_use_vim_autocomplete
    set completefunc=thesaurus_query#auto_complete_integrate
endif

let &cpo = s:save_cpo
