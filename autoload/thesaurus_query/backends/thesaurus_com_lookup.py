# python wrapper for word query from thesaurus.com
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]

'''
handler for lookup method: "_online_thesaurus_lookup". When query_from_source is called, return:
   [status, [[def_0, [synonym_0, synonym_1, ...]],  [def_1, [synonym_0, synonym_1, ...]], ...]]
status:
    0: normal,  synonym found, list will be returned as
    1: normal, synonym not found, return empty synonym list
    -1: unexpected result from query, return empty synonym list
synonym list = [def, list wordlist]
    def('str'): definition the synonyms belong to
    wordlist = [synonym_0, synonym_1, ...]: list of words belonging to a same definition
'''

try:
    from urllib2 import urlopen
    from urllib2 import URLError,HTTPError
    from StringIO import StringIO
except ImportError:
    from urllib.request import urlopen
    from urllib.error import URLError,HTTPError
    from io import StringIO

import sys
import subprocess
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict
import re
import socket
from ..tq_common_lib import decode_utf_8, fixurl, get_variable
from ..tq_common_lib import send_string_to_vim, vim_command, vim_eval

identifier="thesaurus_com"
language="en"

def query(self,word):
    return [-1, []]
