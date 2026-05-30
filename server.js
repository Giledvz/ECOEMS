const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const fs = require('fs');
const os = require('os');
const QRCode = require('qrcode');
const katex = require('katex');
const puppeteer = require('puppeteer');

const PORT = 3000;
const app = express();
const server = http.createServer(app);
const io = new Server(server);

// Branch de git para badge ambiente (dev vs main) en el cliente.
let GIT_BRANCH = 'unknown';
try {
  const { execSync } = require('child_process');
  GIT_BRANCH = execSync('git rev-parse --abbrev-ref HEAD', { cwd: __dirname, encoding: 'utf8' }).trim();
} catch (e) {}
console.log(`Branch: ${GIT_BRANCH}`);

app.use(express.static(path.join(__dirname, 'public'), { etag: false, maxAge: 0, setHeaders: (res) => { res.setHeader('Cache-Control', 'no-store'); } }));
app.use('/katex', express.static(path.join(__dirname, 'node_modules/katex/dist')));
app.use(express.json({ limit: '10mb' }));

// ─── Shuffle (Fisher-Yates) ──────────────────────────────────────────────────
function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// ─── Multi-Room State ───────────────────────────────────────────────────────
const rooms = new Map();       // roomCode -> room state
const socketRoom = new Map();  // socket.id -> roomCode

function generateRoomCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code;
  do {
    code = '';
    for (let i = 0; i < 6; i++) code += chars[Math.floor(Math.random() * chars.length)];
  } while (rooms.has(code));
  return code;
}

function createRoom(data, jsonFilename = null, lockedOptions = false) {
  const roomCode = generateRoomCode();
  const room = {
    roomCode,
    phase: 'waiting',
    title: data.exam?.title || 'Examen',
    group: data.exam?.group || 'Sin grupo',
    date: data.exam?.date || new Date().toISOString().split('T')[0],
    studentList: data.exam?.students || [],
    questions: [],
    answerKey: {},
    students: {},
    timeLimitMinutes: data.timeLimitMinutes || 180,
    startTime: null,
    jsonFilename,
    lockedOptions: !!lockedOptions,
  };

  const sections = data.exam?.sections || [];
  sections.forEach(section => {
    section.questions.forEach(q => {
      room.questions.push({
        id: q.id,
        text: q.text,
        context: q.context || null,
        options: q.options,
        option_images: q.option_images || null,
        image: q.image || null,
        topic: q.topic,
        topic_name: q.topic_name || '',
        subject: section.subject,
        explanation: q.explanation || '',
      });
      room.answerKey[q.id] = q.answer;
    });
  });

  rooms.set(roomCode, room);
  return room;
}

function buildRoomsList() {
  const list = [];
  rooms.forEach(room => {
    list.push({
      roomCode: room.roomCode,
      title: room.title,
      group: room.group,
      phase: room.phase,
      totalQuestions: room.questions.length,
      studentCount: Object.values(room.students).filter(s => s.connected).length,
    });
  });
  return list;
}

function broadcastRoomsList() {
  io.to('teachers').emit('roomsList', buildRoomsList());
}

function getStudentSummary(room) {
  return Object.entries(room.students).map(([id, s]) => {
    let correct = 0;
    if (s.submitted) {
      room.questions.forEach(q => {
        const key = s.answerKey?.[q.id] ?? room.answerKey[q.id];
        if (s.answers[q.id] === key) correct++;
      });
    }
    const timeUsed = s.submitted && s.submitTime && s.startTime
      ? Math.round((s.submitTime - s.startTime) / 1000)
      : null;
    return {
      id,
      name: s.name,
      group: s.group,
      answered: Object.keys(s.answers).length,
      total: room.questions.length,
      marked: s.marked.length,
      submitted: s.submitted,
      connected: s.connected,
      correct: s.submitted ? correct : null,
      timeUsed,
      tabSwitches: s.tabSwitches || 0,
      cancelled: !!s.cancelled,
    };
  });
}

function generateCSV(room) {
  if (room.questions.length === 0) return '';

  const questionIds = room.questions.map(q => q.id);
  const fecha = room.date || new Date().toISOString().split('T')[0];
  let header = 'Fecha,Alumno,Grupo,Tiempo_min,Salidas_pestaña';
  questionIds.forEach(id => { header += `,P${id}`; });
  header += '\n';

  let rows = '';
  Object.values(room.students).forEach(s => {
    const timeMin = s.submitted && s.submitTime && s.startTime
      ? Math.round((s.submitTime - s.startTime) / 60000)
      : '';
    let row = `${fecha},${s.name},${s.group},${timeMin},${s.tabSwitches || 0}`;
    questionIds.forEach(id => {
      const ans = s.answers[id];
      if (!ans || !s.optionOrders?.[id]) {
        row += `,${ans || ''}`;
      } else {
        const origLetters = Object.keys(room.questions.find(q => q.id === id).options);
        row += `,${s.optionOrders[id][origLetters.indexOf(ans)] || ''}`;
      }
    });
    rows += row + '\n';
  });

  return header + rows;
}

function generateAnswerKeyCSV(room) {
  if (room.questions.length === 0) return '';
  let header = 'Pregunta,Asignatura,Tema,Tema_nombre,Respuesta_correcta\n';
  let rows = '';
  room.questions.forEach(q => {
    rows += `P${q.id},${q.subject},${q.topic},"${q.topic_name}",${room.answerKey[q.id]}\n`;
  });
  return header + rows;
}

function getLocalIP() {
  const nets = os.networkInterfaces();
  for (const ifaces of Object.values(nets)) {
    for (const iface of ifaces) {
      if (iface.family === 'IPv4' && !iface.internal) return iface.address;
    }
  }
  return 'localhost';
}

// ─── API Endpoints ──────────────────────────────────────────────────────────

// Teacher uploads exam JSON → creates a new room
// Versión del server (branch de git) — cliente la usa para mostrar badge ambiente.
app.get('/api/version', (_req, res) => {
  res.json({ branch: GIT_BRANCH });
});

