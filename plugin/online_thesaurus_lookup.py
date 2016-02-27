# Online Thesaurus Lookup routine. Find synonyms of a target word from www.thesaurus.com
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
# Version:      0.0.3
# Ported from shell script by Anton Beloglazov <http://beloglazov.info/>

import urllib2
import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

def online_thesaurus_lookup(target):
    output = ""
    try:
        response = urllib2.urlopen('http://www.thesaurus.com/browse/{}'.format(target))
        parser = StringIO(response.read())
    except urllib2.HTTPError, error:
        output = "The word \"{}\" has not been found on thesaurus.com!\n".format(target)
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
