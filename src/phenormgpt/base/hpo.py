from typing import List

class Concept:
    def __init__(self, hpo_id: str, preferred_term: str = None, preferred_terms: List[str] = [],
                 synonyms: List[str] = [], hierarchies: List[str] = []):
        self.hpo_id = hpo_id
        self.preferred_term = preferred_term
        self.preferred_terms = preferred_terms
        self.synonyms = synonyms
        self.hierarchies = hierarchies
    
    def get_preferred_term(self) -> str:
        if self.preferred_term is not None and len(self.preferred_term) > 0:
            return self.preferred_term
        elif self.preferred_terms is not None and len(self.preferred_terms) > 0:
            return self.preferred_terms[0]
        elif self.synonyms is not None and len(self.synonyms) > 0:
            return self.synonyms[0]
        else:
            return None
    
    def get_all_terms(self) -> List[str]:
        terms = []
        if self.preferred_term is not None and len(self.preferred_term) > 0:
            terms.append(self.preferred_term)
        if self.preferred_terms is not None and len(self.preferred_terms) > 0:
            terms.extend(self.preferred_terms)
        if self.synonyms is not None and len(self.synonyms) > 0:
            terms.extend(self.synonyms)
        
        return terms
            
    
    def __str__(self, simplified: bool = True) -> str:
        if simplified:
            terms = list(set(self.preferred_terms + self.synonyms))
            return '\t'.join([
                self.hpo_id,
                '|'.join(terms)
            ])
        else:
            return '\t'.join([
                self.hpo_id,
                '|'.join(self.preferred_terms),
                '|'.join(self.synonyms),
                '|'.join(self.hierarchies)
            ])

class HPO:
    def __init__(self):
        self.concepts = {}
    
    def get_hpo_ids(self) -> List[str]:
        return list(self.concepts.keys())
    
    def get_concepts(self) -> List[Concept]:
        return list(self.concepts.values())
    
    def add_concept(self, concept: Concept):
        if concept.hpo_id in self.get_hpo_ids():
            # Overwrite concepts where applicable
            if concept.preferred_term is not None and len(concept.preferred_term) > 0:
                self.concepts[concept.hpo_id].preferred_term = concept.preferred_term
            if concept.preferred_terms is not None and len(concept.preferred_terms) > 0:
                self.concepts[concept.hpo_id].preferred_terms = concept.preferred_terms
            if concept.synonyms is not None and len(concept.synonyms) > 0:
                self.concepts[concept.hpo_id].synonyms = concept.synonyms
            if concept.hierarchies is not None and len(concept.hierarchies) > 0:
                self.concepts[concept.hpo_id].hierarchies = concept.hierarchies
        else:
            # Add a new concept
            self.concepts[concept.hpo_id] = concept        
    
    # Merge two HPOs, used to initiate from multiple files
    def merge(self, hpo):
        for concept in hpo.get_concepts():
            self.add_concept(concept)
    
    # Subtract one HPO from another, used to apply exclusion files
    def subtract(self, hpo):
        for hpo_id in hpo.get_hpo_ids():
            if hpo_id in self.concepts.keys():
                self.concepts.pop(hpo_id)
    
    # Only returns concepts that include given aui in their hierarchy
    def filter_auis(self, auis: List[str]):
        filtered_hpo = HPO()
        for concept in self.get_concepts():
            added = False
            for hierarcy in concept.hierarchies:
                for aui in auis:
                    if aui in hierarcy:
                        filtered_hpo.add_concept(concept)
                        added = True
                        break
                if added:
                    break
                    
        return filtered_hpo
    
    def get_concept_by_hpo_id(self, hpo_id: str) -> Concept:
        if hpo_id in self.get_hpo_ids():
            return self.concepts[hpo_id]
        return None
    
    def get_concepts_by_hpo_ids(self, hpo_ids: List[str]) -> List[Concept]:
        concepts = []
        for hpo_id in hpo_ids:
            concepts += self.get_concept_by_hpo_id(hpo_id)
        
        return [concept for concept in concepts if concept is not None]
    
    def find_concept_by_term(self, term: str) -> Concept:
        for concept in self.get_concepts():
            if term.lower() in [term_.lower() for term_ in concept.get_all_terms()]:
                return concept
        return None

    def __str__(self, include_headers: bool = True, simplified: bool = True) -> str:
        hpo_str = ''
        if include_headers:
            if simplified:
                hpo_str += 'HPO ID\tTerms\n'
            else:
                hpo_str += 'HPO ID\tPreferred Terms\tSynonyms\tHierarchies\n'
        
        hpo_str += '\n'.join([concept.__str__(simplified) for concept in self.get_concepts()])
        
        return hpo_str