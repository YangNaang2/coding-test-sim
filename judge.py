"""채점기: 언어별 하네스로 solution()을 실행해 반환값을 비교하고, SQL은 SQLite로 실행해 결과 표를 비교한다."""
import datetime as dt
import json
import math
import os
import queue
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
RUNNERS = os.path.join(ROOT, 'runners')
MARK = '@@CT@@'
STARTUP_LIMIT = 20.0      # 프로세스 시작·케이스 사이 대기 한도(초)
COMPILE_LIMIT = 60.0
SQL_LIMIT = 5.0
DISPLAY_LIMIT = 3000      # 화면에 보여 줄 값의 최대 글자 수

_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0


# ---------------------------------------------------------------- 언어

def detect_languages():
    return {
        'python': True,
        'javascript': shutil.which('node') is not None,
        'java': shutil.which('javac') is not None and shutil.which('java') is not None,
        'cpp': shutil.which('g++') is not None,
    }


LANGUAGES = detect_languages()

PY_DEFAULT = {'int': '0', 'long': '0', 'double': '0.0', 'bool': 'True', 'string': "''"}
JS_DEFAULT = {'int': '0', 'long': '0', 'double': '0', 'bool': 'true', 'string': "''"}
JAVA_TYPE = {'int': 'int', 'long': 'long', 'double': 'double', 'bool': 'boolean', 'string': 'String'}
JAVA_DEFAULT = {'int': '0', 'long': '0', 'double': '0', 'bool': 'true', 'string': '""'}
CPP_TYPE = {'int': 'int', 'long': 'long long', 'double': 'double', 'bool': 'bool', 'string': 'string'}
CPP_DEFAULT = {'int': '0', 'long': '0', 'double': '0', 'bool': 'true', 'string': '""'}


def _base(t):
    return t.replace('[]', ''), t.count('[]')


def java_type(t):
    b, d = _base(t)
    return JAVA_TYPE[b] + '[]' * d


def cpp_type(t):
    b, d = _base(t)
    s = CPP_TYPE[b]
    for _ in range(d):
        s = 'vector<' + s + '>'
    return s


def templates(problem):
    names = [p['name'] for p in problem['params']]
    ret = problem['returnType']
    b, d = _base(ret)
    py = 'def solution({}):\n    answer = {}\n    return answer'.format(
        ', '.join(names), '[]' if d else PY_DEFAULT[b])
    js = 'function solution({}) {{\n    var answer = {};\n    return answer;\n}}'.format(
        ', '.join(names), '[]' if d else JS_DEFAULT[b])
    jparams = ', '.join('{} {}'.format(java_type(p['type']), p['name']) for p in problem['params'])
    java = ('class Solution {{\n    public {r} solution({p}) {{\n        {r} answer = {v};\n'
            '        return answer;\n    }}\n}}').format(r=java_type(ret), p=jparams, v='{}' if d else JAVA_DEFAULT[b])
    cparams = ', '.join('{} {}'.format(cpp_type(p['type']), p['name']) for p in problem['params'])
    cdecl = '{} answer;'.format(cpp_type(ret)) if d else '{} answer = {};'.format(cpp_type(ret), CPP_DEFAULT[b])
    cpp = ('#include <string>\n#include <vector>\n\nusing namespace std;\n\n{r} solution({p}) {{\n    {decl}\n'
           '    return answer;\n}}').format(r=cpp_type(ret), p=cparams, decl=cdecl)
    return {'python': py, 'javascript': js, 'java': java, 'cpp': cpp}


# ---------------------------------------------------------------- 값 검사·비교

def check_type(v, t):
    """사용자가 추가한 테스트 케이스 값이 선언된 타입과 맞는지 검사한다."""
    b, d = _base(t)
    if d:
        return isinstance(v, list) and all(check_type(x, t[:-2]) for x in v)
    if b in ('int', 'long'):
        return isinstance(v, int) and not isinstance(v, bool)
    if b == 'double':
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    if b == 'bool':
        return isinstance(v, bool)
    if b == 'string':
        return isinstance(v, str)
    return False


