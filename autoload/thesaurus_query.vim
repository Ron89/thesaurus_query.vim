" An thesaurus query & replacing framework written in python.
" Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
"
" part of the code and idea of using online resources for thesaurus query:
"       Anton Beloglazov <http://beloglazov.info/>

let s:save_cpo = &cpo
set cpo&vim

" environs setup
if !has("python")
    echoerr 'thesaurus_query framework require vim with python support.'
endif

" --------------------------------
"  Setting up default values & Initialize
" --------------------------------

if !exists("g:tq_display_list_all_time")
    let g:tq_display_list_all_time = 0
endif

" this variable defines which query backend language do you want to use. It
" can be either string or list
if !exists("g:tq_language")
    let g:tq_language = 'en'
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
    let g:tq_enabled_backends=["jeck_ru","thesaurus_com","jeck_ru","datamuse_com","mthesaur_txt"]
endif


" --------------------------------
" legacy settings (depreciated, do NOT use)

if !exists("g:thesaurus_query#display_list_all_time")
    let g:thesaurus_query#display_list_all_time = g:tq_display_list_all_time
endif

if !exists("g:thesaurus_query#truncation_on_relavance")
    let g:thesaurus_query#truncation_on_relavance = g:tq_truncation_on_relavance
endif

if !exists("g:thesaurus_query#truncation_on_definition_num")
    let g:thesaurus_query#truncation_on_definition_num = g:tq_truncation_on_definition_num
endif

if !exists("g:thesaurus_query#truncation_on_syno_list_size")
    let g:thesaurus_query#truncation_on_syno_list_size = g:tq_truncation_on_syno_list_size
endif

if !exists("g:thesaurus_query#use_local_thesaurus_source_as_primary")
    let g:thesaurus_query#use_local_thesaurus_source_as_primary = g:tq_use_local_thesaurus_source_as_primary
endif

if !exists("g:thesaurus_query#use_alternative_backend")
    let g:thesaurus_query#use_alternative_backend=g:tq_use_alternative_backend
endif

if !exists("g:thesaurus_query#mthesaur_file")
    let g:thesaurus_query#mthesaur_file=g:tq_mthesaur_file
endif

if !exists("g:thesaurus_query#enabled_backends")
    let g:thesaurus_query#enabled_backends=g:tq_enabled_backends
endif

let s:tq_separator_regexp = "[^\^ :=+\\-_\\/;`'\"!@#$%&*\(\)\\[\\]{}|,<\.>?~]"

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

python import sys
python import os
python import vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))
python import thesaurus_query.thesaurus_query as thesaurus_query



function! thesaurus_query#Thesaurus_Query_Init()
python<<endOfPython
tq_framework = thesaurus_query.Thesaurus_Query_Handler()
endOfPython
endfunction


function! thesaurus_query#Thesaurus_Query_Restore_Handler()
    py tq_framework.restore_thesaurus_query_handler()
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
python tq_synonym_result = tq_framework.query(vim.eval("l:word").decode('utf-8'))

python<<endOfPython
# mark for exit function if no candidate is found
if not tq_synonym_result:
    vim.command(u"echom 'No synonym found for \"{}\".'".format(vim.eval("l:word").decode('utf-8')))
    vim.command("let l:syno_found=0")
# if replace flag is on, prompt user to choose after populating candidate list
elif vim.eval('l:replace') != '0':
    thesaurus_query.tq_replace_cursor_word_from_candidates(tq_synonym_result)
endOfPython

" exit function if no candidate is found
    if !l:syno_found + l:replace*(!g:thesaurus_query#display_list_all_time)
        python del tq_synonym_result
        return
    endif

" create new buffer to display all query result and return to original buffer
    python thesaurus_query.tq_generate_thesaurus_buffer(tq_synonym_result)
    python del tq_synonym_result
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
        let l:synoList = []
python<<endOfPython
tq_synonym_result = tq_framework.query(vim.eval("l:word").decode('utf-8'))
tq_synonym_combined = [tq_iterator[1] for tq_iterator in tq_synonym_result]
tq_synonym_annexed = []
tq_synonym_combined = map(tq_synonym_annexed.extend, tq_synonym_combined)
tq_synonym_annexed = [thesaurus_query.tq_word_form_reverse(tq_iterator) for tq_iterator in tq_synonym_annexed]
if tq_synonym_annexed:
    tq_synonym_annexed.insert(0,vim.eval("a:base").decode('utf-8'))
for tq_iterator in tq_synonym_annexed:
    vim.command(u'call add(l:synoList, "{}")'.format(tq_iterator))
# delete all variable used in the function, keep namespace clean
if 'tq_iterator' in locals():
    del tq_iterator
del tq_synonym_result
del tq_synonym_combined
del tq_synonym_annexed
endOfPython
        return l:synoList
    endif
endfunction

call thesaurus_query#Thesaurus_Query_Init()

let &cpo = s:save_cpo
