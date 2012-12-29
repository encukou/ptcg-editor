<%inherit file="base.mako" />
<%!
from ptcgdex import tcg_tables
%>

<div class="container">

    <h1>Illustrators</h1>

    <table class="table table-hover">
    <thead>
        <tr>
            <th>Cards illustrated</th>
            <th>Name</th>
        </tr>
    </thead>
    <tbody>
    % for illustrator in this.illustrator_query:
        <tr>
            <td>
                <%
                query = this.request.db.query(tcg_tables.Print)
                query = query.filter(tcg_tables.Print.illustrator == illustrator)
                %>
                ${query.count()}
            </td>
            <td>${link(illustrator)}</td>
        </tr>
    % endfor
    </tbody>
    </table>

</div>