def same(exp, got):
    if isinstance(exp, bool) or isinstance(got, bool):
        return isinstance(exp, bool) and isinstance(got, bool) and exp == got
    if isinstance(exp, float):
        return isinstance(got, (int, float)) and abs(exp - got) <= 1e-6 * max(1.0, abs(exp))
    if isinstance(exp, int):
        return isinstance(got, int) and exp == got
    if isinstance(exp, list):
        return isinstance(got, list) and len(exp) == len(got) and all(same(a, b) for a, b in zip(exp, got))
    return type(exp) == type(got) and exp == got


def show(v):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= DISPLAY_LIMIT else s[:DISPLAY_LIMIT] + ' ...(생략)'


# ---------------------------------------------------------------- 실행

def _spawn(cmd, cwd):
    return subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, creationflags=_NO_WINDOW)


def _kill(proc):
    try:
        proc.kill()
    except OSError:
        pass
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass


def _pump(stream, q):
    for raw in iter(stream.readline, b''):
        line = raw.decode('utf-8', 'replace').rstrip('\r\n')
        if line.startswith(MARK):
            try:
                q.put(json.loads(line[len(MARK):]))
            except ValueError:
                pass
    q.put(None)


def _drain(stream, buf):
    total = 0
    for raw in iter(lambda: stream.read(4096), b''):
        if total < 20000:
            buf.append(raw.decode('utf-8', 'replace'))
        total += len(raw)


def _tail(s, n=4000):
    s = s.strip()
    return s if len(s) <= n else '...\n' + s[-n:]


def _run_cases(cmd_for, cwd, n, limit):
    """케이스를 한 프로세스에서 차례로 실행하고, 시간 초과나 비정상 종료가 나면 다음 케이스부터 다시 띄운다."""
    results = [None] * n
    i = 0
    while i < n:
        proc = _spawn(cmd_for(i), cwd)
        q = queue.Queue()
        threading.Thread(target=_pump, args=(proc.stdout, q), daemon=True).start()
        errbuf = []
        err_thread = threading.Thread(target=_drain, args=(proc.stderr, errbuf), daemon=True)
        err_thread.start()
        cur = None
        deadline = time.monotonic() + STARTUP_LIMIT
        while True:
            try:
                msg = q.get(timeout=max(0.0, deadline - time.monotonic()))
            except queue.Empty:
                _kill(proc)
                k = cur if cur is not None else i
                results[k] = {'status': 'timeout'}
                i = k + 1
                break
            if msg is None:
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    _kill(proc)
                err_thread.join(1)
                if cur is not None:
                    err = _tail(''.join(errbuf)) or '프로그램이 비정상 종료되었습니다. (exit code {})'.format(proc.returncode)
                    results[cur] = {'status': 'error', 'error': err}
                    i = cur + 1
                elif i < n:
                    results[i] = {'status': 'error', 'error': _tail(''.join(errbuf)) or '실행기를 시작하지 못했습니다.'}
                    i += 1
                break
            if msg['t'] == 'compile':
                _kill(proc)
                return {'compile_error': msg['err']}
            if msg['t'] == 'start':
                cur = msg['i']
                deadline = time.monotonic() + limit
            elif msg['t'] == 'res':
                results[msg['i']] = msg
                i = msg['i'] + 1
                cur = None
                deadline = time.monotonic() + STARTUP_LIMIT
    return {'results': results}


def _clean_compile(text, work):
    return _tail(text.replace(work + os.sep, '').replace(work, ''))


