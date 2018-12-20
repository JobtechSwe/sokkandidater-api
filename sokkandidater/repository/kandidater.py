import logging
from valuestore import taxonomy
from sokkandidater import settings
from sokkandidater.repository import elastic
import json

log = logging.getLogger(__name__)


def find_candidates(args):
    query_dsl = _parse_args(args)
    log.debug(json.dumps(query_dsl, indent=2))
    query_result = elastic.search(index=settings.ES_INDEX, body=query_dsl)
    return query_result.get('hits', {})


# Todo: Refactor
def _parse_args(args):
    offset = args.get('offset', 0)
    limit = args.get('limit', 10)

    sekundaryrken = _find_secondary_yrkesroller(args.get(taxonomy.GROUP),
                                                args.get(taxonomy.FIELD))
    yrke_bool_query = _build_yrkes_query(args.get(taxonomy.OCCUPATION), sekundaryrken)
    kompetens_bool_query = _build_bool_should_query("erfarenhet.kompetens.kod",
                                                    args.get(taxonomy.SKILL))
    plats_bool_query = _build_plats_query(args.get(taxonomy.MUNICIPALITY),
                                          args.get(taxonomy.REGION))
    sprak_bool_query = _build_bool_should_query("erfarenhet.sprak.kod",
                                                args.get(taxonomy.LANGUAGE))
    worktime_bool_query = _build_worktimeextent_should_query(
        args.get(taxonomy.WORKTIME_EXTENT))

    query_dsl = {"query": {"bool": {"must": []}}, "from": offset, "size": limit}

    if yrke_bool_query:
        query_dsl['query']['bool']['must'].append(yrke_bool_query)
    if kompetens_bool_query:
        query_dsl['query']['bool']['must'].append(kompetens_bool_query)
    if plats_bool_query:
        query_dsl['query']['bool']['must'].append(plats_bool_query)
    if sprak_bool_query:
        query_dsl['query']['bool']['must'].append(sprak_bool_query)
    if worktime_bool_query:
        query_dsl['query']['bool']['must'].append(worktime_bool_query)

    if args.get(settings.EXPERIENCE) == 'no' and yrke_bool_query:
        no_exp = sekundaryrken
        if args.get(taxonomy.OCCUPATION):
            no_exp += args.get(taxonomy.OCCUPATION)
        query_dsl['query']['bool']['must_not'] = \
            {"terms": {"erfarenhet.yrkesroll.kod": no_exp}}

    if args.get(settings.SORT):
        query_dsl['sort'] = [settings.sort_options.get(args.pop(settings.SORT))]
    return query_dsl


def _find_secondary_yrkesroller(yrkesgrupper, yrkesomraden):
    sekundaryrken = []
    yrkesgrupper = yrkesgrupper or []
    yrkesomraden = yrkesomraden or []
    if yrkesomraden:
        yrkesgrupper += [t['_source']['legacy_ams_taxonomy_id']
                         for t in
                         taxonomy.find_concepts(elastic, None, yrkesomraden, 'jobgroup')
                         .get('hits', {})
                         .get('hits', [])]
    log.info("yrkesgrupper: %s" % yrkesgrupper)
    if yrkesgrupper:
        sekundaryrken = [t['_source']['legacy_ams_taxonomy_id']
                         for t in
                         taxonomy.find_concepts(elastic, None, yrkesgrupper, 'jobterm')
                         .get('hits', {})
                         .get('hits', [])]

    log.debug("sekundaryrken: %s" % sekundaryrken)
    return sekundaryrken


def _build_yrkes_query(yrkesroller, sekundaryrken):
    yrken = [] if not yrkesroller else yrkesroller

    yt_query = [{"term":
                 {"krav.yrkesroll.kod": {
                     "value": y, "boost": 2.0}}} for y in yrken]
    yt_query += [{"term": {"erfarenhet.yrkesroll.kod": {"value": y}}} for y in yrken]

    syt_query = [{"term": {"krav.yrkesroll.kod": {
        "value": y, "boost": 1.0}}} for y in sekundaryrken]
    syt_query += [{"term": {"erfarenhet.yrkesroll.kod": y}} for y in sekundaryrken]

    primary_choice = {"bool": {"should": yt_query,
                               "boost": 2.0}} if yt_query else None
    secondary_choice = {"bool": {"should": syt_query}} if sekundaryrken else None

    if primary_choice or secondary_choice:
        combined_query = {"bool": {"should": []}}
        if primary_choice:
            combined_query['bool']['should'].append(primary_choice)
        if secondary_choice:
            combined_query['bool']['should'].append(secondary_choice)
        return combined_query
    else:
        return None


def _build_plats_query(kommunkoder, lanskoder):
    kommuner = [] if not kommunkoder else kommunkoder
    lan = [] if not lanskoder else lanskoder

    plats_term_query = [{"term": {"krav.kommun.id": {
        "value": kkod,
        "boost": 5.0}}} for kkod in kommuner]
    plats_term_query += [{"term": {
        "krav.lan.id": {"value": lkod,
                        "boost": 1.0}}} for lkod in lan]
    additional_lan = [kommunkod[0:2] for kommunkod in kommuner if len(kommunkod) > 2]
    plats_query = {"bool": {"should": plats_term_query}}
    secondary_plats_query = [{"term": {
        "krav.lan.id": {"value": lkod}}} for lkod in additional_lan]

    if plats_query and secondary_plats_query:
        plats_query["bool"]["should"].append({
            "bool": {
                "must": secondary_plats_query,
                "must_not": [{"exists": {"field": "krav.kommun"}}],
                "boost": 0.5}})
        return plats_query
    return None


def _build_worktimeextent_should_query(lista):
    arbetstidskoder = [] if not lista else lista

    # If the chosen code is '1' (heltid (default)) we don't need to search for it
    term_query = [{"term": {"krav.arbetstidsomfattning.kod":
                            {"value": kod}}} for kod in arbetstidskoder if kod != '1']

    return {"bool": {"should": term_query}} if term_query else None


def _build_bool_should_query(key, itemlist):
    items = [] if not itemlist else itemlist

    term_query = [{"term": {key: {"value": item}}} for item in items]

    return {"bool": {"should": term_query}} if term_query else None
