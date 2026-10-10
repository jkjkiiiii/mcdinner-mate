/* 麦麦陪餐搭子 · 前端
   交互：按住麦克风说话（push-to-talk，最稳），松开即发送；也可直接打字。
   打断：AI 播报期间用户一开口就停掉播放（本地 ASR 已带 VAD，这里做播放侧中断）。
*/
const log = document.getElementById('log');
const mic = document.getElementById('mic');
const txt = document.getElementById('txt');
const player = document.getElementById('player');
const hint = document.getElementById('hint');

let ws = null;
let recorder = null;
let chunks = [];
let sessionId = null;

function bubble(cls, text) {
  const d = document.createElement('div');
  d.className = 'bubble ' + cls;
  d.textContent = text;
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
  return d;
}

function sys(text) { bubble('sys', text); }

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function showCard(c) {
  const d = document.createElement('div');
  d.className = 'card';
  if (c.type === 'report') {
    d.innerHTML = '<b>今日报告已生成</b><br>' +
      (c.items || []).map(i => '· ' + esc(i)).join('<br>') +
      (c.kcal ? `<br>热量 ${esc(c.kcal)} kcal` : '') +
      (c.mood ? `<br>心情 ${esc(c.mood)}` : '') +
      `<br><a href="/audio/${encodeURIComponent(String(c.image).split(/[\\/]/).pop())}" target="_blank">查看大图</a>`;
  } else if (c.type === 'order') {
    const rows = [];
    if (c.store) rows.push(`<div class="o-row"><span>门店</span><i>${esc(c.store)}${c.address ? '（' + esc(c.address) + '）' : ''}</i></div>`);
    if (c.takeWay) rows.push(`<div class="o-row"><span>取餐</span><i>${esc(c.takeWay)}</i></div>`);
    if (c.total) rows.push(`<div class="o-row"><span>金额</span><i class="o-total">¥${esc(c.total)}</i></div>`);
    if (c.discount && String(c.discount) !== '0') rows.push(`<div class="o-row"><span>优惠</span><i>-¥${esc(c.discount)}</i></div>`);
    if (c.expire) rows.push(`<div class="o-row"><span>支付时限</span><i>${esc(c.expire)}</i></div>`);
    d.innerHTML =
      `<div class="o-head"><b>订单已创建</b><span class="o-badge">${esc(c.status || '待支付')}</span></div>` +
      rows.join('') +
      `<div class="o-foot">订单号 ${esc(c.orderId)}<br>` +
      `付款请前往麦当劳 App / 小程序 · 本工具不代付</div>`;
  } else {
    d.innerHTML = '<b>卡片</b><br>' + esc(JSON.stringify(c));
  }
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
}

function connect() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/ws`);

  ws.onopen = () => sys('连接中…');
  ws.onclose = () => { sys('连接断开，刷新页面重试'); mic.disabled = true; };

  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.type === 'ready') { sessionId = m.session_id; sys(`已就位（会话 ${sessionId}）`); }
    else if (m.type === 'asr') {
      if (m.empty) { sys('没听清，再说一次？'); return; }
      stopPlay();                       // 用户开口 → 立即打断播报
      bubble('user', m.text);
    }
    else if (m.type === 'thinking') sys('…');
    else if (m.type === 'reply') {
      bubble('bot', m.text);
      (m.cards || []).forEach(showCard);
      if (m.audio) play(m.audio);
    }
    else if (m.type === 'error') sys('出错：' + m.message);
  };
}

function play(url) {
  player.src = url;
  player.play().catch(() => {});
}

function stopPlay() {
  if (!player.paused) { player.pause(); player.currentTime = 0; }
}

/* ---------- 录音：按住说话 ---------- */
async function startRec() {
  if (!navigator.mediaDevices) { sys('浏览器不支持录音，请直接打字'); return; }
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  recorder = new MediaRecorder(stream);
  chunks = [];
  recorder.ondataavailable = e => { if (e.data.size) chunks.push(e.data); };
  recorder.onstop = () => {
    stream.getTracks().forEach(t => t.stop());
    const blob = new Blob(chunks, { type: recorder.mimeType || 'audio/webm' });
    if (blob.size > 1000) { stopPlay(); ws.send(blob); sys('识别中…'); }
  };
  recorder.start();
  mic.classList.add('rec');
  mic.textContent = '⏹';
}

function stopRec() {
  if (recorder && recorder.state !== 'inactive') {
    recorder.stop();
    mic.classList.remove('rec');
    mic.textContent = '🎙';
  }
}

mic.addEventListener('pointerdown', startRec);
mic.addEventListener('pointerup', stopRec);
mic.addEventListener('pointerleave', stopRec);

/* ---------- 文字兜底 ---------- */
txt.addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  const v = txt.value.trim();
  if (!v) return;
  stopPlay();
  bubble('user', v);
  ws.send(JSON.stringify({ type: 'text', text: v }));
  txt.value = '';
});

connect();
