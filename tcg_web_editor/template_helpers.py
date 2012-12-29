# Encoding: UTF-8

from __future__ import unicode_literals

from markupsafe import Markup
import functools

def _best_parent(this, objs):
    best = None
    longest_len = 0
    for obj in objs:
        if obj in this.lineage and (
                best is None or len(obj.lineage) > longest_len):
            longest_len = len(obj.lineage)
            best = obj
    return best

def nav_tabs(this, paths):
    objs = [this.root.traverse(p) for p in paths]
    best = _best_parent(this, objs)
    result = []
    for obj in objs:
        result.append(Markup('<li{active}><a href="{url}">{text}</a></li>').format(
            active=Markup(' class="active"') if obj is best else '',
            url=obj.url,
            text=obj.short_name,
        ))
    return Markup().join(result)


def card_named_mechanic_note(card):
    named_mechanics = [m.name for m in card.mechanics if m.name]
    if named_mechanics:
        return '({})'.format(', '.join(named_mechanics))
    else:
        return ''

def type_icon(type):
    return Markup(
        '<span class="ptcg-type ptcg-type-{type.initial}" title="{type.name}">[{type.initial}]</span>'
        ).format(type=type)

def class_icon(cls):
    return Markup(
        '<span class="ptcg-cardclass" title="{cls.name}">{cls.name[0]}</span>'
        ).format(cls=cls)

def asset_url_factory(request):
    def asset_url(url):
        return request.static_url('tcg_web_editor:assets/{}'.format(url))
    return asset_url

class Link(object):
    def __init__(self, context, obj, text=None, class_=None, **attrs):
        from tcg_web_editor.resource import Resource
        if isinstance(obj, basestring):
            obj = context.traverse(obj)
        elif not isinstance(obj, Resource):
            obj = context.root.wrap(obj)
        self.text = text
        self.obj = obj
        self.attrs = attrs
        self.attrs.setdefault('href', obj.url)
        if class_ is not None:
            self.attrs.setdefault('class', class_)

    def __html__(self):
        text = self.text or self.obj.friendly_name
        url = self.obj.url
        attrs = ' '.join(Markup('{}="{}"').format(name, value) for name, value
            in self.attrs.items())
        return Markup('<a {}>{}</a>'.format(attrs, text))
    __unicode__ = __html__

def link(context):
    return functools.partial(Link, context)
