# Thesaurus Lookup routine for local mthesaur.txt file.
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

identifier="cilin_txt"
language="cn"

_header_len=9  # length of line number information

def query(word):
    _cilin_verified, _cilin_file = _cilin_file_locate()
    if not _cilin_verified:
        return [-1, []]
    match_found = 0
    thesaur_file = open(os.path.expanduser(_cilin_file), 'r')
    while True:
        line_curr=decode_utf_8(thesaur_file.readline())[_header_len:]
        if not line_curr:
            break
        synonym_list = line_curr.rstrip(u"\r\n").split(u' ')
        if word in synonym_list:
            match_found = 1
            synonym_list.remove(word)
            break

    if match_found:
        return [0, [[u"", synonym_list]]]
    return [1, []]

def _cilin_file_locate():
    verified_file = get_variable(
        "tq_cilin_txt_file",
        "~/.vim/thesaurus/cilin.txt")
    if os.path.exists(os.path.expanduser(verified_file)):
        return (True, verified_file)

    for thesaurus_file in get_variable("&thesaurus").split(','):
        if "cilin.txt" in thesaurus_file:
            if os.path.exists(os.path.expanduser(thesaurus_file)):
                verified_file = os.path.expanduser(thesaurus_file)
                return (True, verified_file)
    return (False, None)


# initiation ------------
_cilin_file_locate()
