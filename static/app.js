/* 코딩테스트 모의 응시 — 화면 로직 */
'use strict';

const MONACO_BASE = 'https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min';
const ALGO_LANGS = [
  { id: 'python', name: 'Python3', monaco: 'python' },
  { id: 'javascript', name: 'JavaScript', monaco: 'javascript' },
  { id: 'java', name: 'Java', monaco: 'java' },
  { id: 'cpp', name: 'C++', monaco: 'cpp' },
];
const SQL_LANGS = [
  { id: 'mysql', name: 'MySQL', monaco: 'mysql' },
  { id: 'oracle', name: 'Oracle', monaco: 'sql' },
];
const SQL_TEMPLATE = '-- 코드를 입력하세요\nSELECT ';
const LEVEL = { 1: '쉬움', 2: '보통', 3: '어려움' };

const $ = sel => document.querySelector(sel);
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

let META = { languages: { python: true } };
let LIST = [];
const CACHE = {};
let state = {};
let dirty = false;
let editor = null;
let curKey = null;
let busy = false;
let warned = {};

const DEFAULT_STATE = () => ({
  settings: { examMinutes: 70, fontSize: 15, theme: 'dark', autocomplete: false, plainEditor: false, left: 42, res: 36 },
  drafts: {}, lang: {}, custom: {}, best: {}, session: null, lastResult: null,
});

/* ---------------------------------------------------------------- 서버 통신 */
async function api(path, body) {
  const opt = body === undefined ? {} : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) };
  const r = await fetch(path, opt);
  if (!r.ok && r.status !== 404) throw new Error('서버 응답 오류 ' + r.status);
  return r.json();
}
async function getProblem(id) {
  if (!CACHE[id]) CACHE[id] = await api('/api/problem?id=' + encodeURIComponent(id));
  return CACHE[id];
}
function markDirty() { dirty = true; }
async function saveState() {
  if (!dirty) return;
  dirty = false;
  try { await api('/api/state', state); } catch (e) { dirty = true; }
}
setInterval(saveState, 3000);
window.addEventListener('beforeunload', () => {
  flushEditor();
  try { navigator.sendBeacon('/api/state', new Blob([JSON.stringify(state)], { type: 'application/json' })); } catch (e) {}
});

/* ---------------------------------------------------------------- 공용 UI */
function show(view) {
  for (const v of document.querySelectorAll('.view')) v.hidden = v.id !== 'view-' + view;
  if (view === 'ws' && editor) setTimeout(() => editor.layout(), 0);
}
let toastTimer = null;
function toast(msg, ms = 3500) {
  const t = $('#toast');
  t.textContent = msg;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.hidden = true; }, ms);
}
function overlay(msg) {
  $('#overlay').hidden = !msg;
  if (msg) $('#overlay-msg').innerHTML = '<span class="spinner"></span>' + esc(msg);
}
function openModal(html, wide) {
  const box = $('#modal-box');
  box.className = 'modal-box' + (wide ? ' wide' : '');
  box.innerHTML = html;
  $('#modal').hidden = false;
  return box;
}
function closeModal() { $('#modal').hidden = true; $('#modal-box').innerHTML = ''; }
function confirmBox(title, text, okLabel = '확인', danger = false) {
  return new Promise(resolve => {
    const box = openModal('<h3>' + esc(title) + '</h3><p>' + text + '</p><div class="modal-actions">' +
      '<button class="btn" data-r="0">취소</button><button class="btn ' + (danger ? 'danger' : 'primary') + '" data-r="1">' + esc(okLabel) + '</button></div>');
    box.querySelectorAll('[data-r]').forEach(b => b.onclick = () => { closeModal(); resolve(b.dataset.r === '1'); });
  });
}
function fmtVal(v) {
  if (Array.isArray(v)) return '[' + v.map(fmtVal).join(', ') + ']';
  if (typeof v === 'string') return JSON.stringify(v);
  if (v === null || v === undefined) return 'null';
  return String(v);
}
function fmtTime(sec) {
  sec = Math.max(0, Math.floor(sec));
  const h = Math.floor(sec / 3600), m = Math.floor(sec % 3600 / 60), s = sec % 60;
  return String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
}
function fmtMin(sec) {
  const m = Math.floor(sec / 60), s = Math.floor(sec % 60);
  return m + '분 ' + String(s).padStart(2, '0') + '초';
}
function applyTheme() {
  document.documentElement.dataset.theme = state.settings.theme;
  document.documentElement.style.setProperty('--left', state.settings.left + '%');
  document.documentElement.style.setProperty('--res', state.settings.res + '%');
  document.documentElement.style.setProperty('--fs', state.settings.fontSize + 'px');
  if (editor) editor.configure(state.settings);
}

/* ---------------------------------------------------------------- 에디터 */
function loadMonaco(timeoutMs) {
  return new Promise(resolve => {
    let done = false;
    const finish = v => { if (!done) { done = true; resolve(v); } };
    setTimeout(() => finish(null), timeoutMs);
    window.MonacoEnvironment = {
      getWorkerUrl: () => 'data:text/javascript;charset=utf-8,' + encodeURIComponent(
        "self.MonacoEnvironment={baseUrl:'" + MONACO_BASE + "/'};importScripts('" + MONACO_BASE + "/vs/base/worker/workerMain.js');"),
    };
    const s = document.createElement('script');
    s.src = MONACO_BASE + '/vs/loader.js';
    s.onerror = () => finish(null);
    s.onload = () => {
      try {
        window.require.config({ paths: { vs: MONACO_BASE + '/vs' } });
        window.require(['vs/editor/editor.main'], () => finish(window.monaco), () => finish(null));
      } catch (e) { finish(null); }
    };
    document.head.appendChild(s);
  });
}

