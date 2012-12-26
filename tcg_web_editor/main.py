from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.response import Response

from pokedex.db import connect

from tcg_web_editor.resource import Resource, Root

def view(context, request):
    return context()

def make_app(global_config, **settings):

    class SQLARequest(Request):
        db = connect()

    settings.setdefault('mako.directories', 'tcg_web_editor:templates/')
    config = Configurator(
        root_factory=Root,
        request_factory=SQLARequest,
        settings=settings,
    )
    config.add_static_view('assets', 'tcg_web_editor:assets')

    config.add_view(view, context=Resource)
    return config.make_wsgi_app()

def serve():
    app = make_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
