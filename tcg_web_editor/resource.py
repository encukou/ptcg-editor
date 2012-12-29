# Encoding: UTF-8

from __future__ import unicode_literals

import string

from pyramid.response import Response
from pyramid.renderers import render
from pyramid.traversal import find_interface, resource_path, traverse
from pyramid.decorator import reify
from pyramid.location import lineage
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from pokedex.db import util as dbutil
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
        kwargs.setdefault('wrap', self.root.wrap)
        kwargs.setdefault('request', self.request)
        kwargs.setdefault('asset_url', helpers.asset_url_factory(self.request))
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


class Print(TemplateResource):
    template_name = 'print.mako'

    def __init__(self, parent, print_):
        self.print_ = print_
        super(Print, self).__init__(parent)

    @reify
    def name(self):
        return '{}~{}'.format(
            self.print_.set.identifier,
            self.print_.set_number.lower(),
        )

    @reify
    def friendly_name(self):
        return '{} ({})'.format(self.print_.card.name, self.short_name)

    @reify
    def short_name(self):
        return '{} #{}'.format(self.print_.set.name, self.print_.set_number)

    def __call__(self):
        query = self.request.db.query(tcg_tables.Print)
        query = query.filter(tcg_tables.Print.set == self.print_.set)

        def prev_next(offset):
            num = self.print_.order + offset
            q = query.filter(tcg_tables.Print.order == num)
            try:
                return q.one()
            except NoResultFound:
                return None

        return self.render_response(
            prev_print=prev_next(-1),
            next_print=prev_next(+1),
        )


class Families(TemplateResource):
    template_name = 'families.mako'

    def __init__(self, parent, name, first_letter=None):
        if first_letter and first_letter.islower():
            self.first_letter = first_letter
            self.base_families = parent
        else:
            self.first_letter = None
            self.base_families = self
        super(Families, self).__init__(parent, name)

    def init(self):
        query = self.request.db.query(tcg_tables.CardFamily)
        query = dbutil.order_by_name(query, tcg_tables.CardFamily)
        self.family_query = query
        if self.first_letter:
            self.filtered_query = query.filter(
                func.lower(tcg_tables.CardFamily.names_table.name).like(
                    '{}%'.format(self.first_letter)))
        else:
            self.filtered_query = query.filter(
                ~func.lower(func.substr(
                        tcg_tables.CardFamily.names_table.name, 1, 1)).in_(
                    string.ascii_lowercase))

    def get(self, family_identifier):
        if self is not self.base_families:
            return self.base_families[family_identifier]
        if len(family_identifier) == 1:
            return Families(
                self.base_families, family_identifier, family_identifier)
        print family_identifier, self.family_query
        family = self.family_query.filter(
            tcg_tables.CardFamily.identifier == family_identifier).one()
        return self.wrap(family)

    def wrap(self, family):
        if self is not self.base_families:
            return self.base_families.wrap(family)
        return Family(self, family)

    @reify
    def friendly_name(self):
        if self.first_letter:
            return 'Card list ({})'.format(self.first_letter.upper())
        else:
            return 'Card list'

    @reify
    def short_name(self):
        if self.first_letter:
            return self.first_letter.upper()
        else:
            return 'Cards'


class Family(TemplateResource):
    template_name = 'family.mako'

    def __init__(self, parent, family):
        self.family = family
        super(Family, self).__init__(parent)

    @reify
    def name(self):
        return self.family.identifier

    @reify
    def friendly_name(self):
        return 'Cards named "{}"'.format(self.family.name)

    @reify
    def short_name(self):
        return self.family.name

    def get(self, set_and_number):
        try:
            set_identifier, number = set_and_number.split('~')
        except ValueError:
            raise LookupError('Must include a ~ character')
        query = self.request.db.query(tcg_tables.Print)
        query = query.join(tcg_tables.Print.set)
        query = query.join(tcg_tables.Print.card)
        query = query.filter(tcg_tables.Card.family == self.family)
        query = query.filter(tcg_tables.Set.identifier == set_identifier)
        query = query.filter(func.lower(tcg_tables.Print.set_number) == number)
        try:
            print_ = query[0]
        except NoResultFound:
            raise LookupError('No such print')
        return self.wrap(print_)

    def wrap(self, print_):
        if print_.card.family is not self.family:
            return self.root.wrap(print_.card.family).wrap(print_)
        return Print(self, print_)


class Root(TemplateResource):
    template_name = 'index.mako'
    friendly_name = u'PokéBeach Card Database Editor'
    short_name = 'Home'

    @classmethod
    def factory(cls, request):
        return cls(parent=None, name=None, request=request)

    def __call__(self):
        return self.render_response(
            set_query=self.request.db.query(tcg_tables.Set),
            card_query=self.request.db.query(tcg_tables.Card),
        )

    def wrap(self, obj):
        if isinstance(obj, tcg_tables.Set):
            return self['sets'].wrap(obj)
        elif isinstance(obj, tcg_tables.Print):
            return self.wrap(obj.card.family).wrap(obj)
        elif isinstance(obj, tcg_tables.CardFamily):
            return self['cards'].wrap(obj)
        else:
            raise TypeError("Don't know how to wrap a {}".format(
                type(obj).__name__))

    child_sets = Sets
    child_cards = Families
