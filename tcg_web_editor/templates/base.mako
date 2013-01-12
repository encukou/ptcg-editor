<!DOCTYPE html>
<%def name="extra_scripts()"></%def>
<%def name="extra_css()"></%def>

<html lang="en">
  <head>
    % if this is this.root:
        <title>${this.friendly_name}</title>
    % else:
        <title>${this.friendly_name} – ${this.root.friendly_name}</title>
    % endif
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <link href="${asset_url('css/bootstrap.css')}" rel="stylesheet">
    <link href="${asset_url('css/bootstrap-responsive.css')}" rel="stylesheet">
    <link href="${asset_url('css/ptcg-symbols.css')}" rel="stylesheet">
    <link href="${asset_url('css/ptcg-editor.css')}" rel="stylesheet">
    <link href="${asset_url('css/prettify.css')}" rel="stylesheet" />
    ${self.extra_css()}

    <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <link rel="apple-touch-icon-precomposed" href="${asset_url('img/staryu-precomposed.png')}">
    <link rel="shortcut icon" href="${asset_url('img/staryu-32.png')}">
  </head>

  <body>

    <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          ${link(this.root, class_="brand", text="Card DB Editor")}
          <div class="nav-collapse collapse">
            <ul class="nav">
              ${h.nav_tabs(this, ('/sets', '/cards'))}
            </ul>
          </div>
        </div>
      </div>
    </div>

    <ul class="breadcrumb">
        % for obj in reversed(this.lineage[1:]):
            <li>${link(obj, text=obj.short_name)} <span class="divider">/</span></li>
        % endfor
        <li class="active">${this.short_name}</li>
    </ul>

    ${next.body()}

    <hr style="margin-top: 50px;">

    <footer class="muted container">
        <a href="http://www.pokemon.com">Pokémon</a> and the
            <a href="http://www.pokemontcg.com">Pokémon Trading Card Game</a>
            are ©1995-2013 Nintendo, Creatures, Game Freak and/or Wizards of the Coast.
            This is a fan website and is not official in any way nor associated
            with the aforementioned companies.
        <br>
        <a href="https://github.com/encukou/ptcgdex/tree/editor">Site</a> built by
            <a href="mailto:encukou@gmail.com">Petr Viktorin</a>
            for <a href="http://pokebeach.com/">PokéBeach</a>.
    </footer>

    <script src="http://code.jquery.com/jquery-1.8.3.min.js"></script>
    <script src="${asset_url('js/bootstrap.js')}"></script>
    <script>
        $(".ptcg-type").tooltip();
        $(".tooltipped").tooltip();
    </script>
    ${self.extra_scripts()}

  </body>
</html>
