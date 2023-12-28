from typing import List

class Term:
    def __init__(self, hpo_id: str, preferred_term: str, polarity: bool, spans: List[str], text: str):
        self.hpo_id = hpo_id
        self.preferred_term = preferred_term
        self.polarity = polarity
        self.spans = spans
        self.text = text.replace('[', '(').replace(']', ')')
        self.matcher = None
        self.extracted_term = None
        
    def get_spans(self, numeric: bool = True) -> list:
        if numeric:
            return [[int(index) for index in span.split('-')] for span in self.spans]
        else:
            return self.spans
        
    def get_preferred_term(self) -> str:
        return self.preferred_term
    
    # Returns true if input can be a valid prediction
    def is_valid(self) -> bool:
        # Check if HPO term is a valid prediction
        hpo_id_valid = self.hpo_id is not None and self.hpo_id.startswith('HP')
        
        # Check if we have spans
        spans_valid = self.spans is not None and len(self.spans) > 0
        
        # Check if span values are valid
        if spans_valid:
            last_index = self.get_spans()[-1][-1]
            spans_valid = spans_valid and last_index <= len(self.text)
        
        return hpo_id_valid and spans_valid
    
    def __str__(self, extended: bool = True) -> str:
        try:
            term_string = '\t'.join([
                self.hpo_id,
                #'X' if self.polarity else '',
                ','.join(self.spans)
            ])
        except Exception:
            print(self.hpo_id)
            print(','.join(self.spans))
        if extended:
            term_string = '%s\t%s' % (self.preferred_term, term_string)
        
        return term_string
    
    def get_tagged_text(self) -> str:
        text = self.text
        offset = 0
        for span in self.spans:
            begin, end = span.split('-')
            begin = int(begin) + offset
            end = int(end) + offset
            text = text[:end] + ']' + text[end:]
            text = text[:begin] + '[' + text[begin:]
            offset += 2
        return text
    
    def get_observed_term(self) -> str:
        observed_term_parts = [self.text[span[0]:span[1]] for span in self.get_spans(True)]
        observed_term = ' '.join(observed_term_parts)
        return observed_term

class Observation:
    def __init__(self, observation_id: str, text: str, bodyloc: str):
        self.observation_id = observation_id
        self.text = text.replace('[', '(').replace(']', ')')
        self.bodyloc = bodyloc.replace('"', '')
        self.terms = []
    
    def add_term(self, term: Term):
        self.terms.append(term)
    
    def get_observation_text(self) -> 'Observation':
        observation = Observation(self.observation_id, self.text, self.bodyloc)
        return observation
    
    def get_hpo_ids(self) -> List[str]:
        return [term.hpo_id for term in self.terms]
    
    def get_valid_terms(self) -> List[Term]:
        return [term for term in self.terms if term.is_valid()]
    
    # Function to get a subset of terms for the observation, based on HPO IDs.
    # Used to filter validation set by train set HPO IDs for error analysis.
    def filter_by_hpo_ids(self, hpo_ids: List[str]):
        filtered_terms = [term for term in self.terms if term.hpo_id in hpo_ids]
        self.terms = filtered_terms
    
    # Function to get a subset of terms for the observation, based on HPO IDs.
    # Used to filter validation set by train set HPO IDs for error analysis.
    def filter_out_by_hpo_ids(self, hpo_ids: List[str]):
        filtered_terms = [term for term in self.terms if term.hpo_id not in hpo_ids]
        self.terms = filtered_terms
        
    def has_terms(self) -> bool:
        return len(self.terms) > 0
    
    def __str__(self, include_terms: bool = True) -> str:
        
        if self.observation_id is None:
            observation_id_str = ''
        else:
            observation_id_str = self.observation_id
        
        if not include_terms:
            return '%s\t%s\n' % (observation_id_str, self.text)
        
        term_strs = [term.__str__() for term in self.terms]
        if len(term_strs) == 0:
            term_strs = ['\t'.join(['NA', 'NA', 'NA'])]
            
        obs_str = ''
        for term_str in term_strs:
            obs_str += '\t'.join([observation_id_str, self.text, term_str]) + '\n'
        return obs_str
    
    def get_word_concept_matches(self, matching_function) -> List[str]:
        concept_ids = []
        for word in self.text.split(' '):
            if len(word) > 2:
                concept_ids += matching_function(word)
        return concept_ids
    
    def copy_id(self, observation: 'Observation'):
        self.observation_id = observation.observation_id
        
