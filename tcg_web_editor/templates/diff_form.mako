
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
