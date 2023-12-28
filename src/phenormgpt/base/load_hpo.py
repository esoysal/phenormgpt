from typing import List

from base.hpo import HPO
from base.init_hpo import init_hpo_from_json_file, init_hpo_from_tsv_file
from config.config import HPO_JSON_FILEPATH, HPO_TERMS_FILEPATH, \
    ABNORMAL_HPO_TERMS_FILEPATH, OBSOLETE_HPO_TERMS_FILEPATH, UNOBSERVABLE_HPO_TERMS_FILEPATH

def load_hpo(json_filepaths: List[str], tsv_filepaths: List[str],
             exclude_json_filepaths: List[str], exclude_tsv_filepaths: List[str]) -> HPO:
    
    if len(json_filepaths) > 0:
        hpo = init_hpo_from_json_file(json_filepaths[0])
        print('Loaded %d concepts from initial file.' % len(hpo.get_concepts()))
        for filepath in json_filepaths[1:]:
            hpo.merge(init_hpo_from_json_file(filepath))
        for filepath in tsv_filepaths:
            hpo.merge(init_hpo_from_tsv_file(filepath))
      
    elif len(tsv_filepaths) > 0:
        hpo = init_hpo_from_tsv_file(tsv_filepaths[0])
        print('Loaded %d concepts from initial file.' % len(hpo.get_concepts()))
        for filepath in tsv_filepaths[1:]:
            hpo.merge(init_hpo_from_tsv_file(filepath))
        
    else:
        hpo = HPO()
        print('Loaded 0 concepts from initial file.')
    
    print('Loaded %d concepts in total.' % len(hpo.get_concepts()))
    
    for filepath in exclude_json_filepaths:
        hpo.subtract(init_hpo_from_json_file(filepath))
    
    for filepath in exclude_tsv_filepaths:
        hpo.subtract(init_hpo_from_tsv_file(filepath))
    
    print('Loaded %d concepts after exclusions.' % len(hpo.get_concepts()))
    
    return hpo

def load_hpo_instance() -> HPO:
    return load_hpo(
        json_filepaths = [HPO_JSON_FILEPATH],
        tsv_filepaths = [HPO_TERMS_FILEPATH],
        exclude_json_filepaths = [],
        exclude_tsv_filepaths = [
            UNOBSERVABLE_HPO_TERMS_FILEPATH,
            # ABNORMAL_HPO_TERMS_FILEPATH,
            OBSOLETE_HPO_TERMS_FILEPATH
        ]
    )

hpo = load_hpo_instance()