class Dataset:
    def __init__(self, observations: List[str] = []):
        self.observations = observations
    
    def get_observation_index(self, observation_id: str) -> int:
        for index, observation in enumerate(self.observations):
            if observation.observation_id == observation_id:
                return index
        print('Error: Observation ID not found: %s.' % observation_id)
        return -1
            
    def add_observation(self, observation: Observation):
        self.observations.append(observation)
    
    def get_hpo_ids(self) -> List[str]:
        all_obs_hpo_ids = [observation.get_hpo_ids() for observation in self.observations]
        hpo_ids = [hpo_id for obs_hpo_ids in all_obs_hpo_ids for hpo_id in obs_hpo_ids]
        return hpo_ids
    
    # Function to get a subset of the dataset, based on HPO IDs.
    # Used to filter validation set by train set HPO IDs for error analysis.
    def filter_by_hpo_ids(self, hpo_ids: List[str]):
        for observation in self.observations:
            observation.filter_by_hpo_ids(hpo_ids)
    
    # Function to get a subset of the dataset, based on HPO IDs.
    # Used to filter validation set by train set HPO IDs for error analysis.
    def filter_out_by_hpo_ids(self, hpo_ids: List[str]):
        for observation in self.observations:
            observation.filter_out_by_hpo_ids(hpo_ids)
                    
    def filter_bodylocs(self, bodylocs: List[str]):
        observations = [observation for observation in self.observations if observation.bodyloc in bodylocs]
        return Dataset(observations)
        
    def __str__(self, include_terms: bool = True, include_headers: bool = True, bodylocs: List[str] = []) -> str:
        if len(bodylocs) > 0:
            dataset_str = ''.join([observation.__str__(include_terms) for observation in self.filter_bodylocs(bodylocs).observations])
        else:
            dataset_str = ''.join([observation.__str__(include_terms) for observation in self.observations])
        if include_headers:
            headers = 'ObservationID\tText'
            if include_terms:
                headers += '\tHPO Term\tPolarity\tSpans'
            dataset_str = '%s\n%s' % (headers, dataset_str)
        return dataset_str
    
    def filter_has_terms(self) -> 'Dataset':
        dataset = Dataset()
        dataset.observations = []
        for observation in self.observations:
            if observation.has_terms():
                dataset.add_observation(observation)
        return dataset
    
    def filter_no_terms(self) -> 'Dataset':
        dataset = Dataset()
        dataset.observations = []
        for observation in self.observations:
            if not observation.has_terms():
                dataset.add_observation(observation)
        return dataset
    
    def copy_observation_ids(self, dataset: 'Dataset'):
        num_observations = len(self.observations)
        assert(num_observations == len(dataset.observations))
        for i in range(num_observations):
            self.observations[i].copy_id(dataset.observations[i])
    
    def write_to_tsv(self, filename: str):
        with open(filename, 'w') as outfile:
            outfile.write('ObservationID\tText\tHPO Term\tSpans\n')
            for observation in self.observations:
                past_spans = []
                terms = observation.get_valid_terms()
                if len(terms) != len(observation.terms):
                    for term in observation.terms:
                        if term not in terms and term.hpo_id is not None:
                            print('Error: Invalid term present in observation: %s' % observation.text)
                            print('\t', term.get_preferred_term())
                if len(terms) == 0:
                    outfile.write('%s\t%s\tNA\tNA\n' % (observation.observation_id, observation.text))
                else:
                    for term in terms:
                        spans = ','.join(term.spans)
                        if spans not in past_spans:
                            outfile.write('%s\t%s\t%s\t%s\n' % (observation.observation_id, observation.text,
                                                               term.hpo_id, spans))
                            past_spans.append(spans)
                        else:
                            print('Error: Multiple concepts for single span for observation: %s' % observation.text)
    
    def write(self, filename: str):
        with open(filename, 'w') as outfile:
            outfile.write(self.__str__())