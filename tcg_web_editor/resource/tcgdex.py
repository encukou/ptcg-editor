# Encoding: UTF-8

from __future__ import unicode_literals

from pyramid.decorator import reify
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import (
    joinedload, joinedload_all, subqueryload, subqueryload_all, lazyload)

from pokedex.db import util as dbutil
from ptcgdex import tcg_tables

from tcg_web_editor.resource import TemplateResource
from tcg_web_editor.resource import prints as res_prints

class Sets(TemplateResource):
    template_name = 'sets.mako'
    friendly_name = 'Sets'

    @reify
    def query(self):
        query = self.request.db.query(tcg_tables.Set)
        query = query.options(joinedload('names_local'))
        return query

    @reify
    def sets(self):
        return self.query.all()

    def get(self, set_ident):
        query = self.query
        query = query.filter_by(identifier=set_ident)
        query = query.options(joinedload('names_local'))
        query = query.options(joinedload_all('set_prints.print_.card.family.names_local'))
        query = query.options(joinedload_all('set_prints.print_.card.class_.names_local'))
        query = query.options(joinedload_all('set_prints.print_.card.card_types.type.names_local'))
        query = query.options(joinedload_all('set_prints.print_.card.card_mechanics.mechanic.names_local'))
        query = query.options(subqueryload('set_prints.print_'))
        query = query.options(subqueryload('set_prints.print_.card.card_mechanics'))
        try:
            tcg_set = query.one()
        except NoResultFound:
            raise LookupError(set_ident)
        return self.wrap(tcg_set)

    def wrap(self, tcg_set):
        return Set(self, tcg_set)

    def iter_dynamic(self):
        for entity in self.query.all():
            yield self.wrap(entity)


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


class Illustrators(TemplateResource):
    template_name = 'illustrators.mako'
    friendly_name = 'Illustrators'

    def init(self):
        query = self.request.db.query(tcg_tables.Illustrator)
        query = query.order_by(tcg_tables.Illustrator.name)
        for key in (
                'print_illustrators.print_.set_prints.set.names_local',
                'print_illustrators.print_.card.family.names_local',
                'print_illustrators.print_.card.class_',
                'print_illustrators.print_.card.card_types.type.names_local',
                'print_illustrators.print_.card.card_mechanics.mechanic.names_local',
            ):
            query = query.options(joinedload_all(key))
        query = query.options(lazyload('print_illustrators'))
        query = query.options(subqueryload('print_illustrators.print_.set_prints'))
        query = query.options(subqueryload('print_illustrators.print_.card.card_types'))
        query = query.options(subqueryload('print_illustrators.print_.card.card_mechanics'))
        self.illustrator_query = query

    def get(self, ident):
        query = self.illustrator_query.filter_by(identifier=ident)
        query = query.options(joinedload_all('print_illustrators.print_'))
        query = query.options(subqueryload('print_illustrators'))
        return self.wrap(query.one())

    def wrap(self, entity):
        return Illustrator(self, entity)

    def iter_dynamic(self):
        for entity in self.illustrator_query:
            yield self.wrap(entity)


class Illustrator(TemplateResource):
    template_name = 'illustrator.mako'

    def __init__(self, parent, ilustrator):
        self.illustrator = ilustrator
        super(Illustrator, self).__init__(parent)

    @reify
    def name(self):
        return self.illustrator.identifier

    @reify
    def friendly_name(self):
        return self.illustrator.name


class Root(TemplateResource):
    template_name = 'index.mako'
    friendly_name = u'PokéBeach Card Database Editor'
    short_name = 'Home'

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
        elif isinstance(obj, tcg_tables.SetPrint):
            return self.wrap(obj.print_.card.family).wrap(obj)
        elif isinstance(obj, tcg_tables.CardFamily):
            return self['cards'].wrap(obj)
        elif isinstance(obj, tcg_tables.Illustrator):
            return self['illustrators'].wrap(obj)
        else:
            raise TypeError("Don't know how to wrap a {}".format(
                type(obj).__name__))

    child_sets = Sets
    child_cards = res_prints.Families
    child_illustrators = Illustrators
