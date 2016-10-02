# Python backend for looking up words in an online thesaurus. 
#
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]

try:
    import vim
    independent_session = False
except ImportError:
    independent_session = True

import re
from . import backends as tq_backends
import unicodedata as _unicode_data
from .tq_common_lib import decode_utf_8, encode_utf_8, send_string_to_vim, get_variable, vim_command, vim_eval

_double_width_type = ["Lo"]
query_session=list()

class Thesaurus_Query_Handler:
    ''' Handler for thesaurus_query
    Description:
        It interfaces the query request from vim with default query routine or
        other user defined routine when word.
    '''

    def __init__(self):
        ''' Initialize handler, load all available backends. '''
        self.restore_thesaurus_query_handler()
        self.query_backends = tq_backends.query_backends
        self._session_inited=False

    def session_init(self):
        ''' Initiate a query session, will be called at start of a query. '''
        if self._session_inited:
            return
        self.good_backends = []
        self.bad_backends = []
        self.backend_in_line = self.query_backend_priority[:]
        self.last_valid_result = []
        self._session_inited = True

    def session_terminate(self):
        ''' Terminate a query session, adjust query backend priority according
        to query result'''
        if not self._session_inited:
            return

#       if int(get_variable("tq_raise_backend_priority_if_synonym_found",
#                           0)) == 1:
#           for good in good_backends:
#               self.query_backend_priority.remove(good)
#           self.query_backend_priority=good_backends+self.query_backend_priority
        self.query_backend_priority = \
                self.good_backends+self.backend_in_line+self.bad_backends
        del self.good_backends
        del self.bad_backends
        del self.backend_in_line
        self._session_inited = False

    def query(self, word, next=True, use_cache=True):
        """ Query from enabled backend one by one until synonym found
        return:
            synonym_list
        """
        found = False
        if not self._session_inited:
            self.session_init()  # start a session if not started
        # word not found, start searching
        error_encountered = 0
# use session-wise backend management to prepare for current query
        if next:
            to_use_list = self.backend_in_line[:]
            success_list = self.good_backends[:]
            if len(to_use_list)==0:
                return self.last_valid_result
        else:
            to_use_list = self.good_backends[::-1]
            success_list = self.backend_in_line[::-1]
            if len(to_use_list)<=1:
                return self.last_valid_result
            success_list.append(to_use_list.pop(0))
        local_bad_backends=[]
        for query_backend_curr in to_use_list:  # query each of the backend list till found
            specified_language = get_variable("tq_language", ['en'])
            if specified_language!="All" and \
                    (self.query_backends[query_backend_curr].language not in \
                        specified_language):
                continue
            [state, synonym_list]=self.query_backends[query_backend_curr].query(word)
            if state == -1:
                error_encountered = 1
                local_bad_backends.append(
                    self.query_backends[query_backend_curr].identifier)
                continue
            if state == 0:
                found = True
                if next:
                    success_list.append(
                        self.query_backends[query_backend_curr].identifier)
                break
        if found and next:
            to_use_list.remove(success_list[-1])

        if (not found) and (not next):
            to_use_list.insert(0, success_list.pop())

        for used_backend in local_bad_backends:
            to_use_list.remove(used_backend)
# update session-wise backends management
        self.bad_backends=local_bad_backends+self.bad_backends
        if next:
            self.backend_in_line = to_use_list
            self.good_backends = success_list
        else:
            self.good_backends = to_use_list[::-1]
            self.backend_in_line = success_list[::-1]
        if 'state' not in locals():
            if not self.last_valid_result:
                vim_command('echohl WarningMSG | echon "WARNING: " | echohl None | echon "No thesaurus source is used. Please check on your configuration on g:tq_enabled_backends and g:tq_language or b:tq_language.\n"')
            return self.last_valid_result
        if not synonym_list:    # update last valid result if positive result is found
            return self.last_valid_result
        else:
            self.last_valid_result=synonym_list

        return synonym_list

    def restore_thesaurus_query_handler(self):
        self.query_backend_priority = get_variable(
            "tq_enabled_backends",
            ["woxikon_de","jeck_ru","thesaurus_com","openoffice_en","mthesaur_txt"])
        local_as_primary = get_variable(
            'tq_use_local_thesaurus_source_as_primary')
        if local_as_primary=="1":
            self.query_backend_priority.remove("mthesaur_txt")
            self.query_backend_priority.insert(0,"mthesaur_txt")

