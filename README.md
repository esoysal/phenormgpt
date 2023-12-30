# PheNormGPT

PheNormGPT is a framework for extracting and normalizing key findings in clinical text to Human Phenotype Ontology (HPO) concepts by leveraging OpenAI's GPT-3.5 Turbo and GPT-4 models. It was developed and evaluated in the [BioCreative VIII Track 3 shared task](https://biocreative.bioinformatics.udel.edu/tasks/biocreative-viii/track-3/), focusing on genetic phenotype extraction from dysmorphology physical examination notes.

## Contents

The [notebook](src/phenormgpt/notebook/) directory contains two IPython notebooks to run the code in this repository:
- [finetune.ipynb](src/phenormgpt/notebook/finetune.ipynb): Fine-tune an OpenAI GPT model using the dataset provided. Currently, only GPT-3.5 fine-tuning is supported though the OpenAI API.
- [inference.ipynb](src/phenormgpt/notebook/inference.ipynb): Generate predictions on an inference dataset, using a base or a fine-tuned OpenAI GPT model. Optionally generate few-shot prompts, given a few-shot dataset.

## Installation

1. Install the dependencies:

```bash
pip install -r requirements.txt
```

2. Add your OpenAI API key to the [OpenAI config file](src/phenormgpt/config/openai_config.py).

3. Double check the [main config file](src/phenormgpt/config/config.py) for locations of the dataset and resources. The dataset and resources used by this project can be found on the [GitHub repository](https://github.com/Ian-Campbell-Lab/Clinical-Genetics-Training-Data/) or the [main page](https://biocreative.bioinformatics.udel.edu/tasks/biocreative-viii/track-3/) of the shared task.

## Citation

Please cite our work as follows:
```bibtex
@proceedings{soysal_2023_10104725,
  title        = {UTH-Olympia@BC8 Track 3: Adapting GPT-4 for Entity
                   Extraction and Normalizing Responses to Detect Key
                   Findings in Dysmorphology Physical Examination
                   Observations
                  },
  year         = 2023,
  publisher    = {Zenodo},
  month        = nov,
  doi          = {10.5281/zenodo.10104725},
  url          = {https://doi.org/10.5281/zenodo.10104725},
}
```