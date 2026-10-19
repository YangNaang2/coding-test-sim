"""tools/specs/의 출제 명세로 problems/ 아래 문제 JSON을 만든다.

알고리즘 명세(a*.py)에는 META, SOLUTION, BRUTE, WRONG, examples(), handmade(), small(rng), large(rng)가 있다.
SQL 명세(s*.py)에는 META, SCHEMA, sample(), hidden(rng), SOLUTION, ALT, WRONG가 있다.
정답은 모두 SOLUTION을 실행해 만든다. 입출력 예는 명세에 적은 기댓값과 같은지 확인한다.
"""
import importlib.util
import json
import os
import random
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, ROOT)
import judge  # noqa: E402

SPECS = os.path.join(TOOLS, 'specs')
sys.path.insert(0, SPECS)


def load_spec(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SPECS, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def spec_names(prefix):
    return sorted(f[:-3] for f in os.listdir(SPECS) if f.startswith(prefix) and f.endswith('.py'))


def compile_solution(code):
    ns = {'__name__': 'solution'}
    exec(code, ns)
    return ns['solution']


def deep(v):
    return json.loads(json.dumps(v))


def build_algo(name):
    m = load_spec(name)
    solve = compile_solution(m.SOLUTION)
    rng = random.Random(name)
    examples = []
    for args, expected in m.examples():
        got = solve(*deep(args))
        assert judge.same(deep(expected), deep(got)), (name, 'example', args, expected, got)
        examples.append({'input': deep(args), 'output': deep(expected)})
    inputs = [deep(a) for a, _ in m.examples()]
    inputs += [deep(a) for a in m.handmade()]
    for _ in range(getattr(m, 'N_SMALL', 6)):
        inputs.append(deep(m.small(rng)))
    inputs += [deep(a) for a in m.large(random.Random(name + '-large'))]
    tests = [{'input': a, 'output': deep(solve(*deep(a)))} for a in inputs]
    for a in tests:
        for p, v in zip(m.META['params'], a['input']):
            assert judge.check_type(v, p['type']), (name, p, str(v)[:80])
    assert 15 <= len(tests) <= 25, (name, len(tests))
    prob = dict(m.META)
    prob.update(type='algo', examples=examples, tests=tests, solution=m.SOLUTION.strip())
    prob.setdefault('timeLimit', 10)
    return prob


def build_sql(name):
    m = load_spec(name)
    data = {'sample': m.sample(), 'hidden': m.hidden(random.Random(name))}
    expected = {}
    for w in ('sample', 'hidden'):
        cols, rows = judge.run_sql(m.SCHEMA, data[w], m.SOLUTION)
        expected[w] = {'columns': cols, 'rows': rows}
    prob = dict(m.META)
    prob.update(type='sql', schema=m.SCHEMA, data=data, expected=expected, solution=m.SOLUTION.strip())
    return prob


def main():
    parts = sys.argv[1:] or ['algo', 'sql']
    for prefix, builder, sub in (('a', build_algo, 'algo'), ('s', build_sql, 'sql')):
        if sub not in parts:
            continue
        outdir = os.path.join(ROOT, 'problems', sub)
        for f in os.listdir(outdir):
            if f.endswith('.json'):
                os.remove(os.path.join(outdir, f))
        for name in spec_names(prefix):
            prob = builder(name)
            path = os.path.join(outdir, prob['id'] + '.json')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(prob, f, ensure_ascii=False, separators=(',', ':'))
            n = len(prob['tests']) if sub == 'algo' else len(prob['expected']['hidden']['rows'])
            print('{:6} {:28} level={} {}={} {:.0f}KB'.format(
                prob['id'], prob['title'], prob['level'], 'tests' if sub == 'algo' else 'rows', n,
                os.path.getsize(path) / 1024))


if __name__ == '__main__':
    main()
