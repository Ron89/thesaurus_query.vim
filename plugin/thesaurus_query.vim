" An thesaurus query & replacing framework written in python.
" Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
" Version:      0.0.3
" part of the code and default online thesaurus lookup routine:
"       Anton Beloglazov <http://beloglazov.info/>

if exists("g:loaded_thesaurus_query")
    finish
endif
let g:loaded_thesaurus_query = 1

let s:save_cpo = &cpo
set cpo&vim

" environs setup
if !has("python")
    echoerr 'thesaurus_query framework require vim with python support.'
endif

" --------------------------------
"  Function(s)
" --------------------------------

" Trim input_string before query
function! s:Trim(input_string)
    let l:str = substitute(a:input_string, '[\r\n:]', '', '')
    return substitute(l:str, '^\s*\(.\{-}\)\s*$', '\1', '')
endfunction

" command|[content]|command
function! g:TQ_echo_HL(message_for_echo)
    let l:index = 0
    for item in split(a:message_for_echo, "|")
        if l:index % 2
            echon item
        else
            exec "echohl " . item
        endif
        let l:index+=1
    endfor
endfunction

python import sys as tq_sys_api
python import vim as tq_vim_api
python tq_sys_api.path.append(tq_vim_api.eval('expand("<sfile>:h")'))
python import thesaurus_query

function! g:Thesaurus_Query_Init()
python<<endOfPython
tq_framework = thesaurus_query.Thesaurus_Query_Handler()
tq_framework.query_backend.truncation_on_relavance = int(tq_vim_api.eval("g:thesaurus_query#truncation_on_relavance"))
tq_framework.truncate_definition = int(tq_vim_api.eval("g:thesaurus_query#truncation_on_definition_num"))
tq_framework.truncate_syno_list = int(tq_vim_api.eval("g:thesaurus_query#truncation_on_syno_list_size"))

endOfPython
endfunction

" a:word        word to be looked up
" a:replace     flag:
"                       0 - don't replace word under cursor
"                       1 - replace word under cursor
function! g:Thesaurus_Query_Lookup(word, replace)
    let l:replace = a:replace
    let l:trimmed_word = s:Trim(a:word)
    let l:word = substitute(tolower(l:trimmed_word), '"', '', 'g')
    let l:word_fname = fnameescape(l:word)
    let l:syno_found = 1  " initialize the value

" query the current word
python tq_synonym_result = tq_framework.query(tq_vim_api.eval("l:word"))

python<<endOfPython
# mark for exit function if no candidate is found
if not tq_synonym_result:
    tq_vim_api.command("echom 'No synonym found for \"{}\".'".format(tq_vim_api.eval("l:word")))
    tq_vim_api.command("let l:syno_found=0")
# if replace flag is on, prompt user to choose after populating candidate list
elif tq_vim_api.eval('l:replace') != '0':
    thesaurus_query.tq_replace_cursor_word_from_candidates(tq_synonym_result)    
endOfPython

" exit function if no candidate is found
    if !l:syno_found + l:replace*(!g:thesaurus_query#display_list_all_time)
        return
    endif

" create new buffer to display all query result and return to original buffer
python thesaurus_query.tq_generate_thesaurus_buffer(tq_synonym_result)
endfunction


" --------------------------------
"  Setting up default values & Initialize
" --------------------------------
if !exists("g:thesaurus_query#display_list_all_time")
    let g:thesaurus_query#display_list_all_time = 0
endif

if !exists("g:thesaurus_query#map_keys")
    let g:thesaurus_query#map_keys = 1
endif

" This variable is for default query routine, if according to thesaurus.com,
" the found synonym's relavance is smaller or equal to this value, it is
" neglected
if !exists("g:thesaurus_query#truncation_on_relavance")
    let g:thesaurus_query#truncation_on_relavance = 0
endif

" This variable is for core query handler. If value is -1, no truncate of
" output is made upon number of definitions. Else, if number is n, only
" synonyms of the first n word definitions were retained.
if !exists("g:thesaurus_query#truncation_on_definition_num")
    let g:thesaurus_query#truncation_on_definition_num = -1
endif

" This variable is for core query handler. If value is -1, no truncate of
" output is made upon number of synonyms from a single definition. Else, if
" number is n, only first n synonyms of that definition will be retained.
if !exists("g:thesaurus_query#truncation_on_syno_list_size")
    let g:thesaurus_query#truncation_on_syno_list_size = -1
endif

call g:Thesaurus_Query_Init()


" --------------------------------
"  Expose our commands to the user
" --------------------------------
command! ThesaurusQueryReplaceCurrentWord :call g:Thesaurus_Query_Lookup(expand('<cword>'), 1)
command! ThesaurusQueryLookupCurrentWord :call g:Thesaurus_Query_Lookup(expand('<cword>'), 0)
command! -nargs=1 Thesaurus :call g:Thesaurus_Query_Lookup(<q-args>, 0)


" --------------------------------
"  Map keys
" --------------------------------
if g:thesaurus_query#map_keys
    nnoremap <unique> <LocalLeader>cs :ThesaurusQueryReplaceCurrentWord<CR>
    vnoremap <unique> <LocalLeader>cs y:Thesaurus <C-r>"<CR>
endif

let &cpo = s:save_cpo
