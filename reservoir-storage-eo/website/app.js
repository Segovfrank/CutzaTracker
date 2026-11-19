// Valle de Bravo storage: pick a month, show the estimate. Data comes from server.py (/api/history, /api/estimate).
const $ = (id) => document.getElementById(id);
const nf = (digits) => new Intl.NumberFormat('en', { minimumFractionDigits: digits, maximumFractionDigits: digits });
const one = nf(1), two = nf(2), whole = nf(0);
const pct = new Intl.NumberFormat('en', { style: 'percent', minimumFractionDigits: 1, maximumFractionDigits: 1 });
const MINUS = '−';
const signed = (v, f = one) => (v > 0 ? '+' : v < 0 ? MINUS : '') + f.format(Math.abs(v));
const hm3 = (v) => (v == null ? '—' : `${one.format(v)} hm³`);
const asDate = (key) => new Date(`${key.length === 7 ? key + '-01' : key}T00:00:00`);
const longMonth = (key) => asDate(key).toLocaleDateString('en', { month: 'long', year: 'numeric' });
const shortMonth = (key) => asDate(key).toLocaleDateString('en', { month: 'short', year: 'numeric' });
const yearBefore = (key) => `${Number(key.slice(0, 4)) - 1}${key.slice(4)}`;

let history = null;
let current = null;
let timer = null;

async function getJSON(url) {
  const response = await fetch(url);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || `The server answered ${response.status}`);
  return body;
}

function setValue(id, number, unit) {
  const el = $(id);
  if (number == null) { el.textContent = '—'; return; }
  el.innerHTML = `${number}${unit ? `<span class="unit">${unit}</span>` : ''}`;
}

// ---- history chart ----------------------------------------------------------
function drawHistory(selected) {
  const el = $('history-chart');
  const message = $('history-message');
  if (!history || history.months.length === 0) {
    el.innerHTML = '';
    message.hidden = false;
    message.textContent = 'No months measured yet. Run scripts.water_level.measure to build the history.';
    return;
  }
  message.hidden = true;
  const labels = history.months.map(shortMonth);
  // one label per January, or every other year when the chart is narrow
  const everyYears = el.clientWidth < 560 ? 2 : 1;
  const januaries = [];
  history.months.forEach((key, i) => {
    if (key.endsWith('-01') && (Number(key.slice(0, 4)) - 2019) % everyYears === 0) januaries.push(i);
  });
  const at = history.months.indexOf(selected);
  el.innerHTML = '';
  Charts.line(el, {
    labels,
    series: [
      { name: 'Estimate', values: history.estimate_hm3 },
      { name: 'CONAGUA', values: history.conagua_hm3 },
    ],
    format: (v) => `${whole.format(v)} hm³`,
    tickFormat: (v) => whole.format(v),
    height: 220,
    xAt: januaries,
    annotations: at >= 0 ? [{ at, label: shortMonth(selected) }] : undefined,
    legend: '#history-legend',
  });
}

// ---- loading, error, result -------------------------------------------------
function setBusy(busy, key) {
  document.body.classList.toggle('busy', busy);
  $('picker').classList.toggle('loading', busy);
  $('go').disabled = busy;
  $('month').disabled = busy;
  $('kpis').setAttribute('aria-busy', String(busy));
  clearInterval(timer);
  const status = $('status');
  status.classList.remove('error');
  if (!busy) { status.textContent = ''; return; }

  const measured = history && history.months.includes(key) && history.estimate_hm3[history.months.indexOf(key)] != null;
  const started = Date.now();
  const tick = () => {
    const s = Math.round((Date.now() - started) / 1000);
    const clock = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
    status.textContent = measured
      ? `Loading ${longMonth(key)}…`
      : `Measuring ${longMonth(key)} from Sentinel-2 · ${clock}. A month seen for the first time takes a few minutes.`;
  };
  tick();
  timer = setInterval(tick, 1000);

  $('finding').textContent = `Estimating ${longMonth(key)}.`;
  $('gauge-month').textContent = longMonth(key);
  const body = $('scenes-body');
  body.innerHTML = '';
  for (let i = 0; i < 4; i++) {
    const tr = document.createElement('tr');
    tr.innerHTML = '<td><span class="skeleton" style="width:84px"></span></td>'
      + '<td class="num" colspan="6"><span class="skeleton" style="width:60%"></span></td>';
    body.appendChild(tr);
  }
  $('scenes-count').textContent = '';
}

