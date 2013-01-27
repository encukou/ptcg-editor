<%inherit file="base.mako" />
<%!
from sqlalchemy import func

from ptcgdex import tcg_tables
%>

<%
count_query = this.request.db.query(tcg_tables.Illustrator.id, func.count(tcg_tables.PrintIllustrator.print_id))
count_query = count_query.filter(tcg_tables.Illustrator.id == tcg_tables.PrintIllustrator.illustrator_id)
count_query = count_query.group_by(tcg_tables.Illustrator.id)
print_count_by_id = {k: v for k, v in count_query}
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
                ${print_count_by_id[illustrator.id]}
            </td>
            <td>${link(illustrator)}</td>
        </tr>
    % endfor
    </tbody>
    </table>

</div>
