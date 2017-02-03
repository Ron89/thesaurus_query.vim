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
    from HTMLParser import HTMLParser
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError
    from io import StringIO
    from html.parser import HTMLParser

import re
import socket
from ..tq_common_lib import decode_utf_8, encode_utf_8, fixurl, get_variable

identifier="woxikon_de"
language="de"

_timeout_period_default = 10.0

try:
    from html import unescape
except ImportError:
    try:
        from html.parser import HTMLParser
    except ImportError:
        from HTMLParser import HTMLParser
    unescape = HTMLParser().unescape

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
    Query woxikon for sysnonym
    '''
    time_out_choice = float(get_variable(
        'tq_online_backends_timeout', _timeout_period_default))
    try:
        response = urlopen(fixurl(u'http://synonyms.woxikon.com/de/{0}'.format(target)).decode('ASCII'), timeout = time_out_choice)
        web_content = StringIO(unescape(decode_utf_8(response.read())))
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

def obtainGroups(webcontent, groupNum):
    synonym_list = []
    for group in range(groupNum):
        while not re.search("synonyms-list-group", webcontent.readline(), re.UNICODE):
            continue
        meaning = re.search("Meaning: <b>([^<]+)</b>", webcontent.readline(), re.UNICODE).group(1)
        webcontent.readline() # </div> line
        webcontent.readline() # synonyms-list_content line
        sublist = webcontent.readline().split(',')
        subSynList = []
        for wordContainer in sublist:
            potential_synonym = re.search("<a href=[^>]+>([^<]+)</a>", wordContainer, re.UNICODE)
            if potential_synonym:
                subSynList.append(potential_synonym.group(1))
        synonym_list.append([meaning, subSynList])
    return synonym_list

def _parser(webcontent):
    end_tag_count=4
    pointer = webcontent.tell()
    end = len(webcontent.getvalue())
    while pointer<end:
        line_curr = webcontent.readline()
        found = re.search("Found ([0-9]+) synonym[ a-z]+([0-9]+) group", line_curr, re.UNICODE)
        notFound = re.search("<div class=\"no-results\">", line_curr, re.UNICODE)
        if found:
            groupNum = int(found.group(2))
            synonymNum = int(found.group(1))
            synonym_list = obtainGroups(webcontent, groupNum)
            webcontent.close()
            return synonym_list
        if notFound:
            webcontent.close()
            return []

    webcontent.close()
    return synonym_list
