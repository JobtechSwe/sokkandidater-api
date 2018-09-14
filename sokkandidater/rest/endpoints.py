from sokkandidater.rest import api
from flask import request
from flask_restplus import Resource, abort
from sokkandidater.repository import kandidater
from sokkandidater.repository import taxonomy
from sokkandidater import settings
from sokkandidater.settings import taxonomy_type
from sokkandidater.rest.models import kandidat_lista, sok_kandidat_query, taxonomy_query


@api.route('/sok')
class Search(Resource):
    @api.doc(
        params={
            settings.OFFSET: "Börja lista resultat från denna position "
            "(0-%d)" % settings.MAX_OFFSET,
            settings.LIMIT: "Antal resultat att visa (0-%d)" % settings.MAX_LIMIT,
            settings.OCCUPATION: "En eller flera yrkesbenämningskoder enligt taxonomi",
            settings.GROUP: "En eller flera yrkesgruppskoder enligt taxonomi",
            settings.FIELD: "En eller flera yrkesområdeskoder enligt taxonomi",
            settings.SKILL: "En eller flera kompetenskoder enligt taxonomi",
            settings.LANGUAGE: "En eller flera språkkoder enligt taxonomi",
            settings.MUNICIPALITY: "En eller flera kommunkoder",
            settings.REGION: "En eller flera länskoder",
            settings.WORKTIME_EXTENT: "Arbetstidsomfattningskod enligt taxonomi",
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
        return self.marshal_kandidater(result)

    # Prepare to be able to marshal with different result models
    @api.marshal_with(kandidat_lista)
    def marshal_kandidater(self, result):
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
            "(giltiga värden: %s)" % list(taxonomy_type.keys())
        }
    )
    @api.expect(taxonomy_query)
    def get(self):
        q = request.args.get('q', None)
        kod = request.args.get('kod', None)
        typ = taxonomy_type.get(request.args.get('typ', None), None)
        offset = request.args.get('offset', 0)
        limit = request.args.get('offset', 10)
        response = taxonomy.find_concepts(q, kod, typ, offset, limit)
        if not response:
            abort(500, custom="The server failed to respond properly")
        return response
