from pyramid.response import Response
from pyramid.renderers import render

class Resource(object):
    def __init__(self, request):
        self.request = request

class Root(Resource):
    def __init__(self, request):
        self.request = request
        print request

    def __call__(self):
        kwargs = {}
        return Response(render('index.mako', kwargs, self.request))
