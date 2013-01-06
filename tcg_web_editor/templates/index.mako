<%inherit file="base.mako" />

<div class="container">

    <div class="hero-unit">

        <h1>PokéBeach Card Database Editor</h1>

        <br>

        <p>
            Here, you can view
                <span class="tooltipped" style="cursor:default;"
                        title="or suggest edits, if you're not an admin">
                    and edit*
                </span>
            our database of Pokémon Trading Cards.
        </p>

        <br>

        <p>
            Currently, we have
            ${link('sets', text='{} sets'.format(set_query.count()))} with
            ${link('cards', text='{} cards'.format(card_query.count()))}.
        </p>

    </div>


    <p>
        This site is <a href="https://github.com/encukou/ptcgdex/tree/editor">open-source</a>,
        the data is <a href="https://github.com/encukou/ptcgdex/tree/master/ptcgdex/data">also available</a>.
        Run your own!
        <br>
        Documentation is sorely lacking; e-mail
        <a href="mailto:encukou@gmail.com">En-Cu-Kou</a> or try
        <a href="irc://irc.veekun.com/veekun">veekun IRC</a> if you have any questions.
        <br>
        Built using
            <a href="http://veekun.com">veekun pokédex</a>,
            <a href="http://www.python.org/">Python</a>,
            <a href="http://www.sqlalchemy.org/">SQLAlchemy</a>,
            <a href="http://www.pylonsproject.org/">Pyramid</a>,
            <a href="http://www.makotemplates.org/">Mako</a>,
            <a href="http://jquery.com/">JQuery</a>,
            and <a href="http://twitter.github.com/bootstrap/">Twitter Bootstrap</a> for
            <a href="http://pokebeach.com/">PokéBeach</a>.
    <p>

</div>
