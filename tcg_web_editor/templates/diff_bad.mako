<%inherit file="base.mako" />

<div class="container">

    <h1>Bad diff</h1>

    <p class="alert alert-error">${this.error_message}</p>

    <p>
        This diff is invalid.
        Press your Back button, or go back to ${link(this.parent)}.
    </p>

</div>

<%include file="diff_form.mako" />
