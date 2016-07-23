# Python backend for looking up words in an online thesaurus. Idea from
# project vim-online_thesaurus by Anton Beloglazov <http://beloglazov.info/>.
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
# Original idea: Anton Beloglazov <http://beloglazov.info/>

try:
    import vim
    independent_session = False
except ImportError:
    independent_session = True

import re
from . import backends as tq_backends
from .tq_common_lib import decode_utf_8, send_string_to_vim, get_variable, vim_command, vim_eval

class Thesaurus_Query_Handler:
    '''
    It holds and manages wordlist from previous query. It also interface the
    query request from vim with default query routine or other user defined
    routine when word is not already in the wordlist.
    '''

    def __init__(self, cache_size_max=100):
        self.wordlist_size_max = cache_size_max
        self.restore_thesaurus_query_handler()
        self.query_backends = tq_backends.query_backends

    def query(self, word):
        if word in self.word_list:  # search word_list first to save query time
            return self.word_list[word]

        error_encountered = 0
        good_backends=[]
        faulty_backends=[]
        for query_backend_curr in self.query_backend_priority:  # query each of the backend list till found
            specified_language = get_variable("tq_language", ['en'])
            if specified_language!="All" and \
                    (self.query_backends[query_backend_curr].language not in \
                        specified_language):
                continue
            [state, synonym_list]=self.query_backends[query_backend_curr].query(word)
            if state == -1:
                error_encountered = 1
                faulty_backends.append(self.query_backends[query_backend_curr].identifier)
                continue
            if state == 0:
                good_backends.append(self.query_backends[query_backend_curr].identifier)
                break
        for faulty in faulty_backends:
            self.query_backend_priority.remove(faulty)
        self.query_backend_priority+=faulty_backends
        if int(get_variable("tq_raise_backend_priority_if_synonym_found",
                            0)) == 1:
            for good in good_backends:
                self.query_backend_priority.remove(good)
            self.query_backend_priority=good_backends+self.query_backend_priority
        if error_encountered == 1:
            vim_command('echohl WarningMSG | echon "WARNING: " | echohl None | echon "one or more query backends report error. Please check on thesaurus source(s).\n"')
        if 'state' not in locals():
            vim_command('echohl WarningMSG | echon "WARNING: " | echohl None | echon "No thesaurus source is used. Please check on your configuration on g:tq_enabled_backends and g:tq_language or b:tq_language.\n"')
            return []
        if state == 0:  # save to word_list buffer only when synonym is found
            self.word_list[word]=synonym_list
            self.word_list_keys.append(word)
            if len(self.word_list_keys) > self.wordlist_size_max:
                del self.word_list[self.word_list_keys.pop(0)]
        return synonym_list

    def restore_thesaurus_query_handler(self):
        self.query_backend_priority = get_variable(
            "tq_enabled_backends",
            ["woxikon_de","jeck_ru","thesaurus_com","mthesaur_txt"])
        self.word_list = {}  # hold wordlist obtained in previous query
        self.word_list_keys = []  # hold all keys for wordlist
                                  # in old->new order
        # depreciated variable

        local_as_primary = get_variable(
            'tq_use_local_thesaurus_source_as_primary')
        if local_as_primary=="1":
            self.query_backend_priority.remove("mthesaur_txt")
            self.query_backend_priority.insert(0,"mthesaur_txt")

def truncate_synonym_list(synonym_list):
    truncated_flag = 0
    # number of definitions retained in output
    truncate_on_definition = int(
        get_variable("tq_truncation_on_definition_num", -1))
    # number of synonyms retained for each definition in output
    truncate_syno_list = int(
        get_variable("tq_truncation_on_syno_list_size", -1))
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

def tq_word_form_reverse(target_word):
    '''
    adjust candidate according to trimmed word
    '''
    if independent_session:     # this module don't work in Vim independent session
        return None
    wordOriginal = decode_utf_8(vim.eval('l:trimmed_word'))
    if wordOriginal.isupper():
        return target_word.upper()
    elif wordOriginal[0].isupper():
        return target_word[0].upper()+target_word[1:]
    return target_word

