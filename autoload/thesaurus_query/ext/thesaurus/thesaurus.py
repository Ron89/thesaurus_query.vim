"""
Thesaurus-API
~~~~~~~~~~~~~

An api for thesaurus.com. See the README for instructions.

A pythonic poem authored by Robert.
Inspiration and help from others (see credits).

If there's anything in here you don't understand or want me to change, just
make an issue or send me an email at robert <at> robertism <dot> com. Thanks :)
"""

from collections import namedtuple
import json

import requests
from bs4 import BeautifulSoup

# ===========================   GLOBAL CONSTANTS   =============================
ALL = 'all'

## form=
FORM_INFORMAL = 'informal'
FORM_COMMON =   'common'

# TODO: also include nltk pos_tagger constants
## partOfSpeech=
POS_ADJECTIVE, POS_ADJ =        'adj', 'adj'
POS_ADVERB, POS_ADV =           'adv', 'adv'
POS_CONTRADICTION, POS_CONT =   'contraction', 'contraction'
POS_CONJUNCTION, POS_CONJ =     'conj', 'conj'
POS_DETERMINER, POS_DET =       'determiner', 'determiner'
POS_INTERJECTION, POS_INTERJ =  'interj', 'interj'
POS_NOUN =                      'noun'
POS_PREFIX =                    'prefix'
POS_PREPOSITION, POS_PREP =     'prep', 'prep'
POS_PRONOUN, POS_PRON =         'pron', 'pron'
POS_VERB =                      'verb'
POS_ABBREVIATION, POS_ABB =     'abb', 'abb'
POS_PHRASE =                    'phrase'
POS_ARTICLE =                   'article'
# =========================   END GLOBAL CONSTANTS   ===========================


def formatWordUrl(inputWord):
    """Format our word in the url. I could've used urllib's quote thing, but
    this is more efficient I think. Let me know if there's a word it doesn't
    work for and I'll change it.
    """
    url = 'http://www.thesaurus.com/browse/'
    url = url + inputWord.strip().lower().replace(' ', '%20')
    return url

def btw(inputString, lh, rh):
    """Extract a string between two other strings."""
    return inputString.split(lh, 1)[1].split(rh, 1)[0]

