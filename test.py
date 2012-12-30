import sys
import time
import itertools
from StringIO import StringIO

from sqlalchemy import event
from sqlalchemy.engine.base import Engine
from pyramid.events import ContextFound

from tcg_web_editor import main

queries = []
contexts = []

def add_sqla_events():
    # Inspired by pyramid.debugtoolbar. Not thread-safe
    @event.listens_for(Engine, "before_cursor_execute")
    def _before_cursor_execute(conn, cursor, stmt, params, context, execmany):
        setattr(conn, 'ptcg_test_start_timer', time.time())

    @event.listens_for(Engine, "after_cursor_execute")
    def _after_cursor_execute(conn, cursor, stmt, params, context, execmany):
        stop_timer = time.time()
        queries.append({
            'engine_id': id(conn.engine),
            'duration': stop_timer - conn.ptcg_test_start_timer,
            'statement': stmt,
            'parameters': params,
            'context': context
        })
        delattr(conn, 'ptcg_test_start_timer')


def context_found_subscriber(event):
    contexts[:] = [event.request.context]


def check_page(app, path, query_string=''):
    environ = {
        'REQUEST_METHOD': "GET",
        'SCRIPT_NAME': "",
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'SERVER_NAME': "test",
        'SERVER_PORT': "0",
        'SERVER_PROTOCOL': "HTTP/1.1",
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'http',
        'wsgi.input': StringIO(''),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    def start_response(status, response_headers, exc_info=None):
        #print 'STARTED RESPONSE', (status, response_headers, exc_info)
        def write():
            raise RuntimeError('Not Implemented')
        return write
    start = time.time()
    output = ''.join(app(environ, start_response))
    end = time.time()
    #print queries
    print '{url:37} {time:8.5f} {size:8d} {a_num:4d}{a_dst:4d} {a_min:4.1f} {a_max:4.1f} {a_avg:4.1f}'.format(
        url=path if path == '/' else ' ' * path.count('/') + path.split('/')[-1],
        time=end - start,
        size=len(output),
        a_num=len(queries),
        a_dst=len(set(q['statement'] for q in queries)),
        a_min=min(q['duration'] for q in queries) * 1000,
        a_max=max(q['duration'] for q in queries) * 1000,
        a_avg=sum(q['duration'] for q in queries) / len(queries) * 1000,
    )
    queries[:] = []
    [context] = contexts
    for child in itertools.chain(context.iter_children(), list(context.iter_dynamic())[:5]):
        if path == '/':
            new_path = path + child.name
        else:
            new_path = '/'.join([path, child.name])
        check_page(app, new_path)


def check_pages():
    config = main.get_config()
    config.add_subscriber(context_found_subscriber, ContextFound)
    app = config.make_wsgi_app()
    print '---------------- URL ---------------- - time - - size - -------- SQLA ---------'
    print '                                       s        m  k  b  num dst  min  max  avg'
    check_page(app, '/')


add_sqla_events()

if __name__ == '__main__':
    check_pages()
