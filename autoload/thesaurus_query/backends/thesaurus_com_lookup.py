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
        query_result_raw = _online_thesaurus_lookup(word)
        self.query_result = StringIO(query_result_raw)

    def synonym_found(self):
        first_line = self.query_result.readline()
        if first_line != u'\n':
            if u"Internet Error." in first_line:
                self.query_result.close()
                return -1
            self.query_result.close()
            return 1
        return 0

    def syno_populating(self):
        word_dic={}
        syno_list_curr=[]
        self.query_result.readline()  # skip the line 'Synonyms:'
        while True:
            self.line_curr = self.query_result.readline()
            if self.line_curr[:_relavent_val_pos] != u"relevant-":
                break
            self.line_curr=self.line_curr.rstrip(u'\n')
            if self.line_curr[_relavent_val_pos] in word_dic.keys():
                word_dic[self.line_curr[_relavent_val_pos]].append(self.line_curr[_syno_pos:])
            else:
                word_dic[self.line_curr[_relavent_val_pos]]=[self.line_curr[_syno_pos:]]
        # truncate on which relavance level?
        truncation_on_relavance=int(
            get_variable("tq_truncation_on_relavance", '0')) 
        for key in sorted(word_dic, reverse=True):
            if int(key) <= truncation_on_relavance:
                continue
            syno_list_curr=syno_list_curr+word_dic[key]     # sorted
        del word_dic
        return syno_list_curr

    def process_query_result(self):
        status = True
        self.line_curr=self.query_result.readline()
        while self.line_curr and status:
            if self.line_curr[:_header_length] == u'Definition:':
                self.line_curr=self.line_curr.rstrip(u'\n')
                definition_curr = self.line_curr[_header_length+1:]
                self.syno_list.append([definition_curr, []])
                self.syno_list[-1][1] = self.syno_populating()
                status = bool(status)
            else:
                self.line_curr=self.query_result.readline()
        self.query_result.close()
        return status and bool(self.syno_list)
    def query(self,word):
        self.query_cmd_handler(word)
        query_status = self.synonym_found()
        if query_status!=0:
            return [query_status, self.syno_list]
        if self.process_query_result():
            return [0, self.syno_list]
        return [1, []]

_querier = _word_query_handler_thesaurus_lookup()
query = _querier.query

def _online_thesaurus_lookup(target):
    '''
    Direct query from thesaurus.com. All returns are decoded with utf-8.
    '''
    output = u""
    time_out_choice = float(get_variable(
        'tq_online_backends_timeout', _timeout_period_default))

    try:
        response = urlopen(fixurl(u'http://www.thesaurus.com/browse/{0}'.format(target)).decode('ASCII'), timeout = time_out_choice)
        parser = StringIO(decode_utf_8(response.read()))
        response.close()
    except HTTPError:
        output = u"The word \"{0}\" has not been found on dictionary.com!\n".format(target)
        return output
    except URLError as err:
        if isinstance(err.reason, socket.timeout):
            return u"Timeout!"
        output = u"Internet Error. The word \"{0}\" has not been found on dictionary.com!\n".format(target)
        return output
    except socket.timeout:  # timeout only means underperforming
        return u"Timeout!"

    end_tag_count=2
    while True:
        line_curr = parser.readline()
        if not line_curr:
            break
        if u"no thesaurus results" in line_curr:
            output = u"The word \"{0}\" has not been found on thesaurus.com!\n".format(target)
            break
        if u"synonym-description" in line_curr:
            end_tag_count=0
            continue
        elif end_tag_count<2:
            if u"</div>" in line_curr:
                end_tag_count+=1
                continue
            fields = re.split(u"<|>|&quot;", line_curr)
            if len(fields)<3:
                continue
            elif len(fields)<10:
                if u"txt" in fields[1]:
                    output+=u"\nDefinition: {0}. ".format(fields[2])
                    continue
                elif u"ttl" in fields[1]:
                    output+=u"{0}\nSynonyms:\n".format(fields[2])
                    continue
            elif u"www.thesaurus.com" in fields[3]:
                output+=u"{0} {1}\n".format(fields[6], fields[14])
    parser.close()
    return output
