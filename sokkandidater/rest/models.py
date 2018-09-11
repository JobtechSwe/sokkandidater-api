from flask_restplus import fields, reqparse
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

matchande_kandidat = api.model('MatchandeKandidat', {
    'arbetssokandeprofilId': fields.String(attribute='_source.id'),
    'rubrik': fields.String(attribute='_source.rubrik'),
     'senastModifierad': fields.DateTime(attribute='_source.timestamp'),
    'efterfragadArbetsplats': fields.Nested({
        'land': fields.List(fields.Nested(resultat_plats), attribute='krav.land'),
        'lan': fields.List(fields.Nested(resultat_plats), attribute='krav.lan'),
        'kommun': fields.List(fields.Nested(resultat_plats), attribute='krav.kommun'),
        'geoPosition': fields.List(fields.Nested(resultat_geoposition), attribute='krav.geoPosition')
    }, attribute='_source', skip_none=True),
    'matchningsresultatKandidat': fields.Nested({
        'efterfragade': fields.Nested({
            'yrke': fields.List(fields.Nested(resultat_taxonomi)),
            'anstallningstyp': fields.List(fields.Nested(resultat_taxonomi)),
            'efterfragade': fields.List(fields.Nested(resultat_taxonomi)),
        }, attribute='krav', skip_none=True),
        'erbjudande': fields.Nested({
            'yrke': fields.List(fields.Nested(resultat_taxonomi)),
            'kompetens': fields.List(fields.Nested(resultat_taxonomi))
        }, attribute='erfarenhet', skip_none=True)
    }, attribute='_source')
})

kandidat_lista = api.model('Kandidater', {
    'antal': fields.Integer(attribute='total'),
    'kandidater': fields.List(fields.Nested(matchande_kandidat), attribute='hits')
})


# Frågemodeller
sok_kandidat_query = reqparse.RequestParser()
sok_kandidat_query.add_argument('offset', type=int, default=0)
sok_kandidat_query.add_argument('limit', type=int, default=10)
sok_kandidat_query.add_argument(settings.OCCUPATION, action='append')
sok_kandidat_query.add_argument(settings.GROUP, action='append')
sok_kandidat_query.add_argument(settings.FIELD, action='append')
sok_kandidat_query.add_argument(settings.SKILL, action='append')
sok_kandidat_query.add_argument(settings.LANGUAGE, action='append')
sok_kandidat_query.add_argument(settings.MUNICIPALITY, action='append')
sok_kandidat_query.add_argument(settings.REGION, action='append')
sok_kandidat_query.add_argument(settings.WORKTIME_EXTENT)

taxonomy_query = reqparse.RequestParser()
taxonomy_query.add_argument('q')
taxonomy_query.add_argument('kod')
taxonomy_query.add_argument('typ', choices=(settings.OCCUPATION, settings.GROUP, settings.FIELD, settings.SKILL,
                                            settings.LANGUAGE, settings.MUNICIPALITY, settings.REGION, settings.WORKTIME_EXTENT))
