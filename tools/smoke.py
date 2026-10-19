"""채점기 동작 확인: 언어별 정답·오답·런타임 에러·시간 초과·잘못된 반환 타입·컴파일 오류."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import judge  # noqa: E402

P = {'params': [{'name': 'nums', 'type': 'int[]'}, {'name': 'k', 'type': 'int'}], 'returnType': 'int[]', 'timeLimit': 3}
CASES = [
    {'input': [[1, 2, 3], 2], 'output': [2, 4, 6]},
    {'input': [[], 5], 'output': []},
    {'input': [[-1], 0], 'output': [0]},   # 0이면 일부 코드가 무한 루프 / 예외
]

CODES = {
    'python': {
        'ok': 'def solution(nums, k):\n    print("debug", k)\n    return [x * k for x in nums]',
        'tle_err': 'def solution(nums, k):\n    if k == 0:\n        while True: pass\n    if k == 5:\n        raise ValueError("boom")\n    return [x * k for x in nums]',
        'type': 'def solution(nums, k):\n    return {x * k for x in nums}',
        'compile': 'def solution(nums, k)\n    return nums',
        'deep': 'import sys\nsys.setrecursionlimit(10**6)\ndef f(n):\n    return 0 if n == 0 else 1 + f(n - 1)\ndef solution(nums, k):\n    f(100000)\n    return [x * k for x in nums]',
    },
    'javascript': {
        'ok': 'function solution(nums, k) {\n  console.log("debug", k, [1,2]);\n  return nums.map(x => x * k);\n}',
        'tle_err': 'const solution = (nums, k) => {\n  if (k === 0) while (true) {}\n  if (k === 5) throw new Error("boom");\n  return nums.map(x => x * k);\n};',
        'type': 'function solution(nums, k) { return undefined; }',
        'compile': 'function solution(nums, k) { return nums.map(x => ; }',
        'deep': 'function f(n){ return n === 0 ? 0 : 1 + f(n - 1); }\nfunction solution(nums, k) { f(100000); return nums.map(x => x * k); }',
    },
    'java': {
        'ok': 'import java.util.*;\nclass Solution {\n    public int[] solution(int[] nums, int k) {\n        System.out.println("debug " + k);\n        int[] a = new int[nums.length];\n        for (int i = 0; i < nums.length; i++) a[i] = nums[i] * k;\n        return a;\n    }\n}',
        'tle_err': 'class Solution {\n    public int[] solution(int[] nums, int k) {\n        if (k == 0) while (true) {}\n        if (k == 5) throw new RuntimeException("boom");\n        int[] a = new int[nums.length];\n        for (int i = 0; i < nums.length; i++) a[i] = nums[i] * k;\n        return a;\n    }\n}',
        'type': 'class Solution {\n    public String solution(int[] nums, int k) { return "x"; }\n}',
        'compile': 'class Solution {\n    public int[] solution(int[] nums, int k) { return nums }\n}',
        'deep': 'class Solution {\n    int f(int n) { return n == 0 ? 0 : 1 + f(n - 1); }\n    public int[] solution(int[] nums, int k) {\n        f(100000);\n        int[] a = new int[nums.length];\n        for (int i = 0; i < nums.length; i++) a[i] = nums[i] * k;\n        return a;\n    }\n}',
    },
}

for lang, codes in CODES.items():
    if not judge.LANGUAGES.get(lang):
        print(lang, 'not available')
        continue
    for name, code in codes.items():
        t = time.time()
        r = judge.judge_algo(P, lang, code, CASES)
        if 'compile_error' in r:
            print(lang, name, 'COMPILE', r['compile_error'].splitlines()[0][:90])
        else:
            print(lang, name, [x['status'] for x in r['results']], round(time.time() - t, 1), 's',
                  repr(r['results'][0].get('out', ''))[:40], (r['results'][1].get('error') or '')[:60].replace('\n', ' | '))
