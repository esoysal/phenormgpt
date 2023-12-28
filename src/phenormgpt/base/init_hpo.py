import json

from base.hpo import HPO, Concept

def init_hpo_from_tsv_file(hpo_filename: str) -> HPO:
    hpo = HPO()
    print('Initializing HPO from TSV file: %s' % hpo_filename)
    with open(hpo_filename, 'r') as hpo_file:
        headers = hpo_file.readline()
        line = hpo_file.readline()
        while line:
            hpo_id, preferred_term = line.replace('\n', '').split('\t')
            preferred_term = preferred_term.lower()
            if not preferred_term.startswith('obsolete'):
                concept = Concept(hpo_id, preferred_term = preferred_term)
                hpo.add_concept(concept)
            
            line = hpo_file.readline()
    return hpo

def init_hpo_from_json_file(hpo_filename: str) -> HPO:
    hpo = HPO()
    print('Initializing HPO from JSON file: %s' % hpo_filename)
    with open(hpo_filename, 'r') as hpo_file:
        hpo_json = json.loads(hpo_file.read())
        
    for hpo_id, hpo_value in hpo_json.items():
        if 'synonyms' in hpo_value.keys():
            synonyms = hpo_value['synonyms']
        else:
            synonyms = []
        concept = Concept(hpo_id,
                            preferred_term = hpo_value['pref_term'],
                            synonyms = synonyms)
        hpo.add_concept(concept)
        
    return hpo

def init_hpo_from_terminology_json_file(hpo_filename: str) -> HPO:
    hpo = HPO()
    print('Initializing HPO from JSON file: %s' % hpo_filename)
    hpo_dict = json.load(open(hpo_filename, 'r'))
    
    nodes = hpo_dict['graphs'][0]['nodes']
    for node in nodes:
        hpo_id = node['id'].split('/')[-1].replace('_', ':')
        if not hpo_id.startswith('HP:'):
            continue
        preferred_term = node['lbl']
        if 'meta' not in node.keys():
            synonyms = []
        else:
            if 'synonyms' in node['meta'].keys():
                synonyms = [synonym['val'] for synonym in node['meta']['synonyms']]
            else:
                synonyms = []
        
        concept = Concept(hpo_id, preferred_term = preferred_term, synonyms = synonyms)
        hpo.add_concept(concept)
    return hpo