// ============================================================
// comprobante-telegram.js
// Tarjeta CORTA "Número editorial" del comprobante ECOEMS, enviada al
// alumno por Telegram como IMAGEN (PNG, se ve inline en el chat).
//
// NO es el PDF largo (ese lo sigue generando buildComprobanteHTML en
// server.js). Esto es solo la portada-resumen: resultado grande + desglose
// por materia, en una sola tarjeta.
//
// Diseño: "Editorial cálido funcional" (Fraunces / IBM Plex, crema-coñac).
// Reusa room/student tal cual ya existen en server.js — cero datos nuevos.
//
// ── Wiring en server.js (3 pasos) ───────────────────────────
//   1) Arriba, junto a los otros require:
//        const { sendComprobanteTelegram } = require('./comprobante-telegram');
//
//   2) Donde HOY llamas enqueueComprobantePDF(room, student) al recibir la
//      entrega del alumno, agrega justo debajo:
//        sendComprobanteTelegram(room, student, {
//          getBrowser: getPdfBrowser,          // reusa tu navegador Puppeteer
//          port: PORT,                         // sirve /fonts/tercial-fonts.css
//          token: process.env.TELEGRAM_BOT_TOKEN,
//          getChatId: (s) => s.telegramChatId, // ← mapea alumno → chat (ver abajo)
//        });
//
//   3) Variables de entorno:
//        TELEGRAM_BOT_TOKEN=123456:ABC...        (de @BotFather)
//        TELEGRAM_CHAT_ID=-1001234567890         (fallback: grupo/clase o tu chat)
//
// ── ¿De dónde sale el chat de cada alumno? ──────────────────
//   Telegram NO permite escribir a alguien por nombre; necesitas su chat_id.
//   Opciones:
//     a) El alumno (o su tutor) le escribe /start a tu bot una vez; guardas el
//        chat_id que llega en el update y lo asocias a su nombre.
//     b) Mientras tanto, omite getChatId y todo se manda a TELEGRAM_CHAT_ID
//        (p. ej. el grupo del salón o tu propio chat) — útil para probar ya.
//
// Node 18+ (fetch / FormData / Blob globales). Sin dependencias nuevas.
// ============================================================

// Colores por nivel (tono apagado del sistema, el aprobado en el diseño).
const OK = '#4a6b3f';      // domina ≥70%
const WARN = '#8a5208';    // en proceso 50–69%
const ERR = '#9c3525';     // requiere atención <50%
const lvlColor = (p) => (p >= 70 ? OK : p >= 50 ? WARN : ERR);

const esc = (s) =>
  String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// ── Extrae resultado + desglose por materia desde room/student ──
// Misma lógica de puntaje que getStudentSummary()/buildComprobanteHTML():
// la clave correcta puede venir remapeada por alumno (student.answerKey).
function computeResultados(room, student) {
  const answers = student.answers || {};
  const ak = student.answerKey || {};
  const subjects = {};
  let correct = 0;
  let total = 0;

  room.questions.forEach((q) => {
    const key = ak[q.id] != null ? ak[q.id] : room.answerKey[q.id];
    const ok = answers[q.id] === key;
    total++;
    if (ok) correct++;
    const s = q.subject;
    if (!subjects[s]) subjects[s] = { name: s, correct: 0, total: 0 };
    subjects[s].total++;
    if (ok) subjects[s].correct++;
  });

  const list = Object.values(subjects).map((s) => ({
    ...s,
    pct: s.total ? Math.round((s.correct / s.total) * 100) : 0,
  }));
  list.sort((a, b) => b.pct - a.pct); // fuerte → débil

  const pct = total ? Math.round((correct / total) * 100) : 0;
  const dominadas = list.filter((s) => s.pct >= 70).length;
  const enProceso = list.filter((s) => s.pct >= 50 && s.pct < 70).length;

  let timeStr = '—';
  if (student.submitTime && student.startTime) {
    const used = Math.floor((student.submitTime - student.startTime) / 1000);
    const h = Math.floor(used / 3600);
    const m = Math.floor((used % 3600) / 60);
    const sec = used % 60;
    timeStr = h > 0 ? `${h}h ${m}m` : `${m}m ${sec}s`;
  }

  return { correct, total, pct, dominadas, enProceso, subjects: list, timeStr };
}