def _prepare(lang, code, problem, work):
    """언어별로 코드를 저장·컴파일하고, 시작 인덱스를 받아 실행 명령을 만드는 함수를 돌려준다."""
    cases_path = os.path.join(work, 'cases.json')
    if lang == 'python':
        path = os.path.join(work, 'solution.py')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        runner = os.path.join(RUNNERS, 'py_runner.py')
        return lambda s: [sys.executable, '-X', 'utf8', '-u', runner, path, cases_path, str(s)], None
    if lang == 'javascript':
        path = os.path.join(work, 'solution.js')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        runner = os.path.join(RUNNERS, 'js_runner.js')
        return lambda s: ['node', runner, path, cases_path, str(s)], None
    if lang == 'java':
        with open(os.path.join(work, 'Solution.java'), 'w', encoding='utf-8') as f:
            f.write(code)
        shutil.copy(os.path.join(RUNNERS, 'Main.java'), work)
        try:
            r = subprocess.run(['javac', '-encoding', 'UTF-8', '-nowarn', '-d', work, 'Main.java', 'Solution.java'],
                               cwd=work, capture_output=True, timeout=COMPILE_LIMIT, creationflags=_NO_WINDOW)
        except subprocess.TimeoutExpired:
            return None, '컴파일 시간이 초과되었습니다.'
        if r.returncode != 0:
            return None, _clean_compile((r.stdout + r.stderr).decode('utf-8', 'replace'), work)
        return lambda s: ['java', '-Xss256m', '-Dfile.encoding=UTF-8', '-cp', work, 'Main', cases_path, str(s)], None
    if lang == 'cpp':
        with open(os.path.join(work, 'solution.cpp'), 'w', encoding='utf-8') as f:
            f.write(code)
        shutil.copy(os.path.join(RUNNERS, 'ct_head.hpp'), work)
        with open(os.path.join(work, 'main.cpp'), 'w', encoding='utf-8') as f:
            f.write(_cpp_main(problem))
        exe = os.path.join(work, 'main.exe' if os.name == 'nt' else 'main')
        cmd = ['g++', '-std=c++17', '-O2', '-o', exe, 'main.cpp']
        if os.name == 'nt':
            cmd.append('-Wl,--stack,268435456')
        try:
            r = subprocess.run(cmd, cwd=work, capture_output=True, timeout=COMPILE_LIMIT, creationflags=_NO_WINDOW)
        except subprocess.TimeoutExpired:
            return None, '컴파일 시간이 초과되었습니다.'
        if r.returncode != 0:
            return None, _clean_compile((r.stdout + r.stderr).decode('utf-8', 'replace'), work)
        return lambda s: [exe, cases_path, str(s)], None
    return None, '지원하지 않는 언어입니다: ' + lang


def _cpp_main(problem):
    decls = []
    for k, p in enumerate(problem['params']):
        decls.append('        auto a{k} = ctj::C<{t}>::f(args.a[{k}]);'.format(k=k, t=cpp_type(p['type'])))
    call = ', '.join('a{}'.format(k) for k in range(len(problem['params'])))
    return '''#include "ct_head.hpp"
#include "solution.cpp"

int main(int argc, char** argv) {
    string text = ctj::readfile(argv[1]);
    int start = atoi(argv[2]);
    ctj::J data = ctj::Parser(text).value();
    const ctj::J& cases = ctj::get(data, "cases");
    for (int i = start; i < (int)cases.a.size(); i++) {
        const ctj::J& args = cases.a[i];
%s
        ostringstream cap;
        streambuf* old = cout.rdbuf(cap.rdbuf());
        ctj::send("{\\"t\\":\\"start\\",\\"i\\":" + to_string(i) + "}");
        auto t0 = chrono::steady_clock::now();
        try {
            auto r = solution(%s);
            double ms = chrono::duration<double, milli>(chrono::steady_clock::now() - t0).count();
            cout.rdbuf(old);
            string o;
            ctj::out(o, r);
            ctj::send("{\\"t\\":\\"res\\",\\"i\\":" + to_string(i) + ",\\"ok\\":true,\\"ret\\":" + o +
                      ",\\"ms\\":" + to_string(ms) + ",\\"out\\":" + ctj::captured(cap) + "}");
        } catch (exception& e) {
            cout.rdbuf(old);
            string m;
            ctj::esc(m, string("예외 발생: ") + e.what());
            ctj::send("{\\"t\\":\\"res\\",\\"i\\":" + to_string(i) + ",\\"ok\\":false,\\"kind\\":\\"error\\",\\"ms\\":0,\\"out\\":" +
                      ctj::captured(cap) + ",\\"err\\":" + m + "}");
        } catch (...) {
            cout.rdbuf(old);
            ctj::send("{\\"t\\":\\"res\\",\\"i\\":" + to_string(i) + ",\\"ok\\":false,\\"kind\\":\\"error\\",\\"ms\\":0,\\"out\\":" +
                      ctj::captured(cap) + ",\\"err\\":\\"알 수 없는 예외가 발생했습니다.\\"}");
        }
    }
    return 0;
}
''' % ('\n'.join(decls), call)


_slots = threading.Semaphore(2)


