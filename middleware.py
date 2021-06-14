from werkzeug.wrappers import Response

from pydantic import ValidationError


class ApiErrorResponseMiddleware:
    """
    Converts Pydantic ValidationError
    to a JSON error response.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except ValidationError as ve:
            resp = Response(ve.json(), 400, mimetype="application/json")
            return resp(environ, start_response)
