# -*- coding: utf-8 -*-
#
# python wrapper for word query from cnrtl.fr
# Author:       Eloi perdereau [[eloi@perdereau.eu][E-mail]]

try:
    from urllib2 import urlopen
    from urllib2 import URLError, HTTPError
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError
import sys
import re
import socket


from ..tq_common_lib import fixurl, decode_utf_8, get_variable, vim_eval

identifier="cnrtl_fr"
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
    result_list= _cnrtl_fr_wrapper(target, query_method=query_method)
    if result_list == -1:
        return [-1,[]]
    elif result_list == 1:
        return [1, []]
    else:
        return result_list


def get_html(url, time_out):
    try:
        response = urlopen(fixurl(url).decode('ASCII'), timeout = time_out)
    except HTTPError:
        return 1
    except URLError as err:
        if isinstance(err.reason, socket.timeout):  # timeout error?
            return 1
        return -1   # other error
    except socket.timeout:  # timeout error failed to be captured by URLError
        return 1
    return response.read()


def get_class_tds(soup, clas):
    synonym_tds = soup.find_all('td', {'class': clas})
    if not synonym_tds:
        return []
    else:
        synonyms = [ td.a.get_text() for td in synonym_tds ]
        return synonyms


def _cnrtl_fr_wrapper(target, query_method='synonym'):
    '''
    query_method:
        synonym anyonym
    '''
    time_out_choice = float(get_variable(
        'tq_online_backends_timeout', _timeout_period_default))
    case_mapper={"synonym":u"synonymie",
                 "antonym":u"antonymie",
                }
    class_mapper={"synonym":u"syno_format",
                  "antonym":u"anto_format"
                }
    base_url = u'http://cnrtl.fr'
    html = get_html(base_url+'/{0}/{1}'.format(
                case_mapper[query_method], target), time_out_choice)

    soup = BeautifulSoup.BeautifulSoup(html, features="html.parser")
    if re.search('Erreur|Terme introuvable', soup.find(id="contentbox").get_text()):
        return 1
    targets_li = soup.find(id="vtoolbar").find_all('li')
    synonym_lists = [ [targets_li[0].a.get_text(),
                            get_class_tds(soup, class_mapper[query_method])] ]

    # get alternative found targers
    link_pattern = re.compile("sendRequest\(\d+,\s*'([^']*)'\)")
    for alt_li in targets_li[1:]:
        link = link_pattern.search(alt_li.a['onclick']).group(1)
        alt_html = get_html(base_url+link, time_out_choice)
        alt_soup = BeautifulSoup.BeautifulSoup(alt_html, features="html.parser")
        synonym_lists.append([alt_li.a.get_text(),
                            get_class_tds(alt_soup, class_mapper[query_method])])
    return [ 0, synonym_lists ]

