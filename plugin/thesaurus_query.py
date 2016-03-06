# Python backend for looking up words in an online thesaurus. Idea from
# project vim-online_thesaurus by Anton Beloglazov <http://beloglazov.info/>.
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
# Version:      0.1.0
# Original idea: Anton Beloglazov <http://beloglazov.info/>

import vim

class Thesaurus_Query_Handler:
    '''
    It holds and manages wordlist from previous query. It also interface the
    query request from vim with default query routine or other user defined
    routine when word is not already in the wordlist.
    '''

    def __init__(self, cache_size_max=100):
        self.word_list = {}  # hold wordlist obtained in previous query
        self.word_list_keys = []  # hold all keys for wordlist
                                  # in old->new order
        self.wordlist_size_max = cache_size_max
        self.query_source_cmd = ''
        self.query_backend_define()
#        self.raise_backend_priority_if_synonym_found =
#        self.truncate_definition = -1  # number of definitions retained in output
#        self.truncate_syno_list = -1   # number of synonyms retained for each definition in output

    def query_backend_define(self):
        """
        Define the query routine used.
        """
        from tq_local_mthesaur_lookup import word_query_mthesaur_lookup
        from online_query_handler import word_query_handler_thesaurus_lookup
        self.query_backends = []
        local_as_primary = vim.eval("g:thesaurus_query#use_local_thesaurus_source_as_primary")
        use_fallback = vim.eval("g:thesaurus_query#use_alternative_backend")
        if local_as_primary=="1":
            self.query_backends.append(word_query_mthesaur_lookup())
            if use_fallback=="1":
                self.query_backends.append(word_query_handler_thesaurus_lookup())
        else:
            self.query_backends.append(word_query_handler_thesaurus_lookup())
            if use_fallback=="1":
                self.query_backends.append(word_query_mthesaur_lookup())

        self.use_fallback=int(use_fallback)


    def query(self, word):
        if word in self.word_list:  # search word_list first to save query time
            return self.word_list[word]

        error_encountered = 0
        good_backends=[]
        faulty_backends=[]
        for query_backend_curr in self.query_backends:  # query each of the backend list till found
            [state, synonym_list]=query_backend_curr.query(word)
            if state == -1:
                error_encountered = 1
                faulty_backends.append(query_backend_curr)
                continue
            if state == 0:
                good_backends.append(query_backend_curr)
                break
        for faulty in faulty_backends:
            self.query_backends.remove(faulty)
        self.query_backends+=faulty_backends
        if int(vim.eval("g:raise_backend_priority_if_synonym_found")) == 1:
            for good in good_backends:
                self.query_backends.remove(good)
            self.query_backends=good_backends+self.query_backends
        if error_encountered == 1:
            vim.command('echohl WarningMSG | echon "WARNING: " | echohl None | echon "one or more query backends report error. Please check on thesaurus source(s).\n"')
        if state == 0:  # save to word_list buffer only when synonym is found
            self.word_list[word]=synonym_list
            self.word_list_keys.append(word)
            if len(self.word_list_keys) > self.wordlist_size_max:
                dumped_item=self.word_list.pop(self.word_list_keys.pop(0))
                del dumped_item
        return synonym_list

def truncate_synonym_list(synonym_list):
    truncated_flag = 0
    truncate_on_definition = int(vim.eval("g:thesaurus_query#truncation_on_definition_num"))  # number of definitions retained in output
    truncate_syno_list = int(vim.eval("g:thesaurus_query#truncation_on_syno_list_size"))   # number of synonyms retained for each definition in output
    output_buffer = []
    if truncate_on_definition > 0:
        if truncate_on_definition<=len(synonym_list):
            truncated_flag = 1

    output_buffer_temp = (synonym_list if truncate_on_definition==-1 else synonym_list[:truncate_on_definition])

    for definition in output_buffer_temp:
        if truncate_syno_list==-1:
            output_buffer.append(definition)
        else:
            if truncate_syno_list<len(definition[1]):
                truncated_flag = 1
            output_buffer.append([definition[0],definition[1][:truncate_syno_list]])

    del output_buffer_temp
    return [truncated_flag, output_buffer]

def tq_candidate_list_populate(candidates):
    '''
    generate thesaurus_wait_list and syno_result_prompt to be shown on terminal
    '''
    thesaurus_wait_list = []
    syno_result_prompt = []
    wordOriginal = vim.eval('l:trimmed_word')
    word_ID = 0
    for syno_case in candidates:
        syno_result_prompt.append([syno_case[0],[]])
        for word_curr in syno_case[1]:
            if wordOriginal.isupper():
                syno_result_prompt[-1][1].append("({}){}".format(word_ID, word_curr.upper()))
                thesaurus_wait_list.append("{}".format(word_curr.upper()))
            elif wordOriginal[0].isupper():
                syno_result_prompt[-1][1].append("({}){}".format(word_ID, word_curr[0].upper()+word_curr[1:]))
                thesaurus_wait_list.append("{}".format(word_curr[0].upper()+word_curr[1:]))
            else:
                syno_result_prompt[-1][1].append("({}){}".format(word_ID, word_curr))
                thesaurus_wait_list.append("{}".format(word_curr))
            word_ID+=1
    return [word_ID, thesaurus_wait_list, syno_result_prompt]

