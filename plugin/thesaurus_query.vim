" An thesaurus query & replacing framework written in python.
" Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
" Version:      0.0.1
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

python import sys
python import vim
python sys.path.append(vim.eval('expand("<sfile>:h")'))
python import thesaurus_query

function! g:Thesaurus_Query_Init()
python<<endOfPython
thesaurus_query_framework = thesaurus_query.Thesaurus_Query_Handler()
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

" query word and prompt user to choose word after populating the list
python<<endOfPython
synonym_result = thesaurus_query_framework.query(vim.eval("l:word"))
if vim.eval('l:replace') != '0' and not not synonym_result:
    thesaurus_wait_list = []
    syno_result_prompt = []
    word_ID = 0
    for syno_case in synonym_result:
        thesaurus_wait_list = thesaurus_wait_list+syno_case[1]
        syno_result_prompt.append([syno_case[0],[]])
        for word_curr in syno_case[1]:
            syno_result_prompt[-1][1].append("({}){}".format(word_ID, word_curr))
            word_ID+=1
    vim.command("echon \"In line: ... \"|echohl Keyword|echon \"{}\"|echohl None |echon \" ...\n\"".format(vim.current.line))
    vim.command("echon \"Synonym for \"|echohl Special|echon\"{}\n\"|echohl None".format(vim.eval("l:word")))
    for case in syno_result_prompt:
        vim.command('echohl Keyword | echon "Definition: "|echohl None|echon "{}\n"'.format(case[0]))
        vim.command('echohl Keyword | echon "Synonyms: "|echohl None|echon "{}\n"'.format(", ".join(case[1])))

    thesaurus_user_choice = int(vim.eval("input('Choose from wordlist(type -1 to cancel): ')"))
    while thesaurus_user_choice>=word_ID or thesaurus_user_choice<-1:
        thesaurus_user_choice = int(vim.eval("input('Invalid input, choose again(type -1 to cancel): ')"))
    if thesaurus_user_choice!=-1:
        vim.command("normal wbcw{}".format(thesaurus_wait_list[thesaurus_user_choice]))
tq_current_buffer = vim.current.buffer.name
if not synonym_result:
    vim.command("echom 'No synonym found for \"{}\".'".format(vim.eval("l:word")))
    vim.command("let l:syno_found=0")
endOfPython
if ((l:replace==0)+g:thesaurus_query#display_list_all_time)*l:syno_found
" create new buffer to display thesaurus query result and go to it
    silent! let l:thesaurus_window = bufwinnr('^thesaurus: ')
    if l:thesaurus_window > -1
        exec l:thesaurus_window . "wincmd w"
    else
        exec ":silent keepalt belowright split thesaurus:\\ " . l:word_fname
    endif
    exec ":silent file thesaurus:\\ " . l:word_fname

    setlocal noswapfile nobuflisted nospell nowrap modifiable
    setlocal buftype=nofile

python<<endOfPython
thesaurus_buffer = vim.current.buffer
del thesaurus_buffer[:]
line_count=0
for case in synonym_result:
    thesaurus_buffer[line_count:line_count+2]=['Definition: {}'.format(case[0]),
            'Synonyms: {}'.format(", ".join(case[1]))]
    line_count+=2
vim.command("setlocal bufhidden=")
vim.command("silent g/^Synonyms:/ normal! 0Vgq")
vim.command("exec 'resize ' . (line('$') - 1)")
vim.command("nnoremap <silent> <buffer> q :q<CR>")
vim.command("setlocal filetype=thesaurus")
vim.command("normal! gg")
tq_current_buffer_goto = vim.eval('bufwinnr("{}")'.format(tq_current_buffer))
vim.command('exec {} . "wincmd w"'.format(tq_current_buffer_goto))
endOfPython

endif

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

call Thesaurus_Query_Init()


" --------------------------------
"  Expose our commands to the user
" --------------------------------
command! ThesaurusQueryReplaceCurrentWord :call Thesaurus_Query_Lookup(expand('<cword>'), 1)
command! ThesaurusQueryLookupCurrentWord :call Thesaurus_Query_Lookup(expand('<cword>'), 0)
command! -nargs=1 Thesaurus :call Thesaurus_Query_Lookup(<q-args>, 0)


" --------------------------------
"  Map keys
" --------------------------------
if g:thesaurus_query#map_keys
    nnoremap <LocalLeader>cs :ThesaurusQueryReplaceCurrentWord<CR>
    vnoremap <LocalLeader>cs y:Thesaurus <C-r>"<CR>
endif

let &cpo = s:save_cpo
