# -*- coding: utf-8 -*-
#
# python wrapper for word query from synonymo.fr
# Author:       Eloi perdereau [[eloi@perdereau.eu][E-mail]]


try:
    from urllib2 import urlopen
    from urllib2 import URLError, HTTPError
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError
import sys
import socket


from ..tq_common_lib import fixurl, decode_utf_8, get_variable, vim_eval

identifier="synonymo_fr"
language="fr"

_timeout_period_default = 1.0
_backendDisabled = False

try:
    import bs4 as BeautifulSoup
except ImportError:
    userChoice = vim_eval("confirm(\"Required package bs4 can not be imported. Please use '{} -m pip install bs4 --user --upgrade' to install the latest bs4. Do you want to try to import it again?\", \"&Yes\\n&Disable '{}' backend for this Vim session\")".format(sys.executable, identifier, identifier))
    if userChoice == "1":
        import bs4 as BeautifulSoup
    else:
        _backendDisabled = True

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
    if _backendDisabled:
        return [-1,[]]
    target=target.replace(u" ", u"+")
    result_list=_synonymo_fr_wrapper(target, query_method=query_method)
    if result_list == -1:
        return [-1, []]
    elif result_list == 1:
        return [1, []]
    else:
        return _parser(result_list)


def _synonymo_fr_wrapper(target, query_method='synonym'):
    '''
    query_method:
        synonym anyonym
    '''
    time_out_choice = float(get_variable(
        'tq_online_backends_timeout', _timeout_period_default))
    case_mapper={"synonym":u"syno",
                 "antonym":u"anto",
                }

    try:
        response = urlopen(fixurl(
            u'http://synonymo.fr/{0}/{1}'.format(
                case_mapper[query_method], target
                )).decode('ASCII'), timeout = time_out_choice)
    except HTTPError:
        return 1
    except URLError as err:
        if isinstance(err.reason, socket.timeout):  # timeout error?
            return 1
        return -1   # other error
    except socket.timeout:  # timeout error failed to be captured by URLError
        return 1
    return response.read()

def _parser(target_list):
    soup = BeautifulSoup.BeautifulSoup(target_list, features="html.parser")
    fiche = soup.find_all('div', {'class': 'fiche'})[0]
    if "Aucun résultat" in fiche.h1:
        return [1, []]
    else:
        synonym_list = [ a.get_text() for a in fiche.find_all('a', {'class': 'word'}) ]
        if synonym_list:
            return [0, [ ['', synonym_list ] ]]
        else:   # parse error
            return [-1, []]

