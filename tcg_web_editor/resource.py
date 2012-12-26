from pyramid.response import Response
from pyramid.renderers import render

from ptcgdex import tcg_tables

from tcg_web_editor import template_helpers

class Resource(object):
    def __init__(self, request):
        self.request = request

class TemplateResource(Resource):
    def render_response(self, template_name=None, **kwargs):
        kwargs.setdefault('this', self)
        kwargs.setdefault('h', template_helpers)
        kwargs.setdefault('request', self.request)
        if template_name is None:
            template_name = self.template_name
        return Response(render(template_name, kwargs, self.request))

    def __call__(self):
        return self.render_response()

class Root(TemplateResource):
    template_name = 'index.mako'

    def __init__(self, request):
        self.request = request

    def __call__(self):
        return self.render_response(
            sets=self.request.db.query(tcg_tables.Set).all(),
        )
