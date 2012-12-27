from pyramid.response import Response
from pyramid.renderers import render
from pyramid.traversal import find_interface, resource_path, traverse
from pyramid.decorator import reify
from pyramid.location import lineage

from ptcgdex import tcg_tables

from tcg_web_editor import template_helpers as helpers

_UNDEFINED = object()

class Resource(object):
    def __init__(self, parent, name=_UNDEFINED, request=None):
        self.__parent__ = self.parent = parent
        if name is not _UNDEFINED:
            self.name = name
        if request is None:
            self.request = parent.request
        else:
            self.request = request
        self._child_objects = {}
        self.init()

    def init(self):
        pass

    @reify
    def __name__(self):
        return self.name

    @reify
    def friendly_name(self):
        return self.name

    @reify
    def short_name(self):
        return self.friendly_name

    @reify
    def url(self):
        return self.request.resource_url(self)

    def traverse(self, path):
        if path.startswith('/'):
            context = self.root
            path = path[1:]
        else:
            context = self
        result = traverse(context, path)
        if result['view_name']:
            raise KeyError(result['view_name'])
        return result['context']

    @reify
    def lineage(self):
        return list(lineage(self))

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
        kwargs.setdefault('h', helpers)
        kwargs.setdefault('request', self.request)
        if template_name is None:
            template_name = self.template_name
        return Response(render(template_name, kwargs, self.request))

    def __call__(self):
        return self.render_response()


class Sets(TemplateResource):
    template_name = 'sets.mako'
    friendly_name = 'Sets'

    def init(self):
        self.sets = self.request.db.query(tcg_tables.Set).all()
        self.sets_by_identifier = {s.identifier: s for s in self.sets}

    def get(self, set_ident):
        return self.wrap(self.sets_by_identifier[set_ident])

    def wrap(self, tcg_set):
        return Set(self, tcg_set)


class Set(TemplateResource):
    template_name = 'set.mako'

    def __init__(self, parent, tcg_set):
        self.set = tcg_set
        super(Set, self).__init__(parent)

    @reify
    def name(self):
        return self.set.identifier

    @reify
    def friendly_name(self):
        return self.set.name


class Root(TemplateResource):
    template_name = 'index.mako'
    friendly_name = u'Pok\xe9beach Card Database Editor'
    short_name = 'Home'

    @classmethod
    def factory(cls, request):
        return cls(parent=None, name=None, request=request)

    def __call__(self):
        return self.render_response(
            sets=self.request.db.query(tcg_tables.Set).all(),
        )

    child_sets = Sets
