from copy import deepcopy

from base.dataset import Dataset
from base.init_dataset import init_dataset_from_file, init_dataset_from_file_no_terms
from config.config import TRAIN_FILEPATH, TRAIN_ORIGINAL_FILEPATH, TRAIN_SAMPLE_FILEPATH, \
    VAL_FILEPATH, VAL_ORIGINAL_FILEPATH, VAL_SAMPLE_FILEPATH, HANDPICKED_FILEPATH, \
    TEST_FILEPATH, TEST_SAMPLE_FILEPATH

def load_train_dataset() -> Dataset:
    return init_dataset_from_file(TRAIN_FILEPATH)

def load_train_dataset_original() -> Dataset:
    return init_dataset_from_file(TRAIN_ORIGINAL_FILEPATH)

def load_train_dataset_sample() -> Dataset:
    return init_dataset_from_file(TRAIN_SAMPLE_FILEPATH)

def load_val_dataset() -> Dataset:
    return init_dataset_from_file(VAL_FILEPATH)

def load_val_dataset_original() -> Dataset:
    return init_dataset_from_file(VAL_ORIGINAL_FILEPATH)

def load_val_dataset_sample() -> Dataset:
    return init_dataset_from_file(VAL_SAMPLE_FILEPATH)

def load_test_dataset() -> Dataset:
    return init_dataset_from_file_no_terms(TEST_FILEPATH)

def load_test_dataset_sample() -> Dataset:
    return init_dataset_from_file_no_terms(TEST_SAMPLE_FILEPATH)

def load_annotated_dataset() -> Dataset:
    annotated_dataset = deepcopy(load_train_dataset())
    annotated_dataset.observations.extend(load_val_dataset().observations)
    return annotated_dataset

def load_merged_dataset() -> Dataset:
    merged_dataset = deepcopy(load_annotated_dataset())
    merged_dataset.observations.extend(load_test_dataset().observations)
    return merged_dataset

def load_handpicked_dataset() -> Dataset:
    handpicked_dataset = Dataset([])
    handpicked_dataset.observations = []
    
    handpicked_observation_ids = []
    with open(HANDPICKED_FILEPATH, 'r') as f:
        headers = f.readline()
        line = f.readline().replace('\n', '')
        while line:
            line_observation_ids = line.split('\t')[1:]
            for line_observation_id in line_observation_ids:
                if len(line_observation_id) > 3:
                    handpicked_observation_ids.append(line_observation_id)
            line = f.readline().replace('\n', '')
    
    annotated_dataset = load_annotated_dataset()
    for observation in annotated_dataset.observations:
        if observation.observation_id in handpicked_observation_ids:
            handpicked_dataset.add_observation(observation)
            
    return handpicked_dataset