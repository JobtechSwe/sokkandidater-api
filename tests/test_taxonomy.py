import sys
import pytest
from elasticsearch.exceptions import RequestError
import logging as log
from sokkandidater import settings
from sokkandidater.repository import elastic
from valuestore import taxonomy
from tests import test_kandidater


def find_concepts(query_string=None, taxonomy_code=None, entity_type=None, offset=0, limit=10):
    musts = []
    sort = None
    if query_string:
        musts.append({"term": {"label.autocomplete": query_string}})
    else:
        offset = 0
        limit = 5000
        # No numerical sorting for autocomplete-query
        sort = [
            {
                "num_id": {"order": "asc"}
            }
        ]
    if taxonomy_code:
        musts.append({"term": {"parent.id": taxonomy_code}})
    if entity_type:
        musts.append({"term": {"type": entity_type}})

    if not musts:
        query_dsl = {"query": {"match_all": {}}, "from": offset, "size": limit}
    else:
        query_dsl = {
            "query": {
                "bool": {
                    "must": musts
                }
            },
            "from": offset,
            "size": limit
        }
    if sort:
        query_dsl['sort'] = sort
    try:
        #return _format_response(elastic.search(index=settings.ES_TAX_INDEX, body=query_dsl))
        return query_dsl
    except RequestError:
        log.error("Failed to query Elasticsearch")
        return None

@pytest.mark.parametrize("query_string", [ None, [], "query_1"] )
@pytest.mark.parametrize("taxonomy_code", [ None, [], "taxkod_1" ] )
@pytest.mark.parametrize("entity_type", [ None, [], "entity_1" ] )
@pytest.mark.parametrize("offset, limit", [ [0,10], [0,1] ])
def test_find_concepts(query_string, taxonomy_code, entity_type, offset, limit):
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    d = taxonomy.find_concepts(query_string, taxonomy_code, entity_type, offset, limit) #use of find_concept with return query_dsl
    print(d)
    print(query_string, taxonomy_code, entity_type, offset, limit)
    if not query_string: # query_string == None,[]
        assert list(test_kandidater.find('from', d)) == [0]
        assert list(test_kandidater.find('size', d)) == [5000]
        assert list(test_kandidater.find('order', d)) == ['asc']
        if not taxonomy_code and not entity_type:
            print("must NULL")
            assert list(test_kandidater.find('match_all', d)) == [{}]
    else: # query_string not empty
        assert list(test_kandidater.find('label.autocomplete', d)) == [query_string]
        assert list(test_kandidater.find('from', d)) == [offset]
        assert list(test_kandidater.find('size', d)) == [limit]
        if taxonomy_code:
            assert list(test_kandidater.find('parent.id', d)) == [taxonomy_code]
        if entity_type:
            assert list(test_kandidater.find('type', d)) == [entity_type]

def test_format_response(elastic_response): # see elastic_response fixture in conftest.py
    print('============================',sys._getframe().f_code.co_name,'============================ ')
    d = taxonomy._format_response(elastic_response)
    print(d)
    print(list(test_kandidater.find('_id', elastic_response)))
    if elastic_response:
        assert list(test_kandidater.find('antal', d)) == list(test_kandidater.find('total', elastic_response))
        assert list(test_kandidater.find('kod', d)) == list(test_kandidater.find('id', elastic_response))
        assert list(test_kandidater.find('term', d)) == list(test_kandidater.find('label', elastic_response))
        assert list(test_kandidater.find('typ', d)) == list(test_kandidater.find('type', elastic_response))
    else:
        assert list(test_kandidater.find('antal', d)) == [None] and list(test_kandidater.find('entiteter', d)) == [[]]


def get_concept(tax_id, tax_typ):
    query_dsl = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"id": tax_id}},
                        {"term": {"type": tax_typ}}
                    ]
                }
            }
        }
    # return _format_response(elastic.search(index=settings.ES_TAX_INDEX, body=query_dsl))
    return taxonomy._format_response(elastic.search(index=settings.ES_TAX_INDEX, body=query_dsl))