function showError(key, error) {
  clearInterval(timer);
  document.body.classList.remove('busy');
  $('picker').classList.remove('loading');
  $('go').disabled = false;
  $('month').disabled = false;
  const status = $('status');
  status.classList.add('error');
  status.innerHTML = '';
  status.append(`Couldn't estimate ${longMonth(key)}: ${error.message}. `);
  const retry = document.createElement('button');
  retry.type = 'button';
  retry.textContent = 'Retry';
  retry.addEventListener('click', () => run(key));
  status.append(retry);
  $('scenes-body').innerHTML = '<tr><td class="empty" colspan="7">No passes to show.</td></tr>';
}

function render(data) {
  current = data;
  const key = data.month;
  const namo = data.namo_hm3;
  const clear = data.scenes.filter((s) => s.estimate_hm3 != null).length;
  const lastYear = history ? history.estimate_hm3[history.months.indexOf(yearBefore(key))] ?? null : null;

  // finding: the answer, then the comparison with its baseline named
  let finding;
  if (data.estimate_hm3 == null) {
    finding = data.scenes.length === 0
      ? `No Sentinel-2 pass over the lake in ${longMonth(key)}.`
      : `No clear pass in ${longMonth(key)}: clouds hid more than 5% of the lake every time.`;
  } else {
    finding = `${longMonth(key)}: about ${whole.format(data.estimate_hm3)} hm³, ${pct.format(data.estimate_hm3 / namo)} of NAMO`;
    if (lastYear != null) {
      const diff = data.estimate_hm3 - lastYear;
      finding += `, ${whole.format(Math.abs(diff))} hm³ ${diff >= 0 ? 'more' : 'less'} than ${longMonth(yearBefore(key))}`;
    }
    finding += '.';
  }
  $('finding').textContent = finding;

  // KPIs
  setValue('k-estimate', data.estimate_hm3 == null ? null : one.format(data.estimate_hm3), 'hm³');
  $('k-estimate-note').textContent = data.estimate_hm3 == null ? 'No clear pass this month' : `Median of ${clear} clear ${clear === 1 ? 'pass' : 'passes'}`;
  setValue('k-fill', data.estimate_hm3 == null ? null : pct.format(data.estimate_hm3 / namo));
  $('k-namo').textContent = one.format(namo);
  setValue('k-conagua', data.conagua_hm3 == null ? null : one.format(data.conagua_hm3), 'hm³');
  const conaguaNote = $('k-conagua-note');
  conaguaNote.classList.remove('bad');
  if (data.conagua_error) {
    conaguaNote.textContent = 'SINA did not answer';
  } else if (data.conagua_hm3 == null) {
    conaguaNote.textContent = key > '2025-04' ? 'No SINA report after 23 Apr 2025' : 'No report on these dates';
  } else if (data.estimate_hm3 != null) {
    conaguaNote.textContent = `Estimate is ${signed(data.estimate_hm3 - data.conagua_hm3)} hm³ against it`;
  } else {
    conaguaNote.textContent = 'Median of the reported dates';
  }
  setValue('k-clear', `${clear}<span class="unit"> of ${data.scenes.length}</span>`);

  // gauge
  $('gauge-month').textContent = longMonth(key);
  $('gauge-namo').textContent = `${one.format(namo)} hm³ (NAMO)`;
  $('gauge-fill').style.width = data.estimate_hm3 == null ? '0' : `${Math.min(100, (data.estimate_hm3 / namo) * 100)}%`;
  const tick = $('gauge-tick');
  tick.hidden = data.conagua_hm3 == null;
  if (data.conagua_hm3 != null) tick.style.left = `${Math.min(100, (data.conagua_hm3 / namo) * 100)}%`;
  $('gauge').setAttribute('aria-label', data.estimate_hm3 == null
    ? 'No estimate this month'
    : `Estimated ${pct.format(data.estimate_hm3 / namo)} of NAMO`);
  $('g-estimate').textContent = hm3(data.estimate_hm3);
  $('g-conagua').textContent = hm3(data.conagua_hm3);
  $('g-lastyear-label').textContent = longMonth(yearBefore(key));
  $('g-lastyear').textContent = hm3(lastYear);
  $('model-line').textContent = `V = ${data.model.a.toPrecision(3)} · A^${two.format(data.model.b)}, fitted on ${data.model.pairs} dates with a CONAGUA report.`;

  // table
  const body = $('scenes-body');
  body.innerHTML = '';
  $('scenes-count').textContent = `${data.scenes.length} ${data.scenes.length === 1 ? 'pass' : 'passes'}`;
  if (data.scenes.length === 0) {
    body.innerHTML = `<tr><td class="empty" colspan="7">Sentinel-2 has no pass over the lake in ${longMonth(key)}.</td></tr>`;
  }
  for (const s of [...data.scenes].sort((a, b) => a.date.localeCompare(b.date))) {
    const tr = document.createElement('tr');
    const cell = (text, cls = 'num') => `<td class="${cls}">${text}</td>`;
    const dash = '<td class="num dash">—</td>';
    const measured = s.estimate_hm3 != null;
    tr.innerHTML = cell(s.date, '')
      + cell(s.clear_fraction == null ? '—' : pct.format(s.clear_fraction))
      + (measured ? cell(`${two.format(s.area_km2)} <span class="sub">km²</span>`) : '<td class="num dash">Too cloudy</td>')
      + (measured ? cell(`${one.format(s.estimate_hm3)} <span class="sub">hm³</span>`) : dash)
      + (measured ? cell(pct.format(s.estimate_hm3 / namo)) : dash)
      + (s.conagua_hm3 != null ? cell(`${one.format(s.conagua_hm3)} <span class="sub">hm³</span>`) : dash)
      + (measured && s.conagua_hm3 != null ? cell(`${signed(s.estimate_hm3 - s.conagua_hm3)} <span class="sub">hm³</span>`) : dash);
    body.appendChild(tr);
  }

  drawHistory(key);
}