def fetchWordData(inputWord):
    """Downloads the data thesaurus.com has for our word.

    Parameters
    ----------
    inputWord : str
        The word you are searching for on thesaurus.com
    
    Returns
    -------
    list of dict
        A list of n+1 dictionaries, where n is the number of definitions for the
        word, and the last dictionary holds information on word origin and
        example sentences.

        Each definition dict is of the form:
            {
                'meaning' : str,
                'partOfSpeech' : str,
                'isVulgar' : bool,
                'syn' : [Entry(
                                word=str,
                                relevance=int,
                                length=int,
                                complexity=int,
                                form=str
                        )],
                'ant' : [... same as 'syn' ...]
            }
        where `Entry` is a namedtuple.
    """
    url = formatWordUrl(inputWord)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    try:
        data = soup.select('script')[12].text
        data = data[22+1:-1] # remove 'window.INITIAL_STATE = ' and ';'
        data = json.loads(data)
    except:
        # Find the JS block with the most text in it. This is our data.
        dataIdx = max([(i, len(x.text)) for i, x in enumerate(soup.select('script'))],
            key=lambda z: z[1])[0] # sort by length of text. Idx is 0th elment.
        data = soup.select('script')[dataIdx].text
        data = data[22+1:-1] # remove 'window.INITIAL_STATE = ' and ';'
        data = json.loads(data)

    defns = [] # where we shall store data for each definition tab

    # how we will represent an individual synonym/antonym
    Entry = namedtuple('Entry', ['word', 'relevance', 'length',
                                 'complexity', 'form'])

    ## Utility functions to process attributes for our entries.
    # a syn/ant's relevance is marked 1-3, where 10 -> 1, 100 -> 3.
    calc_relevance = lambda x: [None, 10, 50, 100].index(x)
    calc_length    = lambda x: 1 if x < 8 else 2 if x < 11 else 3
    calc_form      = lambda x: 'informal' if x is True else 'common'

    # iterate through each definition tab, extracting the data for the section
    for defn in data['searchData']['tunaApiData']['posTabs']:
        # this dict shall store the relevant data we found under the current def
        curr_def = {
            'partOfSpeech' : defn.get('pos'),
            'meaning' : defn.get('definition'),
            'isVulgar' : bool(int(defn.get('isVulgar'))),
            'syn' : [],
            'ant' : []
        }

        """
        the synonym and antonym data will each be stored as lists of tuples.
          Each item in the tuple corresponds to a certain attribute of the
          given syn/ant entry, and is used to filter out specific results when
          Word.synonym() or Word.antonym() is called.
        """

        ### NOTE, TODO ###
        """
        Currently, length and complexity are both set to level == 0.
          Originally, they were 1-3. In thesaurus.com's newest update, when they
          began obfuscating the css classes, they removed the complexity data,
          and made the length data harder to extract. I actually haven't found
          anything to suggest that the complexity data still even exists, but
          I can't imagine them deleting this data... I'll keep looking.

        Until I can find a fix for this, both will be set to 0, and ._filter()
          will just ignore any length/complexity requests.
        """

        for syn in defn.get('synonyms', []):
            # tuple key is (word, relevance, length, complexity, form, isVulgar)
            e = Entry(
                word=syn['term'],
                relevance=calc_relevance(abs(int(syn['similarity']))),
                length=calc_length(len(syn['term'])),
                complexity=0,
                form=calc_form(bool(int(syn['isInformal'])))
                # isVulgar=bool(syn['isVulgar']) # *Nested* key is useless.
            )

            curr_def['syn'].append(e)
        
        for ant in defn.get('antonyms', []):
            # tuple key is (word, relevance, length, complexity, form, isVulgar)
            e = Entry(
                word=ant['term'],
                relevance=calc_relevance(abs(int(ant['similarity']))),
                length=calc_length(len(ant['term'])),
                complexity=0,
                form=calc_form(bool(int(ant['isInformal'])))
                # isVulgar=bool(ant['isVulgar']) # *Nested* key is useless.
            )

            curr_def['ant'].append(e)
        
        defns.append(curr_def)
    

    # add origin and examples to the last element so we can .pop() it out later
    otherData = data['searchData']['tunaApiData']
    examples = [x['sentence'] for x in otherData['exampleSentences']]
    etymology = otherData['etymology']

    if len(etymology) > 0:
        origin = BeautifulSoup(etymology[0]['content'], "html.parser").text
        ## Uncomment this if you actually care about getting the ENTIRE
        ##   origin box. I don't think you do, though.
        # origin = reduce(lambda x,y: x+y, map(
        #     lambda z: BeautifulSoup(z['content'], "html.parser").text
        # ))
    else:
        origin = ''
    
    defns.append({
        'examples': examples,
        'origin': origin
    })

    return defns

