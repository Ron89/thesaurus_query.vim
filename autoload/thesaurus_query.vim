" An thesaurus query & replacing framework written in python.
" Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
"
" part of the code and idea of using online resources for thesaurus query:
"       Anton Beloglazov <http://beloglazov.info/>

if exists("g:loaded_thesaurus_query_autoload")
    finish
endif
let g:loaded_thesaurus_query_autoload = 1

let s:save_cpo = &cpo
set cpo&vim


" environs setup
if has("python3")
    let s:tq_use_python = 'python3 '
elseif has("python")
    let s:tq_use_python = 'python '
else
    echoerr 'thesaurus_query framework require vim with python support.'
    finish
endif

" --------------------------------
" legacy settings (depreciated, do NOT use)

if exists("g:thesaurus_query#display_list_all_time")
    let g:tq_display_list_all_time = g:thesaurus_query#display_list_all_time
endif

if exists("g:thesaurus_query#truncation_on_relavance")
    let g:tq_truncation_on_relavance = g:thesaurus_query#truncation_on_relavance
endif

if exists("g:thesaurus_query#truncation_on_definition_num")
    let g:tq_truncation_on_definition_num = g:thesaurus_query#truncation_on_definition_num
endif

if exists("g:thesaurus_query#truncation_on_syno_list_size")
    let g:tq_truncation_on_syno_list_size = g:thesaurus_query#truncation_on_syno_list_size
endif

if exists("g:thesaurus_query#use_local_thesaurus_source_as_primary")
    let g:tq_use_local_thesaurus_source_as_primary = g:thesaurus_query#use_local_thesaurus_source_as_primary
endif

if exists("g:thesaurus_query#use_alternative_backend")
    let g:tq_use_alternative_backend = g:thesaurus_query#use_alternative_backend
endif

if exists("g:thesaurus_query#mthesaur_file")
    let g:tq_mthesaur_file = g:thesaurus_query#mthesaur_file
endif

if exists("g:thesaurus_query#enabled_backends")
    let g:tq_enabled_backends = g:thesaurus_query#enabled_backends
endif

let s:tq_separator_regexp = "[^\^ :=+\\-_\\/;`'\"!@#$%&*\(\)\\[\\]{}|,<\.>?~]"


" --------------------------------
"  Setting up default values & Initialize
" --------------------------------

if !exists("g:tq_display_list_all_time")
    let g:tq_display_list_all_time = 0
endif

" this variable defines which query backend language do you want to use. It
" can be either string or list
if !exists("g:tq_language")
    let g:tq_language = ['en']
endif

" This variable is for default query routine, if according to thesaurus.com,
" the found synonym's relavance is smaller or equal to this value, it is
" neglected
if !exists("g:tq_truncation_on_relavance")
    let g:tq_truncation_on_relavance = 0
endif

" This variable is for replacing candidate display. If value is -1, no
" truncate of output is made upon number of definitions. Else, if number is n,
" only synonyms of the first n word definitions were retained.
if !exists("g:tq_truncation_on_definition_num")
    let g:tq_truncation_on_definition_num = -1
endif

" This variable is for replacing candidate display. If value is -1, no
" truncate of output is made upon number of synonyms from a single definition.
" Else, if number is n, only first n synonyms of that definition will be
" retained.
if !exists("g:tq_truncation_on_syno_list_size")
    let g:tq_truncation_on_syno_list_size = -1
endif

" This variable is used when initiating core query handler.  It determine
" the priority between online thesaurus backend(based on Thesaurus.com) and
" local thesaurus backend(based on mthesaur.txt). If
" value is
"     0:      query with online backend first.
"     1:      query with local backend first.
"                                                     default=0
if !exists("g:tq_use_local_thesaurus_source_as_primary")
    let g:tq_use_local_thesaurus_source_as_primary = 0
endif

" This variable is used when initiating core query handler
" When default query backend return empty or error, this variable will decide:
"   value: 0    -> don't use alternative backend
"   value: 1    -> use alternative backend
if !exists("g:tq_use_alternative_backend")
    let g:tq_use_alternative_backend=1
endif

" this variable is offered by tq_local_mthesaur_lookup, to determine the
" location of mthesaurus file. File located by this variable will be first
" verified before verifying &thesaurus.
if !exists("g:tq_mthesaur_file")
    let g:tq_mthesaur_file="~/.vim/thesaurus/mthesaur.txt"
endif

" this variable is offered by core query handler, if value is
"       0:      priority of the backend that find the synonyms will be topped
"       1:      backend priority won't be affected by synonym findings
if !exists("g:tq_raise_backend_priority_if_synonym_found")
    let g:tq_raise_backend_priority_if_synonym_found=0
endif

" this variable is offered by core query handler. It's a list of
" query_backends user want to enable, with the sequence of user prefered
" priority.
"       * Please be careful not to mis-spell when setting this variable.
if !exists("g:tq_enabled_backends")
    let g:tq_enabled_backends=["woxikon_de","jeck_ru","thesaurus_com","datamuse_com","mthesaur_txt"]
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
function! thesaurus_query#echo_HL(message_for_echo)
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

