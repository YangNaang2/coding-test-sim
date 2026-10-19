"""문제 은행 전체 검증.

1. 모범 답안이 실제 채점기(Python 하네스)로 입출력 예와 정확성 테스트를 100% 통과하는지
2. 작은 무작위 입력 200개에서 모범 답안과 완전 탐색 풀이의 결과가 같은지
3. 일부러 틀린 풀이가 채점기에서 실제로 실패하는지
4. SQL 모범 답안·다른 방식의 정답이 기댓값과 같고, 흔한 오답 쿼리가 실패하는지
5. 무한 루프·예외·잘못된 반환 타입이 각각 시간 초과·런타임 에러·실패로 판정되는지
6. JavaScript·Java 하네스로 실제 문제를 풀었을 때 통과하는지

사용법: python tools/verify.py [algo|sql|harness ...]
"""
import json
import os
import random
import sys
import time

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, ROOT)
sys.path.insert(0, TOOLS)
import judge  # noqa: E402
from build import compile_solution, deep, load_spec, spec_names  # noqa: E402

ROWS = []


def report(kind, pid, check, ok, detail=''):
    ROWS.append((kind, pid, check, ok, detail))
    mark = 'OK' if ok else ('SKIP' if ok is None else 'FAIL')
    print('{:4} {:5} {:44} {:4} {}'.format(kind, pid, check, mark, detail), flush=True)


def load_problem(sub, pid):
    with open(os.path.join(ROOT, 'problems', sub, pid + '.json'), encoding='utf-8') as f:
        return json.load(f)


def all_cases(p):
    return p['examples'] + p['tests']


def verify_algo():
    for name in spec_names('a'):
        m = load_spec(name)
        p = load_problem('algo', m.META['id'])
        pid = p['id']
        t = time.time()
        r = judge.judge_algo(p, 'python', p['solution'], all_cases(p))
        bad = [k for k, x in enumerate(r.get('results', [])) if x['status'] != 'pass']
        slow = max((x['ms'] for x in r.get('results', [])), default=0)
        report('algo', pid, '모범 답안 전체 통과 ({}개)'.format(len(all_cases(p))),
               'results' in r and not bad, '최대 {:.0f}ms, 총 {:.1f}s {}'.format(slow, time.time() - t, bad or ''))

        solve, brute = compile_solution(m.SOLUTION), compile_solution(m.BRUTE)
        rng = random.Random('verify-' + name)
        diff = 0
        for _ in range(200):
            args = deep(m.small(rng))
            if not judge.same(deep(brute(*deep(args))), deep(solve(*deep(args)))):
                diff += 1
                if diff == 1:
                    print('   mismatch:', str(args)[:200])
        report('algo', pid, '완전 탐색과 교차 검증 200회', diff == 0, '불일치 {}'.format(diff))

        for wname, code in m.WRONG.items():
            r = judge.judge_algo(p, 'python', code, p['tests'])
            if 'compile_error' in r:
                report('algo', pid, '오답 실패 확인: ' + wname, False, 'compile error')
                continue
            st = [x['status'] for x in r['results']]
            failed = [s for s in st if s != 'pass']
            summary = {s: st.count(s) for s in set(failed)}
            report('algo', pid, '오답 실패 확인: ' + wname, bool(failed),
                   '{}/{} 실패 {}'.format(len(failed), len(st), summary))


def verify_sql():
    for name in spec_names('s'):
        m = load_spec(name)
        p = load_problem('sql', m.META['id'])
        pid = p['id']
        r = judge.judge_sql(p, p['solution'], 'mysql')
        report('sql', pid, '모범 답안 일치(예시·채점 데이터)', 'error' not in r and all(v['ok'] for v in r.values()),
               '채점 데이터 {}행'.format(len(p['expected']['hidden']['rows'])))
        for k, alt in enumerate(m.ALT):
            dialect = 'oracle' if 'FETCH FIRST' in alt.upper() or 'NVL' in alt.upper() else 'mysql'
            r = judge.judge_sql(p, alt, dialect)
            report('sql', pid, '다른 정답 쿼리 #{} 통과 ({})'.format(k + 1, dialect),
                   'error' not in r and all(v['ok'] for v in r.values()), r.get('error', ''))
        for wname, q in m.WRONG.items():
            r = judge.judge_sql(p, q, 'mysql')
            ok = 'error' in r or not all(v['ok'] for v in r.values())
            where = r.get('error') or ', '.join(w for w, v in r.items() if not v['ok'])
            report('sql', pid, '오답 실패 확인: ' + wname, ok, where)


