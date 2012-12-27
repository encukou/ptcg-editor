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

        % if card.mechanics:
        <h2>Mechanics</h2>
        % for mechanic in card.mechanics:
        <div class="row-fluid">
            <span class="span2">
            ${mechanic.class_.name if mechanic.class_.identifier != 'attack' else ''}
            ${''.join('[{}]'.format(cost.type.initial) * cost.amount for cost in mechanic.costs)}
            </span>
            <span class="span2">${mechanic.name or ''}</span>
            <span class="span6">${unicode(mechanic.effect)}</span>
            <span class="span2">${mechanic.damage_base or ''}${mechanic.damage_modifier or ''}</span>
        </div>
        % endfor
        % endif

        % if card.damage_modifiers:
        <h2>Damage modifiers</h2>
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

        <h2>Flavor</h2>
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
rarity: rare
holographic: true
evolves from: Flaaffy
legal: false
filename: h1-ampharos
'''
%>