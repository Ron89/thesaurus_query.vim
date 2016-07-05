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
import vim
import socket
from thesaurus_query.tq_common_lib import decode_utf_8, fixurl, get_variable
from thesaurus_query.tq_common_lib import send_string_to_vim
#from online_thesaurus_lookup import online_thesaurus_lookup

identifier="thesaurus_com"
language="en"
_header_length=11    # length of "Definition:", current header of definition
_relavent_val_pos=9
_syno_pos=11


def query(word):
    _query_result = _query_cmd_handler(word)
    syno_list=[]

    def syno_populating():
        word_dic={}
        syno_list_curr=[]
        _query_result.readline()  # skip the line 'Synonyms:'
        while True:
            line_curr = _query_result.readline()
            if line_curr[:_relavent_val_pos] != u"relevant-":
                break
            line_curr=line_curr.rstrip(u'\n')
            if line_curr[_relavent_val_pos] in word_dic.keys():
                word_dic[line_curr[_relavent_val_pos]].append(line_curr[_syno_pos:])
            else:
                word_dic[line_curr[_relavent_val_pos]]=[line_curr[_syno_pos:]]
        truncation_on_relavance=int(vim.eval("g:tq_truncation_on_relavance")) # truncate on which relavance level?
        for key in sorted(word_dic, reverse=True):
            if int(key) <= truncation_on_relavance:
                continue
            syno_list_curr=syno_list_curr+word_dic[key]     # sorted
        del word_dic
        return [not not syno_list_curr, syno_list_curr]

    def process_query_result():
        status = True
        line_curr=_query_result.readline()
        while not (not line_curr or not status):
            if line_curr[:_header_length] == u'Definition:':
                line_curr=line_curr.rstrip(u'\n')
                definition_curr = line_curr[_header_length+1:]
                syno_list.append([definition_curr, []])
                [status, syno_list[-1][1]] = syno_populating()
            else:
                line_curr=_query_result.readline()
        _query_result.close()
        return status and not not syno_list

    query_status = _synonym_found(_query_result)
    if query_status!=0:
        return [query_status, syno_list]
    if process_query_result():
        return [0, syno_list]
    return [1, []]

def _synonym_found(query_result):
    first_line = query_result.readline()
    if first_line != u'\n':
        if u"Internet Error." in first_line:
            query_result.close()
            return -1
        query_result.close()
        return 1
    return 0

def _query_cmd_handler(word):
    query_result_raw = _online_thesaurus_lookup(word)
    return StringIO(query_result_raw)

def _online_thesaurus_lookup(target):
    '''
    Direct query from thesaurus.com. All returns are decoded with utf-8.
    '''
    output = u""
    time_out_choice = float(get_variable('tq_online_backends_timeout'))

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
