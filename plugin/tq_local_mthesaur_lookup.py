# Thesaurus Lookup routine for local mthesaur.txt file.
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
# Version:      0.0.3

import vim
import os

class word_query_mthesaur_lookup:
    '''
    Lookup routine for local mthesaur.txt file. When query_from_source is called, return:
       [status, [[def_0, [synonym_0, synonym_1, ...]],  [def_1, [synonym_0, synonym_1, ...]], ...]]
    status:
        0: normal,  synonym found, list will be returned as 
        1: normal, synonym not found, return empty synonym list
        -1: unexpected result from query, return empty synonym list
    synonym list = [def, list wordlist]
        def('str'): definition the synonyms belong to
        wordlist = [synonym_0, synonym_1, ...]: list of words belonging to a same definition
    '''
    def __init__(self):
        self.mthesaur_file="./mthesaurus.txt"
        self.identifier="mthesaur_default"
        self.mthesaur_verified = 0
        self.mthesaur_file_locate()

    def mthesaur_file_locate(self):
        if os.path.exists(self.mthesaur_file):
            self.mthesaur_verified = 1
            return
        if os.path.exists(os.path.expanduser(vim.eval("g:thesaurus_query#mthesaur_file"))):
            self.mthesaur_file = os.path.expanduser(vim.eval("g:thesaurus_query#mthesaur_file"))
            self.mthesaur_verified = 1
            return

        for mthesaur_file in vim.eval("&thesaurus").split(','):
            if "mthesaur.txt" in mthesaur_file:
                self.mthesaur_file=os.path.expanduser(mthesaur_file)
                self.mthesaur_verified = 1
                return
        self.mthesaur_verified = 0


    def query(self, word):
        if self.mthesaur_verified == 0:
            return [-1, []]
        match_found = 0
        thesaur_file = open(self.mthesaur_file, 'r')
        while True:
            line_curr=thesaur_file.readline()
            if not line_curr:
                break
            synonym_list = line_curr.rstrip("\r\n").split(',')
            if word in synonym_list:
                match_found = 1
                synonym_list.remove(word)
                break

        if match_found:
            return [0, [["", synonym_list]]]
        return [1, []]


