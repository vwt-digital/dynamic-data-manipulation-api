import os

import config

import connexion
from flask_cors import CORS
from flask import request, current_app, g

from openapi_server.datastoredatabase import DatastoreDatabase
from openapi_server.firestoredatabase import FirestoreDatabase

from openapi_server import encoder, openapi_spec


def get_app():
    """
    Returns the OpenAPI app
    """

    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml',
                arguments={'title': 'Dynamic Data Manipulator API'},
                strict_validation=True)
    if 'GAE_INSTANCE' in os.environ or 'K_SERVICE' in os.environ:
        CORS(app.app, origins=config.ORIGINS, expose_headers=['Content-Disposition'])
    else:
        CORS(app.app, expose_headers=['Content-Disposition'])

    with app.app.app_context():
        current_app.__pii_filter_def__ = None
        current_app.db_client = None
        g.db_table_name = None
        g.db_table_id = None
        g.db_keys = None
        g.response_keys = None
        g.request_id = None
        g.request_queries = None
        g.forced_filters = None
        g.user = None
        g.token = None
        g.ip = None

        if hasattr(config, 'DATABASE_TYPE'):
            if config.DATABASE_TYPE == 'datastore':
                current_app.db_client = DatastoreDatabase()
            elif config.DATABASE_TYPE == 'firestore':
                current_app.db_client = FirestoreDatabase()

    @app.app.before_request
    def before_request_func():
        try:
            g.db_table_name, g.db_table_id, g.db_keys, g.response_keys, \
                g.request_id, g.request_queries, g.forced_filters = openapi_spec.get_database_info(request)
        except ValueError as e:
            g.ip = request.remote_addr
            g.user = ''

            return str(e), 400

    @app.app.after_request
    def add_header(response):
        response.headers['Content-Security-Policy'] = "default-src 'none'; script-src 'self' 'unsafe-inline'; " \
                                                      "img-src 'self' data:; font-src 'self' fonts.gstatic.com data:; " \
                                                      "style-src 'self' fonts.googleapis.com 'unsafe-inline'; " \
                                                      "style-src-elem 'self' fonts.googleapis.com 'unsafe-inline'; " \
                                                      "connect-src 'self' opensource.zalando.com; form-action 'none'; frame-src data:; " \
                                                      "frame-ancestors 'none'"
        response.headers['X-Frame-Options'] = "SAMEORIGIN"
        response.headers['X-Content-Type-Options'] = "nosniff"
        response.headers['Referrer-Policy'] = "no-referrer-when-downgrade"
        response.headers['Feature-Policy'] = "geolocation 'none'; midi 'none'; notifications 'none'; push 'none'; " \
                                             "sync-xhr 'none'; microphone 'none'; camera 'none'; " \
                                             "magnetometer 'none'; gyroscope 'none'; speaker 'none'; vibrate 'none'; " \
                                             "fullscreen 'none'; payment 'none';"
        return response

    return app