def tq_candidate_list_populate(candidates):
    '''
    generate waitlist and result_IDed to be shown on message_box
    '''
    waitlist = []
    result_IDed = []
    word_ID = 0
    for syno_case in candidates:
        result_IDed.append([syno_case[0],[]])
        for word_curr in syno_case[1]:
            word_curr = tq_word_form_reverse(word_curr)
            result_IDed[-1][1].append(u"({0}){1}".format(word_ID, word_curr))
            waitlist.append(u"{0}".format(word_curr))
            word_ID+=1
    return [word_ID, waitlist, result_IDed]

def tq_replace_cursor_word_from_candidates(candidate_list):
    '''
    Using vim's color message box to populate a candidate list from found
    synonyms. Then ask user to choose suitable candidate to replace word under
    cursor.
    '''
    if independent_session:     # this module don't work in Vim independent session
        return None

    def candidate_list_printing(result_IDed):
        '''
        Print candidate list to the messagebox
        '''
        if independent_session:     # this module don't work in Vim independent session
            return None
        for case in result_IDed:
            if case[0] != u"":
                vim_command('call thesaurus_query#echo_HL("Keyword|Found as: |Directory|{0}|None|\\n")'.format(send_string_to_vim(case[0])))
            vim_command('call thesaurus_query#echo_HL("Keyword|Synonyms: |None|")')
            col_count = 10
            col_count_max = int(vim.eval("&columns"))
            for synonym_i in case[1]:
                if (col_count+len(synonym_i)+1)<col_count_max:
                    vim_command('echon "{0} "'.format(send_string_to_vim(synonym_i)))
                    col_count += len(synonym_i)+1
                else:
                    vim_command('echon "\n          {0} "'.format(send_string_to_vim(synonym_i)))
                    col_count = 10 + len(synonym_i)+1
            vim_command('echon "\n"')

    [truncated_flag, candidates] = truncate_synonym_list(candidate_list)

    [candidate_num, thesaurus_wait_list, syno_result_IDed] = tq_candidate_list_populate(candidates)

    vim_command("echon \"In line: ... \"|echohl Keyword|echon \"{0}\"|echohl None |echon \" ...\n\"".format(vim.current.line.replace('\\','\\\\').replace('"','\\"')))
    vim_command("call thesaurus_query#echo_HL(\"None|Candidates for |WarningMSG|{0}\\n|None\")".format(vim.eval("l:trimmed_word")))

    candidate_list_printing(syno_result_IDed)

    def obtain_user_choice(trunc_flag):
        ''' return user choice
        if KeyboardInterrupt is detect, return None as normal input
        '''
        try:
            if trunc_flag==0:
                thesaurus_user_choice=vim.eval("input('Type number and <Enter> (empty cancels): ')")
            else:
                thesaurus_user_choice = vim.eval("input('Type number and <Enter> (results truncated, Type `A<Enter>` to browse all results\nin split; empty cancels): ')")
        except KeyboardInterrupt:
            return None 
        return thesaurus_user_choice

    thesaurus_user_choice = obtain_user_choice(truncated_flag)

    if not thesaurus_user_choice:
        return
    if thesaurus_user_choice == "A":
        tq_generate_thesaurus_buffer(candidate_list)
        return
    try:
        thesaurus_user_choice=int(thesaurus_user_choice)
    except ValueError:
        vim_command('call thesaurus_query#echo_HL("WarningMSG|\n\nInvalid Input! |None|Ending synonym replacing session without making changes.")')
        return
    if thesaurus_user_choice>=candidate_num or thesaurus_user_choice<0:
        vim_command('call thesaurus_query#echo_HL("WarningMSG|\n\nInvalid Input! |None|Ending synonym replacing session without making changes.")')
        return
    current_line = vim.current.line
    current_cursor = vim.current.window.cursor
    word_original = vim.eval("l:trimmed_word")

    def find_word_over_cursor(target_word):
        ''' Try locate the word on current line
        '''
        state = False
        letter_iter = - current_line[current_cursor[1]:].find(target_word)
        if current_line[
                current_cursor[1]: current_cursor[1]-letter_iter].isspace():
            state = True
        else:
            for letter_iter in range(len(target_word)):
                if current_line[
                        current_cursor[1]-letter_iter :
                        current_cursor[1]-letter_iter+len(target_word)] == \
                        target_word:
                    state = True
                    break
        return [state, letter_iter]

    def remove_wrapped_part(target_word, layer):
        ''' Recursively remove wrapped content from the following lines
        '''
        def scan_current_layer():
            tail_found = False
            overlap_size = 0
            result_word = target_word
            word_split = target_word.split()
            line_split = vim.current.buffer[current_cursor[0]-1+layer].split()
            for overlap_size in range(
                    1, min( len(word_split)+1, len(line_split)+1)):
                if word_split[-overlap_size:] == line_split[:overlap_size]:
                    tail_found = True
                    result_word = ' '.join(
                        word_split[:len(word_split)-overlap_size])
                    vim.current.buffer[
                        current_cursor[0]-1+layer]=re.sub(
                            " ".join(
                                line_split[ : overlap_size])+r'\s*', '',
                            vim.current.buffer[ current_cursor[0]-1+layer]
                            , 1)
                    break
            return (tail_found, result_word)
        current_layer_tailored, remainder_target = scan_current_layer()
        if not current_layer_tailored:
            target_word = remove_wrapped_part(target_word, layer+1)
            current_layer_tailored, remainder_target = scan_current_layer()
            if not current_layer_tailored:
                return target_word
        return remainder_target

    word_in_one_line, relative_pos = find_word_over_cursor(word_original)
    if not word_in_one_line:
        unwrapped = remove_wrapped_part(word_original, 1)

        word_in_one_line, relative_pos = find_word_over_cursor(
            unwrapped)

    vim.current.buffer[current_cursor[0]-1] = \
            current_line[:current_cursor[1]-relative_pos] + \
            send_string_to_vim(
                thesaurus_wait_list[thesaurus_user_choice]) + \
                    current_line[
                        current_cursor[1]-relative_pos+len(word_original):
                        ]