def judge_algo(problem, lang, code, cases, limit=None):
    """cases: [{'input': [...], 'output': ...}] → 컴파일 오류 또는 케이스별 결과."""
    if lang not in LANGUAGES or not LANGUAGES[lang]:
        return {'compile_error': '이 PC에서 사용할 수 없는 언어입니다: ' + lang}
    limit = limit or problem.get('timeLimit', 10)
    with _slots:
        work = tempfile.mkdtemp(prefix='ct_')
        try:
            with open(os.path.join(work, 'cases.json'), 'w', encoding='utf-8') as f:
                json.dump({'cases': [c['input'] for c in cases]}, f, ensure_ascii=False)
            cmd_for, err = _prepare(lang, code, problem, work)
            if err:
                return {'compile_error': err}
            raw = _run_cases(cmd_for, work, len(cases), limit)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    if 'compile_error' in raw:
        return raw
    out = []
    for c, r in zip(cases, raw['results']):
        item = {'ms': round(r.get('ms', 0), 2) if r else 0,
                'out': (r or {}).get('out', '').replace('\r\n', '\n')}
        if r is None:
            item.update(status='error', error='결과를 받지 못했습니다.')
        elif r.get('status') == 'timeout':
            item.update(status='timeout')
        elif r.get('status') == 'error':
            item.update(status='error', error=r['error'])
        elif not r['ok']:
            item.update(status='error' if r['kind'] == 'error' else 'fail', error=r['err'])
        else:
            item['status'] = 'pass' if same(c['output'], r['ret']) else 'fail'
            item['got'] = show(r['ret'])
        out.append(item)
    return {'results': out}


# ---------------------------------------------------------------- SQL

