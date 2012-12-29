<%inherit file="base.mako" />
<%
import string

from markupsafe import Markup

def active(page):
    if page is this:
        return Markup('class="active"')
    else:
        return ''
%>

<div class="container">

    <h1>Card list</h1>

    <div class="pagination pagination-small pagination-centered">
        <ul>
            <li ${active(this.base_families)}><a href="${this.base_families.url}">@</a></li>
            % for s in string.ascii_lowercase:
                <li ${active(this[s])}><a href="${this[s].url}">${s.upper()}</a></li>
            % endfor
        </ul>
    </div>

    % for family in this.filtered_query:
        <%
        num_prints = len([p for c in family.cards for p in c.prints])
        %>
        <div class="row-fluid">
        <span class="span10 offset2">
            <a href="${this.wrap(family).url}">
                ${family.name}
                % if num_prints != 1:
                    <%
                    info = []
                    if len(family.cards) != 1:
                        info.append('{} cards'.format(len(family.cards)))
                    if len(family.cards) != num_prints:
                        info.append('{} prints'.format(num_prints))
                    %>
                    <span class="muted">(${', '.join(info)})</span>
                % endif
            </a>
        </span>
        </div>
    % endfor

    % if this is this.base_families:
    <br>
    <div class="container">
        <p class="alert alert-info">
            Use the pagination above to list cards by name.
        </p>
    </div>
    % endif

</div>
