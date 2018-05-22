# python wrapper for word query from openthesaurus.de
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

identifier="openthesaurus_de"
language="de"

_timeout_period_default = 1.0

def query(target, query_method="synonym"):
    ''' return result as list. relavance from high to low in each PoS.
Lookup routine for openthesaurus.de. When query_from_source is called, return:
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
    result_list=_openthesaurus_api_wrapper(target, query_method=query_method)
    if result_list == -1:
        return [-1,[]]
    elif result_list == 1:
        return [1, []]
    else:
        return _parser(result_list, target)


def _openthesaurus_api_wrapper(target, query_method):
    '''
    query_method:
        synonym
    '''
    time_out_choice = float(get_variable(
        'tq_online_backends_timeout', _timeout_period_default))
    case_mapper={"synonym":u"synonyme",
                }
    try:
        response = urlopen(fixurl(
            u'https://www.openthesaurus.de/{0}/search?q={1}&format=application/json'.format(
                case_mapper[query_method], target
                )).decode('ASCII'), timeout = time_out_choice)
        reader = codecs.getreader('utf-8')
        result_list = json.load(reader(response))
        response.close()
    except HTTPError:
        return 1
    except URLError as err:
        if isinstance(err.reason, socket.timeout):
            return 1
        return -1
    except socket.timeout:  # timeout only means underperforming
        return 1
    return result_list


def _parser(target_list, target):
    target=target.replace(u"+", u" ")

    result = {}
    for synsetIter in enumerate(target_list['synsets']):
        termList=[]
        for termIter in synsetIter[1]["terms"]:
            if termIter['term'].lower() != target.lower():
                termList.append(termIter['term'])
        if termList:
            result["Category {}: {}".format(
                synsetIter[0], 
                u','.join(synsetIter[1]['categories']))]=termList
    if not result:
        return [1, []]
    output = [0,[]]
    for item in sorted(result.keys()):
        output[1].append([item,result[item]])
    return output
