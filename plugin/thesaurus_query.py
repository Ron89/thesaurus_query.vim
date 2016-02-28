# Python backend for looking up words in an online thesaurus. Idea from
# project vim-online_thesaurus by Anton Beloglazov <http://beloglazov.info/>.
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
# Version:      0.0.3
# Original idea: Anton Beloglazov <http://beloglazov.info/>

import vim as tq_vim_api

class Thesaurus_Query_Handler:
    '''
    It holds and manages wordlist from previous query. It also interface the
    query request from vim with default query routine or other user defined
    routine when word is not already in the wordlist.
    '''

    def __init__(self, cache_size_max=10000):
        self.word_list = {}  # hold wordlist obtained in previous query
        self.word_list_keys = []  # hold all keys for wordlist
                                  # in old->new order
        self.wordlist_size_max = cache_size_max
        self.query_source_cmd = ''
        from online_query_handler import word_query_handler_thesaurus_lookup
        self.query_backend = word_query_handler_thesaurus_lookup()
        self.truncate_definition = -1  # number of definitions retained in output
        self.truncate_syno_list = -1   # number of synonyms retained for each definition in output

    def query(self, word):
        if word in self.word_list:
            return self.word_list[word]

        [state, synonym_list]=self.query_backend.query(word)
        if state == -1:
            print "WARNING: query backend reports error. Please check on thesaurus source."
            return []
        if state == 0:  # save to word_list buffer only when synonym is found
            self.word_list[word]=synonym_list
            self.word_list_keys.append(word)
            if len(self.word_list_keys) > self.wordlist_size_max:
                dumped_item=self.word_list.pop(self.word_list_keys.pop(0))
                del dumped_item
        output_buffer = []
        output_buffer_temp = (synonym_list if self.truncate_definition==-1 else synonym_list[:self.truncate_definition])
        for definition in output_buffer_temp:
            if self.truncate_syno_list==-1:
                output_buffer.append(definition)
            else:
                output_buffer.append([definition[0],definition[1][:self.truncate_syno_list]])

        del output_buffer_temp
        return output_buffer


def tq_replace_cursor_word_from_candidates(candidates):
    '''
    Using vim's color message box to populate a candidate list from found
    synonyms. Then ask user to choose suitable candidate to replace word under
    cursor.
    '''
    thesaurus_wait_list = []
    syno_result_prompt = []
    word_ID = 0
    for syno_case in candidates:
        thesaurus_wait_list = thesaurus_wait_list+syno_case[1]
        syno_result_prompt.append([syno_case[0],[]])
        for word_curr in syno_case[1]:
            syno_result_prompt[-1][1].append("({}){}".format(word_ID, word_curr))
            word_ID+=1
    tq_vim_api.command("echon \"In line: ... \"|echohl Keyword|echon \"{}\"|echohl None |echon \" ...\n\"".format(tq_vim_api.current.line.replace('\\','\\\\').replace('"','\\"')))
    tq_vim_api.command("call TQ_echo_HL(\"None|Synonym for |Special|{}\\n|None\")".format(tq_vim_api.eval("l:word")))
    for case in syno_result_prompt:
        tq_vim_api.command('call TQ_echo_HL("Keyword|Definition: |None|{}\\n")'.format(case[0]))
        tq_vim_api.command('call TQ_echo_HL("Keyword|Synonyms: |None|{}\\n")'.format(", ".join(case[1])))
    try:
        thesaurus_user_choice = int(tq_vim_api.eval("input('Choose from wordlist(type -1 to cancel): ')"))
    except ValueError:
        print "Invalid Input. Ending replacing session without making changes."
        return
    while thesaurus_user_choice>=word_ID or thesaurus_user_choice<-1:
        try:
            thesaurus_user_choice = int(tq_vim_api.eval("input('Invalid input, choose again(type -1 to cancel): ')"))
        except ValueError:
            print "Invalid Input. Ending replacing session without making changes."
            return
    if thesaurus_user_choice!=-1:
        tq_vim_api.command("normal wbcw{}".format(thesaurus_wait_list[thesaurus_user_choice]))


def tq_generate_thesaurus_buffer(candidates):
    '''
    generate a buffer showing all found synonyms in the candidate list from
    query
    '''
    tq_current_buffer = tq_vim_api.current.buffer.name
    tq_vim_api.command("silent! let l:thesaurus_window = bufwinnr('^thesaurus: ')")
    if int(tq_vim_api.eval("l:thesaurus_window")) > -1:
        tq_vim_api.command('exec l:thesaurus_window . "wincmd w"')
    else:
        tq_vim_api.command('exec ":silent keepalt belowright split thesaurus:\\\\ " . l:word_fname')
    tq_vim_api.command('exec ":silent file thesaurus:\\\\ " . l:word_fname')

    tq_vim_api.command('setlocal noswapfile nobuflisted nospell nowrap modifiable')
    tq_vim_api.command('setlocal buftype=nofile')

    tq_thesaurus_buffer = tq_vim_api.current.buffer
    del tq_thesaurus_buffer[:]
    line_count=0
    for case in candidates:
        tq_thesaurus_buffer[line_count:line_count+2]=['Definition: {}'.format(case[0]), 'Synonyms: {}'.format(", ".join(case[1]))]
        line_count+=2
    tq_vim_api.command("setlocal bufhidden=")
    tq_vim_api.command("silent g/^Synonyms:/ normal! 0Vgq")
    tq_vim_api.command("exec 'resize ' . (line('$'))")
    tq_vim_api.command("nnoremap <silent> <buffer> q :q<CR>")
    tq_vim_api.command("setlocal filetype=thesaurus")
    tq_vim_api.command("normal! gg")
    tq_vim_api.command("setlocal nomodifiable")
    tq_current_buffer_goto = tq_vim_api.eval('bufwinnr("{}")'.format(tq_current_buffer))
    tq_vim_api.command('exec {} . "wincmd w"'.format(tq_current_buffer_goto))

