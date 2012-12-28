<%inherit file="base.mako" />

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
    % for print_ in this.set.prints:
        <tr>
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