def tq_generate_thesaurus_buffer(candidates):
    '''
    generate a buffer showing all found synonyms in the candidate list from
    query
    '''
    if independent_session:     # this module don't work in Vim independent session
        return None
    vim_command("silent! let l:thesaurus_window = bufwinnr('^thesaurus: ')")
    if int(vim.eval("l:thesaurus_window")) > -1:
        vim_command('exec l:thesaurus_window . "wincmd w"')
    else:
        vim_command('exec ":silent keepalt belowright split thesaurus:\\\\ " . l:word_fname')
    vim_command('exec ":silent file thesaurus:\\\\ " . l:word_fname . "\\\\ (press\\\\ q\\\\ to\\\\ close\\\\ this\\\\ split.)"')

    vim_command('setlocal noswapfile nobuflisted nospell nowrap modifiable nonumber foldcolumn=0')
    if vim_eval('exists("+relativenumber")')=='1':
        vim_command('setlocal norelativenumber')
    vim_command('setlocal buftype=nofile')

# obtain window dimension:
    win_width = int(vim_eval('winwidth(0)'))

# initialize buffer
    tq_thesaurus_buffer = vim.current.buffer
    del tq_thesaurus_buffer[:]

    def candidate_list_printing(word_list):
        """ Append a list of synonyms to the end of buffer,
        Acceptable structure:
            [ word1, word2, word3, ... ]
        """
        tq_thesaurus_buffer.append([""])
        tq_thesaurus_buffer[-1]='Synonyms: '
        column_curr = 10
        word_list_size = len(word_list)

        for word_curr in enumerate(word_list):
            if column_curr+len(word_curr[1])+2 >= win_width:
                tq_thesaurus_buffer.append(["          "])
                column_curr = 10
            if word_curr[0]<word_list_size-1 :
                tq_thesaurus_buffer[-1]+= \
                    send_string_to_vim(word_curr[1])+', '
                column_curr += len(word_curr[1])+2
            else:
                tq_thesaurus_buffer[-1]+= \
                    send_string_to_vim(word_curr[1])

    tq_thesaurus_buffer[-1]="Result for word \"{0}\" (press \"q\" to close this split)".format(vim.eval('l:word'))
    for case in candidates:
        tq_thesaurus_buffer.append([""])
        if not case[0]:
            candidate_list_printing(case[1])
            continue
        tq_thesaurus_buffer.append([""])
        tq_thesaurus_buffer[-1]='Found_as: {0}'.format(send_string_to_vim(case[0]))
        candidate_list_printing(case[1])
    vim_command("setlocal bufhidden=")
    vim_command("exec 'resize ' . (line('$'))")
    vim_command("nnoremap <silent> <buffer> q :q<CR>")
    vim_command("setlocal filetype=thesaurus")
    vim_command("normal! gg")
    vim_command("setlocal nomodifiable")

