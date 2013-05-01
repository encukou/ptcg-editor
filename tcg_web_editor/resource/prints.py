# Encoding: UTF-8

from __future__ import unicode_literals

import string
import json
import difflib
import itertools
import re

from pyramid.response import Response
from pyramid.decorator import reify
from pyramid.httpexceptions import (HTTPMovedPermanently, HTTPNotFound,
                                    HTTPForbidden)
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from markupsafe import Markup
from sqlalchemy.orm import (
    joinedload, joinedload_all, subqueryload, subqueryload_all, lazyload)

from pokedex.db import util as dbutil
from ptcgdex import tcg_tables, load

from tcg_web_editor.resource import TemplateResource, Resource, exporting

@exporting
class Print(TemplateResource):
    template_name = 'print.mako'

    def __init__(self, parent, print_):
        self.print_ = print_
        super(Print, self).__init__(parent)

    @reify
    def name(self):
        return str(self.print_.id)

    @reify
    def friendly_name(self):
        return self.print_.card.name

    @reify
    def short_name(self):
        return self.print_.card.name

    def __json__(self):
        return load.export_print(self.print_)


@exporting
class SetPrint(Print):
    def __init__(self, parent, set_print):
        self.set_print = set_print
        super(SetPrint, self).__init__(parent, set_print.print_)

    @reify
    def friendly_name(self):
        return '{} ({})'.format(self.print_.card.name, self.short_name)

    @reify
    def short_name(self):
        if self.set_print.number is None:
            return self.set_print.set.name
        else:
            return '{} #{}'.format(self.set_print.set.name, self.set_print.number)

    @reify
    def name(self):
        if self.set_print.number:
            return '{}~{}'.format(
                self.set_print.set.identifier,
                self.set_print.number.lower(),
            )
        else:
            return '{}~'.format(self.set_print.set.identifier)

    def __call__(self):
        query = self.request.db.query(tcg_tables.SetPrint)
        query = query.filter(tcg_tables.SetPrint.set == self.set_print.set)
        query = query.options(joinedload_all('print_.card.family.names_local'))

        num = self.set_print.order
        query = query.filter(tcg_tables.SetPrint.order.in_([num + 1, num - 1]))
        prev_set_print = next_set_print = None
        for sp in query:
            if sp.order == num - 1:
                prev_set_print = sp
            elif sp.order == num + 1:
                next_set_print = sp

        return self.render_response(
            prev_set_print=prev_set_print,
            next_set_print=next_set_print,
        )


class FamilyNamesJson(Resource):
    template_name = 'family.mako'

    def __call__(self):
        substr = self.request.GET.get('query', '')
        if len(substr) > 1 and '?' not in substr and '%' not in substr:
            query = self.request.db.query(tcg_tables.CardFamily)
            query = query.outerjoin(tcg_tables.CardFamily.names_local)
            print tcg_tables.CardFamily.names_table.name, type(tcg_tables.CardFamily.names_table.name)
            query = query.filter(tcg_tables.CardFamily.names_table.name.like(
                '%{}%'.format(substr)))
            text = json.dumps(sorted([f.name for f in query]))
            return Response(text)
        else:
            raise HTTPForbidden()


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

    @reify
    def family_query(self):
        query = self.request.db.query(tcg_tables.CardFamily)
        query = dbutil.order_by_name(query, tcg_tables.CardFamily)
        query = query.options(joinedload('names_local'))
        query = query.options(subqueryload('cards.prints'))
        query = query.options(subqueryload('cards'))
        return query

    @reify
    def filtered_query(self):
        if self.first_letter:
            return self.family_query.filter(
                func.lower(tcg_tables.CardFamily.names_table.name).like(
                    '{}%'.format(self.first_letter)))
        else:
            return self.family_query.filter(
                ~func.lower(func.substr(
                        tcg_tables.CardFamily.names_table.name, 1, 1)).in_(
                    string.ascii_lowercase))

    def get(self, family_identifier):
        if self is not self.base_families:
            return self.base_families[family_identifier]
        if len(family_identifier) == 1:
            if family_identifier not in string.ascii_lowercase:
                raise KeyError(family_identifier)
            return Families(
                self.base_families, family_identifier, family_identifier)
        query = self.family_query.filter(
            tcg_tables.CardFamily.identifier == family_identifier)
        query = query.options(joinedload_all('cards.class_.names_local'))
        query = query.options(joinedload_all('cards.prints.set_prints.set.names_local'))
        query = query.options(joinedload_all('cards.card_mechanics.mechanic.names_local'))
        query = query.options(joinedload_all('cards.card_types.type.names_local'))
        query = query.options(subqueryload('cards.prints.set_prints'))
        query = query.options(subqueryload('cards.card_mechanics'))
        query = query.options(subqueryload('cards.card_types'))
        try:
            family = query.one()
        except NoResultFound:
            raise LookupError('No such print')
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
            return self.first_letter.upper() + "⁓"
        else:
            return 'Cards'

    def iter_dynamic(self):
        for entity in self.filtered_query:
            yield self.wrap(entity)
        if not self.first_letter:
            for letter in string.ascii_lowercase:
                yield self[letter]

    child_namelist = FamilyNamesJson


