# Encoding: UTF-8

from __future__ import unicode_literals

import string
import json
import difflib
import itertools

from pyramid.response import Response
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPMovedPermanently, HTTPNotFound
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from markupsafe import Markup

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

    def __json__(self):
        return load.export_print(self.print_)


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
            if family_identifier not in string.ascii_lowercase:
                raise KeyError(family_identifier)
            return Families(
                self.base_families, family_identifier, family_identifier)
        query = self.family_query.filter(
            tcg_tables.CardFamily.identifier == family_identifier)
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
            for tag, i1, i2, j1, j2 in differ.get_opcodes():
                if tag == 'equal':
                    assert lines[0][i1:i2] == lines[1][j1:j2]
                    for i, j in zip(range(i1, i2), range(j1, j2)):
                        rows.append([
                            {'num': i, 'text': lines[0][i]},
                            {'num': j, 'text': None},
                        ])
                else:
                    for i in range(i1, i2):
                        rows.append([
                            {'num': i, 'text': lines[0][i]},
                            {'num': None, 'text': None},
                        ])
                    for j in range(j1, j2):
                        rows.append([
                            {'num': None, 'text': lines[1][j]},
                            {'num': j, 'text': None},
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
                        else:
                            row[i]['num'] = n
                            row[i]['text'] = line[n]
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
        query = query.join(tcg_tables.Print.set)
        query = query.join(tcg_tables.Print.card)
        query = query.filter(tcg_tables.Card.family == self.family)
        return query

    def get(self, set_and_number):
        try:
            set_identifier, number = set_and_number.split('~')
        except ValueError:
            raise LookupError('Must include a ~ character')
        query = self.query
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

    def iter_dynamic(self):
        for entity in self.query:
            yield self.wrap(entity)
