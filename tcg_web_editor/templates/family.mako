<%inherit file="base.mako" />
<%!
import string

def set_print_sort_key(sp):
    return sp.set.id, sp.number, sp.print_.id
%>

<%
set_prints = [sp
              for c in this.family.cards
              for p in c.prints
              for sp in p.set_prints]
set_prints.sort(key=set_print_sort_key)
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
    % for set_print in set_prints:
    <%
        print_ = set_print.print_
        other_set_prints = [sp
                            for p in set_print.print_.card.prints
                            for sp in p.set_prints]
        first_set_print = min(other_set_prints, key=set_print_sort_key)
        mechanic_note = h.card_named_mechanic_note(print_.card)
    %>
    <tr>
        <td>${link(set_print.set)}</td>
        <td>${set_print.number}</td>
        <td class="warning">
            <a href="${wrap(set_print).url}">
                <span class="muted">
                ${h.card_icon(print_.card)}
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
            % if set_print is first_set_print:
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
                <input type="hidden" name="diff" value="uni">
                <input type="hidden" name="fmt" value="yaml">
                <input type="submit" value="Diff">
            </td>
        </tr>
    </tfoot>
    </table>
    </form>

</div>
