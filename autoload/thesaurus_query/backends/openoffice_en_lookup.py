# Thesaurus lookup routine for OpenOffice thesaurus source.
# Author: HE Chong [[chong.he.1989@gmail.com][E-mail]]

'''
Lookup routine for local OpenOffice thesaurus file. When query_from_source is called, return:
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
import mmap
from ..tq_common_lib import decode_utf_8, encode_utf_8, get_variable

identifier="openoffice_en"
language = "en"

_oo_file = "/usr/share/myspell/dicts/th_en_US_v2"

def query(word):
    if not _oo_file_access():
        return [-1, []]
    index_file, data_file = _data_pair()
    with open(index_file) as index_opened:
        index = mmap.mmap(
            index_opened.fileno(), 0, access=mmap.ACCESS_READ
        )
        decorated = encode_utf_8(u''.join([u'\n',word,u'|']))
        found_loc = index.find(decorated)
        if found_loc==-1:
            index.close()
            return [1, []]
        index.seek(found_loc+1)
        item_index = int(index.readline().strip().split(
            encode_utf_8('|'))[1])
        index.close()
    query_result = list()
    with open(data_file) as data:
        data.seek(item_index)
        header = decode_utf_8(data.readline())
        num_groups = int(header.strip().split(u'|')[1])
        for i in range(num_groups):
            group = decode_utf_8(
                data.readline()).strip().split(u'|')
            query_result.append(
                [group[0][1:-1], [
                    _strip_descriptor(group_item)
                    for group_item in group[1:]]])
    return [0, query_result]

def _strip_descriptor(string):
    """ Strip additional information (usually wrapped in parenthesis) of the
    candidate from the candidate itself.
    """
    if string.find(u"(")!=-1:
        return string[:string.find(u"(")].strip()
    return string.strip()

def _oo_file_access():
    index_file, data_file = _data_pair()
    if os.access(index_file, os.R_OK) and os.access(data_file, os.R_OK):
        return True
    return False

def _data_pair():
    file_base = get_variable(
        "tq_openoffice_en_file",
        "/usr/share/myspell/dicts/th_en_US_v2")
    if file_base:
        file_base = os.path.expanduser(file_base)
    index_file = file_base+'.idx'
    data_file = file_base+'.dat'
    return (index_file, data_file)
