import os

# Elasticsearch settings
ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = os.getenv("ES_PORT", 9200)
ES_INDEX = os.getenv("ES_INDEX", "kandidater")
ES_TAX_INDEX = os.getenv("ES_TAX_INDEX", "taxonomy")

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# Query parameters
OCCUPATION = 'yrke'
GROUP = 'yrkesgrupp'
FIELD = 'yrkesomrade'
SKILL = 'kompetens'
LANGUAGE = 'sprak'
MUNICIPALITY = 'kommunkod'
REGION = 'lanskod'
WORKTIME_EXTENT = 'arbetstidsomfattning'

MAX_OFFSET = 2000
MAX_LIMIT = 1000

taxonomy_type = {
    OCCUPATION: 'jobterm',
    GROUP: 'jobgroup',
    FIELD: 'jobfield',
    SKILL: 'skill',
    LANGUAGE: 'language',
    MUNICIPALITY: 'municipality_code',
    REGION: 'region_code',
    WORKTIME_EXTENT: 'worktime_extent'
}
