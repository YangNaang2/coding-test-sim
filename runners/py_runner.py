"""Python 하네스: solution.py를 테스트 케이스마다 새 네임스페이스에서 실행하고 결과를 한 줄 JSON으로 보낸다.

사용법: python py_runner.py <코드 경로> <케이스 JSON 경로> <시작 인덱스>
"""
import io
import json
import sys
import time
import traceback

MARK = '@@CT@@'
OUT_LIMIT = 20000


class Capture(io.TextIOBase):
    """print 출력을 모으되 OUT_LIMIT 글자까지만 보관한다."""

    def __init__(self):
        self.parts = []
        self.size = 0
        self.cut = False

    def writable(self):
        return True

    def write(self, s):
        if self.size < OUT_LIMIT:
            self.parts.append(s[:OUT_LIMIT - self.size])
            if len(s) > OUT_LIMIT - self.size:
                self.cut = True
        else:
            self.cut = True
        self.size += len(s)
        return len(s)

    def text(self):
        return ''.join(self.parts) + ('\n...(출력이 너무 길어 생략)' if self.cut else '')


def user_traceback(exc):
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename == 'solution.py']
    lines = ['Traceback (most recent call last):\n']
    lines += traceback.format_list(frames)
    lines += traceback.format_exception_only(type(exc), exc)
    return ''.join(lines)


def main():
    code_path, cases_path, start = sys.argv[1], sys.argv[2], int(sys.argv[3])
    real = sys.stdout

    def send(obj):
        real.write(MARK + json.dumps(obj, ensure_ascii=False) + '\n')
        real.flush()

    with open(code_path, encoding='utf-8') as f:
        src = f.read()
    try:
        code = compile(src, 'solution.py', 'exec')
    except SyntaxError as e:
        send({'t': 'compile', 'err': ''.join(traceback.format_exception_only(type(e), e))})
        return
    with open(cases_path, encoding='utf-8') as f:
        cases = json.load(f)['cases']

    for i in range(start, len(cases)):
        args = cases[i]
        cap = Capture()
        send({'t': 'start', 'i': i})
        sys.stdout = cap
        t0 = time.perf_counter()
        try:
            ns = {'__name__': 'solution', '__builtins__': __builtins__}
            exec(code, ns)
            fn = ns.get('solution')
            if not callable(fn):
                raise NameError("solution 함수가 정의되어 있지 않습니다.")
            ret = fn(*args)
            ms = (time.perf_counter() - t0) * 1000
            sys.stdout = real
            try:
                json.dumps(ret, ensure_ascii=False, allow_nan=False)
            except (TypeError, ValueError):
                send({'t': 'res', 'i': i, 'ok': False, 'kind': 'type', 'ms': ms, 'out': cap.text(),
                      'err': '반환값을 비교할 수 없는 형식입니다: ' + type(ret).__name__})
                continue
            send({'t': 'res', 'i': i, 'ok': True, 'ret': ret, 'ms': ms, 'out': cap.text()})
        except BaseException as e:  # SystemExit, RecursionError 등도 런타임 에러로 처리
            ms = (time.perf_counter() - t0) * 1000
            sys.stdout = real
            send({'t': 'res', 'i': i, 'ok': False, 'kind': 'error', 'ms': ms, 'out': cap.text(),
                  'err': user_traceback(e)})


if __name__ == '__main__':
    main()
