import json

def _parser(result):
    result_dict = result[0]
    if not result_dict:
        return [1, []]
    syns = [syn for arr in result_dict[u'meta'][u'syns'] for syn in arr]
    ants = [ant for arr in result_dict[u'meta'][u'ants']for ant in arr]
    sseqs = [d[u'sseq'] for d in result_dict[u'def'] if d[u'sseq']]
    flattened = [d for a in sseqs for b in a for c in b for d in c if isinstance(d,dict)]
    near_lists = [d[u'near_list'] for d in flattened if d[u'near_list']]
    rel_lists = [d[u'rel_list'] for d in flattened if d[u'rel_list']]
    nears = [d[u'wd'] for arr in near_lists for c in arr for d in c if d[u'wd']]
    rels = [d[u'wd'] for arr in rel_lists for c in arr for d in c if d[u'wd']]
    return [0,[
        [ 'Synonyms', syns],
        [ 'Related', rels],
        [ 'Near', nears],
        [ 'Antonyms', ants]
    ]]

result_string='[{"meta":{"id":"laughter","uuid":"d5568d3d-0a4b-4ad9-a7fa-ef61c4a3aa2b","src":"coll_thes","section":"alpha","target":{"tuuid":"3a26c05a-c942-4c40-8358-14abec28e469","tsrc":"collegiate"},"stems":["laughter","laughters"],"syns":[["belly laugh","boff","boffola","cachinnation","cackle","chortle","chuckle","giggle","guffaw","hee-haw","horselaugh","laugh","snicker","snigger","titter","twitter"]],"ants":[],"offensive":false},"hwi":{"hw":"laughter"},"fl":"noun","def":[{"sseq":[[["sense",{"dt":[["text","an explosive sound that is a sign of amusement "],["vis",[{"t":"the nervous producers were reassured by the sounds of {it}laughter{\/it} coming from the theater"}]]],"syn_list":[[{"wd":"belly laugh"},{"wd":"boff","wvrs":[{"wvl":"or","wva":"boffo"}]},{"wd":"boffola"},{"wd":"cachinnation"},{"wd":"cackle"},{"wd":"chortle"},{"wd":"chuckle"},{"wd":"giggle"},{"wd":"guffaw"},{"wd":"hee-haw"},{"wd":"horselaugh"},{"wd":"laugh"},{"wd":"snicker"},{"wd":"snigger"},{"wd":"titter"},{"wd":"twitter"}]],"rel_list":[[{"wd":"crow"},{"wd":"whoop"}],[{"wd":"grin"},{"wd":"simper"},{"wd":"smile"},{"wd":"smirk"}]],"near_list":[[{"wd":"cry"},{"wd":"groan"},{"wd":"moan"},{"wd":"sob"},{"wd":"wail"}],[{"wd":"face"},{"wd":"frown"},{"wd":"grimace"},{"wd":"lower","wvrs":[{"wvl":"also","wva":"lour"}]},{"wd":"mouth"},{"wd":"pout"},{"wd":"scowl"}]]}]]]}],"shortdef":["an explosive sound that is a sign of amusement"]}]'
r_json=json.loads(result_string)
print(_parser(r_json))