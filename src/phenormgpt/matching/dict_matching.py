import json
from typing import Tuple

from base.hpo import HPO
from base.load_hpo import hpo
from config.config import OBSERVATION_DICT_FILEPATH
from util.stemming import stem

def stem_term(term: str) -> str:
    return stem(term, sort=False, lower=True, clean=True, stop_words=True)

# Observation Dictionary Matching

# Load observation dictionary
observation_dict = json.loads(open(OBSERVATION_DICT_FILEPATH, 'r').read())

def match_observation_dict(term: str) -> Tuple[str, str]:
    term = stem_term(term)
    if term in observation_dict['resolution'].keys():
        return observation_dict['resolution'][term], 'Observation dictionary matching'
    elif term in observation_dict['observation'].keys():
        return observation_dict['observation'][term], 'Observation dictionary matching'
    return None, None

# HPO Dictionary Matching

def get_stemmed_hpo_dict(hpo: HPO) -> dict:
    print('Building HPO dict for matching...')
    
    # Load prefs first, sometimes others' synonyms create conflicts.
    hpo_dict = {}
    for concept in hpo.get_concepts():
        term = concept.get_preferred_term()
        stemmed_term = stem_term(term)
        if stemmed_term in hpo_dict.keys() and hpo_dict[stemmed_term] != concept.hpo_id \
                                           and stemmed_term not in observation_dict['resolution']:
            print('Warning: pref term already in dictionary: %s.' % stemmed_term)
            print('\tConflicting HPO IDs: %s and %s.' % (hpo_dict[stemmed_term], concept.hpo_id))
        else:
            hpo_dict[stemmed_term] = concept.hpo_id

    hpo_synonym_dict = {}
    for concept in hpo.get_concepts():
        terms = concept.get_all_terms()
        stemmed_terms = [stem_term(term) for term in terms]
        for stemmed_term in stemmed_terms:
            if stemmed_term in hpo_dict.keys():
                continue # Don't bother
            if stemmed_term in hpo_synonym_dict.keys() and hpo_synonym_dict[stemmed_term] != concept.hpo_id \
                                                       and stemmed_term not in observation_dict['resolution']:
                print('Warning: synonym already in dictionary: %s.' % stemmed_term)
                print('\tConflicting HPO IDs: %s and %s.' % (hpo_synonym_dict[stemmed_term], concept.hpo_id))
            else:
                hpo_synonym_dict[stemmed_term] = concept.hpo_id
    
    for synonym in hpo_synonym_dict.keys():
        if synonym not in hpo_dict.keys():
            hpo_dict[synonym] = hpo_synonym_dict[synonym]
    return hpo_dict


hpo_dict = get_stemmed_hpo_dict(hpo)

def match_hpo_dict(term: str) -> Tuple[str, str]:
    stemmed_term = stem_term(term)
    if stemmed_term in hpo_dict.keys():
        return hpo_dict[stemmed_term], 'HPO dictionary matching'
    else:
        return None, None