def _num(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _parse_dt(s):
    if s is None:
        return None
    s = str(s).strip()
    for fmt, n in (('%Y-%m-%d %H:%M:%S', 19), ('%Y-%m-%d %H:%M', 16), ('%Y-%m-%d', 10), ('%Y%m%d', 8)):
        try:
            return dt.datetime.strptime(s[:n], fmt)
        except ValueError:
            continue
    return None


_MYSQL_FMT = {'%Y': '%Y', '%y': '%y', '%m': '%m', '%c': '{c}', '%d': '%d', '%e': '{e}', '%H': '%H',
              '%h': '%I', '%i': '%M', '%s': '%S', '%S': '%S', '%p': '%p', '%M': '%B', '%b': '%b', '%W': '%A', '%a': '%a'}


def f_date_format(d, fmt):
    t = _parse_dt(d)
    if t is None or fmt is None:
        return None
    out, k = [], 0
    while k < len(fmt):
        tok = fmt[k:k + 2]
        if tok in _MYSQL_FMT:
            spec = _MYSQL_FMT[tok]
            out.append(str(t.month) if spec == '{c}' else str(t.day) if spec == '{e}' else t.strftime(spec))
            k += 2
        else:
            out.append(fmt[k])
            k += 1
    return ''.join(out)


_ORA_TOKENS = [('YYYY', '%Y'), ('HH24', '%H'), ('HH12', '%I'), ('HH', '%I'), ('MI', '%M'), ('SS', '%S'),
               ('MM', '%m'), ('DD', '%d'), ('YY', '%y'), ('AM', '%p'), ('PM', '%p')]


def _ora_fmt(fmt):
    out, k, up = [], 0, fmt.upper()
    while k < len(fmt):
        for tok, spec in _ORA_TOKENS:
            if up.startswith(tok, k):
                out.append(spec)
                k += len(tok)
                break
        else:
            out.append(fmt[k].replace('%', '%%'))
            k += 1
    return ''.join(out)


def f_to_char(v, fmt=None):
    if v is None:
        return None
    if fmt is None:
        return str(v)
    t = _parse_dt(v)
    if t is None:
        return str(v)
    return t.strftime(_ora_fmt(fmt))


def f_to_date(s, fmt=None):
    if s is None:
        return None
    t = None
    if fmt:
        try:
            t = dt.datetime.strptime(str(s), _ora_fmt(fmt))
        except ValueError:
            t = None
    t = t or _parse_dt(s)
    if t is None:
        return None
    return t.strftime('%Y-%m-%d %H:%M:%S') if (t.hour or t.minute or t.second) else t.strftime('%Y-%m-%d')


def _part(attr):
    def f(d):
        t = _parse_dt(d)
        return getattr(t, attr) if t else None
    return f


def f_datediff(a, b):
    ta, tb = _parse_dt(a), _parse_dt(b)
    if ta is None or tb is None:
        return None
    return (ta.date() - tb.date()).days


def f_concat(*args):
    if any(a is None for a in args):
        return None
    return ''.join(str(int(a)) if isinstance(a, float) and a.is_integer() else str(a) for a in args)


def f_decode(*args):
    if len(args) < 3:
        return None
    expr, rest = args[0], list(args[1:])
    while len(rest) >= 2:
        s, r = rest.pop(0), rest.pop(0)
        if s == expr or (s is None and expr is None):
            return r
    return rest[0] if rest else None


def f_trunc(x, d=0):
    if x is None:
        return None
    if isinstance(x, str):
        t = _parse_dt(x)
        return t.strftime('%Y-%m-%d') if t else None
    m = 10 ** int(d)
    return math.trunc(x * m) / m if d else math.trunc(x)


def f_lpad(s, n, p=' '):
    if s is None or n is None:
        return None
    s, n = str(s), int(n)
    if len(s) >= n:
        return s[:n]
    return ((p * n)[:n - len(s)] + s) if p else s


def f_rpad(s, n, p=' '):
    if s is None or n is None:
        return None
    s, n = str(s), int(n)
    if len(s) >= n:
        return s[:n]
    return (s + (p * n))[:n] if p else s


def _connect():
    con = sqlite3.connect(':memory:')
    fns = [
        ('IF', 3, lambda c, a, b: a if c else b),
        ('NVL', 2, lambda a, b: b if a is None else a),
        ('NVL2', 3, lambda a, b, c: c if a is None else b),
        ('DECODE', -1, f_decode),
        ('DATE_FORMAT', 2, f_date_format),
        ('TO_CHAR', 1, f_to_char), ('TO_CHAR', 2, f_to_char),
        ('TO_DATE', 1, f_to_date), ('TO_DATE', 2, f_to_date),
        ('YEAR', 1, _part('year')), ('MONTH', 1, _part('month')), ('DAY', 1, _part('day')),
        ('DAYOFMONTH', 1, _part('day')), ('HOUR', 1, _part('hour')), ('MINUTE', 1, _part('minute')),
        ('SECOND', 1, _part('second')),
        ('DATEDIFF', 2, f_datediff),
        ('CONCAT', -1, f_concat),
        ('LEFT', 2, lambda s, n: None if s is None else str(s)[:int(n)]),
        ('RIGHT', 2, lambda s, n: None if s is None else (str(s)[-int(n):] if int(n) > 0 else '')),
        ('LPAD', 2, f_lpad), ('LPAD', 3, f_lpad), ('RPAD', 2, f_rpad), ('RPAD', 3, f_rpad),
        ('TRUNCATE', 2, f_trunc), ('TRUNC', 1, f_trunc), ('TRUNC', 2, f_trunc),
        ('MOD', 2, lambda a, b: None if a is None or not b else a - b * math.trunc(a / b)),
        ('FLOOR', 1, lambda x: None if x is None else math.floor(x)),
        ('CEIL', 1, lambda x: None if x is None else math.ceil(x)),
        ('CEILING', 1, lambda x: None if x is None else math.ceil(x)),
        ('POWER', 2, lambda a, b: None if a is None or b is None else a ** b),
        ('SQRT', 1, lambda x: None if x is None or x < 0 else math.sqrt(x)),
        ('CHAR_LENGTH', 1, lambda s: None if s is None else len(str(s))),
        ('SUBSTRING', 2, lambda s, a: None if s is None else _substr(s, a)),
        ('SUBSTRING', 3, lambda s, a, n: None if s is None else _substr(s, a, n)),
    ]
    for name, n, fn in fns:
        con.create_function(name, n, fn, deterministic=True)
    con.execute('CREATE TABLE DUAL (DUMMY TEXT)')
    con.execute("INSERT INTO DUAL VALUES ('X')")
    return con


def _substr(s, a, n=None):
    s, a = str(s), int(a)
    st = a - 1 if a > 0 else len(s) + a if a < 0 else 0
    return s[st:] if n is None else s[st:st + int(n)]


def _create(con, schema, data):
    for t in schema:
        cols = ', '.join('{} {}{}'.format(c['name'], c['type'], '' if c.get('nullable') else ' NOT NULL')
                         for c in t['columns'])
        con.execute('CREATE TABLE {} ({})'.format(t['name'], cols))
        rows = data.get(t['name'], [])
        if rows:
            con.executemany('INSERT INTO {} VALUES ({})'.format(t['name'], ', '.join('?' * len(t['columns']))), rows)


_COMMENT = re.compile(r'--[^\n]*|/\*.*?\*/', re.S)


class SqlError(Exception):
    pass


def prepare_query(q, dialect):
    body = _COMMENT.sub(' ', q).strip()
    while body.endswith(';'):
        body = body[:-1].rstrip()
    if not body:
        raise SqlError('실행할 SQL을 입력하세요.')
    if ';' in re.sub(r"'(?:[^']|'')*'", "''", body):
        raise SqlError('SQL 문은 하나만 실행할 수 있습니다.')
    if not re.match(r'(?is)^\s*(select|with)\b', body):
        raise SqlError('SELECT(또는 WITH로 시작하는) 조회문만 실행할 수 있습니다.')
    if dialect == 'oracle':
        body = re.sub(r'(?i)\bFETCH\s+(?:FIRST|NEXT)\s+(\d+)\s+ROWS?\s+ONLY\b', r'LIMIT \1', body)
    return body


def run_sql(schema, data, query, dialect='mysql', limit=SQL_LIMIT):
    body = prepare_query(query, dialect)
    con = _connect()
    try:
        _create(con, schema, data)
        deadline = time.monotonic() + limit
        con.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 20000)
        try:
            cur = con.execute(body)
            cols = [d[0] for d in cur.description or []]
            rows = [list(r) for r in cur.fetchall()]
        except sqlite3.OperationalError as e:
            if 'interrupted' in str(e):
                raise SqlError('실행 시간이 초과되었습니다 ({}초).'.format(int(limit)))
            raise SqlError(_ko_sql_error(str(e)))
        except sqlite3.Error as e:
            raise SqlError(_ko_sql_error(str(e)))
        return cols, rows
    finally:
        con.close()