class Word(object):
    def __init__(self, inputWord):
        """Downloads and stores the data thesaurus.com has for a given word.

        Parameters
        ----------
        inputWord : str
            The word you wish to search for on thesaurus.com
        """
        # in case you want to visit it later
        self.url = formatWordUrl(inputWord)

        try:
            # fetch the data from thesaurus.com
            self.data = fetchWordData(inputWord)
        except:
            # Thesaurus.com doesn't have this word.
            # TODO: Question: Should an error be raised? Warning printed?
            self.data = [{'origin':'', 'examples':[]}]

        self.extra = self.data.pop()

    def __len__(self):
        # returns the number of definitions the word has
        return len(self.data)

    ### FUNCTIONS TO HELP ORGANIZE DATA WITHIN THE CLASS ###
    def _filter(self, mode, defnNum='all', **filters):
        """Filter out our self.data to reflect only words with certain
        attributes specified by the user. Ex: return informal synonyms that are
        relevant and have many characters.

        NOTE:
        COMPLEXITY filter is STILL BROKEN thanks to the site's update. It will
        simply be ignored for the time being.

        Parameters
        ----------
        mode : {'syn', 'ant'}
            Filters through the synonyms if 'syn', or antonyms if 'ant'.
        defnNum : int or 'all', optional
            The word definition we are filtering data from (index of self.data).
            Thus, as it is an index, it must be >= 0. If 'all' is specified,
            however, it will filter through all definitions. This is the default

        NOTE:
        The following filters are capable of being specified as explicit values,
        or lists of acceptable values. Ex: relevance=1 or relevance=[1,2].

        relevance : {1, 2, 3} or list, optional
            1 least relevant - 'enfeebled'
            2 
            3 most relevant  - 'elderly'
        partOfSpeech : { POS_* } or list, optional
            The following possible values are also defined as constants at the
            beginning of the file. You can call them as: POS_ADVERB or POS_ADV.
            The complete list is as follows:
                adjective: 'adj'
                adverb: 'adv'
                contraction: 'contraction'
                conjunction: 'conj'
                determiner: 'determiner'
                interjection: 'interj'
                noun: 'noun'
                prefix: 'prefix'
                preposition: 'prep'
                pronoun: 'pron'
                verb: 'verb'
                abbreviation: 'abb'
                phrase: 'phrase'
                article: 'article'
        length : {1, 2, 3} or list, optional
            1 shortest - aged
            2
            3 longest - experienced
        complexity : {1, 2, 3} or list, optional
            Reminder that this is CURRENTLY BROKEN. It will default to `None`, 
            no matter what values you choose.
            1 least complex
            2
            3 most complex
        form : {'informal', 'common'} or list, optional
            Similar to the partOfSpeech options, these values are also defined
            as constants: FORM_INFORMAL and FORM_COMMON.

            Before thesaurus.com changed their code, it used to be that the
            majority of words were neither informal nor common. Thus, it wasn't
            the case that common inferred not-informal. Now, however, all words
            are either informal or common.
        isVulgar : bool, optional
            Similar to partOfSpeech, if `True`, will blank out non-vulgar
            definition entries. If `False`, will filter out vulgar definitions.
            Think of it as having only two different POS's to select from.

        Returns
        -------
        list of list of str OR list of str
            If defnNum is set to 'all', it will filter over all definitions, and
            will return a list of list of str, where each nested list is a
            single definition.
            If defnNum is set to an integer, it will return a list of str, where
            the str's are the filtered words for that single definition.
        """

        def compare_entries(e1, e2):
            if isinstance(e2, list):
                if None in e2:
                    return True
                else:
                    return e1 in e2
            else:
                if None in {e1, e2}:
                    return True
                else:
                    return e1 == e2

        Filters = namedtuple('Filters', [
            'relevance',
            'partOfSpeech',
            'length',
            'complexity', # currently unavailable
            'form',
            'isVulgar'
        ])

        filters = filters.get('filters', {})
        for key, val in filters.items():
            # make all filters in list format, so 1 becomes [1]. This makes
            #   checking equality between entries and filters easier.
            if not isinstance(val, list):
                filters[key] = [val]
        
        # We can't change a namedtuple's values after creating it. We have to
        #   make sure it matches the user's filter value before we set it.
        _tempForm = filters.get('form')
        if _tempForm: # make sure it's not NoneType first.
            for i, _form in enumerate(_tempForm):
                if 'informal' in _form.lower():
                    _tempForm[i] = 'informal'
                elif 'common' in _form.lower():
                    _tempForm[i] = 'common'
                else:
                    # reset form to be None, thus ignoring the improper option
                    print('Please select `informal` or `common` for `form=` filter.')
                    print('Defaulting to select both.')
                    _tempForm = None
                    break

        fs = Filters(
            relevance=      filters.get('relevance'),
            partOfSpeech=   filters.get('partOfSpeech', filters.get('pos')),
            length=         filters.get('length'),
            complexity=     None, # not currently implemented.
            form=           _tempForm,
            isVulgar=       filters.get('isVulgar')
        )

        if defnNum == 'all':
            # examines all definition tabs for a word
            startRange, endRange = 0, len(self.data)
        else:
            # examines only the tab index specified (starting at 0)
            startRange, endRange = defnNum, defnNum+1
        
        filtered_data = []  # data we are going to return

        for defn in self.data[startRange:endRange]:
            # current defn tab is not of the pos we require. continue.
            if not compare_entries(defn['partOfSpeech'], fs.partOfSpeech):
                filtered_data.append([])
                continue
            
            # current defn tab is not of the vulgarity we require. continue.
            if not compare_entries(defn['isVulgar'], fs.isVulgar):
                filtered_data.append([])
                continue
            
            # holds all the relevant entries for this defn.
            cur_data = []

            for entry in defn.get(mode):
                if (
                    compare_entries(entry.relevance, fs.relevance) and
                    compare_entries(entry.length, fs.length) and
                    compare_entries(entry.form, fs.form)
                ):
                    cur_data.append(entry.word)
            
            # if we only care about a single definition, just return a 1d list.
            if defnNum != 'all':
                return cur_data

            filtered_data.append(cur_data)

        return filtered_data

    ### FUNCTIONS TO RETURN DATA YOU WANT ###
    """Each of the following functions allow you to filter the output
    accordingly: relevance, partOfSpeech, length, complexity, form.
    """
    def synonyms(self, defnNum=0, allowEmpty=True, **filters):
        """Return synonyms for specific definitions, filtered to only include
        words with specified attribute values.
        
        PLEASE see _filter()'s docstring or the README for more information on
        filtering.

        Parameters
        ----------
        defnNum : int or 'all', optional
            The word definition we are returning data from (index of self.data).
            Thus, as it is an index, it must be >= 0. If 'all' is specified,
            however, it will filter through all definitions. 0 is the default.
        allowEmpty : bool, optional
            Filters the output to only include defns (represented as lists) that
            are not empty after being filtered. Useful if you are trying to only
            see definitions of a certain part of speech. This way, you can
            enumerate over the returned values without having to worry if you're
            enumerating over an empty value.

        Returns
        -------
        list of list of str OR list of str
            If defnNum is set to 'all', it will include data from all
            definitions, returning a list of list of str, where each nested list
            is a single definition.
            If defnNum is set to an integer, it will return a list of str, where
            the str's are the filtered words for that single definition.
        """

        data = self._filter(mode='syn', defnNum=defnNum, filters=filters)

        # the word does not exist. return empty.
        if not data:
            return []
        
        if allowEmpty:
            return data
        else:
            return [d for d in data if len(d) > 0]

    def antonyms(self, defnNum=0, allowEmpty=True, **filters):
        """Return antonyms for specific definitions, filtered to only include
        words with specified attribute values.
        
        PLEASE see _filter()'s docstring or the README for more information on
        filtering.

        Parameters
        ----------
        defnNum : int or 'all', optional
            The word definition we are returning data from (index of self.data).
            Thus, as it is an index, it must be >= 0. If 'all' is specified,
            however, it will filter through all definitions. 0 is the default.
        allowEmpty : bool, optional
            Filters the output to only include defns (represented as lists) that
            are not empty after being filtered. Useful if you are trying to only
            see definitions of a certain part of speech. This way, you can
            enumerate over the returned values without having to worry if you're
            enumerating over an empty value.

        Returns
        -------
        list of list of str OR list of str
            If defnNum is set to 'all', it will include data from all
            definitions, returning a list of list of str, where each nested list
            is a single definition.
            If defnNum is set to an integer, it will return a list of str, where
            the str's are the filtered words for that single definition.
        """
        
        data = self._filter(mode='ant', defnNum=defnNum, filters=filters)

        # the word does not exist. return empty.
        if not data:
            return []
        
        if allowEmpty:
            return data
        else:
            return [d for d in data if len(d) > 0]

    def origin(self):
        """Gets the origin of a word.

        Returns
        -------
        str
            It's the paragraph that's on the right side of the page. It talks a
            bit about how the modern meaning of the word came to be.
        """
        return self.extra['origin']

    def examples(self):
        """Gets sentences the word is used in.

        Returns
        -------
        list of str
            Each str is a sentence the word is used in.
        """
        return self.extra['examples']