app.post('/api/upload-exam', (req, res) => {
  try {
    const filename = req.headers['x-exam-filename'] || null;
    const lockedOptions = req.headers['x-locked-options'] === '1';
    const room = createRoom(req.body, filename, lockedOptions);
    console.log(`Sala ${room.roomCode} creada: "${room.title}" (${room.questions.length} preguntas${lockedOptions ? ', candado activado' : ''})${filename ? ` [archivo: ${filename}]` : ''}`);
    broadcastRoomsList();
    res.json({ success: true, totalQuestions: room.questions.length, roomCode: room.roomCode });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// DEV ONLY: re-read the JSON file from disk and update room.questions/answerKey
// without resetting students, answers, or phase. Bloqueado en fase 'active'.
app.post('/api/dev-reload/:roomCode', (req, res) => {
  const room = rooms.get(req.params.roomCode);
  if (!room) return res.status(404).json({ error: 'Sala no encontrada' });
  if (room.phase === 'active') return res.status(400).json({ error: 'No se puede recargar con el examen activo' });
  if (!room.jsonFilename) return res.status(400).json({ error: 'Sala sin archivo asociado (re-súbela)' });

  const filepath = path.join(__dirname, room.jsonFilename);
  if (!fs.existsSync(filepath)) return res.status(404).json({ error: `No encuentro: ${room.jsonFilename}` });

  let data;
  try { data = JSON.parse(fs.readFileSync(filepath, 'utf8')); }
  catch (err) { return res.status(400).json({ error: `JSON inválido: ${err.message}` }); }

  const newQuestions = [];
  const newAnswerKey = {};
  (data.exam?.sections || []).forEach(section => {
    (section.questions || []).forEach(q => {
      newQuestions.push({
        id: q.id, text: q.text, context: q.context || null,
        options: q.options, image: q.image || null,
        topic: q.topic, topic_name: q.topic_name || '',
        subject: section.subject, explanation: q.explanation || '',
      });
      newAnswerKey[q.id] = q.answer;
    });
  });

  // Validar que la estructura no cambió (#preguntas e IDs iguales)
  if (newQuestions.length !== room.questions.length) {
    return res.status(400).json({ error: `El número de preguntas cambió (${room.questions.length} → ${newQuestions.length}). Re-súbelo como sala nueva.` });
  }
  const oldIds = room.questions.map(q => q.id).join(',');
  const newIds = newQuestions.map(q => q.id).join(',');
  if (oldIds !== newIds) {
    return res.status(400).json({ error: 'Los IDs de las preguntas cambiaron. Re-súbelo como sala nueva.' });
  }

  // Reemplazar contenido
  room.questions = newQuestions;
  room.answerKey = newAnswerKey;
  room.title = data.exam?.title || room.title;
  room.group = data.exam?.group || room.group;

  // Limpiar dedup de la clave para que se regenere con el contenido nuevo
  pdfEnqueued.delete(`${room.roomCode}:__answerkey__`);

  // Notificar a los clientes de esa sala que recarguen su página
  io.to(room.roomCode).emit('examReloaded');

  console.log(`[${room.roomCode}] JSON recargado desde ${room.jsonFilename}`);
  res.json({ success: true });
});

// List all rooms
app.get('/api/rooms', (_req, res) => {
  const list = [];
  rooms.forEach(room => {
    list.push({
      roomCode: room.roomCode,
      title: room.title,
      group: room.group,
      phase: room.phase,
      totalQuestions: room.questions.length,
      studentCount: Object.keys(room.students).length,
    });
  });
  res.json(list);
});

// Download CSV results
app.get('/api/download-csv', (req, res) => {
  const room = rooms.get(req.query.room);
  if (!room) return res.status(404).json({ error: 'Sala no encontrada' });

  const csv = generateCSV(room);
  const [y, m, d] = (room.date || new Date().toISOString().split('T')[0]).split('-');
  const filename = `resultados_${room.roomCode}_${d}${m}${y.slice(2)}.csv`;
  fs.writeFileSync(path.join(__dirname, filename), '\uFEFF' + csv, 'utf8');
  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', `attachment; filename=${filename}`);
  res.send('\uFEFF' + csv);
});

// Download answer key CSV
app.get('/api/download-key', (req, res) => {
  const room = rooms.get(req.query.room);
  if (!room) return res.status(404).json({ error: 'Sala no encontrada' });

  const csv = generateAnswerKeyCSV(room);
  const fecha = (room.date || new Date().toISOString().split('T')[0]).replace(/-/g, '');
  const filename = `clave_respuestas_${room.roomCode}_${fecha}.csv`;
  fs.writeFileSync(path.join(__dirname, filename), '\uFEFF' + csv, 'utf8');
  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', `attachment; filename=${filename}`);
  res.send('\uFEFF' + csv);
});

// QR code (includes room code if provided)
app.get('/api/qr', async (req, res) => {
  const localIP = getLocalIP();
  let url = `http://${localIP}:${PORT}`;
  if (req.query.room) url += `?sala=${req.query.room}`;
  try {
    const dataUrl = await QRCode.toDataURL(url, { width: 256, margin: 2, color: { dark: '#0f172a', light: '#ffffff' } });
    res.json({ qr: dataUrl, url });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Teacher page
app.get('/teacher', (_req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'teacher.html'));
});

// ─── Comprobante PDF (server-side render con Puppeteer) ────────────────────

// Replica de renderMath() en /public/index.html (mismas reglas para KaTeX,
// markdown ligero, tablas y escape HTML).
function renderInlineMath(text) {
  const parts = text.split(/(\$\$[\s\S]+?\$\$|\$[^$\n]+?\$)/g);
  return parts.map(p => {
    const isDisplay = p.indexOf('$$') === 0 && p.lastIndexOf('$$') === p.length - 2 && p.length >= 4;
    const isInline = !isDisplay && p.length >= 2 && p.charAt(0) === '$' && p.charAt(p.length - 1) === '$' && p.indexOf('\n') === -1;
    if (isDisplay || isInline) {
      const inner = isDisplay ? p.slice(2, -2) : p.slice(1, -1);
      try { return katex.renderToString(inner, { throwOnError: false, displayMode: false, macros: { "\\sen": "\\operatorname{sen}", "\\tg": "\\operatorname{tg}" } }); }
      catch (e) { return inner.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
    }
    return p.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/&lt;(\/?(u|b|i|strong|em))&gt;/g, '<$1>')
      .replace(/&lt;br\s*\/?&gt;/g, '<br>')
      .replace(/&lt;img\s+([^&]*?)\/?&gt;/g, '<img $1 style="max-width:100%;height:auto;">')
      .replace(/_{3,}/g, m => `<span style="display:inline-block; width:${(m.length * 0.85).toFixed(2)}em; height:2.5px; background-color:currentColor; vertical-align:-0.08em; margin:0 0.18em;"></span>`)
      .replace(/\*\*([^*\n]+?)\*\*/g, '<b>$1</b>');
  }).join('');
}

function renderMarkdownTable(block) {
  const lines = block.split('\n').map(l => l.trim()).filter(l => l.length > 0);
  if (lines.length < 2) return block;
  const parseCells = line => line.replace(/^\||\|$/g, '').split('|').map(c => c.trim());
  const header = parseCells(lines[0]);
  const body = lines.slice(2).map(parseCells);
  const cellStyle = 'border:1px solid #cbd5e0; padding:6px 12px; text-align:center;';
  const headStyle = cellStyle + ' background:#edf2f7; font-weight:600;';
  const thead = '<thead><tr>' + header.map(c => `<th style="${headStyle}">${renderInlineMath(c)}</th>`).join('') + '</tr></thead>';
  const tbody = '<tbody>' + body.map(row => '<tr>' + row.map(c => `<td style="${cellStyle}">${renderInlineMath(c)}</td>`).join('') + '</tr>').join('') + '</tbody>';
  return `<table style="border-collapse:collapse; margin:12px 0; font-size:inherit;">${thead}${tbody}</table>`;
}

function renderMath(text) {
  if (!text) return '';
  try {
    text = String(text).replace(/\\\$/g, '\x00DOLLAR\x00');
    const tables = [];
    text = text.replace(/(?:^|\n)(\|[^\n]+\|[ \t]*\n\|[-:\s|]+\|[ \t]*\n(?:\|[^\n]+\|[ \t]*(?:\n|$))+)/g, (match, block) => {
      const html = renderMarkdownTable(block);
      const idx = tables.push(html) - 1;
      return '\n\x00TBL' + idx + '\x00\n';
    });
    const parts = text.split(/(\$\$[\s\S]+?\$\$|\$[^$\n]+?\$)/g);
    let out = parts.map(part => {
      const isDisplay = part.indexOf('$$') === 0 && part.lastIndexOf('$$') === part.length - 2 && part.length >= 4;
      const isInline = !isDisplay && part.length >= 2 && part.charAt(0) === '$' && part.charAt(part.length - 1) === '$' && part.indexOf('\n') === -1;
      if (isDisplay || isInline) {
        const inner = isDisplay ? part.slice(2, -2) : part.slice(1, -1);
        try {
          return katex.renderToString(inner, { throwOnError: false, displayMode: isDisplay, macros: { "\\sen": "\\operatorname{sen}", "\\tg": "\\operatorname{tg}" } });
        } catch (e) {
          return inner.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        }
      }
      if (/<img\s/.test(part)) return part;
      return part
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/&lt;(\/?(u|b|i|strong|em))&gt;/g, '<$1>')
        .replace(/_{3,}/g, m => `<span style="display:inline-block; width:${(m.length * 0.85).toFixed(2)}em; height:2.5px; background-color:currentColor; vertical-align:-0.08em; margin:0 0.18em;"></span>`)
        .replace(/\*\*([^*\n]+?)\*\*/g, '<b>$1</b>')
        .replace(/\n/g, '<br>');
    }).join('');
    out = out.replace(/(?:<br>)?\x00TBL(\d+)\x00(?:<br>)?/g, (m, i) => tables[Number(i)]);
    return out.replace(/\x00DOLLAR\x00/g, '$');
  } catch (e) {
    return String(text).replace(/\$\$/g, '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\x00DOLLAR\x00/g, '$');
  }
}

// Construye el HTML del comprobante igual que _downloadPDFImpl() del cliente.
function buildComprobanteHTML(room, student) {
  const origin = `http://localhost:${PORT}`;

  const questionsForStudent = student.questionOrder.map(qid => {
    const q = room.questions.find(x => x.id === qid);
    const origLetters = Object.keys(q.options);
    const srcLetters = student.optionOrders[qid];
    const newOptions = {};
    origLetters.forEach((newLetter, i) => {
      newOptions[newLetter] = q.options[srcLetters[i]];
    });
    const newOptionImages = q.option_images ? {} : null;
    if (newOptionImages) {
      origLetters.forEach((newLetter, i) => {
        newOptionImages[newLetter] = q.option_images[srcLetters[i]] || null;
      });
    }
    return {
      id: q.id,
      text: q.text,
      options: newOptions,
      option_images: newOptionImages,
      image: q.image,
      subject: q.subject,
      topic_name: q.topic_name,
    };
  });

  const answerKey = student.answerKey || {};
  const answers = student.answers || {};
  const total = questionsForStudent.length;
  let correct = 0;
  questionsForStudent.forEach(q => { if (answers[q.id] === answerKey[q.id]) correct++; });

  let timeStr = '—';
  if (student.submitTime && student.startTime) {
    const used = Math.floor((student.submitTime - student.startTime) / 1000);
    const h = Math.floor(used / 3600);
    const m = Math.floor((used % 3600) / 60);
    const s = used % 60;
    timeStr = h > 0 ? `${h}h ${m}m` : `${m}m ${s}s`;
  }

  const fecha = new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric' });

  const subjects = {};
  questionsForStudent.forEach(q => {
    const key = q.subject;
    if (!subjects[key]) subjects[key] = { total: 0, correct: 0 };
    subjects[key].total++;
    if (answers[q.id] === answerKey[q.id]) subjects[key].correct++;
  });
  const sortedSubjects = Object.entries(subjects).sort((a, b) => (b[1].correct / b[1].total) - (a[1].correct / a[1].total));
  const subjectRowsHTML = sortedSubjects.map(([name, data]) => {
    const pct = Math.round((data.correct / data.total) * 100);
    const barColor = pct >= 70 ? '#16a34a' : pct >= 50 ? '#eab308' : '#e53e3e';
    const pctColor = pct >= 70 ? '#16a34a' : pct >= 50 ? '#a16207' : '#e53e3e';
    return `
      <div style="margin-bottom:10px;">
        <div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:3px;">
          <span style="font-size:12px; color:#555; flex:1; padding-right:8px;">${name}</span>
          <span style="font-size:12px; font-weight:700; margin-left:8px; color:${pctColor};">${pct}%</span>
        </div>
        <div style="height:7px; background:#ebebeb; border-radius:4px; overflow:hidden;">
          <div style="height:100%; width:${pct}%; background:${barColor}; border-radius:4px;"></div>
        </div>
        <div style="font-size:10px; color:#999; margin-top:2px;">${data.correct} de ${data.total} preguntas correctas</div>
      </div>`;
  }).join('');
  const topicBreakdownHTML = sortedSubjects.length > 0 ? `
    <div style="margin:20px auto; max-width:480px; page-break-inside:avoid;">
      <h3 style="font-size:14px; font-weight:600; margin-bottom:12px; text-align:center; color:#444;">Desempeño por materia</h3>
      ${subjectRowsHTML}
    </div>` : '';

  const questionsHTML = questionsForStudent.map((q, idx) => {
    const mine = answers[q.id];
    const correctAns = answerKey[q.id];
    const letters = Object.keys(q.options);
    const optionsHTML = letters.map(letter => {
      const isCorrect = letter === correctAns;
      const isMine = letter === mine;
      let style = 'padding:6px 10px; margin:2px 0; border-radius:6px; font-size:12px;';
      let marker = '';
      if (isCorrect && isMine) { style += ' background:#dcfce7; border:1px solid #16a34a;'; marker = ' ✓ (tu respuesta)'; }
      else if (isCorrect) { style += ' background:#dcfce7; border:1px solid #16a34a;'; marker = ' ✓'; }
      else if (isMine) { style += ' background:#fef2f2; border:1px solid #e53e3e;'; marker = ' ✗ (tu respuesta)'; }
      else { style += ' background:#f8f8f8; border:1px solid #e5e5e5;'; }
      const optImg = q.option_images && q.option_images[letter]
        ? `<img src="${q.option_images[letter]}" style="max-width:140px;max-height:80px;margin-left:8px;vertical-align:middle;display:inline-block;">`
        : '';
      return `<div style="${style}"><b>${letter}.</b> ${renderMath(q.options[letter])}${optImg}${marker}</div>`;
    }).join('');

    let qText = q.text || '';
    const maxLen = 1500;
    if (qText.length > maxLen) {
      const lastParagraph = qText.lastIndexOf('\n\n');
      if (lastParagraph > maxLen * 0.3) {
        const readingPart = qText.substring(0, lastParagraph);
        const questionPart = qText.substring(lastParagraph);
        qText = readingPart.substring(0, 300) + '\n\n[...]\n\n' + questionPart;
      }
    }
    const imgHTML = q.image ? `<img src="${q.image}" style="max-width:280px; max-height:200px; margin:6px 0; display:block;">` : '';

    return `
      <div style="page-break-inside:avoid; margin-bottom:14px; padding:10px; border:1px solid #e5e5e5; border-radius:8px;">
        <div style="font-size:11px; color:#666; margin-bottom:4px;">${q.subject} — Pregunta ${idx + 1}</div>
        <div style="font-size:13px; margin-bottom:6px;">${renderMath(qText)}</div>
        ${imgHTML}
        ${optionsHTML}
      </div>`;
  }).join('');

  return `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<base href="${origin}/">
<title>Comprobante — ${student.name}</title>
<link rel="stylesheet" href="${origin}/katex/katex.min.css">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding:20px; color:#1a1a1a; font-size:13px; }
  @page { margin:15mm 10mm; }
  .header { text-align:center; margin-bottom:20px; padding-bottom:14px; border-bottom:2px solid #2c5282; }
  .header h1 { font-size:20px; color:#2c5282; margin-bottom:4px; }
  .stats { display:flex; justify-content:center; gap:24px; margin-top:10px; font-size:14px; }
  .stat-box { text-align:center; }
  .stat-val { font-size:28px; font-weight:700; }
  .stat-label { font-size:11px; color:#666; }
</style></head><body>
<div class="header">
  <h1>${room.title || 'Examen'}</h1>
  <div style="font-size:15px; font-weight:600; margin-top:2px;">${student.name}</div>
  <div style="font-size:12px; color:#666;">${room.group} — ${fecha}</div>
  <div style="display:flex; justify-content:center; margin:16px 0 10px;">
    <div style="width:160px; height:160px; border-radius:50%; display:flex; flex-direction:column; align-items:center; justify-content:center; font-weight:700; background:${correct >= 95 ? '#dcfce7' : correct >= 51 ? '#fef9c3' : '#fef2f2'}; color:${correct >= 95 ? '#16a34a' : correct >= 51 ? '#a16207' : '#e53e3e'};">
      <span style="font-size:46px; line-height:1;">${correct}</span>
      <span style="font-size:13px; font-weight:500; opacity:0.8; margin-top:4px;">de ${total} aciertos</span>
    </div>
  </div>
  <div class="stats">
    <div class="stat-box"><div class="stat-val">${total > 0 ? Math.round(correct / total * 100) : 0}%</div><div class="stat-label">calificación</div></div>
    <div class="stat-box"><div class="stat-val" style="font-size:20px; margin-top:6px;">${timeStr}</div><div class="stat-label">tiempo</div></div>
  </div>
</div>
${topicBreakdownHTML}
${questionsHTML}
</body></html>`;
}

function buildAnswerKeyHTML(room) {
  const origin = `http://localhost:${PORT}`;
  const questions = room.questions;
  const answerKey = room.answerKey;
  const fecha = new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric' });

  const questionsHTML = questions.map((q, idx) => {
    const correctAns = answerKey[q.id];
    const letters = Object.keys(q.options);
    const optionsHTML = letters.map(letter => {
      const isCorrect = letter === correctAns;
      let style = 'padding:6px 10px; margin:2px 0; border-radius:6px; font-size:12px;';
      let marker = '';
      if (isCorrect) { style += ' background:#dcfce7; border:1px solid #16a34a;'; marker = ' ✓'; }
      else { style += ' background:#f8f8f8; border:1px solid #e5e5e5;'; }
      const optImg = q.option_images && q.option_images[letter]
        ? `<img src="${q.option_images[letter]}" style="max-width:140px;max-height:80px;margin-left:8px;vertical-align:middle;display:inline-block;">`
        : '';
      return `<div style="${style}"><b>${letter}.</b> ${renderMath(q.options[letter])}${optImg}${marker}</div>`;
    }).join('');

    let qText = q.text || '';
    const maxLen = 1500;
    if (qText.length > maxLen) {
      const lastParagraph = qText.lastIndexOf('\n\n');
      if (lastParagraph > maxLen * 0.3) {
        const readingPart = qText.substring(0, lastParagraph);
        const questionPart = qText.substring(lastParagraph);
        qText = readingPart.substring(0, 300) + '\n\n[...]\n\n' + questionPart;
      }
    }
    const imgHTML = q.image ? `<img src="${q.image}" style="max-width:280px; max-height:200px; margin:6px 0; display:block;">` : '';

    return `
      <div style="page-break-inside:avoid; margin-bottom:14px; padding:10px; border:1px solid #e5e5e5; border-radius:8px;">
        <div style="font-size:11px; color:#666; margin-bottom:4px;">${q.subject} — Pregunta ${idx + 1}</div>
        <div style="font-size:13px; margin-bottom:6px;">${renderMath(qText)}</div>
        ${imgHTML}
        ${optionsHTML}
      </div>`;
  }).join('');

  return `<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<base href="${origin}/">
<title>Clave de respuestas — ${room.title || 'Examen'}</title>
<link rel="stylesheet" href="${origin}/katex/katex.min.css">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding:20px; color:#1a1a1a; font-size:13px; }
  @page { margin:15mm 10mm; }
  .header { text-align:center; margin-bottom:20px; padding-bottom:14px; border-bottom:2px solid #2c5282; }
  .header h1 { font-size:20px; color:#2c5282; margin-bottom:4px; }
  .header h2 { font-size:16px; color:#16a34a; margin-top:10px; font-weight:600; }
</style></head><body>
<div class="header">
  <h1>${room.title || 'Examen'}</h1>
  <div style="font-size:12px; color:#666;">${room.group} — ${fecha}</div>
  <h2>Clave de respuestas</h2>
</div>
${questionsHTML}
</body></html>`;
}

// Manager: navegador único, cola secuencial, dedup por (sala, alumno).
let pdfBrowser = null;
const pdfQueue = [];
let pdfQueueRunning = false;
const pdfEnqueued = new Set();

async function getPdfBrowser() {
  if (pdfBrowser && pdfBrowser.connected !== false) return pdfBrowser;
  pdfBrowser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  return pdfBrowser;
}

async function runPdfQueue() {
  if (pdfQueueRunning) return;
  pdfQueueRunning = true;
  while (pdfQueue.length > 0) {
    const task = pdfQueue.shift();
    try { await task(); } catch (e) { console.error('PDF queue task error:', e); }
  }
  pdfQueueRunning = false;
}

function safeFilename(name) {
  return String(name).replace(/[^\wÀ-ſ]+/g, '_').substring(0, 60) || 'alumno';
}

function enqueueComprobantePDF(room, student) {
  if (!student || !student.submitted || !student.name) return;
  const key = `${room.roomCode}:${student.name.toLowerCase()}`;
  if (pdfEnqueued.has(key)) return;
  pdfEnqueued.add(key);

  pdfQueue.push(async () => {
    let page = null;
    try {
      const browser = await getPdfBrowser();
      page = await browser.newPage();
      const html = buildComprobanteHTML(room, student);
      await page.setContent(html, { waitUntil: 'networkidle0', timeout: 30000 });
      const dateStr = (room.date || new Date().toISOString().split('T')[0]).replace(/-/g, '');
      const folder = path.join(__dirname, 'comprobantes', `${room.roomCode}_${dateStr}`);
      fs.mkdirSync(folder, { recursive: true });
      const filePath = path.join(folder, `${safeFilename(student.name)}.pdf`);
      await page.pdf({
        path: filePath,
        format: 'A4',
        margin: { top: '15mm', bottom: '15mm', left: '10mm', right: '10mm' },
        printBackground: true,
      });
      console.log(`[${room.roomCode}] PDF guardado: ${path.relative(__dirname, filePath)}`);
    } catch (err) {
      console.error(`[${room.roomCode}] PDF falló para ${student.name}:`, err.message);
      pdfEnqueued.delete(key); // permite reintento
    } finally {
      if (page) { try { await page.close(); } catch (e) {} }
    }
  });
  runPdfQueue();
}

function enqueueAnswerKeyPDF(room) {
  if (!room) return;
  const key = `${room.roomCode}:__answerkey__`;
  if (pdfEnqueued.has(key)) return;
  pdfEnqueued.add(key);

  pdfQueue.push(async () => {
    let page = null;
    try {
      const browser = await getPdfBrowser();
      page = await browser.newPage();
      const html = buildAnswerKeyHTML(room);
      await page.setContent(html, { waitUntil: 'networkidle0', timeout: 30000 });
      const dateStr = (room.date || new Date().toISOString().split('T')[0]).replace(/-/g, '');
      const folder = path.join(__dirname, 'comprobantes', `${room.roomCode}_${dateStr}`);
      fs.mkdirSync(folder, { recursive: true });
      const filePath = path.join(folder, `clave_de_respuestas.pdf`);
      await page.pdf({
        path: filePath,
        format: 'A4',
        margin: { top: '15mm', bottom: '15mm', left: '10mm', right: '10mm' },
        printBackground: true,
      });
      console.log(`[${room.roomCode}] Clave de respuestas guardada: ${path.relative(__dirname, filePath)}`);
    } catch (err) {
      console.error(`[${room.roomCode}] Clave de respuestas falló:`, err.message);
      pdfEnqueued.delete(key);
    } finally {
      if (page) { try { await page.close(); } catch (e) {} }
    }
  });
  runPdfQueue();
}

// ─── Limpieza automática de comprobantes ────────────────────────────────────
// Borra archivos de alumnos en carpetas de comprobantes con más de N días.
// Conserva siempre `clave_de_respuestas.pdf`. Si la carpeta queda vacía, la borra.
const COMPROBANTES_RETENTION_DAYS = 14;

function cleanupOldComprobantes() {
  const root = path.join(__dirname, 'comprobantes');
  if (!fs.existsSync(root)) return;

  const now = Date.now();
  const cutoffMs = COMPROBANTES_RETENTION_DAYS * 24 * 60 * 60 * 1000;
  let filesDeleted = 0;
  let foldersTouched = 0;
  let foldersRemoved = 0;

  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    // Folder name format: <roomCode>_<YYYYMMDD>
    const m = entry.name.match(/_(\d{4})(\d{2})(\d{2})$/);
    if (!m) continue;
    const folderDate = new Date(`${m[1]}-${m[2]}-${m[3]}T00:00:00`);
    if (isNaN(folderDate.getTime())) continue;
    if (now - folderDate.getTime() < cutoffMs) continue;

    const folderPath = path.join(root, entry.name);
    let deletedHere = 0;
    for (const file of fs.readdirSync(folderPath)) {
      if (file === 'clave_de_respuestas.pdf') continue;
      try {
        fs.unlinkSync(path.join(folderPath, file));
        filesDeleted++;
        deletedHere++;
      } catch (err) {
        console.error(`[Cleanup] No pude borrar ${file}: ${err.message}`);
      }
    }
    if (deletedHere > 0) foldersTouched++;
    // Si la carpeta quedó vacía (sin clave tampoco), eliminarla
    try {
      if (fs.readdirSync(folderPath).length === 0) {
        fs.rmdirSync(folderPath);
        foldersRemoved++;
      }
    } catch (err) {}
  }

  if (filesDeleted > 0 || foldersRemoved > 0) {
    console.log(`[Cleanup] Borrados ${filesDeleted} comprobante(s) en ${foldersTouched} carpeta(s) (>${COMPROBANTES_RETENTION_DAYS} días). ${foldersRemoved} carpeta(s) vacía(s) eliminada(s).`);
  }
}

// Corre al arrancar (con pequeño delay para no bloquear el inicio) y cada 24h.
setTimeout(cleanupOldComprobantes, 5000);
setInterval(cleanupOldComprobantes, 24 * 60 * 60 * 1000);

process.on('SIGINT', async () => {
  if (pdfBrowser) { try { await pdfBrowser.close(); } catch (e) {} }
  process.exit(0);
});

// ─── Socket.io ──────────────────────────────────────────────────────────────
io.on('connection', (socket) => {

  // ── Join a room (student) ──
  socket.on('joinRoom', ({ roomCode }) => {
    const room = rooms.get(roomCode);
    if (!room) { socket.emit('joinRoomError', 'Sala no encontrada'); return; }

    socket.join(roomCode);
    socketRoom.set(socket.id, roomCode);

    socket.emit('roomJoined', {
      roomCode,
      phase: room.phase,
      title: room.title,
      group: room.group,
      studentList: room.studentList,
      totalQuestions: room.questions.length,
      startTime: room.startTime,
      timeLimit: room.timeLimitMinutes,
      lockedOptions: !!room.lockedOptions,
      serverTime: Date.now(),
    });
  });

  // ── Student joins exam within their room ──
  socket.on('joinExam', ({ name }) => {
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room) { socket.emit('joinError', 'Primero entra a una sala'); return; }

    if (room.phase === 'closed') { socket.emit('joinError', 'El examen ya fue cerrado'); return; }

    const cleanName = String(name).trim().substring(0, 30);
    if (!cleanName) { socket.emit('joinError', 'Selecciona tu nombre'); return; }

    if (room.studentList.length > 0) {
      const validName = room.studentList.find(s => s.toLowerCase() === cleanName.toLowerCase());
      if (!validName) { socket.emit('joinError', 'Tu nombre no está en la lista'); return; }
    }

    const nameExists = Object.values(room.students).some(
      s => s.name.toLowerCase() === cleanName.toLowerCase() && s.connected
    );
    if (nameExists) { socket.emit('joinError', 'Ese nombre ya está en uso'); return; }

    const prevEntry = Object.entries(room.students).find(
      ([id, s]) => s.name.toLowerCase() === cleanName.toLowerCase() && !s.connected
    );

    if (prevEntry) {
      const [oldId, oldData] = prevEntry;
      oldData.connected = true;
      room.students[socket.id] = oldData;
      delete room.students[oldId];
      console.log(`[${roomCode}] ${cleanName} reconectado`);
    } else {
      const questionsBySubject = {};
      room.questions.forEach(q => {
        if (!questionsBySubject[q.subject]) questionsBySubject[q.subject] = [];
        questionsBySubject[q.subject].push(q.id);
      });
      const shuffledSubjects = shuffle(Object.keys(questionsBySubject));
      const questionOrder = [];
      shuffledSubjects.forEach(subj => {
        questionsBySubject[subj].forEach(id => questionOrder.push(id));
      });

      const optionOrders = {};
      room.questions.forEach(q => {
        optionOrders[q.id] = shuffle(Object.keys(q.options));
      });

      room.students[socket.id] = {
        name: cleanName,
        group: room.group,
        answers: {},
        marked: [],
        submitted: false,
        connected: true,
        startTime: Date.now(),
        submitTime: null,
        questionOrder,
        optionOrders,
        answerKey: {},
        tabSwitches: 0,
        cancelled: false,
        joinedAt: Date.now(),
      };
    }

    const student = room.students[socket.id];
    const questionsForStudent = student.questionOrder.map(qid => {
      const q = room.questions.find(x => x.id === qid);
      const origLetters = Object.keys(q.options);
      const srcLetters = student.optionOrders[qid];

      const newOptions = {};
      const newOptionImages = q.option_images ? {} : null;
      origLetters.forEach((newLetter, i) => {
        newOptions[newLetter] = q.options[srcLetters[i]];
        if (newOptionImages) newOptionImages[newLetter] = q.option_images[srcLetters[i]] || null;
      });

      const correctOrig = room.answerKey[qid];
      student.answerKey[qid] = origLetters[srcLetters.indexOf(correctOrig)];

      return { id: q.id, text: q.text, context: q.context || null, options: newOptions, option_images: newOptionImages, image: q.image, subject: q.subject, topic_name: q.topic_name || '' };
    });

    const joinPayload = {
      name: cleanName,
      group: room.group,
      title: room.title,
      questions: questionsForStudent,
      timeLimit: room.timeLimitMinutes,
      examActive: room.phase === 'active',
      startTime: room.startTime,
      roomCode,
      cancelled: !!student.cancelled,
      lockedOptions: !!room.lockedOptions,
      serverTime: Date.now(),
    };

    if (student.submitted) {
      let correct = 0;
      room.questions.forEach(q => {
        const key = student.answerKey?.[q.id] ?? room.answerKey[q.id];
        if (student.answers[q.id] === key) correct++;
      });
      joinPayload.submitted = true;
      joinPayload.correct = correct;
      joinPayload.answers = student.answers || {};
      joinPayload.answerKey = student.answerKey ?? room.answerKey;
      joinPayload.explanations = Object.fromEntries(
        room.questions.map(q => [q.id, q.explanation || ''])
      );
    }

    socket.emit('joined', joinPayload);

    io.to(roomCode).emit('studentsUpdate', getStudentSummary(room));
    broadcastRoomsList();
    console.log(`[${roomCode}] ${cleanName} (${room.group}) se unió`);
  });

  // ── Student answers a question ──
  socket.on('answer', ({ questionId, answer }) => {
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room) return;
    const student = room.students[socket.id];
    if (!student || student.submitted || student.cancelled) return;
    if (room.phase !== 'active') return;
    student.answers[questionId] = answer;
    io.to(roomCode).emit('studentsUpdate', getStudentSummary(room));
  });

  // ── Student switches tab ──
  socket.on('tabSwitch', () => {
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room) return;
    if (room.phase !== 'active') return;
    const student = room.students[socket.id];
    if (!student || student.submitted || student.cancelled) return;
    student.tabSwitches = (student.tabSwitches || 0) + 1;
    socket.emit('tabSwitchCount', { count: student.tabSwitches });
    if (student.tabSwitches >= 3) {
      student.cancelled = true;
      socket.emit('examCancelled');
      console.log(`[${roomCode}] ${student.name} cancelado por 3 salidas`);
    }
    io.to(roomCode).emit('studentsUpdate', getStudentSummary(room));
  });

  // ── Teacher restores a cancelled student ──
  socket.on('restoreStudent', ({ roomCode, studentId }) => {
    const room = rooms.get(roomCode);
    if (!room) return;
    const student = room.students[studentId];
    if (!student) return;
    student.cancelled = false;
    // Dejar el contador a una salida antes del umbral (3 = cancela), así una más cancela.
    student.tabSwitches = 2;
    io.to(studentId).emit('examRestored');
    // Mostrar al alumno restaurado el aviso de "última oportunidad".
    io.to(studentId).emit('tabSwitchCount', { count: 2 });
    io.to(roomCode).emit('studentsUpdate', getStudentSummary(room));
    console.log(`[${roomCode}] ${student.name} restaurado por profesor (queda 1 salida)`);
  });

  // ── Student marks/unmarks question ──
  socket.on('toggleMark', ({ questionId }) => {
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room) return;
    const student = room.students[socket.id];
    if (!student || student.submitted || student.cancelled) return;
    const idx = student.marked.indexOf(questionId);
    if (idx === -1) student.marked.push(questionId);
    else student.marked.splice(idx, 1);
    socket.emit('markedUpdate', student.marked);
  });

  // ── Student submits exam (idempotent + ACK) ──
  socket.on('submitExam', (ack) => {
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room) { if (typeof ack === 'function') ack({ ok: false, error: 'no room' }); return; }
    const student = room.students[socket.id];
    if (!student) { if (typeof ack === 'function') ack({ ok: false, error: 'no student' }); return; }

    const wasSubmitted = student.submitted;
    if (!wasSubmitted) {
      student.submitted = true;
      student.submitTime = Date.now();
    }

    let correct = 0;
    room.questions.forEach(q => {
      const key = student.answerKey?.[q.id] ?? room.answerKey[q.id];
      if (student.answers[q.id] === key) correct++;
    });

    const payload = {
      ok: true,
      correct,
      total: room.questions.length,
      answerKey: student.answerKey ?? room.answerKey,
      explanations: Object.fromEntries(
        room.questions.map(q => [q.id, q.explanation || ''])
      ),
    };

    if (typeof ack === 'function') ack(payload);
    socket.emit('examSubmitted', payload);

    if (!wasSubmitted) {
      io.to(roomCode).emit('studentsUpdate', getStudentSummary(room));
      console.log(`[${roomCode}] ${student.name} entregó: ${correct}/${room.questions.length}`);
      enqueueComprobantePDF(room, student);
      enqueueAnswerKeyPDF(room);
    }
  });

  // ── Teacher: start exam ──
  socket.on('startExam', ({ roomCode }) => {
    const room = rooms.get(roomCode);
    if (!room) return;
    room.phase = 'active';
    room.startTime = Date.now();
    Object.values(room.students).forEach(s => { s.startTime = room.startTime; });
    io.to(roomCode).emit('examStarted', { startTime: room.startTime, timeLimit: room.timeLimitMinutes, serverTime: Date.now() });
    broadcastRoomsList();
    console.log(`[${roomCode}] Examen iniciado`);
  });

  // ── Teacher: close exam ──
  socket.on('closeExam', ({ roomCode }) => {
    const room = rooms.get(roomCode);
    if (!room) return;
    room.phase = 'closed';
    Object.entries(room.students).forEach(([id, s]) => {
      if (!s.submitted) {
        s.submitted = true;
        s.submitTime = Date.now();
        const sock = io.sockets.sockets.get(id);
        if (sock) {
          let correct = 0;
          room.questions.forEach(q => {
            const key = s.answerKey?.[q.id] ?? room.answerKey[q.id];
            if (s.answers[q.id] === key) correct++;
          });
          sock.emit('examSubmitted', {
            correct,
            total: room.questions.length,
            answerKey: s.answerKey ?? room.answerKey,
            explanations: Object.fromEntries(
              room.questions.map(q => [q.id, q.explanation || ''])
            ),
          });
        }
      }
    });
    io.to(roomCode).emit('examClosed');
    io.to('teachers').emit('roomClosed', { roomCode });
    broadcastRoomsList();
    console.log(`[${roomCode}] Examen cerrado`);
    // Asegura PDF para todos los alumnos que entregaron (incluye los que se
    // auto-entregaron al cerrar; dedup interno evita generar dos veces).
    Object.values(room.students).forEach(s => { if (s.submitted) enqueueComprobantePDF(room, s); });
    enqueueAnswerKeyPDF(room);
  });

  // ── Teacher: reset exam (keep room, clear students) ──
  socket.on('resetExam', ({ roomCode }) => {
    const room = rooms.get(roomCode);
    if (!room) return;
    room.phase = 'waiting';
    room.students = {};
    room.startTime = null;
    io.to(roomCode).emit('examReset');
    broadcastRoomsList();
    console.log(`[${roomCode}] Examen reiniciado`);

    // Reset = se asume que es una prueba: borra toda la carpeta de comprobantes
    // (incluida la clave). La clave se regenerará en cuanto entregue alguien.
    const dateStr = (room.date || new Date().toISOString().split('T')[0]).replace(/-/g, '');
    const folderPath = path.join(__dirname, 'comprobantes', `${roomCode}_${dateStr}`);
    if (fs.existsSync(folderPath)) {
      try {
        fs.rmSync(folderPath, { recursive: true, force: true });
        console.log(`[${roomCode}] Reset: carpeta de comprobantes eliminada`);
      } catch (err) {
        console.error(`[${roomCode}] No pude borrar carpeta: ${err.message}`);
      }
    }

    // Limpia todo el dedup de la sala para que regenere desde cero.
    for (const key of [...pdfEnqueued]) {
      if (key.startsWith(`${roomCode}:`)) pdfEnqueued.delete(key);
    }
  });

  // ── Teacher: delete room entirely ──
  socket.on('deleteRoom', ({ roomCode }) => {
    const room = rooms.get(roomCode);
    if (!room) return;
    io.to(roomCode).emit('roomDeleted');
    rooms.delete(roomCode);
    broadcastRoomsList();
    console.log(`[${roomCode}] Sala eliminada`);
  });

  // ── Teacher: get students for a room ──
  socket.on('getStudents', ({ roomCode }) => {
    const room = rooms.get(roomCode);
    if (!room) return;
    socket.emit('studentsUpdate', getStudentSummary(room));
  });

  // ── Teacher: get all rooms ──
  socket.on('getRooms', () => {
    socket.join('teachers');
    socket.emit('roomsList', buildRoomsList());
  });

  // ── Teacher: watch a room (join for live updates) ──
  socket.on('watchRoom', ({ roomCode }) => {
    for (const r of socket.rooms) {
      if (r !== socket.id && r !== 'teachers') socket.leave(r);
    }
    const room = rooms.get(roomCode);
    if (!room) return;
    socket.join(roomCode);
    socket.emit('roomState', {
      roomCode: room.roomCode,
      phase: room.phase,
      title: room.title,
      group: room.group,
      totalQuestions: room.questions.length,
      startTime: room.startTime,
      timeLimit: room.timeLimitMinutes,
    });
    socket.emit('studentsUpdate', getStudentSummary(room));
  });

  // ── Disconnect ──
  socket.on('disconnect', () => {
    const roomCode = socketRoom.get(socket.id);
    if (roomCode) {
      const room = rooms.get(roomCode);
      if (room && room.students[socket.id]) {
        room.students[socket.id].connected = false;
        io.to(roomCode).emit('studentsUpdate', getStudentSummary(room));
        broadcastRoomsList();
        console.log(`[${roomCode}] ${room.students[socket.id].name} desconectado`);
      }
      socketRoom.delete(socket.id);
    }
  });
});

// ─── Start Server ───────────────────────────────────────────────────────────
server.listen(PORT, '0.0.0.0', () => {
  console.log(`\n══════════════════════════════════════════`);
  console.log(`  PLATAFORMA DE EXAMEN DIGITAL`);
  console.log(`══════════════════════════════════════════`);
  console.log(`\n  Panel del profesor: http://localhost:${PORT}/teacher`);
  const localIP = getLocalIP();
  if (localIP !== 'localhost') {
    console.log(`\n  Los alumnos se conectan a:`);
    console.log(`  → http://${localIP}:${PORT}`);
    console.log(`\n  Panel del profesor (desde otro dispositivo):`);
    console.log(`  → http://${localIP}:${PORT}/teacher`);
  }
  console.log(`\n══════════════════════════════════════════\n`);
});
