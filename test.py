import json
def _parser(target_list):
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
    if u'' in result:
        output = [0, [[u'',result.pop(u'')]]]
    else:
        output = [0,[]]
    for item in result:
        output[1].insert(0,[item,result[item]])
    return output

result_string='[{"word":"content","score":3310},{"word":"bright","score":1804},{"word":"halcyon","score":1706},{"word":"blessed","score":1223},{"word":"prosperous","score":1183},{"word":"glad","score":1164},{"word":"golden","score":1020},{"word":"blissful","score":953},{"word":"euphoric","score":863},{"word":"pleased","score":845},{"word":"expansive","score":828},{"word":"felicitous","score":804},{"word":"joyful","score":780},{"word":"fortunate","score":755},{"word":"elysian","score":496},{"word":"joyous","score":492},{"word":"contented","score":491},{"word":"riant","score":433},{"word":"paradisal","score":181},{"word":"paradisiacal","score":174},{"word":"euphoriant","score":131},{"word":"paradisiac","score":116},{"word":"paradisaical","score":100},{"word":"paradisaic","score":83},{"word":"paradisial","score":71},{"word":"well-chosen","score":56}]'
r_json=json.loads(result_string)
print(_parser(r_json))