'use strict';

const data = window.lab9;
const byId = (id) => document.getElementById(id);
const put = (id, value) => { byId(id).textContent = value; };
const number = new Intl.NumberFormat('vi-VN');
const money = (value) => `${number.format(value)} ₫`;
const percent = (value) => `${number.format(Math.round(value * 10000) / 100)}%`;
const signed = (value) => `${value > 0 ? '+' : ''}${value.toFixed(3).replace('.', ',')}`;
const runButtons = [...document.querySelectorAll('[data-run]')];
let runKey = 'seeded_regression';
let step = 0;

function describe(event) {
  const payload = event.payload;
  switch (event.kind) {
    case 'handoff':
      return ['Chuyển yêu cầu đi kiểm tra', 'Agent giao việc kiểm tra đơn và chính sách cho công cụ tra cứu.'];
    case 'investigator':
      return ['Đọc dữ kiện từ DB', `DB ghi đơn giao trễ ${payload.lookup_order.order.delay_days} ngày.`];
    case 'model_override':
      return ['Ghi đè dữ kiện', `Agent thay số ngày từ DB bằng ${payload.delay_days} ngày trong lời khách. Đây là bước sai đầu tiên (FM-03).`];
    case 'quote':
      return ['Tính khoản hoàn', payload.amount_vnd
        ? `Từ dữ kiện đang dùng, agent tính khoản hoàn ${money(payload.amount_vnd)}.`
        : 'Theo dữ kiện từ DB, đơn chưa đủ điều kiện hoàn tiền.'];
    case 'refund_history':
      return ['Kiểm tra lịch sử hoàn', `Công cụ tìm thấy ${payload.refund_count} khoản đã hoàn trước đó.`];
    case 'reply':
      return ['Trả lời khách', payload.text];
    default:
      return [event.kind, 'Xem dữ liệu gốc của bước này ở bên dưới.'];
  }
}

function showStep(index) {
  const events = data.runs[runKey].events;
  if (index < 0 || index >= events.length) return;
  step = index;
  const event = events[step];
  const [title, explanation] = describe(event);
  put('step-number', `Bước ${step + 1} / ${events.length} · ${event.kind}`);
  put('step-title', title);
  put('step-explanation', explanation);
  put('payload', JSON.stringify(event.payload, null, 2));
  put('step-badge', 'Bước sai đầu tiên');
  byId('step-badge').hidden = event.kind !== 'model_override';
  [...byId('steps').querySelectorAll('button')].forEach((button, i) => {
    button.setAttribute('aria-current', i === step ? 'step' : 'false');
  });
  byId('previous').disabled = step === 0;
  byId('next').disabled = step === events.length - 1;
}

function makeStep(event, index) {
  const item = document.createElement('li');
  const button = document.createElement('button');
  button.type = 'button';
  const indexLabel = document.createElement('span');
  indexLabel.className = 'number';
  indexLabel.textContent = String(index + 1).padStart(2, '0');
  button.append(indexLabel, describe(event)[0]);
  if (event.kind === 'model_override') {
    const flag = document.createElement('span');
    flag.className = 'flag';
    flag.textContent = 'FM-03';
    button.append(flag);
  }
  button.addEventListener('click', () => showStep(index));
  item.append(button);
  return item;
}

function selectRun(key) {
  runKey = key;
  const run = data.runs[key];
  const db = run.events.find((event) => event.kind === 'investigator');
  runButtons.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.run === key)));
  put('db', `${db.payload.lookup_order.order.delay_days} ngày`);
  put('expected', money(run.expected));
  put('actual', money(run.actual));
  put('expected-grader', money(run.expected));
  put('grader-result', run.graderPass ? 'PASS · Ledger khớp số tiền kỳ vọng' : 'FAIL · Ledger ghi sai số tiền');
  byId('grader-result').dataset.pass = run.graderPass;
  const { rate, trialCount, delta, ci, blocked, runId } = run.gate;
  put('gate-scope', `03 / CẢ BỘ ĐÁNH GIÁ · ${trialCount} TRIAL`);
  put('pass-rate', percent(rate));
  put('delta', `${signed(delta * 100)} điểm %`);
  put('ci', `CI 95% của Δ [${signed(ci[0])}; ${signed(ci[1])}]`);
  put('gate-result', blocked.length ? 'CHẶN MERGE · Exit 1' : 'CHO QUA · Exit 0');
  byId('gate-result').dataset.pass = !blocked.length;
  put('run-id', blocked.length ? `${runId} · Chặn ở ${blocked.join(', ')}` : runId);
  byId('steps').replaceChildren(...run.events.map(makeStep));
  const focusStep = run.events.findIndex((event) => event.kind === (run.graderPass ? 'quote' : 'model_override'));
  showStep(Math.max(0, focusStep));
}

put('ticket', `${data.ticketDays} ngày`);
put('judges', `Judge giọng điệu đạt ngưỡng với κ ${number.format(data.tone.kappa)}. Judge helpful chỉ phát hiện ${data.helpful.tp}/${data.helpful.totalFailures} lỗi theo nhãn người, nên bị loại khỏi gate.`);
put('slices', `Bản slice_regression đạt ${percent(data.slice.total)} trên toàn tập. Trong nhóm claim có hoàn tiền, tỉ lệ qua là ${percent(data.slice.money)}, dưới sàn ${percent(data.slice.floor)}, nên bị chặn.`);
put('seeds', `Với flaky_regression, ${percent(data.flaky.at)} item qua ít nhất một lần, nhưng chỉ ${percent(data.flaky.all)} item qua đủ năm lần, dưới sàn ${percent(data.flaky.floor)}.`);
runButtons.forEach((button) => button.addEventListener('click', () => selectRun(button.dataset.run)));
byId('previous').addEventListener('click', () => showStep(step - 1));
byId('next').addEventListener('click', () => showStep(step + 1));
selectRun(runKey);
