<%inherit file="base.mako" />
<%!
from markupsafe import Markup

from ptcgdex import tcg_tables
%>

<div class="container">

    <h1>Cards Illustrated by ${this.illustrator.name}</h1>

    <table class="table table-hover">
    <thead>
        <tr>
            <th>Set</th>
            <th>Number</th>
            <th>Card</th>
        </tr>
    </thead>
    <tbody>
    % for pi in this.illustrator.print_illustrators:
        <% print_ = pi.print_ %>
    % for set_print in print_.set_prints:
        <tr>
            <td>${link(set_print.set)}</td>
            <td>${Markup('&mdash;') if set_print.number is None else set_print.number}</td>
            <td>
                <a href="${wrap(set_print).url}">
                    <span class="muted">
                    ${h.card_icon(print_.card)}
                    </span>
                    ${print_.card.name}
                    <span class="muted">
                        ${h.card_named_mechanic_note(print_.card)}
                    </span>
                </a>
            </td>
        </tr>
    % endfor
    % endfor
    </tbody>
    </table>

</div>
