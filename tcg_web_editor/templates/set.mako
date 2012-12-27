<%inherit file="base.mako" />

<div class="container">

    <h1>${this.set.name}</h1>

    <p>${this.set.name} is a set nominally containing ${this.set.total} cards:</p>

    <table class="table">
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
            <td>${print_.card.name}</td>
            <td>${print_.card.class_.name}</td>
        </tr>
    % endfor
    </tbody>
    </table>

</div>
