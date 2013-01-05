<%inherit file="base.mako" />
<%!
import difflib
import itertools

from markupsafe import Markup

def text_if_not_none(text):
    if text is None:
        return Markup('&nbsp;')
    else:
        return text

def lineno_if_not_none(no):
    if no is None:
        return Markup('&nbsp;')
    else:
        return str(no + 1)
%>

<div class="container">

    <h1>Card Diff</h1>

    <table class="diff-table diff-table-${this.diff_style}">
        <thead>
            % if this.diff_style == 'uni':
                % for i, res in enumerate(this.print_resources):
                <tr>
                    % if i:
                        <td></td><td class="b different">+++</td>
                    % else:
                        <td class="a different">---</td><td></td>
                    % endif
                    <th>${link(res)}</th>
                </tr>
                % endfor
            % else:
            <tr>
                <td colspan="2"></th>
                % for res in this.print_resources:
                    <th>${link(res)}</th>
                % endfor
            </tr>
            % endif
        </thead>
        <tbody>
        % for r1, r2 in this.rows:
            <tr>
                <th>${lineno_if_not_none(r1['num'])}</th>
                <th>${lineno_if_not_none(r2['num'])}</th>
                <td class="${r1['cls']}">${text_if_not_none(r1['text'])}</td>
                % if this.diff_style == 'uni':
                    <% assert r2['text'] is None %>
                % else:
                    <td class="${r2['cls']}">${text_if_not_none(r2['text'])}</td>
                % endif
            </tr>
        % endfor
        </tbody>
    </table>
</div>

<%include file="diff_form.mako" />
