# python wrapper for word query in datamuse.com
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]

import urllib2
import json
#import vim

query_result_trunc=50
identifier="datamuse_com"

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
    target=target.replace(" ", "+")
    result_list=datamuse_api_wrapper(target, query_method=query_method)
    if result_list == -1:
        return [-1,[]]
    else:
        return parser(result_list)


def datamuse_api_wrapper(target, query_method, max_return=query_result_trunc):
    '''
    query_method:
        synonym, antonym, suggest, right_content, left_content
    '''
    case_mapper={"synonym":"words?rel_syn=",
            "suggest":"sug?s=",
            "antonym":"words?rel_ant=",
            "right_content":"words?rc=",
            "left_content":"words?lc="
            }
    try:
        response = urllib2.urlopen(
                'http://api.datamuse.com/{}{}&max={}'.format(
                    case_mapper[query_method], target, max_return
                    ))
    except urllib2.URLError, error:
        print u"Internet Error. The word \"{}\" has not been found on datamuse!\n".format(target)
        return -1
    result_list = json.load(response)
    return result_list


def parser(target_list):
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
    if '' in result:
        output = [0, [[u'',result.pop(u'')]]]
    else:
        output = [0,[]]
    for item in result:
        output[1].insert(0,[item,result[item]])
    return output