class BadInput(ValueError):
    pass


class Diff(TemplateResource):
    friendly_name = 'Card Diff'
    template_name = 'diff.mako'

    def get_resources(self, card_urls):
        if not all(card_urls):
            raise BadInput(Markup("""
                You need to select <em>two</em> cards in order to diff them.
                """))
        try:
            # TODO: This depends too much on URL structure?
            resources = [self.root['cards'].traverse(c) for c in card_urls]
        except LookupError:
            raise BadInput(Markup("You've selected invalid cards."))
            return supercall()
        if any(r == resources[0] for r in resources[1:]):
            raise BadInput(Markup("""
                You need to select two <em>different</em> cards in order to
                diff them."""))
        return resources

    def __call__(self):
        self.request.GET.setdefault('fmt', 'json')
        self.data_format = self.request.GET['fmt']
        self.request.GET.setdefault('diff', 'sbs')
        self.diff_style = self.request.GET['diff']
        card_urls = [self.request.GET.get(p) for p in ('card-a', 'card-b')]
        try:
            resources = self.get_resources(card_urls)
        except BadInput, e:
            self.error_message = e.args[0]
            return self.render_response('diff_bad.mako')

        if self.data_format == 'yaml':
            texts = [load.yaml_dump(p.__json__()).decode('utf-8') for p in resources]
        else:
            texts = [json.dumps(p.__json__(), indent=4) for p in resources]

        self.print_resources = resources
        self.texts = texts

        lines = [t.splitlines() for t in texts]

        if self.diff_style == 'raw':
            patch_generator = difflib.unified_diff(
                *lines,
                fromfile=card_urls[0],
                tofile=card_urls[1],
                lineterm='')
            return Response(b'\n'.join(patch_generator),
                content_type=b'text/plain')
        elif self.diff_style == 'uni':
            differ = difflib.SequenceMatcher(a=lines[0], b=lines[1])
            rows = []
            nonword_re = re.compile(r'(\s+|[^\s\w])')
            for tag, i1, i2, j1, j2 in differ.get_opcodes():
                if tag == 'equal':
                    assert lines[0][i1:i2] == lines[1][j1:j2]
                    for i, j in zip(range(i1, i2), range(j1, j2)):
                        rows.append([
                            {'num': i, 'text': lines[0][i], 'cls': 'same'},
                            {'num': j, 'text': None, 'cls': ''},
                        ])
                elif tag == 'replace':
                    l1 = nonword_re.split('\n'.join(lines[0][i1:i2]))
                    l2 = nonword_re.split('\n'.join(lines[1][j1:j2]))
                    linematcher = difflib.SequenceMatcher(a=l1, b=l2)
                    lineparts = [[], []]
                    for tag, ii1, ii2, jj1, jj2 in linematcher.get_opcodes():
                        a = ''.join(l1[ii1:ii2])
                        b = ''.join(l2[jj1:jj2])
                        if a == b:
                            lineparts[0].append(a)
                            lineparts[1].append(b)
                        else:
                            if a:
                                lineparts[0].append(Markup(
                                    '<span class="d">{}</span>').format(a).
                                    replace('\n', Markup('</span>\n<span class="d">')))
                            if b:
                                lineparts[1].append(Markup(
                                    '<span class="d">{}</span>').format(b).
                                    replace('\n', Markup('</span>\n<span class="d">')))
                    for n, line in enumerate(Markup().join(lineparts[0]).splitlines()):
                        rows.append([
                            {'num': i + n + 1, 'text': line, 'cls': 'a different'},
                            {'num': None, 'text': None, 'cls': ''},
                        ])
                    for n, line in enumerate(Markup().join(lineparts[1]).splitlines()):
                        rows.append([
                            {'num': None, 'text': line, 'cls': 'b different'},
                            {'num': j + n + 1, 'text': None, 'cls': ''},
                        ])
                else:
                    for i in range(i1, i2):
                        rows.append([
                            {'num': i, 'text': lines[0][i], 'cls': 'a d different'},
                            {'num': None, 'text': None, 'cls': ''},
                        ])
                    for j in range(j1, j2):
                        rows.append([
                            {'num': None, 'text': lines[0][j], 'cls': 'b d different'},
                            {'num': j, 'text': None, 'cls': ''},
                        ])
        else:
            differ = difflib.SequenceMatcher(a=lines[0], b=lines[1])
            rows = []
            for tag, i1, i2, j1, j2 in differ.get_opcodes():
                for i, j in itertools.izip_longest(range(i1, i2), range(j1, j2)):
                    row = [{}, {}]
                    for i, (line, n) in enumerate(zip(lines, (i, j))):
                        if n is None:
                            row[i]['num'] = None
                            row[i]['text'] = None
                            row[i]['cls'] = 'empty'
                        else:
                            row[i]['num'] = n
                            row[i]['text'] = line[n]
                            row[i]['cls'] = ' '.join([
                                'ab'[i],
                                'same' if tag == 'equal' else 'different',
                            ])
                    rows.append(row)
        self.rows = rows
        return self.render_response()


