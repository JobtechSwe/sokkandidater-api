from flask_restplus import Api

api = Api(version='1.0', title='Sök Kandidater',
          description='Hitta kandidater baserat på kompetenser, önskad arbetsort och yrkeserfarenhet.',
          default='sokkandidater',
          default_label="Verktyg för att hitta kandidater")
