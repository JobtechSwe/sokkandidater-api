from flask_restplus import fields, reqparse, inputs
from valuestore import taxonomy
from sokkandidater.rest import api
from sokkandidater import settings


# Resultatmodeller
resultat_plats = api.model('Plats', {
    'id': fields.String(attribute='id'),
    'namn': fields.String(attribute='label')
})

resultat_geoposition = api.inherit('GeoPosition', resultat_plats, {
    'longitud': fields.Float(attribute='longitude'),
    'latitud': fields.Float(attribute='latitude')
})

resultat_taxonomi = api.model('TaxonomiEntitet', {
    'kod': fields.String(),
    'term': fields.String()
})

resultat_taxonomi_niva = api.model('TaxonomiEntitetWithLevel', {
    'kod': fields.String(),
    'term': fields.String(),
    'niva': fields.String()
})

matchande_kandidat = api.model('MatchandeKandidat', {
    'arbetssokandeprofilId': fields.String(attribute='_source.referensid'),
    'anvandarId': fields.String(attribute='_source.anvandarid'),
    'namn': fields.String(attribute='_source.namn'),
    'score': fields.Float(attribute='_score'),
    'senastModifierad': fields.String(attribute='_source.timestamp'),
    'kommun': fields.List(fields.Nested(resultat_taxonomi),
                          attribute='_source.krav.kommun'),
    'lan': fields.List(fields.Nested(resultat_taxonomi), attribute='_source.krav.lan'),
    'land': fields.List(fields.Nested(resultat_taxonomi), attribute='_source.krav.land'),
    'yrkesroller': fields.List(fields.Nested(resultat_taxonomi),
                               attribute='_source.krav.yrkesroll'),
    'kompetenser': fields.List(fields.Nested(resultat_taxonomi),
                               attribute='_source.erfarenhet.kompetens'),
    'erfarenheter': fields.List(fields.Nested(resultat_taxonomi_niva),
                                attribute='_source.erfarenhet.yrkesroll'),
    'sprak': fields.List(fields.Nested(resultat_taxonomi_niva),
                         attribute='_source.erfarenhet.sprak'),
    'korkort': fields.List(fields.Nested(resultat_taxonomi),
                           attribute='_source.erfarenhet.korkort'),
    'utbildningsinriktning': fields.List(
        fields.Nested(resultat_taxonomi_niva),
        attribute='_source.erfarenhet.utbildningsinriktning'),
    'bostadsplats': fields.List(
        fields.Nested(resultat_taxonomi),
        attribute='_source.erfarenhet.bostadsplats')
})

kandidat_lista = api.model('Kandidater', {
    'antal': fields.Integer(attribute='total'),
    'totalScore': fields.Float(attribute='max_score'),
    'kandidater': fields.List(fields.Nested(matchande_kandidat), attribute='hits')
})


# Frågemodeller
sok_kandidat_query = reqparse.RequestParser()
sok_kandidat_query.add_argument('offset', type=inputs.int_range(0, settings.MAX_OFFSET),
                                default=0)
sok_kandidat_query.add_argument('limit', type=inputs.int_range(0, settings.MAX_LIMIT),
                                default=10)
sok_kandidat_query.add_argument(taxonomy.OCCUPATION, action='append')
sok_kandidat_query.add_argument(taxonomy.GROUP, action='append')
sok_kandidat_query.add_argument(taxonomy.FIELD, action='append')
sok_kandidat_query.add_argument(settings.EXPERIENCE, choices=['yes', 'no'])
sok_kandidat_query.add_argument(taxonomy.SKILL, action='append')
sok_kandidat_query.add_argument(taxonomy.LANGUAGE, action='append')
sok_kandidat_query.add_argument(taxonomy.MUNICIPALITY, action='append')
sok_kandidat_query.add_argument(taxonomy.REGION, action='append')
sok_kandidat_query.add_argument(taxonomy.WORKTIME_EXTENT)
sok_kandidat_query.add_argument(settings.RESULT_MODEL, choices=['kandidarer',
                                                                'elastic'])

taxonomy_query = reqparse.RequestParser()
taxonomy_query.add_argument('q')
taxonomy_query.add_argument('kod', action='append')
taxonomy_query.add_argument('typ', choices=(taxonomy.OCCUPATION, taxonomy.GROUP,
                                            taxonomy.FIELD, taxonomy.SKILL,
                                            taxonomy.LANGUAGE, taxonomy.MUNICIPALITY,
                                            taxonomy.REGION, taxonomy.WORKTIME_EXTENT))