class MonacoEditor {
  constructor(el, monaco) {
    this.m = monaco;
    this.models = {};
    try {
      monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({ noSemanticValidation: true, noSyntaxValidation: true, noSuggestionDiagnostics: true });
    } catch (e) {}
    this.ed = monaco.editor.create(el, {
      value: '', language: 'python', automaticLayout: true, minimap: { enabled: false }, scrollBeyondLastLine: false,
      tabSize: 4, insertSpaces: true, renderWhitespace: 'none', fontFamily: "D2Coding, Consolas, 'Courier New', monospace",
      fixedOverflowWidgets: true, contextmenu: false,
    });
    this.listeners = [];
    this.ed.onDidChangeModelContent(() => this.listeners.forEach(f => f()));
  }
  open(key, value, lang) {
    let model = this.models[key];
    if (!model || model.isDisposed()) {
      model = this.m.editor.createModel(value, lang);
      model.updateOptions({ tabSize: 4, insertSpaces: true });
      this.models[key] = model;
    } else if (model.getValue() !== value) {
      model.setValue(value);
    }
    this.ed.setModel(model);
  }
  reset(key, value) { const model = this.models[key]; if (model) model.setValue(value); }
  value() { return this.ed.getValue(); }
  onChange(f) { this.listeners.push(f); }
  layout() { this.ed.layout(); }
  focus() { this.ed.focus(); }
  configure(s) {
    const ac = !!s.autocomplete;
    this.m.editor.setTheme(s.theme === 'light' ? 'vs' : 'vs-dark');
    this.ed.updateOptions({
      fontSize: s.fontSize,
      quickSuggestions: ac ? { other: true, comments: false, strings: false } : false,
      suggestOnTriggerCharacters: ac, wordBasedSuggestions: ac ? 'currentDocument' : 'off',
      parameterHints: { enabled: ac }, acceptSuggestionOnEnter: ac ? 'on' : 'off', tabCompletion: 'off',
      snippetSuggestions: ac ? 'inline' : 'none', inlineSuggest: { enabled: false }, hover: { enabled: ac },
      suggest: { showWords: ac, showKeywords: ac, showSnippets: ac, preview: false },
    });
    if (!ac && !this.blocked) {
      // 자동완성을 끈 상태에서는 Ctrl+Space 수동 호출도 막는다
      this.blocked = this.ed.createContextKey('ctNoSuggest', true);
      this.ed.addCommand(this.m.KeyMod.CtrlCmd | this.m.KeyCode.Space, () => {}, 'ctNoSuggest');
    }
    if (this.blocked) this.blocked.set(!ac);
  }
}

