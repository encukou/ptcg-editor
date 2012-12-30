# Encoding: UTF-8

from __future__ import unicode_literals

import json

from pyramid.response import Response
from pyramid.renderers import render
from pyramid.traversal import traverse
from pyramid.decorator import reify
from pyramid.location import lineage
from markupsafe import Markup

from ptcgdex import load

from tcg_web_editor import template_helpers as helpers

class Resource(object):
    def __init__(self, parent, name=None, request=None):
        self.__parent__ = self.parent = parent
        if parent:
            self.root = parent.root
        else:
            self.root = self
        if self.name is None:
            self.name = name
        if request is None:
            self.request = parent.request
        else:
            self.request = request
        self._child_objects = {}
        self.init()

    def init(self):
        pass

    @classmethod
    def root_factory(cls, request):
        root = cls(parent=None, name=None, request=request)
        root.root = root
        return root

    name = None

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
        return Markup(self.request.resource_url(self))

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

    def iter_children(self):
        for attr_name in dir(self):
            if attr_name.startswith('child_'):
                yield self[attr_name[6:]]

    def iter_dynamic(self):
        return ()


class TemplateResource(Resource):
    def render_response(self, template_name=None, **kwargs):
        kwargs.setdefault('this', self)
        kwargs.setdefault('h', helpers)
        kwargs.setdefault('wrap', self.root.wrap)
        kwargs.setdefault('link', helpers.link(self))
        kwargs.setdefault('request', self.request)
        kwargs.setdefault('asset_url', helpers.asset_url_factory(self.request))
        if template_name is None:
            template_name = self.template_name
        return Response(render(template_name, kwargs, self.request))

    def __call__(self):
        return self.render_response()


class JSONExport(Resource):
    """JSON export resource

    Implement __json__() in a Resource and put this class in its child_json
    attribute, that's all there is to it!
    """
    def __call__(self):
        return Response(
            json.dumps(self.parent.__json__(), separators=(',', ':')),
            content_type=b'application/json')


class YAMLExport(Resource):
    def __call__(self):
        return Response(
            load.yaml_dump(self.parent.__json__()),
            content_type=b'application/x-yaml')

def exporting(cls):
    """Decorator for resources that export to JSON & YAML"""
    cls.child_json = JSONExport
    cls.child_yaml = YAMLExport
    return cls
