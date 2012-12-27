from markupsafe import Markup


def _best_parent(this, objs):
    best = None
    longest_len = 0
    for obj in objs:
        if obj in this.lineage and (
                best is None or len(obj.lineage) > longest_len):
            longest_len = len(obj.lineage)
            best = obj
    return best

def nav_tabs(this, paths):
    objs = [this.root.traverse(p) for p in paths]
    best = _best_parent(this, objs)
    result = []
    for obj in objs:
        result.append(Markup('<li{active}><a href="{url}">{text}</a></li>').format(
            active=Markup(' class="active"') if obj is best else '',
            url=obj.url,
            text=obj.short_name,
        ))
    return Markup().join(result)
