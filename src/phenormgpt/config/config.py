from os.path import join

BASE_DIR = '../../../'
DATA_DIR = join(BASE_DIR, 'data')
OUTPUT_DIR = join(BASE_DIR, 'output')
RESOURCES_DIR = join(BASE_DIR, 'src', 'resources')

CACHE_DIR = join(OUTPUT_DIR, 'cache')
FINE_TUNE_DIR = join(OUTPUT_DIR, 'finetuned_datasets')

# BioCreative VIII Track 3 Resources
HPO_TERMS_FILEPATH = join(RESOURCES_DIR, 'HP2Terms.tsv')
UNOBSERVABLE_HPO_TERMS_FILEPATH = join(RESOURCES_DIR, 'UnobservableHPOTerms.tsv')

# Suplemental Resources
ABNORMAL_HPO_TERMS_FILEPATH = join(RESOURCES_DIR, 'AbnormalHPOTerms.tsv')
OBSOLETE_HPO_TERMS_FILEPATH = join(RESOURCES_DIR, 'ObsoleteHPOTerms.tsv')
HPO_JSON_FILEPATH = join(RESOURCES_DIR, 'hpo.json')
BODYLOC_JSON_FILEPATH = join(RESOURCES_DIR, 'category_auis.json')
OBSERVATION_DICT_FILEPATH = join(RESOURCES_DIR, 'hpo_observed_terms.json')
OBSERVATION_TRAIN_ONLY_DICT_FILEPATH = join(RESOURCES_DIR, 'hpo_observed_terms_train_only.json')

# BioCreative VIII Track 3 Datasets
TRAIN_FILEPATH = join(DATA_DIR, 'BioCreativeVIII3_TrainSet.tsv')
VAL_FILEPATH = join(DATA_DIR, 'BioCreativeVIII3_ValSet.tsv')
TEST_FILEPATH = join(DATA_DIR, 'BioCreativeVIII3_TestSetWithDecoy.tsv')

# Supplemental Data
TRAIN_ORIGINAL_FILEPATH = join(DATA_DIR, 'BioCreativeVIII3_TrainSetOriginal.tsv')
VAL_ORIGINAL_FILEPATH = join(DATA_DIR, 'BioCreativeVIII3_ValSetOriginal.tsv')

TRAIN_SAMPLE_FILEPATH = join(DATA_DIR, 'BioCreativeVIII3_TrainSetSample.tsv')
VAL_SAMPLE_FILEPATH = join(DATA_DIR, 'BioCreativeVIII3_ValSetSample.tsv')
TEST_SAMPLE_FILEPATH = join(DATA_DIR, 'BioCreativeVIII3_TestSetWithDecoySample.tsv')

TRAIN_PRED_FILEPATH = join(DATA_DIR, 'BioCreativeVIII3_TrainSetPred.tsv')
VAL_PRED_FILEPATH = join(DATA_DIR, 'BioCreativeVIII3_ValSetPred.tsv')

HANDPICKED_FILEPATH = join(RESOURCES_DIR, 'handpicked.txt')