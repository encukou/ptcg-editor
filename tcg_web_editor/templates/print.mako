<%inherit file="base.mako" />
<%!
import json

from markupsafe import Markup

from ptcgdex import tcg_tables
%>

<%
print_ = this.print_
card = print_.card
flavor = print_.pokemon_flavor
%>

<div class="container">
    <h1>${print_.card.name} <small>${print_.set.name} #${print_.set_number}</small></h1>

    <ul class="nav nav-tabs">
    <li><a href="#edittabs-view" data-toggle="tab">View</a></li>
    <li><a href="#edittabs-json" data-toggle="tab">Data</a></li>
    </ul>

</div>

<div class="tab-content">
<div class="tab-pane active" id="edittabs-view">

<div class="container">

<div class="row-fluid">
    <div class="span10">

        <h2>Card Info</h2>

        <dl class="row-fluid">
            <dt class="span2">Name</dt>
            <dd class="span4" data-tcg-str="card.name" data-tcg-show-modified="name">${card.name}</dd>
            <dt class="span2">Card class</dt>
            <dd class="span4" data-tcg-enum="card.class" data-tcg-show-modified="class"
                data-options="${json.dumps([(c.name[0], c.name) for c in request.db.query(tcg_tables.Class)])}"
                >${card.class_.name}</dd>
        </dl>
        <dl class="row-fluid">
            <dt class="span2">${'Subclass' if len(card.subclasses) == 1 else 'Subclasses'}</dt>
            <dd class="span10" data-tcg-tags="card.subclasses" data-tcg-show-modified="subclasses"
                data-display-separator=", "
                data-options="${json.dumps([(c.name, c.name) for c in request.db.query(tcg_tables.Subclass)])}"
                >${', '.join(sc.name for sc in card.subclasses) or Markup('&nbsp;')}</dd>
        </dl>
        <dl class="row-fluid">
            <dt class="span2">Type</dt>
            <dd class="span4" data-tcg-tags="card.types" data-tcg-show-modified="types"
                data-display-separator="/"
                data-options="${json.dumps([(c.name, c.name) for c in request.db.query(tcg_tables.TCGType)])}"
                >${'/'.join(t.name for t in card.types) or Markup('&nbsp;')}</dd>
            <dt class="span2">Stage</dt>
            <dd class="span4" data-tcg-enum="card.stage" data-tcg-show-modified="stage"
                data-options="${json.dumps([('', u'N/A')] + [(c.name, c.name) for c in request.db.query(tcg_tables.Stage)])}"
                >${card.stage.name if card.stage else 'N/A'}</dd>
        </dl>
        <dl class="row-fluid">
            <dt class="span2">Retreat cost</dt>
            <dd class="span4" data-tcg-int="card.retreat" data-tcg-show-modified="retreat" data-nullable="true">
                ${card.retreat_cost if card.retreat_cost is not None else 'N/A'}</dd>
            <dt class="span2">HP</dt>
            <dd class="span4" data-tcg-int="card.hp" data-tcg-show-modified="hp" data-nullable="true" data-step="10">
                ${card.hp or 'N/A'}</dd>
        </dl>

        % for mod in card.damage_modifiers:
        <dl class="row-fluid">
            % if mod.operation in '-':
                <dt class="span2">Resistance</dt>
            % elif mod.operation in u'+×':
                <dt class="span2">Weakness</dt>
            % endif
            <dd class="span4">
                ${mod.type.name}: ${mod.operation}${mod.amount}
            </dd>
        </dl>
        % endfor

        % for evo in card.evolutions:
        <dl class="row-fluid">
            <dt class="span2">
            % if evo.family_to_card:
                Evolves from
            % else:
                Evolves to
            % endif
            </dt>
            <dd class="span10">
                ${link(evo.family, text=evo.family.name)}
            </dd>
        </dl>
        % endfor
        % for evo in card.family.evolutions:
        <dl class="row-fluid">
            <dt class="span2 muted">
            % if evo.family_to_card:
                Evolves into
            % else:
                Evolves from
            % endif
            </dt>
            <dd class="span10">
                <a href="${wrap(evo.card.prints[0]).url}">
                    ${evo.card.name}
                    <span class="muted">
                        ${h.card_named_mechanic_note(evo.card)}:
                        ${', '.join('{} #{}'.format(
                            p.set.name, p.set_number) for p in evo.card.prints)}
                    </span>
                </a>
            </dd>
        </dl>
        % endfor

        % if card.mechanics:
        % for mechanic in card.mechanics:
        <hr>
        <div class="row-fluid">
            <span class="span2 mechanic-type">
            ${mechanic.class_.name if mechanic.class_.identifier != 'attack' else Markup('&nbsp;')}
            ${Markup().join(h.type_icon(cost.type) * cost.amount for cost in mechanic.costs)}
            % if not mechanic.costs and mechanic.class_.identifier == 'attack':
                <span class="ptcg-type ptcg-type-null">[#]</span>\
            % endif
            </span>
            <span class="span2 mechanic-name">${mechanic.name or Markup('&nbsp;')}</span>
            <span class="span6">${unicode(mechanic.effect) if mechanic.effect else Markup('&nbsp;')}</span>
            <span class="span2">${mechanic.damage_base or ''}${mechanic.damage_modifier or ''}</span>
        </div>
        % endfor
        % endif

        <h2>Print</h2>
        % if flavor:
            % if flavor.species:
            <dl class="row-fluid">
                <dt class="span2">Pokémon</dt>
                <dd class="span4">
                    <a href="http://veekun.com/dex/pokemon/${flavor.species.name.lower()}">
                    ${flavor.species.name}
                    </a><sup>[↗]</sup>
                </dd>
                <dt class="span2">Species</dt>
                <dd class="span4">${flavor.genus}</dd>
            </dl>
            % endif
            % if flavor.height or flavor.weight:
            <dl class="row-fluid">
                <dt class="span2">Height</dt>
                <dd class="span4">${u'{}′{}″'.format(*divmod(flavor.height, 12))}</dd>
                <dt class="span2">Weight</dt>
                <dd class="span4">${flavor.weight} lb</dd>
            </dl>
            % endif
            % if flavor.dex_entry:
            <dl class="row-fluid">
                <dt class="span2">Dex entry</dt>
                <dd class="span10">${flavor.dex_entry}</dd>
            </dl>
            % endif
        % endif
        <dl class="row-fluid">
            <dt class="span2">Rarity</dt>
            <dd class="span4">${print_.rarity.name}</dd>
            <dt class="span2">Holographic</dt>
            <dd class="span4">${'Yes' if print_.holographic else 'No'}</dd>
        </dl>
        <dl class="row-fluid">
            <dt class="span2">Illustrator</dt>
            <dd class="span10">${Markup(', ').join(link(il) for il in print_.illustrators)}</dd>
        </dl>

        <h2>Sets &amp; Reprints</h2>
        <dl class="row-fluid">
            <dt class="span2">Set</dt>
            <dd class="span4">${link(print_.set)}</dd>
            <dt class="span2">Number</dt>
            <dd class="span4">${print_.set_number}${
                '/{}'.format(print_.set.total) if print_.set.total else ''}</dd>
        </dl>
        % if len(card.prints) > 1:
            <dl class="row-fluid">
                <dt class="span2">Also printed as</dt>
                <dd class="span10">
                % for other_print in [p for p in card.prints if p is not print_]:
                    <a href="${wrap(other_print).url}">
                        ${other_print.set.name} #${other_print.set_number}
                    </a>
                    % if not loop.last:
                        &amp;
                    % endif
                % endfor
                </dd>
            </dl>
        % endif

        % if len(card.family.cards) > 1:
            <h2>Other ${card.name} cards</h2>
            <div class="row-fluid">
                <div class="well">
                % for other_card in card.family.cards:
                    <%
                        other_print = other_card.prints[0]
                    %>
                    <div class="row-fluid">
                        <span class="span12">
                            % if other_card is card:
                                ${other_print.set.name} #${other_print.set_number}
                            % else:
                            <a href="${wrap(other_print).url}">
                                ${other_print.set.name} #${other_print.set_number}
                            </a>
                            % endif
                            –
                            ${other_card.name}
                            ${h.card_named_mechanic_note(other_card)}
                        </span>
                    </div>
                % endfor
                </div>
            </div>

            <p>
                See all
                <a href="${wrap(card.family).url}">cards named ${card.name}</a>
                for more details.
            </p>
        % endif

    </div>
    <div class="span2">
    %if print_.scans:
    <a href="/scans/${print_.set.identifier}/${print_.scans[0].filename}.jpg">
        <img src="/scans/${print_.set.identifier}/${print_.scans[0].filename}.jpg"
            alt="Card scan">
    </a>
    % endif
    </div>
</div>

</div>
</div>
<div class="tab-pane active" id="edittabs-json">
<div class="container">

    <h2>JSON Data</h2>
    <pre class="prettyprint linenums" id="orig-data">
    ${json.dumps(this.__json__(), sort_keys=True, ensure_ascii=False, indent=4)}
    </pre>
    <div class="container">
        We also serve raw
        <a href="${this['json'].url}">JSON</a> and
        savory <a href="${this['yaml'].url}">YAML</a>
        to our dear data gastronomists.
        Do however note that the schema is not yet set in stone.
    </div>

    <div style="display: none;" data-tcg-diff-hide="1">
        <h2>Your unsaved edits</h2>
        <pre data-tcg-diff="1"></pre>
    </div>

</div>
</div>
</div>

<div class="container">
    <ul class="pager">
        % if prev_print:
        <li class="previous">
            <a href="${wrap(prev_print).url}">← ${prev_print.card.name}</a>
        </li>
        % endif
        <li>
            <a href="${wrap(print_.set).url}">${print_.set.name}</a>
        </li>
        % if next_print:
        <li class="next">
            <a href="${wrap(next_print).url}">${next_print.card.name} →</a>
        </li>
        % endif
    </ul>
</div>

<%def name="extra_css()">
    <link href="${asset_url('css/editor.css')}" rel="stylesheet" />
</%def>

<%def name="extra_scripts()">
    <script src="${asset_url('js/prettify.js')}"></script>
    <script src="${asset_url('js/editor.js')}"></script>
    <script>
        $(function(){
            $('ul.nav.nav-tabs a').tab('show');
            $('ul.nav.nav-tabs a:first').tab('show');

            if (location.hash !== '') $('a[href="' + location.hash + '"]').tab('show');
            $('a[data-toggle="tab"]').on('shown', function(e) {
                var hash = $(e.target).attr('href').substr(1)
                var node = $( '#' + hash );
                node.attr('id', '');  // Don't scroll when changing tabs
                location.hash = hash;
                node.attr('id', hash);  // Enable the ID again
                return true;
            });
        })
        $(prettyPrint);
        $.tcg_editor(
            "${'{}/{}'.format(this.parent.name, this.name)}",
            JSON.parse($("#orig-data").text()));
    </script>
</%def>

<%def name="extra_html_attrs()">
    data-ng-app="tcg"
    data-ng-controller="tcgCardCtrl"
    id="ng-app"
</%def>

<% ''' TODO:
legal: false
'''
%>