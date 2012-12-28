<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    % if this is this.root:
        <title>${this.friendly_name}</title>
    % else:
        <title>${this.friendly_name} – ${this.root.friendly_name}</title>
    % endif
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <link href="../assets/css/bootstrap.css" rel="stylesheet">
    <link href="../assets/css/ptcg-symbols.css" rel="stylesheet">
    <style>
      body {
        padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
        padding-bottom: 60px;
      }
      dl, dd, dt {
        margin-top: 0px;
        margin-bottom: 0px;
      }
      body .row-fluid [class*="span"] {
        min-height: 0px;
      }
      .mechanic-type, .mechanic-name, dt {
        font-weight: bold;
      }
      @media (min-width: 767px) {
        .mechanic-type, dt {
            text-align: right;
        }
        .mechanic-name {
            text-align: center;
        }
      }
      @media (max-width: 767px) {
        dt {
          margin-top: 5px
        }
      }
    </style>
    <link href="../assets/css/bootstrap-responsive.css" rel="stylesheet">

    <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

  </head>

  <body>

    <div class="navbar navbar-inverse navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <a class="brand" href="${this.root.url}">Pokébeach Card Database Editor</a>
          <div class="nav-collapse collapse">
            <ul class="nav">
              ${h.nav_tabs(this, ('/', '/sets', '/prints'))}
            </ul>
          </div>
        </div>
      </div>
    </div>

    <ul class="breadcrumb">
        % for obj in reversed(this.lineage[1:]):
            <li><a href="${obj.url}">${obj.short_name}</a> <span class="divider">/</span></li>
        % endfor
        <li class="active">${this.short_name}</li>
    </ul>

    ${next.body()}

    <script src="http://code.jquery.com/jquery-1.8.3.min.js"></script>
    <script src="../assets/js/bootstrap.js"></script>
    <script type="text/javascript">$(".ptcg-type").tooltip()</script>

  </body>
</html>
