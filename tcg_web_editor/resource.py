from pyramid.response import Response
from pyramid.renderers import render
from pyramid.traversal import find_interface, resource_path
from pyramid.decorator import reify

from ptcgdex import tcg_tables

from tcg_web_editor.template_helpers import Helpers


class Resource(object):
    def __init__(self, parent, name, request=None):
        self.__parent__ = self.parent = parent
        try:
            self.__name__ = self.name = name
        except AttributeError:
            pass
        if request is None:
            self.request = parent.request
        else:
            self.request = request
        self._child_objects = {}

    @reify
    def url(self):
        return self.request.resource_url(self)

    def __resource_url__(self, request, info):
        return request.application_url + info['virtual_path'].rstrip('/')

    @property
    def root(self):
        return find_interface(self, Root)

    def __getitem__(self, item):
        try:
            return self._child_objects[item]
        except KeyError:
            child = self._child_objects[item] = self._getitem(item)
            return child

    def _getitem(self, item):
        try:
            child = getattr(self, 'child_' + item)
        except AttributeError:
            try:
                return self.get(item)
            except LookupError:
                raise KeyError(item)
        else:
            return child(self, item)

    def get(self, item):
        raise KeyError(item)


class TemplateResource(Resource):
    def render_response(self, template_name=None, **kwargs):
        kwargs.setdefault('this', self)
        kwargs.setdefault('h', Helpers(self))
        kwargs.setdefault('request', self.request)
        if template_name is None:
            template_name = self.template_name
        return Response(render(template_name, kwargs, self.request))

    def __call__(self):
        return self.render_response()


class Sets(TemplateResource):
    template_name = 'sets.mako'

    def __call__(self):
        return self.render_response(
            sets=self.request.db.query(tcg_tables.Set).all(),
        )


class Root(TemplateResource):
    template_name = 'index.mako'
    __name__ = __parent__ = None

    @classmethod
    def factory(cls, request):
        return cls(parent=None, name=None, request=request)

    def __call__(self):
        return self.render_response(
            sets=self.request.db.query(tcg_tables.Set).all(),
        )

    child_sets = Sets
