# Python backend for looking up words in an online thesaurus. Idea from
# project vim-online_thesaurus by Anton Beloglazov <http://beloglazov.info/>.
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
# Version:      0.0.2
# Original idea: Anton Beloglazov <http://beloglazov.info/>

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
