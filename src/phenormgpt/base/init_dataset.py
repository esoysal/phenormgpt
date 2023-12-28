import json

from base.dataset import Dataset, Observation, Term
from base.load_hpo import hpo
from prompting.prompts import ASSISTANT_MESSAGE_TABLE_HEADER, EMPTY_RESPONSE_MESSAGE

def init_dataset_from_file(observations_filepath: str, key_obs_only: bool = True) -> Dataset:
    dataset = Dataset()
    dataset.observations = []

    with open(observations_filepath, 'r', encoding='utf-8') as observations_file:
        # Read headers
        line = observations_file.readline().replace('\n', '')
        headers = line.split('\t')

        last_observation_id = None

        # Read rows
        line = observations_file.readline().replace('\n', '')
        while line:
            # Parse line
            observation_id, text, hpo_id, polarity, spans = line.split('\t')

            # Update observations
            if observation_id != last_observation_id:

                # Save previous observation
                if last_observation_id is not None:
                    dataset.add_observation(observation)

                # Create new observation
                bodyloc = text.split(':')[0]
                observation = Observation(observation_id, text, bodyloc)
                last_observation_id = observation_id

            # Add term if valid
            if hpo_id != 'NA':
                polarity = True if polarity == 'X' else False
                spans = spans.split(',')
                hpo_concept = hpo.get_concept_by_hpo_id(hpo_id)
                term = Term(hpo_id, hpo_concept.preferred_term, polarity, spans, text)
                if not (key_obs_only and polarity):
                    observation.add_term(term)

            # Read next line
            line = observations_file.readline().replace('\n', '')

        dataset.add_observation(observation)
        return dataset

def init_dataset_from_file_no_terms(observations_filepath: str) -> 'Dataset':
    dataset = Dataset()
    dataset.observations = []
    
    with open(observations_filepath, 'r', encoding='utf-8') as observations_file:
        headers = observations_file.readline().replace('\n', '')
        line = observations_file.readline().replace('\n', '')
        while line:
            observation_id, text = line.split('\t')
            bodyloc = text.split(':')[0]
            observation = Observation(observation_id, text, bodyloc)
            dataset.add_observation(observation)
            line = observations_file.readline().replace('\n', '')
            
    return dataset

# Initialize dataset from a JSON including observations and extracted concepts.
# Must pass in a matcher function to normalize the extracted concepts.
def init_dataset_from_openai_responses(responses_filepath: str) -> Dataset:
    dataset = Dataset()
    dataset.observations = []
    
    responses_dict = json.loads(open(responses_filepath, 'r').read())
    for item in responses_dict:
        
        # Create observation
        text = item['observation']
        bodyloc = text.split(':')[0]
        observation = Observation(None, text, bodyloc)
        
        # Create terms
        response = item['response']
        
        # Parse response
        if response != EMPTY_RESPONSE_MESSAGE: # Skip if there are no concepts
            term_lines = response.split('\n')[ASSISTANT_MESSAGE_TABLE_HEADER.count('\n') + 1:] # Skip table headers
            for line in term_lines:
                try:
                    _, preferred_term, tagged_text, _ = line.split('|')
                except ValueError as e:
                    print('Error: Can\'t parse line: %s' % line)
                    raise e
                preferred_term = preferred_term.strip()
                tagged_text = tagged_text.strip()
                
                # Calculate Spans
                spans = []
                start_indices = [i for i in range(len(tagged_text)) if tagged_text.startswith('[', i)]
                end_indices = [i for i in range(len(tagged_text)) if tagged_text.startswith(']', i)]

                if len(start_indices) != len(end_indices):
                    print('Error parsing extracted term line: %s. Uneven tagging.' % preferred_term)

                # Calculate spans from tagged_text, accounting index shifts.
                for i in range(len(start_indices)):
                    span = '%d-%d' % (start_indices[i] - (2 * i), end_indices[i] - ((2 * i) + 1))
                    spans.append(span)
                
                term = Term(None, preferred_term, False, spans, text)
                observation.add_term(term)
        
        dataset.add_observation(observation)
        
    return dataset