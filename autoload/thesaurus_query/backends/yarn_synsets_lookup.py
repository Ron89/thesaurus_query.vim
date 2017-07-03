# Thesaurus Lookup routine for local synsets.csv file.
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]

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

import os
from ..tq_common_lib import decode_utf_8, get_variable

identifier="yarn_synsets"
language="ru"

def query(word):
    _synsets_valid , _synsets_file = _synsets_file_locate()
    if not _synsets_valid:
        return [-1, []]
    match_found = 0
    thesaur_file = open(os.path.expanduser(_synsets_file), 'r')
    found_synDict=dict()
    thesaur_file.readline()  # discard first line
    while True:
        line_curr=decode_utf_8(thesaur_file.readline())
        if not line_curr:
            break
        line_data = line_curr.rstrip().split(u',')
        synonym_list = line_data[1].split(u';')
        grammar = line_data[2]
        wordDomain = line_data[3]
        if word in synonym_list:
            synonym_list.remove(word)
            dict_keyword = u"{0}{1}".format(grammar, wordDomain) if \
                    (len(grammar)*len(wordDomain)==0) else \
                    u"{0}, {1}".format(grammar, wordDomain)
            if synonym_list:
                for synonym in synonym_list:
                    if dict_keyword not in found_synDict:
                        found_synDict[dict_keyword]=[synonym]
                    elif synonym not in found_synDict[dict_keyword]:
                        found_synDict[dict_keyword].append(synonym)
        else:
            continue
    found_synList = [[entryKey, found_synDict[entryKey]] 
            for entryKey in found_synDict]
    
    # merge
    return [0 if len(found_synList) else 1, found_synList]

def _synsets_file_locate():
    verified_file = get_variable(
        "tq_yarn_synsets_file",
        "~/.vim/thesaurus/yarn-synsets.csv")
    if os.path.exists(os.path.expanduser(verified_file)):
        return (True, verified_file)

    return (False, None)


# initiation ------------
_synsets_file_locate()