HARNESS_PROBLEM = {'params': [{'name': 'a', 'type': 'int[]'}, {'name': 'k', 'type': 'int'}],
                   'returnType': 'int', 'timeLimit': 2}
HARNESS_CASES = [{'input': [[1, 2, 3], 1], 'output': 6}, {'input': [[1], 0], 'output': 1},
                 {'input': [[1], 5], 'output': 1}, {'input': [[1], 7], 'output': 1}]
HARNESS_CODE = {
    'python': 'def solution(a, k):\n    if k == 0:\n        while True: pass\n    if k == 5:\n        raise ValueError("x")\n'
              '    if k == 7:\n        return "wrong type"\n    return sum(a)',
    'javascript': 'function solution(a, k) {\n  if (k === 0) while (true) {}\n  if (k === 5) throw new Error("x");\n'
                  '  if (k === 7) return "wrong type";\n  return a.reduce((s, x) => s + x, 0);\n}',
    'java': 'class Solution {\n  public int solution(int[] a, int k) {\n    if (k == 0) while (true) {}\n'
            '    if (k == 5) throw new RuntimeException("x");\n    int s = 0;\n    for (int x : a) s += x;\n'
            '    return k == 7 ? s + 1 : s;\n  }\n}',
    'cpp': '#include <vector>\n#include <stdexcept>\nusing namespace std;\nint solution(vector<int> a, int k) {\n'
           '  if (k == 0) while (true) {}\n  if (k == 5) throw runtime_error("x");\n  int s = 0;\n  for (int x : a) s += x;\n'
           '  return k == 7 ? s + 1 : s;\n}',
}

JS_A12 = '''function solution(n, balances, links) {
  const p = Array.from({length: n + 1}, (_, i) => i);
  const find = x => { while (p[x] !== x) { p[x] = p[p[x]]; x = p[x]; } return x; };
  for (const [a, b] of links) { const ra = find(a), rb = find(b); if (ra !== rb) p[ra] = rb; }
  const sum = new Map();
  for (let i = 1; i <= n; i++) { const r = find(i); sum.set(r, (sum.get(r) || 0) + balances[i - 1]); }
  return [...sum.values()].sort((x, y) => y - x);
}'''

JAVA_A12 = '''import java.util.*;
class Solution {
    int[] p;
    int find(int x) { while (p[x] != x) { p[x] = p[p[x]]; x = p[x]; } return x; }
    public long[] solution(int n, int[] balances, int[][] links) {
        p = new int[n + 1];
        for (int i = 0; i <= n; i++) p[i] = i;
        for (int[] l : links) { int a = find(l[0]), b = find(l[1]); if (a != b) p[a] = b; }
        Map<Integer, Long> sum = new HashMap<>();
        for (int i = 1; i <= n; i++) sum.merge(find(i), (long) balances[i - 1], Long::sum);
        long[] ans = sum.values().stream().mapToLong(Long::longValue).toArray();
        Arrays.sort(ans);
        for (int i = 0, j = ans.length - 1; i < j; i++, j--) { long t = ans[i]; ans[i] = ans[j]; ans[j] = t; }
        return ans;
    }
}'''

