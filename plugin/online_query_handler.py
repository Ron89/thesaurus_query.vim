# Handler for Online Thesaurus Lookup routine =online_thesaurus_lookup.py=, structurize
# the result with the general word query framework.
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
# Version:      0.1.0

import urllib2
import re
import vim
#from online_thesaurus_lookup import online_thesaurus_lookup
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

class word_query_handler_thesaurus_lookup:
    '''
    handler for lookup method: "online_thesaurus_lookup.py". When query_from_source is called, return:
       [status, [[def_0, [synonym_0, synonym_1, ...]],  [def_1, [synonym_0, synonym_1, ...]], ...]]
    status:
        0: normal,  synonym found, list will be returned as
        1: normal, synonym not found, return empty synonym list
        -1: unexpected result from query, return empty synonym list
    synonym list = [def, list wordlist]
        def('str'): definition the synonyms belong to
        wordlist = [synonym_0, synonym_1, ...]: list of words belonging to a same definition
    '''

    def __init__(self):
#        self.query_source_cmd = os.path.dirname(os.path.realpath(__file__))+"/online_thesaurus_lookup.sh"
        self.identifier="online_thesaurus_default"
        self.header_length=11    # length of "Definition:", current header of definition
        self.relavent_val_pos=9
        self.syno_pos=11
        self.truncation_on_relavance=int(vim.eval("g:thesaurus_query#truncation_on_relavance")) # truncate on which relavance level?

    def query_cmd_handler(self, word):
        self.syno_list=[]
        query_result_raw = online_thesaurus_lookup(word)
        self.query_result = StringIO(query_result_raw)


    def synonym_found(self):
        first_line = self.query_result.readline()
        if first_line != '\n':
            if "Internet Error." in first_line:
                self.query_result.close()
                return -1
            self.query_result.close()
            return 1
        return 0

    def syno_populating(self):
        word_dic={}
        syno_list_curr=[]
        self.query_result.readline()  # skip the line 'Synonyms:'
        while True:
            self.line_curr = self.query_result.readline()
            if self.line_curr[:self.relavent_val_pos] != "relevant-":
                break
            self.line_curr=self.line_curr.rstrip('\n')
            if self.line_curr[self.relavent_val_pos] in word_dic.keys():
                word_dic[self.line_curr[self.relavent_val_pos]].append(self.line_curr[self.syno_pos:])
            else:
                word_dic[self.line_curr[self.relavent_val_pos]]=[self.line_curr[self.syno_pos:]]
        for key in sorted(word_dic, reverse=True):
            if key <= self.truncation_on_relavance:
                continue
            syno_list_curr=syno_list_curr+word_dic[key]     # sorted
        del word_dic
        return [not not syno_list_curr, syno_list_curr]

    def process_query_result(self):
        status = True
        self.line_curr=self.query_result.readline()
        while not (not self.line_curr or not status):
            if self.line_curr[:self.header_length] == 'Definition:':
                self.line_curr=self.line_curr.rstrip('\n')
                definition_curr = self.line_curr[self.header_length+1:]
                self.syno_list.append([definition_curr, []])
                [status, self.syno_list[-1][1]] = self.syno_populating()
            else:
                self.line_curr=self.query_result.readline()
        self.query_result.close()
        return status and not not self.syno_list

    def query(self,word):
        self.query_cmd_handler(word)
        query_status = self.synonym_found()
        if query_status!=0:
            return [query_status, self.syno_list]
        if self.process_query_result():
            return [0, self.syno_list]
        return [-1, []]


def online_thesaurus_lookup(target):
    output = ""
    try:
        response = urllib2.urlopen('http://www.thesaurus.com/browse/{}'.format(target))
        parser = StringIO(response.read())
    except urllib2.HTTPError, error:
        output = "The word \"{}\" has not been found on dictionary.com!\n".format(target)
        return output
    except urllib2.URLError, error:
        output = "Internet Error. The word \"{}\" has not been found on dictionary.com!\n".format(target)
        return output

    end_tag_count=2
    while True:
        line_curr = parser.readline()
        if not line_curr:
            break
        if "no thesaurus results" in line_curr:
            output = "The word \"{}\" has not been found on thesaurus.com!\n".format(target)
            break
        if "synonym-description" in line_curr:
            end_tag_count=0
            continue
        elif end_tag_count<2:
            if "</div>" in line_curr:
                end_tag_count+=1
                continue
            fields = re.split("<|>|&quot;", line_curr)
            if len(fields)<3:
                continue
            elif len(fields)<10:
                if "txt" in fields[1]:
                    output+="\nDefinition: {}. ".format(fields[2])
                    continue
                elif "ttl" in fields[1]:
                    output+="{}\nSynonyms:\n".format(fields[2])
                    continue
            elif "www.thesaurus.com" in fields[3]:
                output+="{} {}\n".format(fields[6], fields[14])
    parser.close()
    return output