class Family(TemplateResource):
    template_name = 'family.mako'

    child_diff = Diff

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

    @reify
    def query(self):
        query = self.request.db.query(tcg_tables.Print)
        query = query.join(tcg_tables.Print.card)
        query = query.filter(tcg_tables.Card.family == self.family)
        return query

    def get(self, set_and_number):
        try:
            print_id = int(set_and_number)
        except ValueError:
            try:
                set_identifier, number = set_and_number.split('~')
                if not number:
                    number = None
            except ValueError:
                raise LookupError('Must be numeric, or include a ~ character')
        else:
            set_identifier = number = None
        query = self.query
        if set_identifier:
            query = self.request.db.query(tcg_tables.SetPrint)
            query = query.join(tcg_tables.SetPrint.set)
            query = query.join(tcg_tables.SetPrint.print_)
            query = query.join(tcg_tables.Print.card)
            query = query.filter(tcg_tables.Card.family == self.family)
            query = query.filter(tcg_tables.Set.identifier == set_identifier)
            query = query.filter(func.lower(tcg_tables.SetPrint.number) == number)
            query = query.options(lazyload('print_'))
        else:
            query = query.filter(tcg_tables.Print.id == print_id)
        for prop in (
                'card.card_subclasses.subclass.names_local',
                'rarity.names_local',
                'pokemon_flavor.flavor_local',
                'pokemon_flavor.species.names_local',
                'card.card_mechanics.mechanic.effects_local',
                'card.card_mechanics.mechanic.class_.names_local',
                'card.card_types.type.names_local',
                'card.stage.names_local',
                'print_illustrators.illustrator',
                'card.evolutions.family.names_local',
                'card.family.evolutions.card.family.names_local',
                'card.family.evolutions.card.prints.set_prints.set.names_local',
                'card.family.evolutions.card.card_mechanics.mechanic.names_local',
                'card.card_mechanics.mechanic.costs.type.names_local',
                'card.damage_modifiers.type.names_local'):
            if set_identifier:
                prop = 'print_.' + prop
            query = query.options(joinedload_all(prop))
        for prop in (
                'card.card_mechanics',
                'card.card_mechanics.mechanic.costs',
                'card.card_subclasses',
                'card.prints',
                'card.damage_modifiers',
                'card.family.evolutions',
                'card.family.evolutions.card.prints',
                'card.family.evolutions.card.card_mechanics',
                'card.family.cards.prints',
                'scans'):
            if set_identifier:
                prop = 'print_.' + prop
            query = query.options(subqueryload(prop))
        for prop in (
                'pokemon_flavor.species.default_pokemon',
                'pokemon_flavor.species.evolutions'):
            if set_identifier:
                prop = 'print_.' + prop
            query = query.options(lazyload(prop))
        try:
            print_or_set_print = query[0]
        except NoResultFound:
            raise LookupError('No such print')
        return self.wrap(print_or_set_print)

    def wrap(self, print_or_set_print):
        if isinstance(print_or_set_print, tcg_tables.SetPrint):
            print_ = print_or_set_print.print_
        else:
            print_ = print_or_set_print
        if print_.card.family is not self.family:
            return self.root.wrap(print_.card.family).wrap(print_or_set_print)
        if print_ is print_or_set_print:
            return Print(self, print_or_set_print)
        else:
            return SetPrint(self, print_or_set_print)

    def iter_dynamic(self):
        for print_ in self.query:
            yield self.wrap(print_)
            for set_print in print_.set_prints:
                yield self.wrap(set_print)
