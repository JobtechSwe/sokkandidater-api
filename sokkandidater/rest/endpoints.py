from sokkandidater.rest import api
from flask import request
from flask_restplus import Resource, abort
from valuestore import taxonomy
from valuestore.taxonomy import tax_type
from sokkandidater import settings
from sokkandidater.repository import kandidater, elastic
from sokkandidater.rest.models import kandidat_lista, sok_kandidat_query, taxonomy_query


@api.route('/sok')
class Search(Resource):
    @api.doc(
        params={
            settings.OFFSET: "Börja lista resultat från denna position "
            "(0-%d)" % settings.MAX_OFFSET,
            settings.LIMIT: "Antal resultat att visa (0-%d)" % settings.MAX_LIMIT,
            taxonomy.OCCUPATION: "En eller flera yrkesbenämningskoder enligt taxonomi",
            taxonomy.GROUP: "En eller flera yrkesgruppskoder enligt taxonomi",
            taxonomy.FIELD: "En eller flera yrkesområdeskoder enligt taxonomi",
            taxonomy.SKILL: "En eller flera kompetenskoder enligt taxonomi",
            taxonomy.LANGUAGE: "En eller flera språkkoder enligt taxonomi",
            taxonomy.MUNICIPALITY: "En eller flera kommunkoder",
            taxonomy.REGION: "En eller flera länskoder",
            taxonomy.WORKTIME_EXTENT: "Arbetstidsomfattningskod enligt taxonomi",
            settings.RESULT_MODEL: "Resultatmodell"
        },
        responses={
            200: 'OK',
            500: 'Bad'
        }
    )
    @api.expect(sok_kandidat_query)
    def get(self):
        args = sok_kandidat_query.parse_args()
        result = kandidater.find_candidates(args)
        if args.get(settings.RESULT_MODEL) == 'elastic':
            return self.marshal_elastic_result(result)
        return self.marshal_kandidater(result)

    # Prepare to be able to marshal with different result models
    @api.marshal_with(kandidat_lista)
    def marshal_kandidater(self, result):
        return result

    def marshal_elastic_result(self, result):
        return result


@api.route('/vardeforrad')
class Valuestore(Resource):

    @api.doc(
        params={
            "q": "Fritextfråga mot taxonomin. (Kan t.ex. användas för "
            "autocomplete / type ahead)",
            "kod": "Begränsa sökning till taxonomier som har överliggande kod "
            "(används med fördel tillsammans med typ)",
            "typ": "Visa enbart taxonomivärden av typ "
            "(giltiga värden: %s)" % list(tax_type.keys())
        }
    )
    @api.expect(taxonomy_query)
    def get(self):
        args = taxonomy_query.parse_args()
        q = request.args.get('q', None)
        kod = args.get('kod') or None
        typ = tax_type.get(request.args.get('typ', None), None)
        offset = request.args.get('offset', 0)
        limit = request.args.get('offset', 10)
        response = taxonomy.find_concepts(elastic, q, kod, typ, offset, limit)
        if not response:
            abort(500, custom="The server failed to respond properly")
        return taxonomy.format_response(response)
