# -*- coding: utf-8 -*-
#
# python wrapper for word query from woxikon.de
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
#
#
# Note: woxikon.de provides good quality synonym list. But it does not stem
# word. German is a language with highly complicated word derivative rules,
# hence this online service alone might not provide good-enough result list.

try:
    from urllib2 import urlopen
    from urllib2 import URLError, HTTPError
    from StringIO import StringIO
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError
    from io import StringIO

import re
import socket
from thesaurus_query.tq_common_lib import decode_utf_8, encode_utf_8, fixurl, get_variable

identifier="woxikon_de"
language="de"

def query(target):
    ''' return result as list. relavance from high to low in each PoS.
Lookup routine for datamuse.com. When query_from_source is called, return:
   [status, [[PoS, [word_0, word_1, ...]],  [PoS, [word_0, word_1, ...]], ...]]
status:
    0: normal,  result found, list will be returned as a nested list
    1: normal, result not found, return empty list
    -1: unexpected result from query, return empty list
nested list = [PoS, list wordlist]
    Classifier('str'): Identifier to classify the resulting wordlist suits.
    wordlist = [word_0, word_1, ...]: list of words belonging to a same definition
    '''
    target=target.replace(u" ", u"+")
    result_list=_woxikon_de_url_handler(target)
    if result_list == -1:
        return [-1, []]
    elif result_list == 1:
        return [1, []]
    else:
        synonym_list = _parser(result_list)
        if synonym_list:
            return [0, synonym_list]
        else:
            return [1, []]

def _woxikon_de_url_handler(target):
    '''
    Query jiport for sysnonym
    '''
    time_out_choice = float(get_variable('tq_online_backends_timeout'))
    try:
        response = urlopen(fixurl(u'http://synonyme.woxikon.de/synonyme/{0}.php'.format(target)).decode('ASCII'), timeout = time_out_choice)
        web_content = StringIO(decode_utf_8(response.read()))
        response.close()
    except HTTPError:
        return 1
    except URLError as err:
        if isinstance(err.reason, socket.timeout):  # timeout error?
            return 1
        return -1   # other error
    except socket.timeout:  # timeout error failed to be captured by URLError
        return 1
    return web_content


def _parser(webcontent):
    end_tag_count=4
    synonym_list = []
    while True:
        line_curr = webcontent.readline()
        if not line_curr:
            break
        if u"Keine Synonyme gefunden" in line_curr:
            break
        if u"synonymsGroupNum" in line_curr:
            end_tag_count=0
            synonym_list.append([u"",[]])
            continue
        elif end_tag_count<4:
            if u"</div>" in line_curr:
                end_tag_count+=1
            fields = re.split(u"<|>", line_curr)
            if len(fields)>2:
                if u'class="meaning"' in fields[1]:
                    synonym_list[-1][0] = fields[6]
                    continue
                if u'class="groupWordType"' in line_curr:
                    synonym_list[-1][0] = fields[2] + u' ' + synonym_list[-1][0]
                    continue
                if u'http://synonyme.woxikon.de/synonyme' in fields[1]:
                    if u'strong' not in line_curr:
                        synonym_list[-1][1].append(fields[2])
            if end_tag_count==4:
                if not synonym_list[-1][1]:
                    del synonym_list[-1]
    webcontent.close()
    return synonym_list
