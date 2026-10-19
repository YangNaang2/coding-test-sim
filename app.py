"""코딩테스트 모의 응시 프로그램 서버.

실행: python app.py  (브라우저가 자동으로 열립니다. 종료는 이 창에서 Ctrl+C)
"""
import json
import os
import random
import socket
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import judge

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(ROOT, 'static')
DATA = os.path.join(ROOT, 'data')
STATE_PATH = os.path.join(DATA, 'state.json')
HISTORY_PATH = os.path.join(DATA, 'history.json')
PORT = int(os.environ.get('CT_PORT', '8765'))
LEVEL_NAME = {1: '쉬움', 2: '보통', 3: '어려움'}
MIME = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
        '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon'}

PROBLEMS = {}
_file_lock = threading.Lock()


def load_problems():
    PROBLEMS.clear()
    for sub in ('algo', 'sql'):
        folder = os.path.join(ROOT, 'problems', sub)
        for f in sorted(os.listdir(folder)):
            if f.endswith('.json'):
                with open(os.path.join(folder, f), encoding='utf-8') as fp:
                    p = json.load(fp)
                PROBLEMS[p['id']] = p


def summary(p):
    return {'id': p['id'], 'type': p['type'], 'title': p['title'], 'level': p['level'],
            'levelName': LEVEL_NAME[p['level']], 'tags': p.get('tags', [])}


def public(p):
    """채점용 데이터와 해설을 뺀, 문제 화면에 보여 줄 정보."""
    out = summary(p)
    out['description'] = p['description']
    if p['type'] == 'algo':
        out.update(constraints=p['constraints'], params=p['params'], returnType=p['returnType'],
                   examples=p['examples'], exampleNotes=p.get('exampleNotes', ''), timeLimit=p.get('timeLimit', 10),
                   templates=judge.templates(p), testCount=len(p['tests']))
    else:
        out.update(schema=p['schema'], sample=p['data']['sample'], sampleExpected=p['expected']['sample'],
                   ordered=p.get('ordered', True))
    return out


def clip(v, n=4000):
    s = judge.show(v)
    return s if len(s) <= n else s[:n] + ' ...(생략)'


def review(p, failed):
    out = {'solution': p['solution'], 'explanation': p.get('explanation', ''), 'edgeCases': p.get('edgeCases', [])}
    if p['type'] == 'algo':
        tests = []
        for i in failed[:30]:
            if 0 <= i < len(p['tests']):
                t = p['tests'][i]
                tests.append({'index': i, 'input': [clip(v, 1500) for v in t['input']], 'output': clip(t['output'])})
        out['failedTests'] = tests
        out['params'] = [x['name'] for x in p['params']]
    else:
        exp = p['expected']['hidden']
        out['hiddenExpected'] = {'columns': exp['columns'], 'rows': exp['rows'][:50], 'total': len(exp['rows'])}
    return out


def read_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def write_json(path, value):
    tmp = path + '.tmp'
    with _file_lock:
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False)
        os.replace(tmp, path)


def pick_exam():
    algo2 = [p for p in PROBLEMS.values() if p['type'] == 'algo' and p['level'] == 2]
    algo23 = [p for p in PROBLEMS.values() if p['type'] == 'algo' and p['level'] >= 2]
    sql = [p for p in PROBLEMS.values() if p['type'] == 'sql']
    first = random.choice(algo2)
    second = random.choice([p for p in algo23 if p['id'] != first['id']])
    return [first['id'], second['id'], random.choice(sql)['id']]


def run_algo(p, lang, code, cases, hide):
    r = judge.judge_algo(p, lang, code, cases)
    if 'compile_error' in r:
        return r
    out = []
    for c, x in zip(cases, r['results']):
        item = {'status': x['status'], 'ms': x['ms']}
        if not hide:
            item.update(input=[clip(v, 1500) for v in c['input']], expected=clip(c['output']), got=x.get('got'),
                        out=x.get('out', ''), error=x.get('error'))
        out.append(item)
    passed = sum(1 for x in out if x['status'] == 'pass')
    return {'results': out, 'passed': passed, 'total': len(out),
            'score': round(passed * 100.0 / len(out), 1) if out else 0.0}