async function run(key) {
  setBusy(true, key);
  try {
    const data = await getJSON(`/api/estimate?month=${encodeURIComponent(key)}`);
    if (data.source === 'satellite') history = await getJSON('/api/history').catch(() => history);
    setBusy(false);
    render(data);
    try { localStorage.setItem('month', key); } catch {} // remembers the last month for this viewer only
  } catch (error) {
    showError(key, error);
  }
}

async function init() {
  const now = new Date();
  const input = $('month');
  input.min = '2019-01';
  input.max = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;

  try {
    history = await getJSON('/api/history');
  } catch (error) {
    $('history-message').hidden = false;
    $('history-message').textContent = `Couldn't load the history: ${error.message}.`;
  }

  let saved = null;
  try { saved = localStorage.getItem('month'); } catch {}
  const start = saved || (history && history.latest) || input.max;
  input.value = start;
  drawHistory(start);
  run(start);

  $('picker').addEventListener('submit', (event) => {
    event.preventDefault();
    const key = input.value;
    if (!/^\d{4}-\d{2}$/.test(key)) { input.reportValidity(); return; }
    run(key);
  });

  window.addEventListener('scroll', () => document.querySelector('.bar').classList.toggle('scrolled', window.scrollY > 4), { passive: true });
  let width = window.innerWidth;
  window.addEventListener('resize', () => {
    if (Math.abs(window.innerWidth - width) < 40) return;
    width = window.innerWidth;
    drawHistory(current ? current.month : input.value);
  });
}

init();
