// JavaScript 하네스: solution.js를 테스트 케이스마다 새 vm 컨텍스트에서 실행한다.
// 사용법: node js_runner.js <코드 경로> <케이스 JSON 경로> <시작 인덱스>
'use strict';
const fs = require('fs');
const vm = require('vm');
const util = require('util');

const MARK = '@@CT@@';
const OUT_LIMIT = 20000;
const [codePath, casesPath, startArg] = process.argv.slice(2);

function send(obj) {
  fs.writeSync(1, MARK + JSON.stringify(obj) + '\n');
}

function userStack(e) {
  if (!(e instanceof Object) || !e.stack) return String(e);
  const lines = String(e.stack).split('\n');
  const keep = [lines[0]];
  for (const l of lines.slice(1)) if (l.includes('solution.js')) keep.push(l);
  return keep.join('\n');
}

// const/let으로 선언한 solution도 찾을 수 있도록 같은 스크립트 끝에서 꺼내 둔다.
const src = fs.readFileSync(codePath, 'utf8') +
  '\n;globalThis.__sol = (typeof solution !== "undefined") ? solution : undefined;';
let script;
try {
  script = new vm.Script(src, { filename: 'solution.js' });
} catch (e) {
  send({ t: 'compile', err: userStack(e) });
  process.exit(0);
}
const cases = JSON.parse(fs.readFileSync(casesPath, 'utf8')).cases;

for (let i = Number(startArg); i < cases.length; i++) {
  let out = '';
  let cut = false;
  const write = (...a) => {
    const s = util.format(...a) + '\n';
    if (out.length < OUT_LIMIT) {
      out += s.slice(0, OUT_LIMIT - out.length);
      if (out.length >= OUT_LIMIT) cut = true;
    } else cut = true;
  };
  const sandbox = {
    console: { log: write, info: write, warn: write, error: write, debug: write, dir: write, table: write },
    require, module: { exports: {} }, exports: {},
    __argsJson: JSON.stringify(cases[i]),
  };
  const ctx = vm.createContext(sandbox);
  send({ t: 'start', i });
  const t0 = process.hrtime.bigint();
  let ret;
  try {
    script.runInContext(ctx);
    if (typeof ctx.__sol !== 'function') throw new ReferenceError('solution 함수가 정의되어 있지 않습니다.');
    // 매개변수 배열을 컨텍스트 안에서 만들어야 instanceof Array 등이 정상 동작한다.
    ret = vm.runInContext('__sol(...JSON.parse(__argsJson))', ctx);
  } catch (e) {
    const ms = Number(process.hrtime.bigint() - t0) / 1e6;
    send({ t: 'res', i, ok: false, kind: 'error', ms, out: out + (cut ? '\n...(출력이 너무 길어 생략)' : ''), err: userStack(e) });
    continue;
  }
  const ms = Number(process.hrtime.bigint() - t0) / 1e6;
  const text = out + (cut ? '\n...(출력이 너무 길어 생략)' : '');
  let json;
  try { json = JSON.stringify(ret); } catch (e) { json = undefined; }
  if (json === undefined) {
    send({ t: 'res', i, ok: false, kind: 'type', ms, out: text, err: '반환값을 비교할 수 없는 형식입니다: ' + typeof ret });
    continue;
  }
  send({ t: 'res', i, ok: true, ret: JSON.parse(json), ms, out: text });
}
