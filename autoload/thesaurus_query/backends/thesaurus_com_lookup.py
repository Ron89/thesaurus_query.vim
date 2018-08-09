# python wrapper for word query from thesaurus.com
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]

'''
handler for lookup method: "_online_thesaurus_lookup". When query_from_source is called, return:
   [status, [[def_0, [synonym_0, synonym_1, ...]],  [def_1, [synonym_0, synonym_1, ...]], ...]]
status:
    0: normal,  synonym found, list will be returned as
    1: normal, synonym not found, return empty synonym list
    -1: unexpected result from query, return empty synonym list
synonym list = [def, list wordlist]
    def('str'): definition the synonyms belong to
    wordlist = [synonym_0, synonym_1, ...]: list of words belonging to a same definition
'''

try:
    from urllib2 import urlopen
    from urllib2 import URLError,HTTPError
    from StringIO import StringIO
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError,HTTPError
    from io import StringIO

try:
    from ..ext.thesaurus.thesaurus import Word
    dependencyMissing=False
except ModuleNotFoundError:
    dependencyMissing=True

import re
import socket
from ..tq_common_lib import decode_utf_8, fixurl, get_variable
from ..tq_common_lib import send_string_to_vim
#from online_thesaurus_lookup import online_thesaurus_lookup

identifier="thesaurus_com"
language="en"
_header_length=11    # length of "Definition:", current header of definition
_relavent_val_pos=9
_syno_pos=11

_timeout_period_default = 1.0

class _word_query_handler_thesaurus_lookup:
    '''
    handler for lookup method: "online_thesaurus_lookup.py". When query_from_source is called, return:
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
#        self.query_source_cmd = os.path.dirname(os.path.realpath(__file__))+"/online_thesaurus_lookup.sh"
        pass

    def query_cmd_handler(self, word):
        self.syno_list=[]
        if dependencyMissing is False:
            self.query_result = Word(word)

    def synonym_found(self):
        if dependencyMissing:
            return -1
        if self.query_result.data == []:
            return 1
        return 0

    def process_query_result(self):
        for itemIter in self.query_result.data:
            self.syno_list.append([
                itemIter['partOfSpeech']+'. ' + itemIter['meaning'],
                []])
            for synItem in itemIter['syn']:
                self.syno_list[-1][1].append(synItem.word)

    def query(self,word):
        self.query_cmd_handler(word)
        query_status = self.synonym_found()
        if query_status!=0:
            return [query_status, self.syno_list]
        self.process_query_result()
        return [0, self.syno_list]

_querier = _word_query_handler_thesaurus_lookup()
query = _querier.query