def truncate_synonym_list(synonym_list):
    """ Truncate synonym_list according to user truncation settings
    return:
        [truncated_flag, truncated_list]
        truncated_flag:
            0 -> no truncation is made
            1 -> valid truncation is made
    """
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
    ''' adjust candidate to match trimmed word's case(upper/lower/mixed) '''
    if independent_session:     # this module don't work in Vim independent session
        return None
    wordOriginal = decode_utf_8(vim.eval('l:trimmed_word'))
    if wordOriginal.isupper():
        return target_word.upper()
    elif wordOriginal[0].isupper():
        return target_word[0].upper()+target_word[1:]
    return target_word

def tq_candidate_list_populate(candidates):
    ''' generate IDed waitlist and prepare it to show on message_box
    return:
        [largest_ID, candidate_waitlist, IDed_candidate_waitlist]
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

def _double_width_char_count(word):
    dw_count = 0
    for char in word:
        if _unicode_data.category(char) in _double_width_type:
            dw_count += 1
    return dw_count

def tq_replace_cursor_word_from_candidates(candidate_list, source_backend=None):
    ''' populate candidate list, replace target word/phrase with candidate
    Description:
        Using vim's color message box to populate a candidate list from found
        synonyms. Then ask user to choose suitable candidate to replace word
        under cursor.

        Return:
            0: signal Vim to terminate query session
            1: use next backend, continue session
            2: use previous backend, continue session
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
                if (col_count+len(synonym_i)+_double_width_char_count(synonym_i)+1)<col_count_max:
                    vim_command('echon "{0} "'.format(send_string_to_vim(synonym_i)))
                    col_count += len(synonym_i)+_double_width_char_count(synonym_i)+1
                else:
                    vim_command('echon "\n          {0} "'.format(send_string_to_vim(synonym_i)))
                    col_count = 10 + len(synonym_i)+_double_width_char_count(synonym_i)+1
            vim_command('echon "\n"')

    [truncated_flag, candidates] = truncate_synonym_list(candidate_list)

    [candidate_num, thesaurus_wait_list, syno_result_IDed] = tq_candidate_list_populate(candidates)

    vim_command("echon \"In line: ... \"|echohl Keyword|echon \"{0}\"|echohl None |echon \" ...\n\"".format(vim.current.line.replace('\\','\\\\').replace('"','\\"')))
    vim_command("echohl None| echon \"Candidates for \"| echohl WarningMSG | echon \"{0}\" | echohl None | echon \", found by backend: \" | echohl Keyword | echon \"{1}\n\"".format(
        vim.eval("l:trimmed_word").replace('\\','\\\\').replace('"','\\"'),
        source_backend
    ))

    candidate_list_printing(syno_result_IDed)

    def obtain_user_choice(trunc_flag):
        ''' return user choice
        if KeyboardInterrupt is detect, return None as normal input
        '''
        try:
            if trunc_flag==0:
                thesaurus_user_choice=vim.eval("input(\"Type number and <Enter> (empty cancels; 'n': use next backend; 'p' use previous backend): \")")
            else:
                thesaurus_user_choice = vim.eval("input('Type number and <Enter> (results truncated, Type `A<Enter>` to browse all resultsin split;\nempty cancels; 'n': use next backend; 'p' use previous backend): ')")
        except KeyboardInterrupt:
            return None
        return thesaurus_user_choice

    thesaurus_user_choice = obtain_user_choice(truncated_flag)

    if not thesaurus_user_choice:
        return 0
    elif thesaurus_user_choice == "A":
        tq_generate_thesaurus_buffer(candidate_list)
        return 0
    elif thesaurus_user_choice == "n":
        return 1
    elif thesaurus_user_choice == "p":
        return 2
    try:
        thesaurus_user_choice=int(thesaurus_user_choice)
    except ValueError:
        vim_command("redraw")
        vim_command('call thesaurus_query#echo_HL("WarningMSG|Invalid Input! |None|Ending synonym replacing session without making changes.")')
        return 0
    if thesaurus_user_choice>=candidate_num or thesaurus_user_choice<0:
        vim_command("redraw")
        vim_command('call thesaurus_query#echo_HL("WarningMSG|Invalid Input! |None|Ending synonym replacing session without making changes.")')
        return 0
    current_line = encode_utf_8(vim.current.line)
    current_cursor = vim.current.window.cursor
    word_original = encode_utf_8(vim.eval("l:trimmed_word"))

    def find_word_over_cursor(target_word):
        ''' Try locate the word on current line
        '''
        state = False
        letter_iter = - current_line[current_cursor[1]:].find(target_word)
        if (letter_iter!=1) and not decode_utf_8(current_line[
                current_cursor[1]: current_cursor[1]-letter_iter]).isalpha():
            state = True
        else:
            for letter_iter in range(len(target_word)):
                if current_line[
                        current_cursor[1]-letter_iter:
                        current_cursor[1]-letter_iter+len(target_word)] == \
                        target_word:
                    state = True
                    break
        return [state, letter_iter]

    def remove_wrapped_part(target_word, layer):
        ''' Recursively remove wrapped content from the following lines
        '''
        def scan_current_layer(find_tail):
            '''
            for letter based languages that space used for separator
            '''
            tail_found = False
            overlap_size = 0
            result_word = target_word
            word_split = target_word.split()
            line_split = vim.current.buffer[current_cursor[0]-1+layer].split()
            for overlap_size in range(
                    1, min(len(word_split)+1, len(line_split)+1)):
                if word_split[-overlap_size:-1] == line_split[:overlap_size-1]:
                    if find_tail:
                        if word_split[-1] in line_split[overlap_size-1]:
                            tail_found = True
                    elif word_split[-1] == line_split[overlap_size-1]:
                        tail_found = True
                if tail_found:
                    result_word = ' '.join(
                        word_split[:len(word_split)-overlap_size])
                    vim.current.buffer[
                        current_cursor[0]-1+layer]=send_string_to_vim(
                            re.sub(
                                " ".join(
                                    word_split[-overlap_size:])+r'\s*', '',
                                decode_utf_8(vim.current.buffer[current_cursor[0]-1+layer]), 1
                            ))
                    break
            return (tail_found, result_word)
        current_layer_tailored, remainder_target = scan_current_layer(True)
        if not current_layer_tailored:
            target_word = remove_wrapped_part(target_word, layer+1)
            current_layer_tailored, remainder_target = scan_current_layer(False)
            if not current_layer_tailored:
                return target_word
        return remainder_target

    word_in_one_line, relative_pos = find_word_over_cursor(word_original)
    if not word_in_one_line:
        unwrapped = remove_wrapped_part(word_original, 1)

        word_in_one_line, relative_pos = find_word_over_cursor(
            unwrapped)

    vim.current.buffer[current_cursor[0]-1] = \
            send_string_to_vim(current_line[:current_cursor[1]-relative_pos]) + \
            send_string_to_vim(
                thesaurus_wait_list[thesaurus_user_choice]) + \
                    send_string_to_vim(current_line[
                        current_cursor[1]-relative_pos+len(word_original):
                        ])
    return 0

def tq_generate_thesaurus_buffer(candidates):
    ''' generate a buffer in Vim to show all found synonyms from query '''
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
        tq_thesaurus_buffer[-1]='Synonyms:'
        column_curr = 10
        word_list_size = len(word_list)

        for word_curr in enumerate(word_list):
            if column_curr+len(word_curr[1])+_double_width_char_count(word_curr[1])+2 >= win_width:
                tq_thesaurus_buffer.append(["         "])
                column_curr = 10
            if word_curr[0]<word_list_size-1:
                tq_thesaurus_buffer[-1]+= \
                    send_string_to_vim(''.join([' ', word_curr[1], ',']))
                column_curr += len(word_curr[1])+_double_width_char_count(word_curr[1])+2
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
