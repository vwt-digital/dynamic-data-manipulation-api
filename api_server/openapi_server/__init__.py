import logging
import os
from typing import AnyStr, Union

import config

import connexion
from connexion import problem
from connexion.decorators.validation import RequestBodyValidator
from connexion.lifecycle import ConnexionResponse
from connexion.utils import is_null
from flask_cors import CORS
from jsonschema import ValidationError
from flask import request, g

from openapi_server import encoder, openapi_spec


def validate_schema(self, data, url):
    # type: (dict, AnyStr) -> Union[ConnexionResponse, None]
    """
    @Override default RequestBodyValidator validate_schema. Only used to edit return String.
    @param self:
    @param data:
    @param url:
    @return:
    """
    if self.is_null_value_valid and is_null(data):
        return None

    try:
        self.validator.validate(data)
    except ValidationError as exception:
        logging.error("{url} validation error: {error}".format(url=url,
                                                               error=exception.message),
                      extra={'validator': 'body'})
        return problem(400, 'Bad Request', 'Some data is missing or incorrect',
                       type='Validation')

    return None


RequestBodyValidator.validate_schema = validate_schema

app = connexion.App(__name__, specification_dir='./openapi/')
app.app.json_encoder = encoder.JSONEncoder
app.add_api('openapi.yaml',
            arguments={'title': 'Dynamic Data Manipulator API'},
            strict_validation=True)
if 'GAE_INSTANCE' in os.environ:
    CORS(app.app, origins=config.ORIGINS)
else:
    CORS(app.app)


@app.app.before_request
def before_request_func():
    g.db_type, g.db_name = openapi_spec.get_database_info(request)


@app.app.after_request
def add_header(response):
    response.headers['Content-Security-Policy'] = "default-src 'none'; script-src 'self' 'unsafe-inline'; " \
                                                  "img-src 'self' data:; font-src 'self' fonts.gstatic.com data:; " \
                                                  "style-src 'self' fonts.googleapis.com 'unsafe-inline'; " \
                                                  "style-src-elem 'self' fonts.googleapis.com 'unsafe-inline'; " \
                                                  "connect-src 'self'; form-action 'none'; frame-src data:; " \
                                                  "frame-ancestors 'none'"
    response.headers['X-Frame-Options'] = "SAMEORIGIN"
    response.headers['X-Content-Type-Options'] = "nosniff"
    response.headers['Referrer-Policy'] = "no-referrer-when-downgrade"
    response.headers['Feature-Policy'] = "geolocation 'none'; midi 'none'; notifications 'none'; push 'none'; " \
                                         "sync-xhr 'none'; microphone 'none'; camera 'none'; " \
                                         "magnetometer 'none'; gyroscope 'none'; speaker 'none'; vibrate 'none'; " \
                                         "fullscreen 'none'; payment 'none';"
    return response