class PlainEditor {
  constructor(el) {
    el.innerHTML = '<div class="plain"><pre class="gutter">1</pre><textarea spellcheck="false" autocapitalize="off" autocomplete="off" wrap="off"></textarea></div>';
    this.ta = el.querySelector('textarea');
    this.gutter = el.querySelector('.gutter');
    this.listeners = [];
    this.ta.addEventListener('input', () => { this.lines(); this.listeners.forEach(f => f()); });
    this.ta.addEventListener('scroll', () => { this.gutter.scrollTop = this.ta.scrollTop; });
    this.ta.addEventListener('keydown', e => this.key(e));
  }
  lines() {
    const n = this.ta.value.split('\n').length;
    if (n !== this.n) { this.n = n; this.gutter.textContent = Array.from({ length: n }, (_, i) => i + 1).join('\n'); }
    this.gutter.scrollTop = this.ta.scrollTop;
  }
  key(e) {
    const ta = this.ta, v = ta.value, s = ta.selectionStart, en = ta.selectionEnd;
    const edit = (text, from, to, caret) => {
      ta.setRangeText(text, from, to, 'end');
      if (caret !== undefined) ta.selectionStart = ta.selectionEnd = caret;
      ta.dispatchEvent(new Event('input'));
    };
    if (e.key === 'Tab') {
      e.preventDefault();
      const ls = v.lastIndexOf('\n', s - 1) + 1;
      if (e.shiftKey || s !== en) {
        const le = v.indexOf('\n', en - (en > s && v[en - 1] === '\n' ? 1 : 0));
        const end = le === -1 ? v.length : le;
        const block = v.slice(ls, end).split('\n');
        const out = block.map(l => e.shiftKey ? l.replace(/^ {1,4}/, '') : '    ' + l).join('\n');
        ta.setRangeText(out, ls, end, 'select');
        ta.dispatchEvent(new Event('input'));
      } else {
        edit('    ', s, en);
      }
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const ls = v.lastIndexOf('\n', s - 1) + 1;
      const line = v.slice(ls, s);
      let ind = (line.match(/^[ \t]*/) || [''])[0];
      if (/[:{\[(]\s*$/.test(line)) ind += '    ';
      edit('\n' + ind, s, en);
    } else if (e.key === 'Backspace' && s === en && s > 0) {
      const ls = v.lastIndexOf('\n', s - 1) + 1;
      const before = v.slice(ls, s);
      if (before.length && /^ +$/.test(before)) {
        e.preventDefault();
        const cut = before.length % 4 || 4;
        edit('', s - cut, s);
      }
    }
  }
  open(key, value) { this.ta.value = value; this.n = -1; this.lines(); this.ta.scrollTop = 0; }
  reset(key, value) { this.open(key, value); }
  value() { return this.ta.value; }
  onChange(f) { this.listeners.push(f); }
  layout() { this.lines(); }
  focus() { this.ta.focus(); }
  configure(s) { this.ta.style.fontSize = s.fontSize + 'px'; this.gutter.style.fontSize = s.fontSize + 'px'; }
}

async function initEditor() {
  const el = $('#editor');
  let monaco = null;
  if (!state.settings.plainEditor) {
    el.innerHTML = '<div class="muted" style="padding:14px">에디터를 불러오는 중…</div>';
    monaco = await loadMonaco(9000);
  }
  el.innerHTML = '';
  editor = monaco ? new MonacoEditor(el, monaco) : new PlainEditor(el);
  if (!monaco && !state.settings.plainEditor) toast('온라인 에디터를 불러오지 못해 기본 에디터로 실행합니다.', 5000);
  editor.configure(state.settings);
  let t = null;
  editor.onChange(() => { clearTimeout(t); t = setTimeout(flushEditor, 400); });
}

/* ---------------------------------------------------------------- 문제 목록 · 기록 */
const filters = { type: 'all', level: '0' };
function renderList() {
  const rows = LIST.filter(p => (filters.type === 'all' || p.type === filters.type) && (filters.level === '0' || String(p.level) === filters.level));
  let html = '<thead><tr><th>번호</th><th>제목</th><th>유형</th><th>난이도</th><th>태그</th><th>최고 점수</th><th></th></tr></thead><tbody>';
  for (const p of rows) {
    const best = state.best[p.id];
    const tags = p.tags.map(t => '<span class="tag' + (t.startsWith('후기 유형') ? ' hot' : '') + '">' + esc(t) + '</span>').join('');
    html += '<tr><td>' + p.id + '</td><td><b>' + esc(p.title) + '</b></td><td>' + (p.type === 'algo' ? '알고리즘' : 'SQL') +
      '</td><td><span class="lv lv' + p.level + '">' + LEVEL[p.level] + '</span></td><td>' + tags + '</td><td>' +
      (best === undefined ? '<span class="muted">-</span>' : '<span class="score' + (best === 100 ? ' full' : '') + '">' + best.toFixed(1) + '</span>') +
      '</td><td><button class="btn sm" data-practice="' + p.id + '">풀기</button></td></tr>';
  }
  $('#plist').innerHTML = html + '</tbody>';
}

async function renderHistory() {
  let hist = [];
  try { hist = await api('/api/history'); } catch (e) {}
  const el = $('#history');
  if (!hist.length) { el.innerHTML = '<p class="muted">아직 응시 기록이 없습니다. 실전 모의고사를 끝내면 여기에 점수 추이가 쌓입니다.</p>'; return; }
  const W = 720, H = 180, P = 30;
  const pts = hist.map((h, i) => [P + (hist.length === 1 ? (W - 2 * P) / 2 : i * (W - 2 * P) / (hist.length - 1)), H - P - h.total / 100 * (H - 2 * P)]);
  let svg = '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="회차별 총점 추이">';
  for (const g of [0, 50, 100]) {
    const y = H - P - g / 100 * (H - 2 * P);
    svg += '<line class="grid" x1="' + P + '" x2="' + (W - P) + '" y1="' + y + '" y2="' + y + '"/><text x="4" y="' + (y + 4) + '">' + g + '</text>';
  }
  svg += '<polyline class="ln" points="' + pts.map(p => p.join(',')).join(' ') + '"/>';
  pts.forEach((p, i) => { svg += '<circle class="dot" cx="' + p[0] + '" cy="' + p[1] + '" r="4"/><text x="' + p[0] + '" y="' + (H - 8) + '" text-anchor="middle">' + (i + 1) + '회</text>'; });
  svg += '</svg>';
  let table = '<table class="rtable"><thead><tr><th>회차</th><th>응시일</th><th>문제</th><th>총점</th><th>사용 시간</th></tr></thead><tbody>';
  hist.slice().reverse().slice(0, 15).forEach((h, k) => {
    const n = hist.length - k;
    table += '<tr><td>' + n + '회</td><td>' + esc(h.date) + '</td><td>' + h.problems.map(p => esc(p.id + ' ' + p.title) + ' <b>' + p.score.toFixed(1) + '</b>').join('<br>') +
      '</td><td class="score">' + h.total.toFixed(1) + '</td><td>' + fmtMin(h.usedSec) + ' / ' + h.durationMin + '분</td></tr>';
  });
  el.innerHTML = '<div class="chart">' + svg + '</div>' + table + '</tbody></table>';
}

function renderHome() {
  $('#exam-desc').textContent = '보통 난이도 알고리즘 1개, 보통~어려움 알고리즘 1개, SQL 1개를 무작위로 뽑아 ' +
    state.settings.examMinutes + '분 동안 풉니다. 문제 사이를 자유롭게 오갈 수 있고, 시간이 끝나면 마지막 코드가 자동으로 제출됩니다.';
  const banner = $('#resume-banner');
  const s = state.session;
  if (s && !s.ended) {
    banner.hidden = false;
    banner.innerHTML = '<span>' + (s.mode === 'exam' ? '진행 중인 실전 모의고사가 있습니다.' : '풀던 연습 문제가 있습니다.') + '</span>' +
      '<span><button class="btn primary sm" data-act="resume">이어서 풀기</button> <button class="btn sm" data-act="discard">' +
      (s.mode === 'exam' ? '시험 종료하고 채점' : '닫기') + '</button></span>';
  } else if (state.lastResult) {
    banner.hidden = false;
    banner.innerHTML = '<span>지난 모의고사 결과: 총점 <b>' + state.lastResult.total.toFixed(1) + '</b></span><span><button class="btn sm" data-act="last-result">결과·해설 다시 보기</button></span>';
  } else banner.hidden = true;
  renderList();
  renderHistory();
  show('home');
}

/* ---------------------------------------------------------------- 세션 */
async function startExam() {
  if (state.session && !state.session.ended && state.session.mode === 'exam') {
    if (!await confirmBox('진행 중인 시험', '진행 중인 시험이 있습니다. 그 시험을 버리고 새로 시작할까요?', '새로 시작', true)) return;
  }
  overlay('문제를 준비하는 중');
  try {
    const { problems } = await api('/api/exam');
    for (const id of problems) await getProblem(id);
    for (const id of problems) for (const k of Object.keys(state.drafts)) if (k.startsWith(id + '|')) delete state.drafts[k];
    state.session = { mode: 'exam', problems, current: 0, start: Date.now(), duration: state.settings.examMinutes * 60, submissions: {}, timeSpent: {}, ended: false };
    warned = {};
    markDirty();
  } finally { overlay(null); }
  await openWorkspace();
}

async function startPractice(id) {
  await getProblem(id);
  state.session = { mode: 'practice', problems: [id], current: 0, start: Date.now(), submissions: {}, timeSpent: {}, ended: false };
  markDirty();
  await openWorkspace();
}

async function openWorkspace() {
  const s = state.session;
  for (const id of s.problems) await getProblem(id);
  if (!editor) await initEditor();
  $('#ws-mode').textContent = s.mode === 'exam' ? '실전 모의고사' : '연습';
  $('#btn-end').textContent = s.mode === 'exam' ? '시험 종료' : '목록으로';
  $('#btn-end').className = s.mode === 'exam' ? 'btn danger sm' : 'btn ghost sm';
  $('#btn-review').hidden = s.mode === 'exam';
  show('ws');
  await selectProblem(s.current || 0);
  tick();
}

function curProblem() { const s = state.session; return CACHE[s.problems[s.current]]; }
function langsFor(p) { return p.type === 'sql' ? SQL_LANGS : ALGO_LANGS; }
function curLang(p) {
  const saved = state.lang[p.id];
  const ok = langsFor(p).filter(l => p.type === 'sql' || META.languages[l.id]);
  return ok.find(l => l.id === saved) || ok[0];
}
function template(p, lang) { return p.type === 'sql' ? SQL_TEMPLATE : p.templates[lang]; }
function draftKey(p, lang) { return p.id + '|' + lang; }
function getCode(p, lang) { const k = draftKey(p, lang); return k in state.drafts ? state.drafts[k] : template(p, lang); }

function flushEditor() {
  if (!editor || !curKey) return;
  const v = editor.value();
  if (state.drafts[curKey] !== v) { state.drafts[curKey] = v; markDirty(); }
}

async function selectProblem(i) {
  flushEditor();
  const s = state.session;
  s.current = i;
  markDirty();
  const p = CACHE[s.problems[i]];
  renderTabs();
  $('#ws-name').textContent = s.mode === 'exam' ? '' : p.id + ' ' + p.title;
  $('#problem').innerHTML = renderProblem(p);
  $('#problem').scrollTop = 0;
  const sel = $('#lang');
  const lang = curLang(p);
  sel.innerHTML = langsFor(p).map(l => {
    const avail = p.type === 'sql' || META.languages[l.id];
    return '<option value="' + l.id + '"' + (avail ? '' : ' disabled') + (l.id === lang.id ? ' selected' : '') + '>' + l.name + (avail ? '' : ' (이 PC에 없음)') + '</option>';
  }).join('');
  openCode(p, lang);
  $('#btn-cases').hidden = p.type === 'sql';
  const sub = s.submissions[p.id];
  $('#result-body').innerHTML = sub && sub.view ? sub.view : '<div class="muted">' +
    (p.type === 'sql' ? '[코드 실행]은 예시 데이터로 결과를 보여 주고, [제출 후 채점하기]는 숨겨진 채점용 데이터로 정답 여부를 판정합니다.'
      : '[코드 실행]은 입출력 예와 추가한 테스트 케이스로 실행합니다. [제출 후 채점하기]는 숨겨진 정확성 테스트 ' + p.testCount + '개로 채점합니다.') + '</div>';
}

function openCode(p, lang) {
  curKey = draftKey(p, lang.id);
  editor.open(curKey, getCode(p, lang.id), lang.monaco);
  editor.focus();
}

function renderTabs() {
  const s = state.session;
  if (s.mode !== 'exam') { $('#ws-tabs').innerHTML = ''; return; }
  $('#ws-tabs').innerHTML = s.problems.map((id, i) => {
    const p = CACHE[id];
    const sub = s.submissions[id];
    const st = sub ? '제출 ' + sub.score.toFixed(0) + '점' : '미제출';
    return '<button class="ws-tab' + (i === s.current ? ' on' : '') + '" data-tab="' + i + '">문제 ' + (i + 1) + ' · ' + (p.type === 'sql' ? 'SQL' : '알고리즘') +
      '<span class="st">' + st + '</span></button>';
  }).join('');
}

function renderProblem(p) {
  let h = '<div class="prob"><h2>' + esc(p.title) + '</h2><div class="meta">' + (p.type === 'algo' ? '알고리즘' : 'SQL') + ' · ' + LEVEL[p.level] +
    (p.type === 'algo' ? ' · 테스트 케이스당 시간 제한 ' + p.timeLimit + '초' : '') + '</div>';
  h += '<h4>문제 설명</h4>' + p.description;
  if (p.type === 'algo') {
    h += '<h4>제한사항</h4><ul>' + p.constraints.map(c => '<li>' + c + '</li>').join('') + '</ul>';
    h += '<h4>입출력 예</h4><div class="dt-wrap"><table class="io"><tr>' + p.params.map(x => '<th>' + esc(x.name) + '</th>').join('') + '<th>result</th></tr>';
    for (const ex of p.examples) h += '<tr>' + ex.input.map(v => '<td>' + esc(fmtVal(v)) + '</td>').join('') + '<td>' + esc(fmtVal(ex.output)) + '</td></tr>';
    h += '</table></div>';
    if (p.exampleNotes) h += '<h4>입출력 예 설명</h4>' + p.exampleNotes;
  } else {
    for (const t of p.schema) {
      h += '<div class="tbl-name">' + esc(t.name) + '</div><div class="muted">' + esc(t.desc || '') + '</div>';
      h += '<div class="dt-wrap"><table class="dt"><tr><th>Column name</th><th>Type</th><th>Nullable</th><th>설명</th></tr>' +
        t.columns.map(c => '<tr><td>' + esc(c.name) + '</td><td>' + esc(c.type) + '</td><td>' + (c.nullable ? 'TRUE' : 'FALSE') + '</td><td style="font-family:var(--font)">' + esc(c.desc) + '</td></tr>').join('') + '</table></div>';
    }
    h += '<h4>예시</h4>';
    for (const t of p.schema) {
      const rows = p.sample[t.name] || [];
      h += '<div class="tbl-name">' + esc(t.name) + '</div>' + dataTable(t.columns.map(c => c.name), rows);
    }
    h += '<p>위 예시 데이터에 SQL을 실행하면 결과는 다음과 같아야 합니다.</p>' + dataTable(p.sampleExpected.columns, p.sampleExpected.rows);
    h += '<p class="muted">채점은 이 예시와 다른, 더 큰 데이터로 합니다. 결과 컬럼의 순서와 값을 비교하며 컬럼 이름(별칭)은 비교하지 않습니다.' +
      (p.ordered ? ' 행의 순서도 비교합니다.' : '') + '</p>';
  }
  return h + '</div>';
}

function dataTable(cols, rows, limit = 300) {
  let h = '<div class="dt-wrap"><table class="dt"><tr>' + cols.map(c => '<th>' + esc(c) + '</th>').join('') + '</tr>';
  for (const r of rows.slice(0, limit)) h += '<tr>' + r.map(v => v === null ? '<td class="null">NULL</td>' : '<td>' + esc(v) + '</td>').join('') + '</tr>';
  if (!rows.length) h += '<tr><td colspan="' + Math.max(1, cols.length) + '" class="muted">(결과 없음)</td></tr>';
  h += '</table></div>';
  if (rows.length > limit) h += '<div class="muted">… 총 ' + rows.length + '행 중 ' + limit + '행만 표시</div>';
  return h;
}

/* ---------------------------------------------------------------- 실행 · 제출 */
function setBusy(on, label) {
  busy = on;
  for (const id of ['#btn-run', '#btn-submit']) $(id).disabled = on;
  if (on) $('#result-body').innerHTML = '<div><span class="spinner"></span>' + esc(label) + '</div>';
}

async function runCode() {
  if (busy) return;
  flushEditor();
  const p = curProblem();
  const lang = $('#lang').value;
  setBusy(true, p.type === 'sql' ? '실행 중입니다…' : '코드를 실행하는 중입니다…');
  try {
    const custom = state.custom[p.id] || [];
    const r = await api('/api/run', { id: p.id, lang, code: editor.value(), custom });
    $('#result-body').innerHTML = p.type === 'sql' ? sqlRunView(r) : algoRunView(p, r, custom.length);
  } catch (e) {
    $('#result-body').innerHTML = '<div class="fail">실행 중 오류가 발생했습니다: ' + esc(e.message) + '</div>';
  } finally { setBusy(false); }
}

function algoRunView(p, r, customCount) {
  if (r.error) return '<div class="fail">' + esc(r.error) + '</div>';
  if (r.compile_error) return '<div class="fail sum-line">컴파일 오류</div><pre>' + esc(r.compile_error) + '</pre>';
  const nEx = r.results.length - customCount;
  let h = '';
  r.results.forEach((c, i) => {
    const label = i < nEx ? '입출력 예 #' + (i + 1) : '추가한 케이스 #' + (i - nEx + 1);
    const pass = c.status === 'pass';
    let verdict;
    if (pass) verdict = '<span class="pass">테스트를 통과하였습니다.</span>';
    else if (c.status === 'timeout') verdict = '<span class="fail">시간 초과 (' + p.timeLimit + '초)</span>';
    else if (c.status === 'error') verdict = '<span class="fail">런타임 에러</span><pre>' + esc(c.error || '') + '</pre>';
    else verdict = c.got !== undefined && c.got !== null
      ? '<span class="fail">실행한 결괏값 ' + esc(c.got) + '이(가) 기댓값 ' + esc(c.expected) + '과(와) 다릅니다.</span>'
      : '<span class="fail">실패</span>' + (c.error ? '<pre>' + esc(c.error) + '</pre>' : '');
    h += '<div class="case ' + (pass ? 'is-pass' : 'is-fail') + '"><div class="case-head"><span>테스트 ' + (i + 1) + ' <span class="muted">' + label + '</span></span><span class="muted">' +
      (c.status === 'timeout' ? '' : c.ms.toFixed(2) + 'ms') + '</span></div><table>' +
      '<tr><td>입력값 〉</td><td>' + esc(c.input.join(', ')) + '</td></tr>' +
      '<tr><td>기댓값 〉</td><td>' + esc(c.expected) + '</td></tr>' +
      '<tr><td>실행 결과 〉</td><td>' + verdict + '</td></tr>' +
      (c.out ? '<tr><td>출력 〉</td><td><pre>' + esc(c.out) + '</pre></td></tr>' : '') + '</table></div>';
  });
  const fails = r.total - r.passed;
  return '<div class="sum-line">' + (fails ? '<span class="fail">' : '<span class="pass">') + '실행 결과: ' + r.total + '개 중 ' + r.passed + '개 성공' + (fails ? ', ' + fails + '개 실패' : '') + '</span></div>' + h;
}

function sqlRunView(r) {
  if (r.error) return '<div class="fail sum-line">SQL 실행 오류</div><pre>' + esc(r.error) + '</pre>';
  return '<div class="sum-line">실행 결과 (예시 데이터 · ' + r.rowCount + '행)</div>' + dataTable(r.columns, r.rows) +
    '<div class="' + (r.sampleOk ? 'pass' : 'fail') + '" style="margin-top:6px">' +
    (r.sampleOk ? '예시의 기댓값과 같습니다. 제출하면 숨겨진 채점용 데이터로 한 번 더 확인합니다.' : '예시의 기댓값과 다릅니다. 컬럼 순서, 정렬, 조건을 확인해 보세요.') + '</div>';
}

async function submitCode(auto) {
  if (busy && !auto) return;
  flushEditor();
  const s = state.session;
  const p = curProblem();
  const lang = $('#lang').value;
  const code = editor.value();
  if (!auto && s.mode === 'exam' && !await confirmBox('제출 후 채점하기', '현재 코드로 채점합니다. 여러 번 제출할 수 있고, 마지막 제출이 점수가 됩니다.', '제출')) return;
  setBusy(true, '채점을 시작합니다…');
  try {
    await submitOne(p, lang, code, true);
  } finally { setBusy(false); }
}

async function submitOne(p, lang, code, render) {
  const s = state.session;
  let view, score, failed = [];
  try {
    const r = await api('/api/submit', { id: p.id, lang, code });
    if (p.type === 'sql') {
      score = r.score || 0;
      view = r.error ? '<div class="big-verdict fail">틀렸습니다.</div><div class="fail">SQL 실행 오류</div><pre>' + esc(r.error) + '</pre>'
        : '<div class="big-verdict ' + (r.correct ? 'pass' : 'fail') + '">' + (r.correct ? '정답입니다!' : '틀렸습니다.') + '</div>' +
          '<div class="muted">채점용 데이터 기준으로 결과를 비교했습니다. 아래는 예시 데이터로 실행한 결과입니다.</div>' + dataTable(r.columns || [], r.rows || [], 50) +
          '<div class="grade-box">채점 결과<br>합계: ' + score.toFixed(1) + ' / 100.0</div>';
    } else if (r.compile_error) {
      score = 0;
      view = '<div class="fail sum-line">컴파일 오류</div><pre>' + esc(r.compile_error) + '</pre><div class="grade-box">채점 결과<br>정확성: 0.0<br>합계: 0.0 / 100.0</div>';
    } else {
      score = r.score;
      const names = { pass: '<span class="pass">통과</span>', fail: '<span class="fail">실패</span>', timeout: '<span class="fail">실패 (시간 초과)</span>', error: '<span class="fail">실패 (런타임 에러)</span>' };
      let lines = '';
      r.results.forEach((c, i) => {
        if (c.status !== 'pass') failed.push(i);
        lines += '테스트 ' + String(i + 1).padStart(2, ' ') + ' 〉 ' + names[c.status] + (c.status === 'timeout' ? '' : ' (' + c.ms.toFixed(2) + 'ms)') + '<br>';
      });
      view = '<div class="sum-line">채점을 시작합니다.</div><div class="muted">정확성 테스트</div><div class="grade-line">' + lines + '</div>' +
        '<div class="grade-box">채점 결과<br>정확성: ' + score.toFixed(1) + '<br>합계: ' + score.toFixed(1) + ' / 100.0</div>';
    }
  } catch (e) {
    if (render) $('#result-body').innerHTML = '<div class="fail">채점 중 오류가 발생했습니다: ' + esc(e.message) + '</div>';
    return;
  }
  const prev = s.submissions[p.id] || { count: 0 };
  s.submissions[p.id] = { score, failed, lang, code, count: prev.count + 1, view };
  state.best[p.id] = Math.max(state.best[p.id] === undefined ? 0 : state.best[p.id], score);
  markDirty();
  if (render) $('#result-body').innerHTML = view;
  renderTabs();
}

/* ---------------------------------------------------------------- 타이머 · 종료 */
setInterval(tick, 1000);
function tick() {
  const s = state.session;
  if (!s || s.ended || $('#view-ws').hidden) return;
  if (document.visibilityState === 'visible') {
    const id = s.problems[s.current];
    s.timeSpent[id] = (s.timeSpent[id] || 0) + 1;
  }
  const el = $('#timer');
  if (s.mode !== 'exam') {
    el.className = 'timer';
    el.textContent = '경과 ' + fmtTime((Date.now() - s.start) / 1000);
    return;
  }
  const left = s.duration - (Date.now() - s.start) / 1000;
  el.textContent = '남은 시간 ' + fmtTime(left);
  el.className = 'timer' + (left <= 300 ? ' danger' : left <= 600 ? ' warn' : '');
  if (left <= 600 && left > 300 && !warned.ten) { warned.ten = true; toast('시험 종료 10분 전입니다.'); }
  if (left <= 300 && !warned.five) { warned.five = true; toast('시험 종료 5분 전입니다. 마지막 제출을 확인하세요.', 6000); }
  if (left <= 0 && !warned.end) { warned.end = true; finishExam(true); }
}

async function finishExam(timeout) {
  const s = state.session;
  if (!s || s.ended) return;
  flushEditor();
  // 마지막 제출 이후 바뀐 코드(또는 한 번도 제출하지 않은 코드)를 자동 제출한다
  const pending = [];
  for (const id of s.problems) {
    const p = CACHE[id];
    const lang = curLang(p).id;
    const code = getCode(p, lang);
    const sub = s.submissions[id];
    const changed = sub ? (sub.code !== code || sub.lang !== lang) : code !== template(p, lang);
    if (changed) pending.push([p, lang, code]);
  }
  overlay((timeout ? '시간이 종료되었습니다. ' : '') + (pending.length ? '제출하지 않은 코드를 자동으로 제출하는 중입니다…' : '채점 결과를 정리하는 중입니다…'));
  try {
    for (const [p, lang, code] of pending) await submitOne(p, lang, code, false);
  } finally { overlay(null); }
  s.ended = true;
  s.endedAt = Date.now();
  const used = Math.min(s.duration, (s.endedAt - s.start) / 1000);
  const items = s.problems.map(id => {
    const p = CACHE[id], sub = s.submissions[id];
    return { id, title: p.title, type: p.type, level: p.level, score: sub ? sub.score : 0, count: sub ? sub.count : 0,
      timeSpent: s.timeSpent[id] || 0, failed: sub ? sub.failed : [], lang: sub ? sub.lang : null, code: sub ? sub.code : null };
  });
  const total = items.reduce((a, b) => a + b.score, 0) / items.length;
  const d = new Date();
  const date = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0') + ' ' +
    String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
  state.lastResult = { date, items, total, usedSec: used, durationMin: s.duration / 60, timeout: !!timeout };
  state.session = null;
  markDirty();
  try { await api('/api/history', { date, total, usedSec: used, durationMin: s.duration / 60, problems: items.map(x => ({ id: x.id, title: x.title, score: x.score })) }); } catch (e) {}
  await saveState();
  renderResult();
}

async function endPressed() {
  const s = state.session;
  if (s.mode === 'practice') {
    flushEditor();
    state.session = null;
    markDirty();
    renderHome();
    return;
  }
  const left = s.duration - (Date.now() - s.start) / 1000;
  const ok = await confirmBox('시험 종료', '남은 시간 ' + fmtTime(left) + '. 시험을 종료하고 채점할까요?<br>마지막 제출 이후 바뀐 코드는 자동으로 제출됩니다.', '종료하고 채점', true);
  if (ok) finishExam(false);
}

function renderResult() {
  const r = state.lastResult;
  if (!r) return renderHome();
  let h = '<h2 style="margin:4px 0 16px">모의고사 결과' + (r.timeout ? ' <span class="muted" style="font-size:14px">(시간 종료로 자동 제출)</span>' : '') + '</h2>';
  h += '<div class="result-hero"><div class="stat"><div class="k">총점 (3문제 평균)</div><div class="v">' + r.total.toFixed(1) + '</div></div>' +
    '<div class="stat"><div class="k">사용 시간</div><div class="v">' + fmtMin(r.usedSec) + '</div><div class="k">제한 ' + r.durationMin + '분</div></div>' +
    '<div class="stat"><div class="k">응시일</div><div class="v" style="font-size:18px">' + esc(r.date) + '</div></div></div>';
  h += '<table class="rtable"><thead><tr><th>문제</th><th>유형</th><th>난이도</th><th>점수</th><th>제출 횟수</th><th>머문 시간</th><th></th></tr></thead><tbody>';
  r.items.forEach((x, i) => {
    h += '<tr><td><b>' + (i + 1) + '. ' + esc(x.title) + '</b> <span class="muted">' + x.id + '</span></td><td>' + (x.type === 'algo' ? '알고리즘' : 'SQL') +
      '</td><td><span class="lv lv' + x.level + '">' + LEVEL[x.level] + '</span></td><td class="score' + (x.score === 100 ? ' full' : '') + '">' + x.score.toFixed(1) +
      '</td><td>' + x.count + '회</td><td>' + fmtMin(x.timeSpent) + '</td><td><button class="btn sm" data-review="' + i + '">해설 보기</button> <button class="btn sm" data-practice="' + x.id + '">다시 풀기</button></td></tr>';
  });
  h += '</tbody></table><div style="margin-top:18px;display:flex;gap:8px"><button class="btn primary" data-act="start-exam">새 모의고사</button><button class="btn" data-act="home">처음으로</button></div>';
  $('#result-main').innerHTML = h;
  show('result');
}

/* ---------------------------------------------------------------- 해설 */
// submitted: true(제출함) / false(시험에서 제출 안 함) / null(연습 중이라 아직 모름)
async function openReview(pid, failed, myCode, myLang, submitted = null) {
  overlay('해설을 불러오는 중');
  let r, p;
  try {
    p = await getProblem(pid);
    r = await api('/api/review', { id: pid, failed: failed || [] });
  } finally { overlay(null); }
  let h = '<h3>' + esc(p.id + ' ' + p.title) + ' · 해설</h3><div class="review-sec">';
  h += '<h4>핵심 아이디어</h4>' + r.explanation;
  if (r.edgeCases && r.edgeCases.length) h += '<h4>놓치기 쉬운 엣지 케이스</h4><ul>' + r.edgeCases.map(e => '<li>' + e + '</li>').join('') + '</ul>';
  h += '<h4>모범 답안 (' + (p.type === 'sql' ? 'SQL' : 'Python') + ')</h4><pre>' + esc(r.solution) + '</pre>';
  if (myCode) h += '<h4>내 마지막 제출 코드 (' + esc(myLang) + ')</h4><pre>' + esc(myCode) + '</pre>';
  if (p.type === 'algo') {
    if (r.failedTests && r.failedTests.length) {
      h += '<h4>통과하지 못한 숨김 테스트</h4>';
      for (const t of r.failedTests) {
        h += '<div class="case is-fail"><div class="case-head">테스트 ' + (t.index + 1) + '</div><table>' +
          r.params.map((n, k) => '<tr><td>' + esc(n) + '</td><td>' + esc(t.input[k]) + '</td></tr>').join('') +
          '<tr><td>기댓값</td><td>' + esc(t.output) + '</td></tr></table></div>';
      }
    } else if (submitted) h += '<p class="pass">마지막 제출에서 모든 테스트를 통과했습니다.</p>';
    else if (submitted === false) h += '<p class="muted">이 문제는 제출 기록이 없습니다.</p>';
  } else {
    const e = r.hiddenExpected;
    h += '<h4>채점용 데이터의 기댓값 (' + e.total + '행 중 ' + e.rows.length + '행)</h4>' + dataTable(e.columns, e.rows, 50);
  }
  h += '</div><div class="modal-actions"><button class="btn primary" data-act="close-modal">닫기</button></div>';
  openModal(h, true);
}

/* ---------------------------------------------------------------- 테스트 케이스 추가 */
function openCases() {
  const p = curProblem();
  const rows = (state.custom[p.id] || []).map(c => ({ input: c.input.map(fmtVal), output: fmtVal(c.output) }));
  const draw = () => {
    let h = '<h3>테스트 케이스 추가</h3><p class="muted">값은 JSON 형식으로 입력합니다. 문자열은 큰따옴표("abc"), 배열은 [1, 2, 3], 2차원 배열은 [[1, 2], [3]]처럼 씁니다.</p>';
    h += '<table class="tc-table"><tr><th>#</th>' + p.params.map(x => '<th>' + esc(x.name) + ' <span class="muted">' + esc(x.type) + '</span></th>').join('') + '<th>result <span class="muted">' + esc(p.returnType) + '</span></th><th></th></tr>';
    p.examples.forEach((ex, i) => {
      h += '<tr><td class="muted">예 ' + (i + 1) + '</td>' + ex.input.map(v => '<td><div class="ro">' + esc(fmtVal(v)) + '</div></td>').join('') + '<td><div class="ro">' + esc(fmtVal(ex.output)) + '</div></td><td></td></tr>';
    });
    rows.forEach((r, i) => {
      h += '<tr data-row="' + i + '"><td>' + (i + 1) + '</td>' + r.input.map((v, k) => '<td><input data-k="' + k + '" value="' + esc(v) + '"></td>').join('') +
        '<td><input data-k="out" value="' + esc(r.output) + '"></td><td><button class="btn sm danger" data-del="' + i + '">삭제</button></td></tr>';
    });
    h += '</table><div style="margin-top:10px"><button class="btn sm" data-add="1">+ 케이스 추가</button></div><div class="err-msg" id="tc-err"></div>' +
      '<div class="modal-actions"><button class="btn" data-act="close-modal">취소</button><button class="btn primary" data-save="1">저장</button></div>';
    const box = openModal(h, true);
    const sync = () => box.querySelectorAll('tr[data-row]').forEach(tr => {
      const r = rows[+tr.dataset.row];
      tr.querySelectorAll('input').forEach(inp => { if (inp.dataset.k === 'out') r.output = inp.value; else r.input[+inp.dataset.k] = inp.value; });
    });
    box.querySelector('[data-add]').onclick = () => { sync(); rows.push({ input: p.params.map(() => ''), output: '' }); draw(); };
    box.querySelectorAll('[data-del]').forEach(b => b.onclick = () => { sync(); rows.splice(+b.dataset.del, 1); draw(); });
    box.querySelector('[data-save]').onclick = () => {
      sync();
      const out = [];
      let bad = null;
      box.querySelectorAll('input').forEach(i => i.classList.remove('err'));
      rows.forEach((r, i) => {
        try {
          out.push({ input: r.input.map(v => JSON.parse(v)), output: JSON.parse(r.output) });
        } catch (e) {
          bad = bad || i;
          box.querySelectorAll('tr[data-row="' + i + '"] input').forEach(inp => { try { JSON.parse(inp.value); } catch (x) { inp.classList.add('err'); } });
        }
      });
      if (bad !== null) { $('#tc-err').textContent = (bad + 1) + '번 케이스의 값이 JSON 형식이 아닙니다. 문자열은 큰따옴표로 감싸야 합니다.'; return; }
      state.custom[p.id] = out;
      markDirty();
      closeModal();
      toast('테스트 케이스 ' + out.length + '개를 저장했습니다. [코드 실행]에서 함께 실행됩니다.', 2500);
    };
  };
  draw();
}

/* ---------------------------------------------------------------- 설정 · 레퍼런스 */
function openSettings() {
  const s = state.settings;
  const h = '<h3>설정</h3>' +
    '<div class="form-row"><label>모의고사 제한 시간(분)<span class="hint">실제 시험은 객관식 포함 120분. 코딩 3문제에 쓸 시간을 정하세요.</span></label><input type="number" id="set-min" min="10" max="300" value="' + s.examMinutes + '"></div>' +
    '<div class="form-row"><label>글자 크기</label><input type="number" id="set-fs" min="11" max="26" value="' + s.fontSize + '"></div>' +
    '<div class="form-row"><label>테마</label><select id="set-theme"><option value="dark"' + (s.theme === 'dark' ? ' selected' : '') + '>어둡게</option><option value="light"' + (s.theme === 'light' ? ' selected' : '') + '>밝게</option></select></div>' +
    '<div class="form-row"><label>자동완성·힌트<span class="hint">실전처럼 연습하려면 끄세요(기본값).</span></label><select id="set-ac"><option value="0"' + (!s.autocomplete ? ' selected' : '') + '>끄기</option><option value="1"' + (s.autocomplete ? ' selected' : '') + '>켜기</option></select></div>' +
    '<div class="form-row"><label>기본 에디터 사용<span class="hint">인터넷이 막힌 환경용. 바꾸면 새로고침 후 적용됩니다.</span></label><select id="set-plain"><option value="0"' + (!s.plainEditor ? ' selected' : '') + '>아니요 (온라인 에디터)</option><option value="1"' + (s.plainEditor ? ' selected' : '') + '>예</option></select></div>' +
    '<div class="modal-actions"><button class="btn" data-act="close-modal">취소</button><button class="btn primary" id="set-save">저장</button></div>';
  const box = openModal(h);
  box.querySelector('#set-save').onclick = () => {
    const plainBefore = s.plainEditor;
    s.examMinutes = Math.min(300, Math.max(10, parseInt($('#set-min').value, 10) || 70));
    s.fontSize = Math.min(26, Math.max(11, parseInt($('#set-fs').value, 10) || 15));
    s.theme = $('#set-theme').value;
    s.autocomplete = $('#set-ac').value === '1';
    s.plainEditor = $('#set-plain').value === '1';
    markDirty();
    applyTheme();
    closeModal();
    if (plainBefore !== s.plainEditor) { saveState().then(() => location.reload()); return; }
    if (!$('#view-home').hidden) renderHome();
  };
}

let REF = null;
async function openReference() {
  if (!REF) {
    const html = await (await fetch('/reference.html')).text();
    const doc = new DOMParser().parseFromString(html, 'text/html');
    REF = [...doc.querySelectorAll('section[data-tab]')].map(sec => ({ name: sec.dataset.tab, html: sec.innerHTML }));
  }
  const tabs = $('#ref-tabs');
  const p = state.session && !$('#view-ws').hidden ? curProblem() : null;
  let cur = p && p.type === 'sql' ? REF.findIndex(r => r.name === 'SQL') : 0;
  const draw = () => {
    tabs.innerHTML = REF.map((r, i) => '<button data-ref="' + i + '"' + (i === cur ? ' class="on"' : '') + '>' + esc(r.name) + '</button>').join('');
    $('#ref-body').innerHTML = REF[cur].html;
    $('#ref-body').scrollTop = 0;
    tabs.querySelectorAll('[data-ref]').forEach(b => b.onclick = () => { cur = +b.dataset.ref; draw(); });
  };
  draw();
  $('#ref-panel').hidden = false;
}

/* ---------------------------------------------------------------- 분할선 드래그 */
function dragSplit(handle, axis) {
  handle.addEventListener('mousedown', e => {
    e.preventDefault();
    const main = $('#ws-main'), right = document.querySelector('.ws-right');
    handle.classList.add('dragging');
    const move = ev => {
      if (axis === 'x') {
        const r = main.getBoundingClientRect();
        state.settings.left = Math.min(75, Math.max(20, (ev.clientX - r.left) / r.width * 100));
      } else {
        const r = right.getBoundingClientRect();
        state.settings.res = Math.min(80, Math.max(10, (r.bottom - ev.clientY) / r.height * 100));
      }
      applyTheme();
      if (editor) editor.layout();
    };
    const up = () => { handle.classList.remove('dragging'); document.removeEventListener('mousemove', move); document.removeEventListener('mouseup', up); markDirty(); };
    document.addEventListener('mousemove', move);
    document.addEventListener('mouseup', up);
  });
}

/* ---------------------------------------------------------------- 이벤트 */
document.addEventListener('click', async e => {
  const t = e.target.closest('[data-act],[data-practice],[data-tab],[data-review]');
  if (!t) {
    if (e.target.id === 'modal') closeModal();
    return;
  }
  if (t.dataset.practice) {
    if (state.session && !state.session.ended && state.session.mode === 'exam') { toast('진행 중인 시험이 있습니다. 시험을 먼저 끝내 주세요.'); return; }
    return startPractice(t.dataset.practice);
  }
  if (t.dataset.tab !== undefined) return selectProblem(+t.dataset.tab);
  if (t.dataset.review !== undefined) {
    const x = state.lastResult.items[+t.dataset.review];
    return openReview(x.id, x.failed, x.code, x.lang, x.count > 0);
  }
  switch (t.dataset.act) {
    case 'start-exam': return startExam();
    case 'scroll-list': return $('#list-title').scrollIntoView({ behavior: 'smooth' });
    case 'resume': return openWorkspace();
    case 'discard':
      if (state.session.mode === 'exam') {
        await openWorkspace();
        return endPressed();
      }
      state.session = null; markDirty(); return renderHome();
    case 'last-result': return renderResult();
    case 'home': return renderHome();
    case 'settings': return openSettings();
    case 'reference': return openReference();
    case 'close-ref': $('#ref-panel').hidden = true; return;
    case 'close-modal': return closeModal();
    case 'run': return runCode();
    case 'submit': return submitCode(false);
    case 'cases': return openCases();
    case 'end': return endPressed();
    case 'review-current': {
      const p = curProblem();
      if (!await confirmBox('해설 보기', '모범 답안과 해설을 엽니다. 스스로 더 풀어 보고 싶다면 취소하세요.', '해설 보기')) return;
      const sub = state.session.submissions[p.id];
      return openReview(p.id, sub ? sub.failed : null, null, null, sub ? true : null);
    }
    case 'reset': {
      const p = curProblem();
      if (!await confirmBox('초기화', '작성한 코드를 지우고 기본 코드로 되돌릴까요? 되돌릴 수 없습니다.', '초기화', true)) return;
      const lang = curLang(p);
      delete state.drafts[draftKey(p, lang.id)];
      editor.reset(draftKey(p, lang.id), template(p, lang.id));
      flushEditor();
      markDirty();
      return;
    }
  }
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { if (!$('#modal').hidden) closeModal(); else $('#ref-panel').hidden = true; }
});

document.querySelectorAll('.seg[data-filter]').forEach(seg => seg.addEventListener('click', e => {
  const b = e.target.closest('button');
  if (!b) return;
  seg.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
  filters[seg.dataset.filter] = b.dataset.v;
  renderList();
}));

$('#lang').addEventListener('change', () => {
  flushEditor();
  const p = curProblem();
  state.lang[p.id] = $('#lang').value;
  markDirty();
  openCode(p, curLang(p));
});

/* ---------------------------------------------------------------- 시작 */
(async function boot() {
  try {
    [META, LIST] = await Promise.all([api('/api/meta'), api('/api/problems')]);
    const saved = await api('/api/state');
    const base = DEFAULT_STATE();
    state = Object.assign(base, saved || {});
    state.settings = Object.assign(DEFAULT_STATE().settings, (saved || {}).settings || {});
  } catch (e) {
    document.body.innerHTML = '<div style="padding:40px">서버에 연결할 수 없습니다. 이 창을 닫고 <code>python app.py</code>를 다시 실행해 주세요.</div>';
    return;
  }
  applyTheme();
  dragSplit($('#vsplit'), 'x');
  dragSplit($('#hsplit'), 'y');
  const s = state.session;
  if (s && !s.ended) {
    if (s.mode === 'exam' && s.duration - (Date.now() - s.start) / 1000 <= 0) {
      await openWorkspace();
      warned.end = true;
      return finishExam(true);
    }
    return openWorkspace();
  }
  renderHome();
})();