def tq_replace_cursor_word_from_candidates(candidate_list):
    '''
    Using vim's color message box to populate a candidate list from found
    synonyms. Then ask user to choose suitable candidate to replace word under
    cursor.
    '''
    [truncated_flag, candidates] = truncate_synonym_list(candidate_list)

    [candidate_num, thesaurus_wait_list, syno_result_prompt] = tq_candidate_list_populate(candidates)

    vim.command("echon \"In line: ... \"|echohl Keyword|echon \"{}\"|echohl None |echon \" ...\n\"".format(vim.current.line.replace('\\','\\\\').replace('"','\\"')))
    vim.command("call g:TQ_echo_HL(\"None|Candidates for |WarningMSG|{}\\n|None\")".format(vim.eval("l:trimmed_word")))
    for case in syno_result_prompt:
        if case[0] != "":
            vim.command('call g:TQ_echo_HL("Keyword|Definition: |None|{}\\n")'.format(case[0]))
        vim.command('call g:TQ_echo_HL("Keyword|Synonyms: |None|")')
        col_count = 10
        col_count_max = int(vim.eval("&columns"))
        for synonym_i in case[1]:
            if (col_count+len(synonym_i)+1)<col_count_max:
                vim.command('echon "{} "'.format(synonym_i))
                col_count += len(synonym_i)+1
            else:
                vim.command('echon "\n          {} "'.format(synonym_i))
                col_count = 10 + len(synonym_i)+1
        vim.command('echon "\n"')
    if truncated_flag==0:
        thesaurus_user_choice = vim.eval("input('Type number and <Enter> (empty cancels): ')")
    else:
        thesaurus_user_choice = vim.eval("input('Type number and <Enter> (results truncated, Type `A<Enter>` to browse all results\nin split; empty cancels): ')")
    if not thesaurus_user_choice:
        return
    if thesaurus_user_choice == "A":
        tq_generate_thesaurus_buffer(candidate_list)
        return
    try:
        thesaurus_user_choice=int(thesaurus_user_choice)
    except ValueError:
        vim.command('call g:TQ_echo_HL("WarningMSG|\nInvalid Input. |None|Ending synonym replacing session without making changes.")')
        return
    if (thesaurus_user_choice>=candidate_num or thesaurus_user_choice<0):
        vim.command('call g:TQ_echo_HL("WarningMSG|\nInvalid Input. |None|Ending synonym replacing session without making changes.")')
    vim.command("normal! wbcw{}".format(thesaurus_wait_list[thesaurus_user_choice]))

def tq_generate_thesaurus_buffer(candidates):
    '''
    generate a buffer showing all found synonyms in the candidate list from
    query
    '''
#    tq_current_buffer = vim.current.buffer.name
    vim.command("silent! let l:thesaurus_window = bufwinnr('^thesaurus: ')")
    if int(vim.eval("l:thesaurus_window")) > -1:
        vim.command('exec l:thesaurus_window . "wincmd w"')
    else:
        vim.command('exec ":silent keepalt belowright split thesaurus:\\\\ " . l:word_fname')
    vim.command('exec ":silent file thesaurus:\\\\ " . l:word_fname . "\\\\ (press\\\\ q\\\\ to\\\\ close\\\\ this\\\\ split.)"')

    vim.command('setlocal noswapfile nobuflisted nospell nowrap modifiable')
    vim.command('setlocal buftype=nofile')

    tq_thesaurus_buffer = vim.current.buffer
    del tq_thesaurus_buffer[:]
    line_count=0
    tq_thesaurus_buffer.append([""])
    tq_thesaurus_buffer[line_count]="Result for word \"{}\" (press \"q\" to close this split)".format(vim.eval('l:word'))
    line_count+=1
    for case in candidates:
        tq_thesaurus_buffer.append([""])
        if not case[0]:
            tq_thesaurus_buffer[line_count]='Synonyms: {}'.format(", ".join(case[1]))
            line_count+=1
            continue
        tq_thesaurus_buffer[line_count:line_count+2]=['Definition: {}'.format(case[0]), 'Synonyms: {}'.format(", ".join(case[1]))]
        line_count+=2
    vim.command("setlocal bufhidden=")
    vim.command("silent g/^Synonyms:/ normal! 0Vgq")
    vim.command("exec 'resize ' . (line('$'))")
    vim.command("nnoremap <silent> <buffer> q :q<CR>")
    vim.command("setlocal filetype=thesaurus")
    vim.command("normal! gg")
    vim.command("setlocal nomodifiable")
#    tq_current_buffer_goto = vim.eval('bufwinnr("{}")'.format(tq_current_buffer))
#    vim.command('exec {} . "wincmd w"'.format(tq_current_buffer_goto))

