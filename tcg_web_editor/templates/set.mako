<%inherit file="base.mako" />
<%!
from markupsafe import Markup
%>

<div class="container">

    <h1>${this.set.name}</h1>

    % if this.set.total:
        <p>${this.set.name} is a set nominally containing ${this.set.total} cards:</p>
    % else:
        <p>${this.set.name} is a TCG set.</p>
    % endif

    <table class="table table-hover">
    <thead>
        <tr>
            <th>No.</th>
            <th>Card</th>
        </tr>
    </thead>
    <tbody>
    % for set_print in this.set.set_prints:
        <tr>
            <td>${Markup('&mdash;') if set_print.number is None else set_print.number}</td>
            <td>
                <a href="${wrap(set_print).url}">
                    <span class="muted">
                    ${h.card_icon(set_print.print_.card)}
                    </span>
                    ${set_print.print_.card.name}
                    <span class="muted">
                        ${h.card_named_mechanic_note(set_print.print_.card)}
                    </span>
                </a>
            </td>
        </tr>
    % endfor
    </tbody>
    </table>

</div>
