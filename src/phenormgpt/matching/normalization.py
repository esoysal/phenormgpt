from typing import Tuple

from base.dataset import Term
from matching.dict_matching import match_hpo_dict, match_observation_dict
#from matching.emb_matching import match_emb
#from matching.es_matching import match_es
#from matching.gpt_matching import match_gpt

# Customizable Matching Logic

# Takes term, returns HPO ID & matching method
def match(term: Term, debug: bool = True) -> Tuple[str, str]:
    predicted_term = term.get_preferred_term() # term predicted by model
    observed_term = term.get_observed_term() # actual text within predicted span

    if observed_term:
        dict_id, method = match_hpo_dict(observed_term)
        if dict_id is not None:
            return dict_id, 'Observed term by %s' % method
        obs_id, method = match_observation_dict(observed_term)
        if obs_id is not None:
            return obs_id, 'Observed term by %s' % method
    
    dict_id, method = match_hpo_dict(predicted_term)
    if dict_id is not None:
        return dict_id, 'Predicted term by %s' % method
    
    obs_id, method = match_observation_dict(predicted_term)
    if obs_id is not None:
        return obs_id, 'Predicted term by %s' % method
    
    if observed_term is not None and debug:
        print('Warning: Term not matched: %s [%s].' % (predicted_term, observed_term))
    return None, 'No match'

def normalize_term(term: Term) -> Term:       
    hpo_id, matcher = match(term) # Calculate HPO ID
    term.hpo_id = hpo_id
    term.matcher = matcher
    return term