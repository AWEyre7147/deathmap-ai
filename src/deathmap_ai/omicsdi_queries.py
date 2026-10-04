"""Fixed, unfiltered OmicsDI capability queries; spelling variants stay separate."""

QUERY_STRATEGY_ID = "omicsdi-coculture-v1"
QUERIES = {
    "Q01": "CRISPR AND coculture",
    "Q02": "CRISPR AND co-culture",
    "Q03": 'CRISPR AND "co culture"',
    "Q04": 'CRISPR AND "T cell"',
    "Q05": 'CRISPR AND "natural killer"',
    "Q06": 'CRISPR AND "immune killing"',
}
