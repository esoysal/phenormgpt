# Creating list of prompts from Dataset objects
# For both fine-tuning and few-shotting

import os
from random import shuffle
from tqdm import tqdm
from typing import List

from base.dataset import Dataset, Observation, Term
from base.hpo import HPO
from config.config import FINE_TUNE_DIR
from prompting.openai_dataset_analysis import save_to_jsonl
from prompting.prompts import EMPTY_RESPONSE_MESSAGE
from prompting.similarity import get_n_most_similar_observations

os.makedirs(FINE_TUNE_DIR, exist_ok=True)

def get_assistant_message_line(term: Term, hpo: HPO) -> str:
    concept = hpo.get_concept_by_hpo_id(term.hpo_id)
    preferred_term = concept.get_preferred_term()
    tagged_text = term.get_tagged_text()
    
    # Build assistant line for term
    assistant_message_line = '| %s | %s |' % (preferred_term, tagged_text)
    return assistant_message_line

def get_openai_messages_for_observation(observation: Observation, hpo: HPO, system_message: str = None,
                                        user_message_wrapper: str = None, assistant_message_table_header: str = None,
                                        include_response: bool = True, few_shot_dataset: Dataset = None,
                                        few_shot_k: int = 10, few_shot_k_min: int = 3,
                                        hand_picked_dataset: Dataset = None) -> List[dict]:
    messages = []
    
    # System message, if any
    if system_message:
        messages.append({'role': 'system', 'content': system_message})
    
    # Add few shot messages here, based on similarity, if any
    if few_shot_dataset is not None:
        dataset = get_n_most_similar_observations(few_shot_dataset, observation, few_shot_k)      
        few_shot_observations = dataset.observations
        
        num_observations_with_terms = len([few_shot_observation for few_shot_observation in few_shot_observations \
                                           if few_shot_observation.has_terms()])
        # We have no observation examples with actual terms
        if num_observations_with_terms < few_shot_k_min:
            num_observations_needed = few_shot_k_min
            dataset_w_terms = get_n_most_similar_observations(few_shot_dataset.filter_has_terms(), observation, num_observations_needed)
            observations_w_terms = dataset_w_terms.observations
            few_shot_observations.extend(observations_w_terms)
            
        # We have no observation examples with no terms (NA)
        elif len(few_shot_observations) - num_observations_with_terms < few_shot_k_min:
            num_observations_needed = few_shot_k_min
            na_dataset = get_n_most_similar_observations(few_shot_dataset.filter_no_terms(), observation, num_observations_needed)
            na_observations = na_dataset.observations
            few_shot_observations.extend(na_observations)
        
        # Add handpick dataset filtered by observation.bodyloc here...
        if hand_picked_dataset is not None:
            hand_picked_observations = hand_picked_dataset.filter_bodylocs([observation.bodyloc]).observations
            few_shot_observations.extend(hand_picked_observations)
        
        shuffle(few_shot_observations)
        
        added_few_shot_observation_ids = []
        for few_shot_observation in few_shot_observations:
            if few_shot_observation.observation_id == observation.observation_id:
                print('Warning: Target observation included in the few shot dataset.')
                continue
            if few_shot_observation.observation_id not in added_few_shot_observation_ids:
                added_few_shot_observation_ids.append(few_shot_observation.observation_id)
                messages.extend(get_openai_messages_for_observation(few_shot_observation, hpo,
                                                                    user_message_wrapper = user_message_wrapper,
                                                                    assistant_message_table_header = assistant_message_table_header))
        
    # User message, provide the observation
    user_message = observation.text
    if user_message_wrapper is not None:
        user_message = user_message_wrapper % user_message
    messages.append({'role': 'user', 'content': user_message})

    # Assistant message, return the terms
    if include_response:
        if len(observation.terms) > 0:
            # Build assistant response from terms
            assistant_message_lines = []
            if assistant_message_table_header:
                assistant_message_lines.append(assistant_message_table_header)
                
            # One line for each term
            for term in observation.terms:                
                # Build assistant line for term
                assistant_message_line = get_assistant_message_line(term, hpo)
                assistant_message_lines.append(assistant_message_line)
            
            assistant_message = '\n'.join(assistant_message_lines)
        else:
            # No terms for an observation
            # assistant_message = '| NA | NA |'
            assistant_message = EMPTY_RESPONSE_MESSAGE
        
        messages.append({'role': 'assistant', 'content': assistant_message})
    
    return messages

def get_openai_messages(dataset: Dataset, hpo: HPO, system_message: str = None,
                              user_message_wrapper: str = None, assistant_message_table_header: str = None,
                              include_response: bool = True, few_shot_dataset: Dataset = None, few_shot_k: int = 15,
                              few_shot_k_min: int = 3, hand_picked_dataset: Dataset = None) -> List[dict]:
        messages = [get_openai_messages_for_observation(observation, hpo, system_message, user_message_wrapper,
                                                        assistant_message_table_header, include_response, few_shot_dataset,
                                                        few_shot_k, few_shot_k_min, hand_picked_dataset) \
                    for observation in tqdm(dataset.observations)]
        return messages

# Generate list to use as input for OpenAI GPT 3.5 Pretraining.
# Uses a HPO object to get preferred terms for observed hpo concepts.
def get_openai_finetuning_messages(dataset: Dataset, include_response: bool = True, hpo = None,
                                   system_message: str = None, user_message_wrapper: str = None,
                                   assistant_message_table_header: str = None, filename: str = None) -> List[dict]:
    openai_dataset = []

    for observation in tqdm(dataset.observations):

        messages = []
        
        if system_message:
            messages.append({'role': 'system', 'content': system_message})
        # User input it observation text only
        user_message = observation.text
        if user_message_wrapper is not None:
            user_message = user_message_wrapper % user_message
        messages.append({'role': 'user', 'content': user_message})

        if include_response:
            if len(observation.terms) > 0:
                # Build assistant response from terms
                assistant_messages_per_term = []
                for term in observation.terms:
                    concept = hpo.get_concept_by_hpo_id(term.hpo_id)
                    preferred_term = concept.get_preferred_term()
                    assistant_message_for_term = ' | '.join([
                        preferred_term,
                        #term.hpo_id,
                        #'X' if term.polarity else 'T',
                        #'Absent' if term.polarity else 'Present',
                        term.get_tagged_text(),
                    ])
                    assistant_message_for_term = '| %s |' % assistant_message_for_term
                    assistant_messages_per_term.append(assistant_message_for_term)
                
                if assistant_message_table_header:
                    assistant_message = '%s\n%s' % (assistant_message_table_header, '\n'.join(assistant_messages_per_term))
                else:
                    assistant_message = '\n'.join(assistant_messages_per_term)
            else:
                # No terms for an observation
                # assistant_message = '| NA | NA |'
                assistant_message = EMPTY_RESPONSE_MESSAGE
            messages.append({'role': 'assistant', 'content': assistant_message})

        openai_dataset.append({'messages': messages})
    
    if filename is not None:
        save_to_jsonl(openai_dataset, os.path.join(FINE_TUNE_DIR, filename))

    return openai_dataset