function subjectRow(s) {
  return `<div style="margin-bottom:11px">
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px">
        <span style="font:500 13px 'IBM Plex Sans';color:#4a3f33">${esc(s.name)}</span>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:11.5px;color:#8c7556;font-variant-numeric:tabular-nums">${s.pct}%</span>
      </div>
      <div style="height:6px;background:#efe7d8;border-radius:999px;overflow:hidden">
        <div style="width:${s.pct}%;height:100%;background:${lvlColor(s.pct)}"></div>
      </div>
    </div>`;
}

// ── HTML de la TARJETA CORTA (id="card" para recortar el screenshot) ──
function buildPortadaCortaHTML(room, student, opts = {}) {
  const port = opts.port || 3000;
  const origin = opts.origin || `http://localhost:${port}`;
  const r = computeResultados(room, student);

  const fecha = new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric' });
  const lede =
    r.enProceso > 0
      ? `Vas por buen camino — afina ${r.enProceso === 1 ? 'la materia que quedó' : `las ${r.enProceso} que quedaron`} en proceso.`
      : '¡Sin materias pendientes!';

  return `<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<base href="${origin}/">
<link rel="stylesheet" href="${origin}/fonts/tercial-fonts.css">
<style>
  * { margin:0; box-sizing:border-box; }
  html,body { background:#cdc3b0; }
  body { font-family:'IBM Plex Sans',sans-serif; -webkit-font-smoothing:antialiased; padding:28px; }
  #card { width:760px; background:#fdfbf6; border:1px solid #e6dcc4; border-top:3px solid #2d4f7a;
          border-radius:2px; padding:42px 46px; }
</style></head><body>
<div id="card">

  <header style="margin-bottom:28px">
    <p style="font:500 11px 'IBM Plex Sans';letter-spacing:.1em;text-transform:uppercase;color:#8c7556;margin:0 0 12px">Comprobante de examen · ${esc(room.group || 'Ingreso a nivel medio superior')}</p>
    <h2 style="font-family:'Fraunces',serif;font-weight:500;font-size:36px;letter-spacing:-.02em;color:#1f1a16;font-variation-settings:'opsz' 96;margin:0 0 10px">${esc(room.title || 'ECOEMS')}</h2>
    <p style="font:400 14px 'IBM Plex Sans';color:#7a6448;margin:0"><strong style="font-weight:600;color:#4a3f33">${esc(student.name)}</strong> · ${fecha} · Tiempo ${esc(r.timeStr)}</p>
  </header>

  <div style="border-top:1px solid #8c7556;padding-top:26px;display:grid;grid-template-columns:auto 1fr;gap:40px;align-items:start">
    <div>
      <p style="font:500 11px 'IBM Plex Sans';letter-spacing:.16em;text-transform:uppercase;color:#8c7556;margin:0 0 6px">Resultado</p>
      <div style="font-family:'Fraunces',serif;font-style:italic;font-weight:500;font-size:118px;line-height:.8;color:#c2410c;font-variation-settings:'opsz' 144;letter-spacing:-.03em">${r.correct}</div>
      <p style="font-family:'IBM Plex Mono',monospace;font-size:15px;color:#4a3f33;margin:12px 0 0;font-variant-numeric:tabular-nums">/ ${r.total} · ${r.pct}%</p>
      <h3 style="font-family:'Fraunces',serif;font-weight:500;font-size:22px;line-height:1.25;color:#1f1a16;margin:20px 0 0;max-width:210px">Dominaste <em style="font-style:italic;color:#c2410c">${r.dominadas} de ${r.subjects.length}</em> materias.</h3>
      <p style="font:400 13px 'IBM Plex Sans';line-height:1.5;color:#7a6448;margin:9px 0 0;max-width:215px">${lede}</p>
    </div>
    <div style="padding-top:6px">
      ${r.subjects.map(subjectRow).join('\n      ')}
    </div>
  </div>

  <div style="display:flex;gap:20px;flex-wrap:wrap;margin-top:24px;padding-top:16px;border-top:1px dotted #d9ccae">
    <span style="display:inline-flex;align-items:center;gap:6px;font:400 11px 'IBM Plex Sans';color:#7a6448"><span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:#4a6b3f"></span>Domina ≥70%</span>
    <span style="display:inline-flex;align-items:center;gap:6px;font:400 11px 'IBM Plex Sans';color:#7a6448"><span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:#8a5208"></span>En proceso 50–69%</span>
    <span style="display:inline-flex;align-items:center;gap:6px;font:400 11px 'IBM Plex Sans';color:#7a6448"><span style="display:inline-block;width:9px;height:9px;border-radius:2px;background:#9c3525"></span>Requiere atención &lt;50%</span>
  </div>

</div>
</body></html>`;
}

