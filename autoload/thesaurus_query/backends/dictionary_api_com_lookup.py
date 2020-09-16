# python wrapper for word query from dictionaryapi.com
# Author:       Aaron Hayman [[ahayman@gmail.com][E-mail]]


try:
    from urllib2 import urlopen
    from urllib2 import URLError, HTTPError
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError
import json
import socket
import codecs
import ssl
from ..tq_common_lib import fixurl, get_variable

query_result_trunc=100
identifier="dictionary_api_com"
language="en"

_timeout_period_default = 1.0

def query(target, query_method="synonym"):
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
    result_list=_dictionary_api_wrapper(target, query_method=query_method)
    if result_list == -1:
        return [-1,[]]
    elif result_list == 1:
        return [1, []]
    else:
        return _parser(result_list)


def _dictionary_api_wrapper(target, query_method, max_return=query_result_trunc):
    api_key = get_variable('tq_dictionary_api_key', '')
    if api_key == '':
        return [-1, []]
    time_out_choice = float(get_variable(
        'tq_online_backends_timeout', _timeout_period_default))
    case_mapper={"synonym":u"words?rel_syn=",
                 "suggest":u"sug?s=",
                 "antonym":u"words?rel_ant=",
                 "right_content":u"words?rc=",
                 "left_content":u"words?lc="
                }
    try:
        url = fixurl(u'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{0}?key={1}'.format(target, api_key)).decode('ASCII') 
        response = urlopen(url, context=ssl.SSLContext(), timeout = time_out_choice).read()
        result_list = json.loads(response.decode('utf-8'))
    except HTTPError:
        return 1
    except URLError as err:
        if isinstance(err.reason, socket.timeout):
            return 1
        print(err)
#        print(u"Internet Error. The word \"{0}\" has not been found on datamuse!\n".format(target))
        return -1
    except socket.timeout:  # timeout only means underperforming
        return 1
    return result_list


def _parser(result):
    result_dict = result[0]
    if not result_dict:
        return [1, []]
    syns = [syn for arr in result_dict[u'meta'][u'syns'] for syn in arr]
    ants = [ant for arr in result_dict[u'meta'][u'ants']for ant in arr]
    sseqs = [d[u'sseq'] for d in result_dict[u'def'] if d[u'sseq']]
    flattened = [d for a in sseqs for b in a for c in b for d in c if isinstance(d,dict)]
    near_lists = [d[u'near_list'] for d in flattened if d[u'near_list']]
    rel_lists = [d[u'rel_list'] for d in flattened if d[u'rel_list']]
    nears = [d[u'wd'] for arr in near_lists for c in arr for d in c if d[u'wd']]
    rels = [d[u'wd'] for arr in rel_lists for c in arr for d in c if d[u'wd']]
    return [0,
        [ 'Synonyms', syns],
        [ 'Related', rels],
        [ 'Near', nears],
        [ 'Antonyms', ants]
    ]