JAVA_A07 = '''import java.util.*;
class Solution {
    public int[] solution(String[] info, String[] queries) {
        Map<String, List<Integer>> t = new HashMap<>();
        for (String line : info) {
            String[] s = line.split(" ");
            int price = Integer.parseInt(s[3]);
            for (int mask = 0; mask < 8; mask++) {
                String key = ((mask & 1) > 0 ? "-" : s[0]) + " " + ((mask & 2) > 0 ? "-" : s[1]) + " " + ((mask & 4) > 0 ? "-" : s[2]);
                t.computeIfAbsent(key, k -> new ArrayList<>()).add(price);
            }
        }
        for (List<Integer> v : t.values()) Collections.sort(v);
        int[] ans = new int[queries.length];
        for (int i = 0; i < queries.length; i++) {
            String[] q = queries[i].split(" ");
            int lo = Integer.parseInt(q[3]), hi = Integer.parseInt(q[4]);
            List<Integer> v = t.getOrDefault(q[0] + " " + q[1] + " " + q[2], Collections.emptyList());
            ans[i] = lo > hi ? 0 : Math.max(0, upper(v, hi) - lower(v, lo));
        }
        return ans;
    }
    int lower(List<Integer> v, int x) { int l = 0, r = v.size(); while (l < r) { int m = (l + r) / 2; if (v.get(m) < x) l = m + 1; else r = m; } return l; }
    int upper(List<Integer> v, int x) { int l = 0, r = v.size(); while (l < r) { int m = (l + r) / 2; if (v.get(m) <= x) l = m + 1; else r = m; } return l; }
}'''

JS_A05 = '''const W = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3];
function solution(accounts) {
  const seen = new Set(), out = [];
  for (const s of accounts) {
    let d = null;
    if (s.length === 11) d = s;
    else if (s.length === 13 && s[3] === '-' && s[6] === '-') d = s.slice(0, 3) + s.slice(4, 6) + s.slice(7);
    if (d === null || !/^[0-9]{11}$/.test(d) || d.startsWith('000')) continue;
    let t = 0;
    for (let i = 0; i < 10; i++) t += Number(d[i]) * W[i];
    if (Number(d[10]) !== (11 - t % 11) % 10 || seen.has(d)) continue;
    seen.add(d);
    out.push(d.slice(0, 3) + '-' + d.slice(3, 5) + '-' + d.slice(5));
  }
  return out;
}'''


def verify_harness():
    expect = ['pass', 'timeout', 'error', 'fail']
    for lang, code in HARNESS_CODE.items():
        if not judge.LANGUAGES.get(lang):
            report('run', lang, '무한 루프/예외/잘못된 반환 판정', None, '이 PC에 컴파일러 없음 (검증 생략)')
            continue
        r = judge.judge_algo(HARNESS_PROBLEM, lang, code, HARNESS_CASES)
        st = [x['status'] for x in r.get('results', [])]
        report('run', lang, '정답/시간 초과/런타임 에러/오답 판정', st == expect, str(st or r))
    for lang, pid, code in (('javascript', 'A12', JS_A12), ('javascript', 'A05', JS_A05),
                            ('java', 'A12', JAVA_A12), ('java', 'A07', JAVA_A07)):
        if not judge.LANGUAGES.get(lang):
            continue
        p = load_problem('algo', pid)
        t = time.time()
        r = judge.judge_algo(p, lang, code, all_cases(p))
        st = [x['status'] for x in r.get('results', [])]
        report('run', lang, '{} 실제 풀이 전체 통과'.format(pid), bool(st) and all(s == 'pass' for s in st),
               '{:.1f}s {}'.format(time.time() - t, r.get('compile_error', '')[:200]))


def main():
    parts = sys.argv[1:] or ['harness', 'sql', 'algo']
    for part in parts:
        {'algo': verify_algo, 'sql': verify_sql, 'harness': verify_harness}[part]()
    fails = [r for r in ROWS if r[3] is False]
    print('\n총 {}개 검사, 실패 {}개'.format(len(ROWS), len(fails)))
    with open(os.path.join(ROOT, 'data', 'verify_report_{}.json'.format('_'.join(parts))), 'w', encoding='utf-8') as f:
        json.dump(ROWS, f, ensure_ascii=False, indent=1)
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