// ── Screenshot de la tarjeta a PNG (Buffer) con tu navegador Puppeteer ──
async function renderCardPNG(browser, html) {
  const page = await browser.newPage();
  try {
    await page.setViewport({ width: 820, height: 1200, deviceScaleFactor: 2 });
    await page.setContent(html, { waitUntil: 'networkidle0', timeout: 30000 });
    await page.evaluate(() => document.fonts.ready); // fuentes Tercial antes de capturar
    const el = await page.$('#card');
    const png = await el.screenshot({ type: 'png' });
    return png;
  } finally {
    try { await page.close(); } catch (e) {}
  }
}

// ── Envío a Telegram (sendPhoto, multipart con fetch global) ──
async function telegramSendPhoto(token, chatId, pngBuffer, caption, filename) {
  const form = new FormData();
  form.append('chat_id', String(chatId));
  if (caption) form.append('caption', caption);
  form.append('photo', new Blob([pngBuffer], { type: 'image/png' }), filename || 'comprobante.png');
  const resp = await fetch(`https://api.telegram.org/bot${token}/sendPhoto`, { method: 'POST', body: form });
  const data = await resp.json().catch(() => ({}));
  if (!data.ok) throw new Error(`Telegram: ${data.description || resp.status}`);
  return data;
}

// ── Cola secuencial + dedup propias (no chocan con la cola de PDF) ──
const tgQueue = [];
let tgRunning = false;
const tgSent = new Set();

async function runTgQueue() {
  if (tgRunning) return;
  tgRunning = true;
  while (tgQueue.length) {
    const task = tgQueue.shift();
    try { await task(); } catch (e) { console.error('Telegram task error:', e.message); }
  }
  tgRunning = false;
}

/**
 * Encola el envío de la tarjeta corta del alumno por Telegram.
 * Llama esto justo después de enqueueComprobantePDF(room, student).
 *
 * @param {Object} room     sala (room.title, room.group, room.questions, room.answerKey, room.date)
 * @param {Object} student  alumno (student.name, student.answers, student.answerKey, tiempos)
 * @param {Object} opts
 *   opts.getBrowser  {() => Promise<Browser>}  reusa tu getPdfBrowser (recomendado)
 *   opts.token       {string}  TELEGRAM_BOT_TOKEN
 *   opts.port        {number}  PORT (para servir las fuentes); default 3000
 *   opts.getChatId   {(student, room) => string|number|null}  alumno → chat_id
 *   opts.chatId      {string|number}  fallback fijo (TELEGRAM_CHAT_ID)
 *   opts.caption     {(room, student, r) => string}  texto opcional del mensaje
 */
function sendComprobanteTelegram(room, student, opts = {}) {
  if (!student || !student.submitted || !student.name) return;

  const token = opts.token || process.env.TELEGRAM_BOT_TOKEN;
  if (!token) { console.warn('[telegram] sin TELEGRAM_BOT_TOKEN — omito envío'); return; }

  const key = `${room.roomCode}:${student.name.toLowerCase()}`;
  if (tgSent.has(key)) return;       // dedup: una vez por alumno
  tgSent.add(key);

  tgQueue.push(async () => {
    try {
      const chatId =
        (opts.getChatId && opts.getChatId(student, room)) ||
        opts.chatId || process.env.TELEGRAM_CHAT_ID;
      if (!chatId) { console.warn(`[telegram] sin chat para ${student.name} — omito`); tgSent.delete(key); return; }

      const browser = opts.getBrowser ? await opts.getBrowser() : null;
      if (!browser) throw new Error('falta opts.getBrowser (navegador Puppeteer)');

      const html = buildPortadaCortaHTML(room, student, { port: opts.port });
      const png = await renderCardPNG(browser, html);

      const r = computeResultados(room, student);
      const caption = opts.caption
        ? opts.caption(room, student, r)
        : `📋 ${room.title || 'Examen'} — ${student.name}\nResultado: ${r.correct}/${r.total} (${r.pct}%)`;

      await telegramSendPhoto(token, chatId, png, caption, `comprobante_${student.name}.png`);
      console.log(`[telegram] enviado a ${student.name} (${r.correct}/${r.total})`);
    } catch (err) {
      console.error(`[telegram] falló para ${student.name}:`, err.message);
      tgSent.delete(key); // permite reintento
    }
  });
  runTgQueue();
}

module.exports = { sendComprobanteTelegram, buildPortadaCortaHTML, computeResultados };
