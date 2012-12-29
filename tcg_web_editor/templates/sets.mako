<%inherit file="base.mako" />

<div class="container">

    <h1>The Set List</h1>

    <table class="table table-hover">
    <thead>
        <tr>
            <th>Card total</th>
            <th>Set name</th>
            <th>Released</th>
            <th>Retired</th>
        </tr>
    </thead>
    <tbody>
    % for tcg_set in this.sets:
        <tr>
            <td>${tcg_set.total or u'—'}</td>
            <td>${link(tcg_set)}</td>
            <td>${tcg_set.release_date or u'—'}</td>
            <td>${tcg_set.ban_date or u'—'}</td>
        </tr>
    % endfor
    </tbody>
    </table>

</div>
