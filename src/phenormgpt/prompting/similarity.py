import spacy
from base.dataset import Observation, Dataset

# Import spacy model for similarity calculations
try:
    model = spacy.load('en_core_web_md')
except OSError:
    from spacy.cli import download
    download('en_core_web_md')
    model = spacy.load('en_core_web_md')
    
def get_observation_similarity_score(observation1: Observation,
                                     observation2: Observation) -> float:
    doc1 = model(observation1.text)
    doc2 = model(observation2.text)
    return doc2.similarity(doc1)

def get_n_most_similar_observations(dataset: Dataset, observation: Observation, n: int = 10,
                                    use_bodyloc: bool = True):
    if use_bodyloc:
        # Search from body locations only
        bodyloc_dataset = dataset.filter_bodylocs([observation.bodyloc])
        dataset = bodyloc_dataset
    else:
        dataset = dataset                                                

    # If n is too large (not enough samples), readjust
    n = min(n, len(dataset.observations))
    
    # Build similarity dict
    similarity_dict = {}
    for candidate_observation in bodyloc_dataset.observations:
        similarity_dict[candidate_observation] = get_observation_similarity_score(candidate_observation,
                                                                                  observation)
    
    top_n_observations = list(dict(sorted(similarity_dict.items(), key=lambda x:-x[1])[:n]).keys())
    return Dataset(top_n_observations)