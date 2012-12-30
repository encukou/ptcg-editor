# Encoding: UTF-8

from __future__ import unicode_literals

from pyramid.decorator import reify

from pokedex.db import util as dbutil
from ptcgdex import tcg_tables

from tcg_web_editor.resource import TemplateResource
from tcg_web_editor.resource import prints as res_prints

class Sets(TemplateResource):
    template_name = 'sets.mako'
    friendly_name = 'Sets'

    @reify
    def sets(self):
        return self.request.db.query(tcg_tables.Set).all()

    @reify
    def sets_by_identifier(self):
        return {s.identifier: s for s in self.sets}

    def get(self, set_ident):
        return self.wrap(self.sets_by_identifier[set_ident])

    def wrap(self, tcg_set):
        return Set(self, tcg_set)

    def iter_dynamic(self):
        for entity in self.sets:
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
        self.illustrator_query = query

    def get(self, ident):
        return self.wrap(dbutil.get(
            self.request.db, tcg_tables.Illustrator, ident))

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
