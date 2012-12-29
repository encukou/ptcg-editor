<%inherit file="base.mako" />
<%!
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
    % for print_ in this.illustrator.prints:
        <tr>
            <td>${link(print_.set)}</a></td>
            <td>${print_.set_number}</td>
            <td>
                <a href="${wrap(print_).url}">
                    <span class="muted">
                    % if print_.card.class_.identifier == 'pokemon':
                        % for t in print_.card.types:
                            ${h.type_icon(t)}
                        % endfor
                    % else:
                        ${h.class_icon(print_.card.class_)}
                    % endif
                    </span>
                    ${print_.card.name}
                    <span class="muted">
                        ${h.card_named_mechanic_note(print_.card)}
                    </span>
                </a>
            </td>
        </tr>
    % endfor
    </tbody>
    </table>

</div>
