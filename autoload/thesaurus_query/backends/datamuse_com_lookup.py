# python wrapper for word query from datamuse.com
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]


try:
    from urllib2 import urlopen
    from urllib2 import URLError, HTTPError
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError
import json
import socket
import codecs
from ..tq_common_lib import fixurl, decode_utf_8, get_variable

query_result_trunc=50
identifier="datamuse_com"
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
    result_list=_datamuse_api_wrapper(target, query_method=query_method)
    if result_list == -1:
        return [-1,[]]
    elif result_list == 1:
        return [1, []]
    else:
        return _parser(result_list)


def _datamuse_api_wrapper(target, query_method, max_return=query_result_trunc):
    '''
    query_method:
        synonym, antonym, suggest, right_content, left_content
    '''
    time_out_choice = float(get_variable(
        'tq_online_backends_timeout', _timeout_period_default))
    case_mapper={"synonym":u"words?rel_syn=",
                 "suggest":u"sug?s=",
                 "antonym":u"words?rel_ant=",
                 "right_content":u"words?rc=",
                 "left_content":u"words?lc="
                }
    try:
        response = urlopen(fixurl(
            u'http://api.datamuse.com/{0}{1}&max={2}'.format(
                case_mapper[query_method], target, max_return
                )).decode('ASCII'), timeout = time_out_choice)
        reader = codecs.getreader('utf-8')
        result_list = json.load(reader(response))
        response.close()
    except HTTPError:
        return 1
    except URLError as err:
        if isinstance(err.reason, socket.timeout):
            return 1
#        print(u"Internet Error. The word \"{0}\" has not been found on datamuse!\n".format(target))
        return -1
    except socket.timeout:  # timeout only means underperforming
        return 1
    return result_list


def _parser(target_list):
    target_list.sort(key=lambda x: x[u'score'], reverse=True)
    result = {}
    for word in target_list:
        if u'partsOfSpeech' in word:
            for i in word[u'partsOfSpeech']:
                if i in result:
                    result[i].append(word[u'word'])
                else:
                    result[i]=[word[u'word']]
        elif u'' in result:
            result[u''].append(word[u'word'])
        else:
            result[u''] = [word[u'word']]
    if not result:
        return [1, []]
    if u'' in result:
        output = [0, [[u'',result.pop(u'')]]]
    else:
        output = [0,[]]
    for item in result:
        output[1].insert(0,[item,result[item]])
    return output