def _ko_sql_error(msg):
    m = re.match(r'no such column: (.+)', msg)
    if m:
        return '존재하지 않는 컬럼입니다: {}  ({})'.format(m.group(1), msg)
    m = re.match(r'no such table: (.+)', msg)
    if m:
        return '존재하지 않는 테이블입니다: {}  ({})'.format(m.group(1), msg)
    m = re.match(r'no such function: (.+)', msg)
    if m:
        return '이 연습 환경에서 지원하지 않는 함수입니다: {}  ({})'.format(m.group(1), msg)
    if 'syntax error' in msg:
        return 'SQL 문법 오류입니다. ({})'.format(msg)
    return msg


def _norm(v):
    if isinstance(v, bool):
        return ('n', float(v))
    if isinstance(v, (int, float)):
        return ('n', round(float(v), 6))
    if v is None:
        return ('z', '')
    return ('s', str(v))


def same_table(exp_rows, got_rows, ordered):
    if len(exp_rows) != len(got_rows):
        return False
    if any(len(a) != len(b) for a, b in zip(exp_rows, got_rows)):
        return False
    a = [tuple(_norm(v) for v in r) for r in exp_rows]
    b = [tuple(_norm(v) for v in r) for r in got_rows]
    if not ordered:
        a, b = sorted(a), sorted(b)
    return a == b


def judge_sql(problem, query, dialect, which=('sample', 'hidden')):
    """각 데이터셋에서 결과가 기댓값과 같은지 확인한다."""
    out = {}
    for w in which:
        exp = problem['expected'][w]
        try:
            cols, rows = run_sql(problem['schema'], problem['data'][w], query, dialect)
        except SqlError as e:
            return {'error': str(e)}
        if exp['columns'] and len(cols) != len(exp['columns']):
            out[w] = {'ok': False, 'columns': cols, 'rows': rows}
            continue
        out[w] = {'ok': same_table(exp['rows'], rows, problem.get('ordered', True)), 'columns': cols, 'rows': rows}
    return out
