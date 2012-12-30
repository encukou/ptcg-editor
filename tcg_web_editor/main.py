from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.httpexceptions import HTTPMovedPermanently

from pokedex.db import connect

from tcg_web_editor.resource import Resource
from tcg_web_editor.resource.tcgdex import Root

def view(context, request):
    want = context.url
    if request.path == '/':
        want += '/'
    if request.path_url != want:
        new_url = context.url
        if request.query_string:
            new_url += '?' + request.query_string
        print request.path_url, '->', new_url
        raise HTTPMovedPermanently(new_url)
    return context()

def make_app(global_config, **settings):
    settings.setdefault('mako.directories', 'tcg_web_editor:templates/')
    settings.setdefault('mako.input_encoding', 'utf-8')

    class SQLARequest(Request):
        db = connect()

    config = Configurator(
        root_factory=Root.root_factory,
        request_factory=SQLARequest,
        settings=settings,
    )
    config.add_static_view('assets', 'tcg_web_editor:assets')
    config.add_static_view('scans', 'tcg_web_editor:scans')

    config.add_view(view, context=Resource)
    return config.make_wsgi_app()

def serve():
    app = make_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