def run_sql(p, query, dialect, submit):
    which = ('sample', 'hidden') if submit else ('sample',)
    r = judge.judge_sql(p, query, dialect, which)
    if 'error' in r:
        return {'error': r['error'], 'score': 0.0}
    s = r['sample']
    res = {'columns': s['columns'], 'rows': s['rows'][:300], 'rowCount': len(s['rows']), 'sampleOk': s['ok']}
    if submit:
        ok = all(v['ok'] for v in r.values())
        res.update(correct=ok, score=100.0 if ok else 0.0)
    return res


class Handler(BaseHTTPRequestHandler):
    server_version = 'CodingTestSim/1.0'

    def log_message(self, fmt, *args):
        pass

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(n) if n else b'{}'
        try:
            return json.loads(raw.decode('utf-8'))
        except ValueError:
            return {}

    def do_GET(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        if url.path == '/api/meta':
            return self.send_json({'languages': judge.LANGUAGES})
        if url.path == '/api/problems':
            return self.send_json([summary(p) for p in PROBLEMS.values()])
        if url.path == '/api/problem':
            p = PROBLEMS.get((q.get('id') or [''])[0])
            return self.send_json(public(p)) if p else self.send_json({'error': '문제가 없습니다.'}, 404)
        if url.path == '/api/state':
            return self.send_json(read_json(STATE_PATH, {}))
        if url.path == '/api/history':
            return self.send_json(read_json(HISTORY_PATH, []))
        if url.path == '/api/exam':
            return self.send_json({'problems': pick_exam()})
        return self.static(url.path)

    def do_POST(self):
        url = urlparse(self.path)
        data = self.body()
        if url.path == '/api/state':
            write_json(STATE_PATH, data)
            return self.send_json({'ok': True})
        if url.path == '/api/history':
            hist = read_json(HISTORY_PATH, [])
            hist.append(data)
            write_json(HISTORY_PATH, hist)
            return self.send_json({'ok': True})
        p = PROBLEMS.get(data.get('id', ''))
        if url.path in ('/api/run', '/api/submit', '/api/review') and not p:
            return self.send_json({'error': '문제가 없습니다.'}, 404)
        submit = url.path == '/api/submit'
        if url.path in ('/api/run', '/api/submit'):
            code = data.get('code', '')
            if p['type'] == 'sql':
                return self.send_json(run_sql(p, code, data.get('lang', 'mysql'), submit))
            if submit:
                return self.send_json(run_algo(p, data.get('lang', 'python'), code, p['tests'], hide=True))
            cases = list(p['examples'])
            for k, c in enumerate(data.get('custom') or []):
                inp = c.get('input', [])
                bad = len(inp) != len(p['params']) or not all(
                    judge.check_type(v, prm['type']) for v, prm in zip(inp, p['params']))
                if bad or not judge.check_type(c.get('output'), p['returnType']):
                    return self.send_json({'error': '추가한 테스트 케이스 {}의 값 형식이 매개변수·반환 타입과 맞지 않습니다.'.format(k + 1)})
                cases.append({'input': inp, 'output': c['output']})
            return self.send_json(run_algo(p, data.get('lang', 'python'), code, cases, hide=False))
        if url.path == '/api/review':
            return self.send_json(review(p, [int(i) for i in data.get('failed', []) if isinstance(i, int)]))
        self.send_json({'error': 'not found'}, 404)

    def static(self, path):
        if path in ('', '/'):
            path = '/index.html'
        full = os.path.normpath(os.path.join(STATIC, path.lstrip('/')))
        if not full.startswith(STATIC) or not os.path.isfile(full):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        with open(full, 'rb') as f:
            body = f.read()
        self.send_response(200)
        self.send_header('Content-Type', MIME.get(os.path.splitext(full)[1], 'application/octet-stream'))
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(body)


def free_port(start):
    for port in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    raise SystemExit('사용할 수 있는 포트를 찾지 못했습니다.')


def main():
    os.makedirs(DATA, exist_ok=True)
    load_problems()
    port = free_port(PORT)
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.daemon_threads = True
    url = 'http://localhost:{}/'.format(port)
    langs = ', '.join(k for k, v in judge.LANGUAGES.items() if v)
    print('코딩테스트 모의 응시 프로그램: {}'.format(url))
    print('문제 {}개 · 사용 가능한 언어: {} + SQL'.format(len(PROBLEMS), langs))
    print('종료하려면 이 창에서 Ctrl+C를 누르세요.')
    if '--no-browser' not in sys.argv:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n종료합니다.')
        server.server_close()


if __name__ == '__main__':
    main()
