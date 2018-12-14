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
OFFSET = 'offset'
LIMIT = 'limit'
RESULT_MODEL = 'resultmodel'
EXPERIENCE = 'workexperience'


MAX_OFFSET = 2000
MAX_LIMIT = 1000
