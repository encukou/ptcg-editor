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
            <th>Class</th>
        </tr>
    </thead>
    <tbody>
    % for print_ in this.set.prints:
        <tr>
            <td>${print_.set_number}</td>
            <td><a href="${this.root['prints'].wrap(print_).url}">${print_.card.name}</a></td>
            <td>${print_.card.class_.name}</td>
        </tr>
    % endfor
    </tbody>
    </table>

</div>
