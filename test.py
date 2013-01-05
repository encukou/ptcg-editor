import sys
import time
import itertools
from StringIO import StringIO

from sqlalchemy import event
from sqlalchemy.engine.base import Engine
from pyramid.events import ContextFound

from blessings import Terminal  # pip install blessings

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
            'engine': conn.engine,
            'engine_id': id(conn.engine),
            'duration': stop_timer - conn.ptcg_test_start_timer,
            'statement': stmt,
            'parameters': params,
            'context': context
        })
        delattr(conn, 'ptcg_test_start_timer')


def context_found_subscriber(event):
    contexts[:] = [event.request.context]


def format_time(term, time, fmt):
    result = fmt.format(time)
    if time < 0.1:
        return term.white(result)
    elif time < 0.5:
        return term.yellow(result)
    else:
        return term.red(result)


def format_size(term, size, fmt):
    result = fmt.format(size)
    if size < 1024 * 50:
        return term.white(result)
    elif size < 1024 * 100:
        return term.yellow(result)
    else:
        return term.red(result)


def format_num_queries(term, num, fmt, distinct):
    result = fmt.format(num)
    if num <= distinct:
        return term.white(result)
    elif num < distinct * 2:
        return term.yellow(result)
    else:
        return term.red(result)


def format_distinct_queries(term, num, fmt):
    result = fmt.format(num)
    if num <= 5:
        return term.white(result)
    elif num < 10:
        return term.yellow(result)
    else:
        return term.red(result)


def check_page(app, path, query_string=''):
    environ = {
        'REQUEST_METHOD': "GET",
        'SCRIPT_NAME': "",
        'PATH_INFO': path,
        'QUERY_STRING': query_string,
        'SERVER_NAME': "localhost",
        'SERVER_PORT': "8080",
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
    [context] = contexts


    distinct_queries = set(q['statement'] for q in queries)
    resultlines = {}
    for styling_on in False, True:
        orig_stdout = sys.stdout
        if not styling_on:
            sys.stdout = open('/dev/null')
        term = Terminal()
        sys.stdout = orig_stdout
        resultlines[styling_on] = ''.join([
            '{0:37} '.format(path if path == '/' else ' ' * path.count('/') + path.split('/')[-1]),
            format_time(term, end - start, '{0:8.5f} '),
            format_size(term, len(output), '{0:8d} '),
            format_num_queries(term, len(queries), '{0:4d} ', len(distinct_queries)),
            format_distinct_queries(term, len(distinct_queries), '{0:3d} '),
            '{0:4.1f} '.format(min(q['duration'] for q in queries) * 1000),
            '{0:4.1f} '.format(max(q['duration'] for q in queries) * 1000),
            '{0:4.1f}'.format(sum(q['duration'] for q in queries) / len(queries) * 1000),
        ])

    full_lines = {f: '{} {}'.format(resultlines[f], context.url) for f in resultlines}
    if len(full_lines[False]) < term.width:
        print full_lines[True]
    else:
        print resultlines[True]

    queries[:] = []
    context.request.db.rollback()

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
