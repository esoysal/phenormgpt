SYSTEM_MESSAGE = """Extract Human Phenotype Ontology (HPO) concepts from the given text of a physical examination note into a table containing standard HPO preferred term and marked original text with square brackets surrounding the words associated with the HPO term.
If there are no abnormal clinical observations, return \"NA\"."""
USER_MESSAGE_WRAPPER = '%s'
ASSISTANT_MESSAGE_TABLE_HEADER = """| HPO Preferred Term | Marked Original Text |
| ------------------ | -------------------- |"""
EMPTY_RESPONSE_MESSAGE = 'NA'