<%inherit file="base.mako" />

<div class="container">

    <h1>Pokébeach Card Database Editor</h1>

    <table class="table">
    <thead>
        <tr>
            <th>Card total</th>
            <th>Set name</th>
            <th>Released</th>
            <th>Retired</th>
        </tr>
    </thead>
    <tbody>
    % for tcg_set in sets:
        <tr>
            <td>${tcg_set.total or '?'}</td>
            <td>${tcg_set.name}</td>
            <td>${tcg_set.release_date or '?'}</td>
            <td>${tcg_set.ban_date or '?'}</td>
        </tr>
    % endfor
    </tbody>
    </table>

</div>
