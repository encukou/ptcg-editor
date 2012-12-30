<%inherit file="base.mako" />
<%!
import difflib
import itertools

from markupsafe import Markup
%>

<%def name="pre_if_not_none(text)">
% if text is None:
    &nbsp;
% else:
    <pre>${text}</pre>
% endif
</%def>
<%def name="lineno_if_not_none(text)">
% if text is None:
    &nbsp;
% else:
    ${str(text + 1)}
% endif
</%def>

<div class="container">

    <h1>Card Diff</h1>

    <table class="diff-table">
        <thead>
            <th colspan="2"></th>
            % if this.diff_style == 'sbs':
                % for res in this.print_resources:
                    <th>${link(res)}</th>
                % endfor
            % else:
                <th>${Markup(' : ').join(link(res) for res in this.print_resources)}</th>
            % endif
        <thead>
        <tbody>
        % for r1, r2 in this.rows:
            <tr>
                <th>${lineno_if_not_none(r1['num'])}</th>
                <th>${lineno_if_not_none(r2['num'])}</th>
                <td>${r1['text'] | pre_if_not_none}</td>
                % if this.diff_style == 'uni':
                    <% assert r2['text'] is None %>
                % else:
                    <td>${r2['text'] | pre_if_not_none}</td>
                % endif
            <tr>
        % endfor
        </tbody>
    </table>
</div>

<div class="container">
<%def name="cbattrs(name, value)">
    name="${name}"
    value="${value}"
    % if request.GET.get(name) == value:
        checked="checked"
    % endif
</%def>
<%def name="txtattrs(name)">
    name="${name}"
    value="${request.GET.get(name)}"
</%def>

    <h1>Diff options</h1>
    <p>
        <form action="${this.url}" method="GET" class="form-horizontal">
            <div class="control-group">
                <label class="control-label" for="input-fmt-json">Data format</label>
                <div class="controls">
                    <label class="checkbox">
                        <input type="radio" ${cbattrs('fmt', 'json')} id="input-fmt-json"> JSON
                    </label>
                    <label class="checkbox">
                        <input type="radio" ${cbattrs('fmt', 'yaml')}> YAML
                    </label>
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="input-diff-sbs">Diff style</label>
                <div class="controls">
                    <label class="checkbox">
                        <input type="radio" ${cbattrs('diff', 'sbs')} id="input-diff-sbs"> Side-by-side table
                    </label>
                    <label class="checkbox">
                        <input type="radio" ${cbattrs('diff', 'uni')}> Unified-style table
                    </label>
                    <label class="checkbox">
                        <input type="radio" ${cbattrs('diff', 'raw')}> Raw unified
                    </label>
                </div>
            </div>
            <div class="control-group">
                <label class="control-label" for="input-card-a">Diffed cards</label>
                <div class="controls">
                    <input type="text" ${txtattrs('card-a')} id="input-card-a">
                    :
                    <input type="text" ${txtattrs('card-b')}>
                </div>
            </div>
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">Diff again!</button>
            </div>
        </form>
    </p>

</div>
