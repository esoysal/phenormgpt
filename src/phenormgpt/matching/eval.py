from copy import deepcopy
from tqdm import tqdm
from typing import Tuple

from base.dataset import Term, Observation, Dataset

def compare_terms(term_true: Term, term_pred: Term, match_func,
                  cui_check: bool = False, span_check: bool = True) -> bool:
    if cui_check:
        term_match = term_true.hpo_id == term_pred.hpo_id
    else:
        matched_id, match_type = match_func(term_pred)
        term_pred.matcher = match_type
        term_match = term_true.hpo_id == matched_id
    
    if span_check:
        span_match = ','.join(term_true.spans) == ','.join(term_pred.spans)
    else:
        if len(term_pred.get_spans()) == 0:
            print('Error: Empty span for term: %s.' % term_pred.__str__(True))
            span_match = False
        else:
            overlap = max(0,
                            min(term_true.get_spans()[-1][1],
                                term_pred.get_spans()[-1][1]) - max(term_true.get_spans()[0][0],
                                                                    term_pred.get_spans()[0][0]))
            span_match = overlap > 0
    
    return term_match and span_match

def compare_observations(observation_true: Observation, observation_pred: Observation, match_func,
                         cui_check: bool = False, span_check: bool = True,
                         skip_polarity: bool = True) -> Tuple[int, int, int]:
    tp = 0       
    fn = 0
    for term_true in observation_true.terms:
        if (skip_polarity and term_true.polarity):
            continue
        found = False
        for term_pred in observation_pred.terms:
            if compare_terms(term_true, term_pred, match_func,
                             cui_check = cui_check, span_check = span_check):
                found = True
                break
        if found:
            tp += 1
        else:
            fn += 1

    fp = 0
    for term_pred in observation_pred.get_valid_terms():
        if (skip_polarity and term_pred.polarity):
            continue
        found = False
        for term_true in observation_true.terms:
            if compare_terms(term_true, term_pred, match_func,
                             cui_check = cui_check, span_check = span_check):
                found = True
                break

        if not found:
            fp += 1
    '''        
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * precision * recall / (precision + recall)
    '''
    return tp, fp, fn

def compare(dataset_true: Dataset, dataset_pred: Dataset, match_func,
            cui_check: bool = False, span_check: bool = True) -> Tuple[float, float, float]:
    assert(len(dataset_true.observations) == len(dataset_pred.observations))
    
    tp = 0
    fp = 0
    fn = 0
    for i in tqdm(range(len(dataset_true.observations))):
        tp_i, fp_i, fn_i = compare_observations(dataset_true.observations[i], dataset_pred.observations[i],
                                                match_func, cui_check = cui_check, span_check = span_check)
        tp += tp_i
        fp += fp_i
        fn += fn_i
    
    print('TP: %d, FP: %d, FN: %d' % (tp, fp, fn))
    if tp > 0:
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * precision * recall / (precision + recall)
    else:
        precision = 0
        recall = 0
        f1 = 0
        
    return precision, recall, f1

# Return datasets consisting exclusively of TP, FP, FN examples, for error analysis.
def compare_get_observations(dataset_true: Dataset, dataset_pred: Dataset, match_func,
                             cui_check: bool = False,
                             span_check: bool = True) -> Tuple[Dataset, Dataset, Dataset]:
    assert(len(dataset_true.observations) == len(dataset_pred.observations))
    
    tp_dataset = Dataset([])
    fp_dataset = Dataset([])
    fn_dataset = Dataset([])
    
    for i in tqdm(range(len(dataset_true.observations))):
        tp, fp, fn = compare_observations(dataset_true.observations[i], dataset_pred.observations[i],
                                          cui_check = cui_check, span_check = span_check,
                                          match_func = match_func)
        
        observation_1 = deepcopy(dataset_true.observations[i])
        observation_2 = deepcopy(dataset_pred.observations[i])
        
        # Remove common predictions
        for term_1 in observation_1.terms:
            for term_2 in observation_2.terms:
                if compare_terms(term_1, term_2, cui_check = cui_check, span_check = span_check,
                                 match_func = match_func):
                    observation_1.terms.remove(term_1)
                    observation_2.terms.remove(term_2)
                    
        if fp == 0 and fn == 0:
            tp_dataset.add_observation(observation_1)
            tp_dataset.add_observation(observation_2)
        else:
            if fp > 0:
                fp_dataset.add_observation(observation_1)
                fp_dataset.add_observation(observation_2)
            if fn > 0:
                fn_dataset.add_observation(observation_1)
                fn_dataset.add_observation(observation_2)
    
    return tp_dataset, fp_dataset, fn_dataset