<%inherit file="base.mako" />
<%
from markupsafe import Markup

print_ = this.print_
card = print_.card
flavor = print_.pokemon_flavor
%>

<div class="container">
    <h1>${print_.card.name} <small>${print_.set.name} #${print_.set_number}</small></h1>
</div>

<div class="container">

<div class="row-fluid">
    <div class="span10">

        <h2>Card info</h2>

        <dl class="row-fluid">
            <dt class="span2">Name</dt>
            <dd class="span4">${card.name}</dd>
            <dt class="span2">Card class</dt>
            <dd class="span4">${card.class_.name}</dd>
        </dl>
        % if card.subclasses:
        <dl class="row-fluid">
            <dt class="span2">${'Subclass' if len(card.subclasses) == 1 else 'Subclasses'}</dt>
            <dd class="span10">${', '.join(sc.name for sc in card.subclasses)}</dd>
        </dl>
        % endif
        % if card.types or card.stage:
        <dl class="row-fluid">
            <dt class="span2">Type</dt>
            <dd class="span4">${'/'.join(t.name for t in card.types) or Markup('&nbsp;')}</dd>
            % if card.stage:
            <dt class="span2">Stage</dt>
            <dd class="span4">${card.stage.name}</dd>
            % endif
        </dl>
        % endif
        % if card.retreat_cost is not None or card.hp:
        <dl class="row-fluid">
            <dt class="span2">Retreat cost</dt>
            <dd class="span4">${card.retreat_cost}</dd>
            <dt class="span2">HP</dt>
            <dd class="span4">${card.hp}</dd>
        </dl>
        % endif

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
                <a href="${wrap(evo.family).url}">${evo.family.name}</a>
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
                    <span class="muted">(${', '.join('{} #{}'.format(
                        p.set.name, p.set_number) for p in evo.card.prints)})</span>
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
            <dd class="span10">${print_.illustrator.name}</dd>
        </dl>

        <h2>Sets &amp; Reprints</h2>
        <dl class="row-fluid">
            <dt class="span2">Set</dt>
            <dd class="span4">
                <a href="${wrap(print_.set).url}">
                    ${print_.set.name}
                </a>
            </dd>
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
            <h2>All ${card.name} cards</h2>
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
                See the
                <a href="${wrap(card.family).url}">${card.name} card family</a>
                for more details.
            </p>
        % endif

    </div>
    <div class="span2">
    %if print_.scans:
    <a href="/scans/${print_.set.identifier}/${print_.scans[0].filename}.jpg" rel="lightbox">
        <img src="/scans/${print_.set.identifier}/${print_.scans[0].filename}.jpg">
    </a>
    % endif
    </div>
</div>

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

<% ''' TODO:
legal: false
'''
%>