exec s:tq_use_python.'import sys'
exec s:tq_use_python.'import os'
exec s:tq_use_python.'import vim'
exec s:tq_use_python."sys.path.append(vim.eval('expand(\"<sfile>:h\")'))"
exec s:tq_use_python.'import thesaurus_query.thesaurus_query as tq_interface'
exec s:tq_use_python.'from thesaurus_query.tq_common_lib import decode_utf_8, encode_utf_8'

function! thesaurus_query#Thesaurus_Query_Init()
    exec s:tq_use_python.'tq_framework = tq_interface.Thesaurus_Query_Handler()'
endfunction


function! thesaurus_query#Thesaurus_Query_Restore_Handler()
    exec s:tq_use_python.'tq_framework.restore_thesaurus_query_handler()'
endfunction

function! thesaurus_query#Thesaurus_Query_Lookup(word, replace)
" a:word        word to be looked up
" a:replace     flag:
"                       0 - don't replace word under cursor
"                       1 - replace word under cursor
    let l:replace = a:replace
    let l:trimmed_word = s:Trim(a:word)
    let l:word = substitute(tolower(l:trimmed_word), '"', '', 'g')
    let l:word_fname = fnameescape(l:word)
    let l:syno_found = 1  " initialize the value

" query the current word
    exec s:tq_use_python.'tq_synonym_result = tq_framework.query(decode_utf_8(vim.eval("l:word")))'

if s:tq_use_python=='python3 '
python3<<endOfPython
# mark for exit function if no candidate is found
if not tq_synonym_result:
    vim.command("echom 'No synonym found for \"{}\".'".format(vim.eval("l:word")))
    vim.command("let l:syno_found=0")
# if replace flag is on, prompt user to choose after populating candidate list
elif vim.eval('l:replace') != '0':
    tq_interface.tq_replace_cursor_word_from_candidates(tq_synonym_result)
endOfPython
else
python<<endOfPython
# mark for exit function if no candidate is found
if not tq_synonym_result:
    vim.command("echom 'No synonym found for \"{}\".'".format(vim.eval("l:word")))
    vim.command("let l:syno_found=0")
# if replace flag is on, prompt user to choose after populating candidate list
elif vim.eval('l:replace') != '0':
    tq_interface.tq_replace_cursor_word_from_candidates(tq_synonym_result)
endOfPython
endif


" exit function if no candidate is found
    if !l:syno_found + l:replace*(!g:tq_display_list_all_time)
        exec s:tq_use_python.'del tq_synonym_result'
        return
    endif

" create new buffer to display all query result and return to original buffer
    exec s:tq_use_python.'tq_interface.tq_generate_thesaurus_buffer(tq_synonym_result)'
    exec s:tq_use_python.'del tq_synonym_result'
endfunction

function! thesaurus_query#auto_complete_integrate(findstart, base)
    if a:findstart
        let l:line = getline('.')
        let l:start = col('.') - 1
        while start > 0 && l:line[l:start - 1] =~ s:tq_separator_regexp
            let l:start -= 1
        endwhile
        return l:start
    else
        " find matching with online backends
        let l:trimmed_word = s:Trim(a:base)
        let l:word = tolower(l:trimmed_word)
        if l:trimmed_word == ''
            return
        endif
        let l:synoList = []
        exec s:tq_use_python.'tq_synonym_result = tq_framework.query(decode_utf_8(vim.eval("l:word")))'
        exec s:tq_use_python.'tq_synonym_combined = [tq_iterator[1] for tq_iterator in tq_synonym_result]'
        exec s:tq_use_python.'tq_synonym_annexed = [tq_interface.tq_word_form_reverse(item) for syn_sublist in tq_synonym_combined for item in syn_sublist]'
        exec s:tq_use_python.'tq_synonym_annexed = [tq_interface.tq_word_form_reverse(tq_iterator) for tq_iterator in tq_synonym_annexed]'
if s:tq_use_python=='python3 '
python3<<endOfPython
if tq_synonym_annexed:
    tq_synonym_annexed.insert(0,decode_utf_8(vim.eval("a:base")))
for tq_iterator in tq_synonym_annexed:
    vim.command('call add(l:synoList, "{}")'.format(tq_interface.send_string_to_vim(tq_iterator)))
# delete all variable used in the function, keep namespace clean
if 'tq_iterator' in locals():
    del tq_iterator
endOfPython
else
python<<endOfPython
if tq_synonym_annexed:
    tq_synonym_annexed.insert(0,decode_utf_8(vim.eval("l:trimmed_word")))
for tq_iterator in tq_synonym_annexed:
    vim.command('call add(l:synoList, "{}")'.format(tq_interface.send_string_to_vim(tq_iterator)))
# delete all variable used in the function, keep namespace clean
if 'tq_iterator' in locals():
    del tq_iterator
endOfPython

endif
        exec s:tq_use_python.'del tq_synonym_result'
        exec s:tq_use_python.'del tq_synonym_combined'
        exec s:tq_use_python.'del tq_synonym_annexed'
        return l:synoList
    endif
endfunction

call thesaurus_query#Thesaurus_Query_Init()

let &cpo = s:save_cpo
