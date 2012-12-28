<%inherit file="base.mako" />
<%
print_ = this.print_
card = print_.card
flavor = print_.pokemon_flavor
%>

<div class="container">
    <h1>${print_.card.name} <span class='muted'>(${print_.set.name})</span></h1>
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
        % if card.types or card.stage:
        <dl class="row-fluid">
            <dt class="span2">Type</dt>
            <dd class="span4">${'/'.join(t.name for t in card.types)}</dd>
            <dt class="span2">Stage</dt>
            <dd class="span4">${card.stage.name}</dd>
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

        % if card.damage_modifiers:
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
        % endif

        % if card.mechanics:
        % for mechanic in card.mechanics:
        <hr>
        <div class="row-fluid">
            <span class="span2">
            ${mechanic.class_.name if mechanic.class_.identifier != 'attack' else ''}
            % for cost in mechanic.costs:
                % for i in range(cost.amount):
<span class="ptcg-type ptcg-type-${cost.type.initial}">[${cost.type.initial}]</span>\
                % endfor
            % endfor
            </span>
            <span class="span2">${mechanic.name or ''}</span>
            <span class="span6">${unicode(mechanic.effect or '')}</span>
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
                    <img src="http://veekun.com/dex/media/pokemon/icons/${flavor.species_id}.png">
                    <a href="http://veekun.com/dex/pokemon/${flavor.species.name.lower()}">
                        ${flavor.species.name}
                    </a>
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

    </div>
    <div class="span2">
    %if print_.scans:
    <img src="/scans/${print_.set.identifier}/${print_.scans[0].filename}.jpg">
    % endif
    </div>
</div>
</div>

<% ''' TODO:
set: aquapolis
number: H1
order: 0
evolves from: Flaaffy
legal: false
'''
%>