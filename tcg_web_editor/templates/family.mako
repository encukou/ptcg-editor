<%inherit file="base.mako" />
<%!
import string

def print_sort_key(p):
    return p.set.id, p.set_number
%>

<%
prints = [p for c in this.family.cards for p in c.prints]
prints.sort(key=print_sort_key)
%>

<div class="container">

    <h1>Cards named ${this.family.name}</h1>

    <form action="${this.url}/diff" method="GET">
    <table class="table table-hover">
    <thead>
        <tr>
            <th>Set name</th>
            <th>No.</th>
            <th>Card</th>
            <th colspan="2">Exact Reprints</th>
            <th></th>
        </tr>
    </thead>
    <tbody>
    <%
        seen_cards = {}
        alphabet = iter(string.ascii_uppercase)
        seen_mechanic_notes = set()
    %>
    % for print_ in prints:
    <%
        first_print = min(print_.card.prints, key=print_sort_key)
        mechanic_note = h.card_named_mechanic_note(print_.card)
    %>
    <tr>
        <td>${link(print_.set)}</td>
        <td>${print_.set_number}</td>
        <td class="warning">
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
                <span class="muted">${mechanic_note}</span>
            </a>
        </td>
        <td>
            % if len(print_.card.prints) > 1:
                <%
                    try:
                        letter = seen_cards[print_.card]
                    except KeyError:
                        letter = seen_cards[print_.card] = next(alphabet)
                %>
                <span class="label label-${letter}">${letter}</span>
            % endif
        </td>
        <td>
            % if print_ is first_print:
                % if mechanic_note in seen_mechanic_notes:
                    <span class="label label-warning tooltipped"
                        title="Rogue reprint?"
                        >⚠</span>
                % endif
                <% seen_mechanic_notes.add(mechanic_note) %>
            % endif
        </td>
        <td>
            <% name = '/'.join([this.name, wrap(print_).name]) %>
            <input type="radio" name="card-a" value="${name}">
            <input type="radio" name="card-b" value="${name}">
        </td>
    </tr>
    % endfor
    </tbody>
    <tfoot>
        <tr>
            <td colspan="5"></td>
            <td>
                <input type="submit" value="Diff">
            </td>
        </tr>
    </tfoot>
    </table>
    </form>

</div>
