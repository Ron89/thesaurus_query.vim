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
import ssl
from ..tq_common_lib import fixurl, get_variable

query_result_trunc=100
identifier="merriam_webster"
language="en"

_timeout_period_default = 1.0
time_out_choice = float(get_variable('tq_online_backends_timeout', _timeout_period_default))
api_key = get_variable('tq_merriam_webster_api_key', '')

def query(target):
    ''' 
    Queries the Merriam Webster API to retrieve thesaurus results for the target word.
    Requires the `tq_merriam_webster_api_key` to be set to an appropriate value.
    Returns Status code and two lists: synonyms and antonyms. Both lists are broken up into their
    appropriate word definitions.

    Note: If no word matches the target, the API may return substitute words. If this happens, both
    synonyms and antonyms will list those words under the "Unknown Word" heading.
    '''
    if not target or target == '':
        return [1, [], []]
    target=target.replace(u" ", u"+")
    result_list=_dictionary_api_wrapper(target)
    if result_list == -1:
        return [-1, [], []]
    elif result_list == 1:
        return [1, [], []]
    else:
        return _parser(result_list)


def _dictionary_api_wrapper(target):
    if api_key == '':
        return [-1, []]
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
        return -1
    except socket.timeout:  # timeout only means underperforming
        return 1
    return result_list

def _parseAntonyms(result_dict):
    defs = result_dict.get(u'shortdef', [])
    ants_list = result_dict.get(u'meta', {}).get(u'ants', [])
    length = min(len(defs), len(ants_list))
    return [ [ defs[idx]+' ('+ result_dict.get(u'fl', '') +')', ants_list[idx] ] for idx in range(length) if len(ants_list) > 0 ]

def _parseSynonyms(result_dict):
    defs = result_dict.get(u'shortdef', [])
    syns_list = result_dict.get(u'meta', {}).get(u'syns', [])
    length = min(len(defs), len(syns_list))
    return [ [ defs[idx]+' ('+ result_dict.get(u'fl', '') +')', syns_list[idx] ] for idx in range(length) if len(syns_list) > 0 ]

def _parser(result):
    if result is None or len(result) == 0:
        return [1, [], []]
    result_dict = result[0]
    if not result_dict:
        return [1, [], []]
    if isinstance(result_dict, str):
        return [0, [['Unknown word (did you mean):', result]], [['Unknown word (did you mean):', result]]]
    return [ 0, 
             [pair for r_dict in result for pair in _parseSynonyms(r_dict)],
             [pair for r_dict in result for pair in _parseAntonyms(r_dict)]
           ]
