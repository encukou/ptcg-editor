from pyramid.traversal import traverse


class Helpers(object):
    def __init__(self, context):
        self.context = context

    def url(self, path):
        if path.startswith('/'):
            context = self.context.root
            path = path[1:]
        else:
            context = self.context
        result = traverse(context, path)
        if result['view_name']:
            raise KeyError(result['view_name'])
        return result['context'].url
