# Encoding: UTF-8

from __future__ import unicode_literals

import sys
import time
import itertools
import urlparse
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


def format_sqla_time(term, time, fmt):
    result = fmt.format(time)
    if time < 10:
        return term.white(result)
    elif time < 20:
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
    if num <= 10:
        return term.white(result)
    elif num < 20:
        return term.yellow(result)
    else:
        return term.red(result)


def format_redirect_count(term, count):
    if count == 0:
        return ' '
    elif count == 1:
        return '→'
    elif count == 2:
        return term.red('⇉')
    else:
        return term.red('⇶')


def format_status(term, status, fmt):
    result = fmt.format(status)
    if status == 200:
        return term.white(result)
    else:
        return term.red(result)


def do_request(app, path, query_string=''):
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
    response_info = [None]
    def start_response(status, response_headers, exc_info=None):
        assert exc_info is None
        response_info[:] = int(status[:3]), response_headers
        def write():
            raise RuntimeError('Not Implemented')
        return write
    start = time.time()
    output = ''.join(s.decode('utf-8') for s in app(environ, start_response))
    end = time.time()
    status, headers = response_info
    return status, headers, output, end - start


def check_page(app, path, query_string=''):
    total_time = 0
    for redirect_count in range(2):
        status, headers, output, elapsed = do_request(app, path, query_string)
        total_time += elapsed
        try:
            url = dict(headers)['Location']
            _s, _n, path, query_string, _f = urlparse.urlsplit(url)
        except KeyError:
            break
    [context] = contexts


    distinct_queries = set(q['statement'] for q in queries)
    resultlines = {}
    term = Terminal()
    resultline = ''.join([
        '{0:37} '.format(path if path == '/' else ' ' * path.count('/') + path.split('/')[-1]),
        format_time(term, total_time, '{0:8.5f} '),
        format_size(term, len(output), '{0:8d} '),
        format_num_queries(term, len(queries), '{0:4d} ', len(distinct_queries)),
        format_distinct_queries(term, len(distinct_queries), '{0:3d} '),
        format_sqla_time(term, sum(q['duration'] for q in queries) * 1000, '{0:4.1f} '),
        format_redirect_count(term, redirect_count),
        format_status(term, status, '{0:3} '),
        ' ' * 9
    ])

    if 80 + len(context.url) < term.width:
        print resultline.encode('utf-8'), context.url
    else:
        print resultline.encode('utf-8')

    queries[:] = []
    context.request.db.rollback()

    if status == 200:
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
    print '---------------- URL ---------------- - time - - size - --- SQLA ---- HTTP ----'
    print '                                       s        m  k  b  num dst time      ----'
    check_page(app, '/')


add_sqla_events()

if __name__ == '__main__':
    check_pages()
