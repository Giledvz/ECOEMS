const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const fs = require('fs');
const os = require('os');
const QRCode = require('qrcode');
const katex = require('katex');
const puppeteer = require('puppeteer');

const PORT = Number(process.env.PORT) || 3000;
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

// Access-Control-Allow-Origin en assets estáticos: el PDF se genera con
// page.setContent(), que deja el documento con origen opaco (about:blank). Las
// fuentes @font-face se piden en modo CORS; sin este header el navegador las
// BLOQUEA (net::ERR_FAILED) y el PDF cae a fuentes de respaldo (Georgia por
// Fraunces, Helvetica por IBM Plex, Times por KaTeX → delimitadores chicos).
// Solo afecta archivos estáticos, no las rutas /api.
const allowCors = (res) => { res.setHeader('Access-Control-Allow-Origin', '*'); };
app.use(express.static(path.join(__dirname, 'public'), { etag: false, maxAge: 0, setHeaders: (res) => { res.setHeader('Cache-Control', 'no-store'); allowCors(res); } }));
app.use('/katex', express.static(path.join(__dirname, 'node_modules/katex/dist'), { setHeaders: allowCors }));
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

function createRoom(data, jsonFilename = null, lockedOptions = false, opts = {}) {
  const roomCode = generateRoomCode();
  const room = {
    roomCode,
    phase: 'waiting',
    mode: opts.mode === 'practice' ? 'practice' : 'exam',
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

  // Modo práctica (Carrusel): preguntas filtradas por materia y barajadas en
  // miscelánea UNA sola vez — todos los participantes ven la misma pregunta
  // con las mismas letras, para poder discutirla en voz alta.
  if (room.mode === 'practice') {
    const subjects = Array.isArray(opts.subjects) && opts.subjects.length ? opts.subjects : null;
    if (subjects) {
      room.questions = room.questions.filter(q => subjects.includes(q.subject));
    }
    room.questions = shuffle(room.questions);
    room.practiceTimerSec = Number.isFinite(opts.timerSec) && opts.timerSec > 0 ? Math.min(opts.timerSec, 900) : 0;
    room.practice = {
      idx: 0,
      phase: 'answering',   // 'answering' | 'revealed'
      turnQueue: [],        // nombres en orden de llegada (estable ante reconexión)
      turnPos: 0,
      turnManual: false,    // true si el profe asignó el turno a mano (Siguiente lo respeta)
      scores: {},           // nombre -> { correct, answered }
      lastResult: null,     // { qid, name, answer, correctAnswer, isCorrect, explanation }
      limit: null,          // corte de equidad: se fija al iniciar (múltiplo de participantes)
      bids: [],             // apuestas {name, answer} en orden de llegada (rebote al vencer el timer)
      openForAll: false,    // timer vencido sin apuestas: contesta el primero que llegue
      answerDeadline: null, // timestamp ms del próximo vencimiento del timer
      timerToken: 0,        // invalida timeouts viejos
    };
  }

  rooms.set(roomCode, room);
  return room;
}

// ─── Modo práctica (Carrusel): helpers ──────────────────────────────────────
function practiceTurnName(room) {
  const p = room.practice;
  if (!p || p.turnQueue.length === 0) return null;
  return p.turnQueue[p.turnPos % p.turnQueue.length];
}

function isNameConnected(room, name) {
  return Object.values(room.students).some(s => s.connected && s.name === name);
}

// Avanza el turno al siguiente alumno conectado (máximo una vuelta completa;
// si nadie está conectado, avanza una posición y el cliente muestra el estado).
function advancePracticeTurn(room) {
  const p = room.practice;
  if (!p || p.turnQueue.length === 0) return;
  for (let i = 0; i < p.turnQueue.length; i++) {
    p.turnPos = (p.turnPos + 1) % p.turnQueue.length;
    if (isNameConnected(room, practiceTurnName(room))) return;
  }
}

// Corte de equidad: cuántas preguntas se juegan en la sesión. Se fija al
// iniciar como el mayor múltiplo del número de participantes que cabe en el
// total — así, con rotación estricta, todos contestan exactamente las mismas.
function practiceLimit(room) {
  const p = room.practice;
  if (!p) return room.questions.length;
  return p.limit ?? room.questions.length;
}

// Quiénes pueden contestar EN DIRECTO la pregunta actual: el del turno, o
// todos si el timer venció sin apuestas. (Los demás apuestan vía practiceBid.)
function practiceEligibleNames(room) {
  const p = room.practice;
  if (!p || p.turnQueue.length === 0) return [];
  if (p.openForAll) return [...p.turnQueue];
  const holder = practiceTurnName(room);
  return holder ? [holder] : [];
}

// Resuelve la pregunta actual con la respuesta de `name` (turno, apuesta
// ganadora o primer llegado tras abrirse): puntúa, revela y difunde.
function resolvePracticeAnswer(room, name, answer, via) {
  const p = room.practice;
  const q = room.questions[p.idx];
  const correctAnswer = room.answerKey[q.id];
  const isCorrect = answer === correctAnswer;
  if (!Object.prototype.hasOwnProperty.call(p.scores, name)) p.scores[name] = { correct: 0, answered: 0 };
  p.scores[name].answered++;
  if (isCorrect) p.scores[name].correct++;
  const holder = practiceTurnName(room);
  const stolen = !!holder && holder.toLowerCase() !== name.toLowerCase();
  p.lastResult = {
    qid: q.id, name, answer, correctAnswer, isCorrect,
    explanation: q.explanation || '',
    stolen, stolenFrom: stolen ? holder : null,
  };
  p.phase = 'revealed';
  p.turnManual = false; // la asignación manual (si la hubo) ya se cumplió
  p.bids = [];
  p.openForAll = false;
  clearPracticeTimer(room);
  broadcastPractice(room);
  console.log(`[${room.roomCode}] Carrusel: ${name} → ${answer} en P${q.id} (${isCorrect ? 'correcta' : `incorrecta, era ${correctAnswer}`})${stolen ? ` — rebote, era turno de ${holder} [${via}]` : ''}`);
}

// Programa el vencimiento del timer por pregunta (rebote). Al vencer:
// gana la apuesta más temprana de un alumno conectado; si nadie apostó,
// la pregunta se abre para todos y contesta el primero que llegue.
function schedulePracticeTimer(room) {
  const p = room.practice;
  if (!p) return;
  p.timerToken++;
  if (room._pTimer) { clearTimeout(room._pTimer); room._pTimer = null; }
  const sec = room.practiceTimerSec || 0;
  const canRun = sec > 0 && room.phase === 'active' && p.phase === 'answering'
    && p.idx < practiceLimit(room) && p.turnQueue.length > 1
    && !p.openForAll;
  if (!canRun) {
    p.answerDeadline = null; // sin próximo vencimiento (revelada, terminada o ya abierta a todos)
    return;
  }
  const token = p.timerToken;
  p.answerDeadline = Date.now() + sec * 1000;
  room._pTimer = setTimeout(() => {
    const r = rooms.get(room.roomCode);
    if (!r || !r.practice || r.practice.timerToken !== token) return;
    const pp = r.practice;
    if (r.phase !== 'active' || pp.phase !== 'answering') return;
    const bid = pp.bids.find(b => isNameConnected(r, b.name));
    if (bid) {
      console.log(`[${r.roomCode}] Carrusel: timer vencido — gana la apuesta de ${bid.name}`);
      resolvePracticeAnswer(r, bid.name, bid.answer, 'apuesta');
      return;
    }
    pp.openForAll = true;
    pp.answerDeadline = null;
    console.log(`[${r.roomCode}] Carrusel: timer vencido sin apuestas — pregunta abierta para todos`);
    broadcastPractice(r);
  }, sec * 1000);
}

function clearPracticeTimer(room) {
  const p = room.practice;
  if (!p) return;
  p.timerToken++;
  p.answerDeadline = null;
  if (room._pTimer) { clearTimeout(room._pTimer); room._pTimer = null; }
}

function buildPracticeState(room) {
  const p = room.practice;
  if (!p) return null;
  const limit = practiceLimit(room);
  const finished = p.idx >= limit;
  const q = finished ? null : room.questions[p.idx];
  return {
    idx: p.idx,
    total: limit,
    qid: q ? q.id : null,
    subject: q ? q.subject : null,
    phase: finished ? 'finished' : p.phase,
    turnName: practiceTurnName(room),
    turnConnected: practiceTurnName(room) ? isNameConnected(room, practiceTurnName(room)) : false,
    turnQueue: p.turnQueue,
    scores: p.scores,
    lastResult: p.lastResult,
    eligibleNames: finished ? [] : practiceEligibleNames(room),
    openForAll: !finished && p.phase === 'answering' && p.openForAll,
    bidNames: (!finished && p.phase === 'answering') ? p.bids.map(b => b.name) : [],
    timerSec: room.practiceTimerSec || 0,
    remainingMs: (!finished && p.phase === 'answering' && p.answerDeadline)
      ? Math.max(0, p.answerDeadline - Date.now()) : null,
  };
}

// Estado extendido SOLO para el panel del profesor: incluye la pregunta
// completa y la respuesta correcta (el alumno la recibe hasta el revelado).
function buildPracticeTeacherState(room) {
  const p = room.practice;
  const limit = practiceLimit(room);
  const q = (p && p.idx < limit) ? room.questions[p.idx] : null;
  const participants = p ? p.turnQueue.length : 0;
  return {
    roomCode: room.roomCode,
    state: buildPracticeState(room),
    question: q ? {
      id: q.id, text: q.text, context: q.context, options: q.options,
      option_images: q.option_images, image: q.image, subject: q.subject,
      topic_name: q.topic_name || '', explanation: q.explanation || '',
    } : null,
    correctAnswer: q ? room.answerKey[q.id] : null,
    bids: (p && p.phase === 'answering') ? p.bids : [],
    limitInfo: {
      limit,
      totalAvailable: room.questions.length,
      participants,
      perStudent: participants > 0 && p && p.limit ? Math.floor(limit / participants) : null,
    },
  };
}

function broadcastPractice(room) {
  io.to(room.roomCode).emit('practiceState', buildPracticeState(room));
  io.to('teachers').emit('practiceTeacherState', buildPracticeTeacherState(room));
}

function buildRoomsList() {
  const list = [];
  rooms.forEach(room => {
    list.push({
      roomCode: room.roomCode,
      title: room.title,
      group: room.group,
      phase: room.phase,
      mode: room.mode || 'exam',
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

// DEBUG: devuelve el HTML del comprobante de la primera persona enviada en la sala.
app.get('/api/debug-comprobante/:roomCode', (req, res) => {
  const room = rooms.get(req.params.roomCode);
  if (!room) return res.status(404).send('Sala no encontrada');
  const student = Object.values(room.students).find(s => s.submitted);
  if (!student) return res.status(404).send('No hay estudiante con entrega en esta sala');
  res.type('html').send(buildComprobanteHTML(room, student));
});

app.post('/api/upload-exam', (req, res) => {
  try {
    const filename = req.headers['x-exam-filename'] || null;
    const lockedOptions = req.headers['x-locked-options'] === '1';
    const mode = req.headers['x-mode'] === 'practice' ? 'practice' : 'exam';
    // x-subjects: encodeURIComponent(JSON.stringify([...materias])) — filtro
    // de materias para el modo práctica.
    let subjects = null;
    if (req.headers['x-subjects']) {
      try { subjects = JSON.parse(decodeURIComponent(req.headers['x-subjects'])); } catch (e) {}
    }
    const timerSec = parseInt(req.headers['x-practice-timer'], 10) || 0;
    const room = createRoom(req.body, filename, lockedOptions, { mode, subjects, timerSec });
    if (room.questions.length === 0) {
      rooms.delete(room.roomCode);
      return res.status(400).json({ error: 'La selección no dejó ninguna pregunta' });
    }
    const modeTag = mode === 'practice' ? ', modo práctica' : '';
    console.log(`Sala ${room.roomCode} creada: "${room.title}" (${room.questions.length} preguntas${lockedOptions ? ', candado activado' : ''}${modeTag})${filename ? ` [archivo: ${filename}]` : ''}`);
    broadcastRoomsList();
    res.json({ success: true, totalQuestions: room.questions.length, roomCode: room.roomCode, mode: room.mode });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// DEV ONLY: re-read the JSON file from disk and update room.questions/answerKey
// without resetting students, answers, or phase. Bloqueado en fase 'active'.
app.post('/api/dev-reload/:roomCode', (req, res) => {
  const room = rooms.get(req.params.roomCode);
  if (!room) return res.status(404).json({ error: 'Sala no encontrada' });
  if (room.mode === 'practice') return res.status(400).json({ error: 'Recargar no aplica a salas de práctica (las preguntas van filtradas y barajadas); crea la sala de nuevo' });
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
        option_images: q.option_images || null,
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

// Download the server-generated comprobante PDF for a student.
// El cliente lo prefiere a html2canvas (que falla con canvas >4096px en iOS).
app.get('/api/comprobante-pdf', (req, res) => {
  const roomCode = req.query.room;
  const studentName = req.query.name;
  if (!roomCode || !studentName) return res.status(400).json({ error: 'Falta room o name' });
  const room = rooms.get(roomCode);
  if (!room) return res.status(404).json({ error: 'Sala no encontrada' });
  const dateStr = (room.date || new Date().toISOString().split('T')[0]).replace(/-/g, '');
  const folder = path.join(__dirname, 'comprobantes', `${room.roomCode}_${dateStr}`);
  const filePath = path.join(folder, `${safeFilename(studentName)}.pdf`);
  if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'PDF aún no generado' });
  res.download(filePath, `comprobante_${safeFilename(studentName)}.pdf`);
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

// Renderers de markdown/KaTeX/tablas: compartidos con el cliente vía
// /public/shared/markdown-render.js (mismo módulo que carga el browser).
const { renderInlineMath, renderMarkdownTable, renderMath } = require('./public/shared/markdown-render');

// Construye el HTML del comprobante igual que _downloadPDFImpl() del cliente.
// CSS Tercial compartido por comprobante + clave de respuestas.
const TERCIAL_PDF_CSS = `
  * { margin:0; padding:0; box-sizing:border-box; }
  /* Forzar light mode: evita que visores como Preview de macOS inviertan
     selectivamente elementos con background-color (resultaba en tablas
     "dark" sobre fondo "light"). */
  html { color-scheme: only light; background-color: #f4ecd8; }
  :root {
    color-scheme: only light;
    --crema-100: #faf6ec; --crema-200: #f4ecd8; --crema-300: #ede2c5;
    --ink-300: #8c7556; --ink-500: #7a6448; --ink-700: #4a3f33; --ink-900: #1f1a16;
    --accent-conac: #6b3a2e; --accent-terracota: #c2410c;
    --state-ok: #5a8045; --state-ok-bg: #d6e3bd;
    --state-err: #b8362c; --state-err-bg: #f1dcd4;
    --state-warn: #b8862e; --state-warn-bg: #f1e6c4;
    --cat-coral: #8c4a3a;
    /* Colores por nivel de dominio en el desglose por materia (umbrales
       ≥70% domina / 50–69% en proceso / <50% requiere atención). Activos: los
       VIVOS acordados en los dashboards. Para alternar al tono apagado Tercial,
       cambia estos 3 por los valores entre comentarios. */
    --level-domina:   #1D9E75;  /* apagado Tercial: #5a8045 */
    --level-proceso:  #EF9F27;  /* apagado Tercial: #b8862e */
    --level-atencion: #E24B4A;  /* apagado Tercial: #b8362c */
    /* Tablas markdown (compartido con cliente vía /shared/markdown-render.js) */
    /* Colores de tabla sincronizados con la versión en pantalla (app) para que
       el PDF coincida: borde tan suave (#c9bda3, el crema-600 del app), NO el
       café oscuro ink-300; y los fondos crema retocados del app. */
    --md-text:     var(--ink-900);
    --md-border:   #c9bda3;
    --md-th-bg:    #efe7d8;
    --md-table-bg: #f8f3e8;
    --md-font:     'IBM Plex Sans', sans-serif;
  }
  @page {
    size: letter;
    margin: 0;
  }
  body {
    font-family: 'IBM Plex Sans', -apple-system, sans-serif;
    background-color: var(--crema-200);
    color: var(--ink-900);
    font-size: 11pt;
    line-height: 1.55;
  }
  /* Marco de página: el thead/tfoot se repiten en CADA página (comportamiento
     estándar de las tablas al imprimir) y dejan aire crema arriba/abajo, sin
     reintroducir márgenes blancos — page.pdf va con margin 0 y el fondo crema
     llega al borde. (Un margen normal de page.pdf dejaría esas franjas BLANCAS.) */
  .page-frame { width: 100%; border-collapse: collapse; }
  .page-frame > thead > tr > td,
  .page-frame > tfoot > tr > td,
  .page-frame > tbody > tr > td { padding: 0; }
  .page-frame__space { height: 0.62in; }

  /* Full-bleed: el fondo crema (html/body) llega al borde del papel; el
     contenido va en una columna centrada. El aire vertical lo da .page-frame. */
  .exam-pdf {
    max-width: 6.7in;
    margin: 0 auto;
    padding: 0;
  }

  /* Hero */
  .exam-pdf__hero {
    border-top: 3px solid var(--cat-coral);
    padding-top: 0.4in;
    margin-bottom: 0.35in;
  }
  .exam-pdf__eyebrow {
    font-size: 10pt;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ink-300);
    margin: 0 0 12pt;
  }
  .exam-pdf__title {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 32pt;
    line-height: 1.05;
    letter-spacing: -0.02em;
    color: var(--ink-900);
    margin: 0 0 12pt;
    font-variation-settings: "opsz" 96;
  }
  .exam-pdf__title em {
    font-style: italic;
    color: var(--accent-conac);
  }
  .exam-pdf__meta {
    font-size: 11pt;
    color: var(--ink-500);
    margin: 0;
    font-variant-numeric: tabular-nums;
  }
  .exam-pdf__meta strong {
    font-weight: 500;
    color: var(--ink-700);
  }

  /* Score block — Tercial editorial */
  .score-block {
    margin: 0.4in 0 0.45in;
    padding: 18pt 0;
    border-top: 1px solid var(--ink-300);
    border-bottom: 1px solid var(--ink-300);
    text-align: center;
    page-break-inside: avoid;
  }
  .score-block__eyebrow {
    font-size: 9pt;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--ink-300);
    margin: 0 0 6pt;
  }
  .score-block__big {
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-weight: 500;
    font-size: 52pt;
    line-height: 1;
    color: var(--accent-conac);
    font-variant-numeric: lining-nums;
    margin: 0;
  }
  .score-block__sub {
    margin-top: 6pt;
    font-size: 10.5pt;
    color: var(--ink-500);
    letter-spacing: 0.02em;
  }
  .score-block__sub strong {
    font-weight: 500;
    color: var(--ink-700);
  }

  /* Breakdown por materia — barras finas coñac/crema */
  .breakdown {
    margin-bottom: 0.4in;
    page-break-inside: avoid;
  }
  .breakdown__title {
    font-size: 9pt;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--ink-300);
    margin: 0 0 14pt;
  }
  .breakdown__row {
    margin-bottom: 11pt;
  }
  .breakdown__head {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 4pt;
    font-size: 10.5pt;
    color: var(--ink-700);
  }
  .breakdown__name { font-weight: 500; }
  .breakdown__pct {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10pt;
    font-weight: 500;
    color: var(--ink-700);
    font-variant-numeric: tabular-nums;
  }
  /* Altura 3.5pt (no 2.5): a 2.5pt la barra es una hairline sub-pixel que en
     pantalla (baja DPI) el anti-aliasing redondea disparejo entre filas. Algo
     más gruesa se ve pareja tanto en pantalla como impresa. */
  .breakdown__bar {
    height: 3.5pt;
    background-color: var(--crema-300);
    border-radius: 1.75pt;
    overflow: hidden;
  }
  .breakdown__fill {
    height: 100%;
    background-color: var(--accent-conac);
    border-radius: 1pt;
  }
  /* Color por nivel de dominio (sobrescribe el coñac por defecto). */
  .breakdown__fill--domina   { background-color: var(--level-domina); }
  .breakdown__fill--proceso  { background-color: var(--level-proceso); }
  .breakdown__fill--atencion { background-color: var(--level-atencion); }
  .breakdown__meta {
    margin-top: 3pt;
    font-size: 9pt;
    color: var(--ink-300);
    font-variant-numeric: tabular-nums;
  }
  .breakdown__legend {
    display: flex;
    flex-wrap: wrap;
    gap: 14pt;
    margin-top: 12pt;
    font-size: 8.5pt;
    color: var(--ink-500);
  }
  .breakdown__legend span { display: inline-flex; align-items: center; gap: 4pt; }
  .breakdown__dot { display: inline-block; width: 7pt; height: 7pt; border-radius: 2pt; }
  .breakdown__dot--domina   { background-color: var(--level-domina); }
  .breakdown__dot--proceso  { background-color: var(--level-proceso); }
  .breakdown__dot--atencion { background-color: var(--level-atencion); }

  /* Lista de ejercicios */
  .exam-pdf__exercises {
    list-style: none;
    padding: 0;
    margin: 0;
    counter-reset: exercise;
  }
  .exam-pdf__exercise {
    counter-increment: exercise;
    display: grid;
    grid-template-columns: 0.42in minmax(0, 1fr);
    column-gap: 16pt;
    margin-bottom: 22pt;
    page-break-inside: avoid;
  }
  .exam-pdf__exercise::before {
    content: counter(exercise) ".";
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-weight: 500;
    font-size: 17pt;
    color: var(--accent-conac);
    text-align: right;
    line-height: 1.1;
    padding-top: 1pt;
    font-variant-numeric: lining-nums;
  }
  .exam-pdf__body {
    font-size: 11pt;
    line-height: 1.5;
    color: var(--ink-900);
    min-width: 0;
  }
  .exam-pdf__subject {
    display: block;
    font-size: 8.5pt;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--ink-300);
    margin-bottom: 4pt;
  }
  .exam-pdf__body p { margin: 0 0 6pt; }
  .exam-pdf__figure {
    margin: 8pt 0;
  }
  .exam-pdf__figure img,
  .exam-pdf__figure svg {
    max-width: 100%;
    max-height: 180pt;
  }

  /* Opciones con estado */
  .exam-pdf__choices {
    list-style: none;
    padding: 0;
    margin: 8pt 0 0;
  }
  .exam-pdf__choice {
    display: flex;
    align-items: flex-start;
    gap: 8pt;
    padding: 5pt 8pt;
    margin-bottom: 2pt;
    border-radius: 4pt;
    font-size: 10.5pt;
    line-height: 1.45;
    color: var(--ink-700);
    background-color: transparent;
    border: 1px solid transparent;
    /* Que una opción (sobre todo con figura alta) no se parta entre páginas. */
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .exam-pdf__choice--correct {
    background-color: var(--state-ok-bg);
    border-color: var(--state-ok);
  }
  .exam-pdf__choice--incorrect {
    background-color: var(--state-err-bg);
    border-color: var(--state-err);
  }
  .exam-pdf__choice__letter {
    font-weight: 500;
    color: var(--ink-500);
    flex-shrink: 0;
    min-width: 18pt;
  }
  .exam-pdf__choice--correct .exam-pdf__choice__letter { color: var(--state-ok); }
  .exam-pdf__choice--incorrect .exam-pdf__choice__letter { color: var(--state-err); }
  .exam-pdf__choice__text { flex: 1; min-width: 0; }
  .exam-pdf__choice__text img,
  .exam-pdf__choice__text svg {
    max-width: 140pt;
    max-height: 80pt;
    vertical-align: middle;
  }
  /* El SVG de opción hereda el color del .exam-pdf__choice (ink-700, más claro).
     Lo forzamos a ink-900 para que las figuras de opción tengan el MISMO color
     que las del enunciado y que la versión en pantalla (currentColor = ink-900). */
  .exam-pdf__choice__text svg { color: var(--ink-900); }
  .exam-pdf__choice__marker {
    flex-shrink: 0;
    font-size: 9pt;
    font-weight: 500;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--ink-300);
  }
  .exam-pdf__choice--correct .exam-pdf__choice__marker { color: var(--state-ok); }
  .exam-pdf__choice--incorrect .exam-pdf__choice__marker { color: var(--state-err); }

`;

function escAttr(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/"/g, '&quot;')
    .replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Imagen para el PDF. Los SVG se inyectan INLINE (no como <img src>) para que
// `fill/stroke="currentColor"` herede el color del documento (--ink-900) — igual
// que en la versión en pantalla. Con <img>, currentColor caería a negro puro y
// las figuras saldrían de distinto color que en el examen. PNG/otros: <img>.
function pdfImg(srcPath, alt) {
  if (!srcPath) return '';
  if (/\.svg$/i.test(srcPath)) {
    try {
      const file = path.join(__dirname, 'public', String(srcPath).replace(/^\//, ''));
      let svg = fs.readFileSync(file, 'utf8')
        .replace(/<\?xml[\s\S]*?\?>/i, '')
        .replace(/<!DOCTYPE[\s\S]*?>/i, '')
        .trim();
      if (alt) svg = svg.replace(/<svg\b/i, `<svg role="img" aria-label="${escAttr(alt)}"`);
      return svg;
    } catch (e) {
      return `<img src="${srcPath}" alt="${escAttr(alt)}">`; // fallback si no se lee
    }
  }
  return `<img src="${srcPath}" alt="${escAttr(alt)}">`;
}

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
  const pct = total > 0 ? Math.round(correct / total * 100) : 0;

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
  // Nivel de dominio por umbral (mismo esquema acordado en los dashboards).
  const levelClass = (pct) => pct >= 70 ? 'domina' : pct >= 50 ? 'proceso' : 'atencion';
  const breakdownRowsHTML = sortedSubjects.map(([name, data]) => {
    const subjectPct = Math.round((data.correct / data.total) * 100);
    return `
      <div class="breakdown__row">
        <div class="breakdown__head">
          <span class="breakdown__name">${name}</span>
          <span class="breakdown__pct">${subjectPct}%</span>
        </div>
        <div class="breakdown__bar"><div class="breakdown__fill breakdown__fill--${levelClass(subjectPct)}" style="width:${subjectPct}%;"></div></div>
        <div class="breakdown__meta">${data.correct} de ${data.total} aciertos</div>
      </div>`;
  }).join('');
  const breakdownLegendHTML = `
    <div class="breakdown__legend">
      <span><span class="breakdown__dot breakdown__dot--domina"></span>Domina ≥70%</span>
      <span><span class="breakdown__dot breakdown__dot--proceso"></span>En proceso 50–69%</span>
      <span><span class="breakdown__dot breakdown__dot--atencion"></span>Requiere atención &lt;50%</span>
    </div>`;
  const breakdownHTML = sortedSubjects.length > 0 ? `
    <section class="breakdown">
      <p class="breakdown__title">Por materia</p>
      ${breakdownRowsHTML}
      ${breakdownLegendHTML}
    </section>` : '';

  const questionsHTML = questionsForStudent.map((q, idx) => {
    const mine = answers[q.id];
    const correctAns = answerKey[q.id];
    const letters = Object.keys(q.options);
    const optionsHTML = letters.map(letter => {
      const isCorrect = letter === correctAns;
      const isMine = letter === mine;
      let cls = 'exam-pdf__choice';
      let marker = '';
      if (isCorrect) { cls += ' exam-pdf__choice--correct'; marker = isMine ? 'Tu respuesta · correcta' : 'Correcta'; }
      else if (isMine) { cls += ' exam-pdf__choice--incorrect'; marker = 'Tu respuesta'; }
      // Con imagen de opción: solo la figura (la descripción de texto va como
      // alt, no visible — sería redundante con la imagen). Sin imagen: el texto.
      const hasImg = q.option_images && q.option_images[letter];
      const optContent = hasImg
        ? pdfImg(q.option_images[letter], q.options[letter])
        : renderMath(q.options[letter]);
      const markerHTML = marker ? `<span class="exam-pdf__choice__marker">${marker}</span>` : '';
      return `<li class="${cls}"><span class="exam-pdf__choice__letter">${letter}.</span><span class="exam-pdf__choice__text">${optContent}</span>${markerHTML}</li>`;
    }).join('');

    const qText = q.text || '';
    const imgHTML = q.image ? `<figure class="exam-pdf__figure">${pdfImg(q.image, '')}</figure>` : '';

    return `
      <li class="exam-pdf__exercise"><div class="exam-pdf__body">
        <span class="exam-pdf__subject">${q.subject}</span>
        <p>${renderMath(qText)}</p>
        ${imgHTML}
        <ol class="exam-pdf__choices">${optionsHTML}</ol>
      </div></li>`;
  }).join('');

  return `<!DOCTYPE html><html lang="es" data-theme="light"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<base href="${origin}/">
<title>Comprobante — ${student.name}</title>
<link rel="stylesheet" href="${origin}/fonts/tercial-fonts.css">
<link rel="stylesheet" href="${origin}/katex/katex.min.css">
<style>${TERCIAL_PDF_CSS}</style></head><body>
<table class="page-frame">
<thead><tr><td><div class="page-frame__space"></div></td></tr></thead>
<tfoot><tr><td><div class="page-frame__space"></div></td></tr></tfoot>
<tbody><tr><td>
<main class="exam-pdf">

  <header class="exam-pdf__hero">
    <p class="exam-pdf__eyebrow">Comprobante de examen · ${room.group || 'Examen'}</p>
    <h1 class="exam-pdf__title">${room.title || 'Examen'}</h1>
    <p class="exam-pdf__meta"><strong>${student.name}</strong> · ${fecha} · Tiempo: ${timeStr}</p>
  </header>

  <section class="score-block">
    <p class="score-block__eyebrow">Resultado</p>
    <p class="score-block__big">${correct} <span style="color:var(--ink-300); font-style:normal; font-family:'IBM Plex Sans',sans-serif; font-size:24pt; font-weight:400;">/ ${total}</span></p>
    <p class="score-block__sub"><strong>${pct}%</strong> · ${correct} de ${total} aciertos</p>
  </section>

  ${breakdownHTML}

  <ol class="exam-pdf__exercises">${questionsHTML}</ol>

</main>
</td></tr></tbody></table>
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
      const cls = isCorrect ? 'exam-pdf__choice exam-pdf__choice--correct' : 'exam-pdf__choice';
      // Con imagen de opción: solo la figura (descripción como alt, no visible).
      // La correcta ya se distingue por el recuadro verde + "Correcta".
      const hasImg = q.option_images && q.option_images[letter];
      const textHTML = hasImg
        ? pdfImg(q.option_images[letter], q.options[letter])
        : renderMath(q.options[letter]);
      const markerHTML = isCorrect ? '<span class="exam-pdf__choice__marker">Correcta</span>' : '';
      return `<li class="${cls}"><span class="exam-pdf__choice__letter">${letter}.</span><span class="exam-pdf__choice__text">${textHTML}</span>${markerHTML}</li>`;
    }).join('');

    const qText = q.text || '';
    const imgHTML = q.image ? `<figure class="exam-pdf__figure">${pdfImg(q.image, '')}</figure>` : '';

    return `
      <li class="exam-pdf__exercise"><div class="exam-pdf__body">
        <span class="exam-pdf__subject">${q.subject}</span>
        <p>${renderMath(qText)}</p>
        ${imgHTML}
        <ol class="exam-pdf__choices">${optionsHTML}</ol>
      </div></li>`;
  }).join('');

  return `<!DOCTYPE html><html lang="es" data-theme="light"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<base href="${origin}/">
<title>Clave de respuestas — ${room.title || 'Examen'}</title>
<link rel="stylesheet" href="${origin}/fonts/tercial-fonts.css">
<link rel="stylesheet" href="${origin}/katex/katex.min.css">
<style>${TERCIAL_PDF_CSS}</style></head><body>
<table class="page-frame">
<thead><tr><td><div class="page-frame__space"></div></td></tr></thead>
<tfoot><tr><td><div class="page-frame__space"></div></td></tr></tfoot>
<tbody><tr><td>
<main class="exam-pdf">

  <header class="exam-pdf__hero">
    <p class="exam-pdf__eyebrow">Clave · profesor · ${room.group || 'Examen'}</p>
    <h1 class="exam-pdf__title">${room.title || 'Examen'} — <em>Respuestas</em></h1>
    <p class="exam-pdf__meta">${fecha} · ${questions.length} preguntas</p>
  </header>

  <ol class="exam-pdf__exercises">${questionsHTML}</ol>

</main>
</td></tr></tbody></table>
</body></html>`;
}

// Ancho de las líneas de relleno (___) en el PDF: misma regla que
// adaptBlankWidths() del cliente (ver CONVENCIONES.md) — cada blanco se mide
// contra la opción (o la parte de opción que le toca) más larga que puede ir
// ahí, + 3px, con la tipografía real de las opciones y tope de 420px. Sin esto
// el PDF dibujaba la raya según el nº de guiones del JSON.
// Mejora sobre el cliente: detecta el separador de partes "/", " - " o " – "
// para los reactivos multi-blanco (el cliente solo parte por "/").
async function applyPdfBlankWidths(page) {
  await page.evaluate(() => {
    const CAP = 420;
    document.querySelectorAll('.exam-pdf__exercise').forEach(ex => {
      const blanks = ex.querySelectorAll('.exam-pdf__body .md-blank');
      if (!blanks.length) return;
      const optEls = Array.from(ex.querySelectorAll('.exam-pdf__choice__text'));
      if (!optEls.length || optEls.some(el => el.querySelector('img'))) return;
      const cs = getComputedStyle(optEls[0]);
      const meas = document.createElement('span');
      meas.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;left:-9999px;top:0;';
      meas.style.fontFamily = cs.fontFamily;
      meas.style.fontSize = cs.fontSize;
      meas.style.fontWeight = cs.fontWeight;
      meas.style.fontStyle = cs.fontStyle;
      meas.style.letterSpacing = cs.letterSpacing;
      document.body.appendChild(meas);
      const widthOf = (s) => { meas.textContent = s; return meas.offsetWidth; };
      const optVals = optEls.map(el => el.textContent.trim());
      const N = blanks.length;
      let parts = null;
      if (N > 1) {
        for (const re of [/\s*\/\s*/, /\s+[–-]\s+/]) {
          const cand = optVals.map(v => v.split(re));
          if (cand.every(p => p.length === N)) { parts = cand; break; }
        }
      }
      blanks.forEach((b, i) => {
        let max = 0;
        if (parts) parts.forEach(p => { max = Math.max(max, widthOf(p[i].trim())); });
        else optVals.forEach(v => { max = Math.max(max, widthOf(v)); });
        b.style.width = Math.min(max + 3, CAP) + 'px';
      });
      document.body.removeChild(meas);
    });
  });
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
      // DEBUG: dump del HTML para inspección
      try { fs.writeFileSync('/tmp/last-comprobante.html', html); } catch(e) {}
      await page.setContent(html, { waitUntil: 'networkidle0', timeout: 30000 });
      await page.evaluate(() => document.fonts.ready); // esperar fuentes (Tercial+KaTeX) antes de medir/capturar
      await applyPdfBlankWidths(page);
      const dateStr = (room.date || new Date().toISOString().split('T')[0]).replace(/-/g, '');
      const folder = path.join(__dirname, 'comprobantes', `${room.roomCode}_${dateStr}`);
      fs.mkdirSync(folder, { recursive: true });
      const filePath = path.join(folder, `${safeFilename(student.name)}.pdf`);
      await page.pdf({
        path: filePath,
        format: 'letter',
        margin: { top: '0', bottom: '0', left: '0', right: '0' },
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
      await page.evaluate(() => document.fonts.ready); // esperar fuentes (Tercial+KaTeX) antes de medir/capturar
      await applyPdfBlankWidths(page);
      const dateStr = (room.date || new Date().toISOString().split('T')[0]).replace(/-/g, '');
      const folder = path.join(__dirname, 'comprobantes', `${room.roomCode}_${dateStr}`);
      fs.mkdirSync(folder, { recursive: true });
      const filePath = path.join(folder, `clave_de_respuestas.pdf`);
      await page.pdf({
        path: filePath,
        format: 'letter',
        margin: { top: '0', bottom: '0', left: '0', right: '0' },
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
      mode: room.mode || 'exam',
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
    // Nombres reservados que contaminarían el prototipo al indexar scores/objetos.
    if (['__proto__', 'constructor', 'prototype'].includes(cleanName.toLowerCase())) {
      socket.emit('joinError', 'Nombre no permitido'); return;
    }

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
      let questionOrder;
      const optionOrders = {};
      if (room.mode === 'practice') {
        // Práctica: orden global de la sala y opciones SIN barajar — todos ven
        // exactamente lo mismo para poder discutirlo en voz alta.
        questionOrder = room.questions.map(q => q.id);
        room.questions.forEach(q => {
          optionOrders[q.id] = Object.keys(q.options);
        });
      } else {
        const questionsBySubject = {};
        room.questions.forEach(q => {
          if (!questionsBySubject[q.subject]) questionsBySubject[q.subject] = [];
          questionsBySubject[q.subject].push(q.id);
        });
        const shuffledSubjects = shuffle(Object.keys(questionsBySubject));
        questionOrder = [];
        shuffledSubjects.forEach(subj => {
          questionsBySubject[subj].forEach(id => questionOrder.push(id));
        });

        room.questions.forEach(q => {
          optionOrders[q.id] = shuffle(Object.keys(q.options));
        });
      }

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

    // Práctica: registrar en la cola de turnos (por nombre, estable ante
    // reconexión) e inicializar marcador. Usa el nombre canónico del registro
    // del alumno (en reconexión puede teclearlo con otras mayúsculas).
    if (room.mode === 'practice' && room.practice) {
      const p = room.practice;
      const canonical = room.students[socket.id].name;
      if (!p.turnQueue.some(n => n.toLowerCase() === canonical.toLowerCase())) {
        p.turnQueue.push(canonical);
      }
      if (!Object.prototype.hasOwnProperty.call(p.scores, canonical)) p.scores[canonical] = { correct: 0, answered: 0 };
      // Si la sesión arrancó con 0-1 alumnos (sin timer corriendo) y ahora ya
      // hay con quién rebotar, arma la ventana — pero solo si no hay una en curso
      // (schedulePracticeTimer reprograma, no queremos reiniciar el reloj del titular).
      if (room.phase === 'active' && p.phase === 'answering' && p.answerDeadline === null) {
        schedulePracticeTimer(room);
      }
    }

    const joinPayload = {
      name: cleanName,
      group: room.group,
      title: room.title,
      mode: room.mode || 'exam',
      questions: questionsForStudent,
      timeLimit: room.timeLimitMinutes,
      examActive: room.phase === 'active',
      startTime: room.startTime,
      roomCode,
      cancelled: !!student.cancelled,
      lockedOptions: !!room.lockedOptions,
      serverTime: Date.now(),
    };

    if (room.mode === 'practice') {
      joinPayload.practice = buildPracticeState(room);
    }

    if (room.mode !== 'practice' && student.submitted) {
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
    if (room.mode === 'practice') broadcastPractice(room);
    broadcastRoomsList();
    console.log(`[${roomCode}] ${cleanName} (${room.group}) se unió`);
  });

  // ── Student answers a question ──
  socket.on('answer', ({ questionId, answer }) => {
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room) return;
    if (room.mode === 'practice') return; // práctica usa practiceAnswer
    const student = room.students[socket.id];
    if (!student || student.submitted || student.cancelled) return;
    if (room.phase !== 'active') return;
    student.answers[questionId] = answer;
    io.to(roomCode).emit('studentsUpdate', getStudentSummary(room));
  });

  // ── Práctica (Carrusel): el alumno en turno (o cualquiera, si la pregunta
  // se abrió para todos) contesta en directo ──
  socket.on('practiceAnswer', ({ answer }) => {
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room || room.mode !== 'practice' || !room.practice) return;
    if (room.phase !== 'active') return;
    const p = room.practice;
    if (p.phase !== 'answering' || p.idx >= practiceLimit(room)) return;
    const student = room.students[socket.id];
    if (!student) return;
    const eligible = practiceEligibleNames(room);
    if (!eligible.some(n => n.toLowerCase() === student.name.toLowerCase())) return; // no es su turno (ni se abrió para él)
    const q = room.questions[p.idx];
    if (!Object.prototype.hasOwnProperty.call(q.options, answer)) return;
    resolvePracticeAnswer(room, student.name, answer, p.openForAll ? 'abierta' : 'turno');
  });

  // ── Práctica (Carrusel): apuesta bajo candado — si el del turno no contesta
  // a tiempo, al vencer el timer gana la apuesta más temprana. El primer toque
  // es definitivo (una apuesta por alumno y pregunta). ──
  socket.on('practiceBid', ({ qid, answer }, ack) => {
    const reply = (ok, reason, extra) => { if (typeof ack === 'function') ack({ ok, reason: reason || null, ...(extra || {}) }); };
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room || room.mode !== 'practice' || !room.practice) return reply(false, 'sala');
    if (room.phase !== 'active') return reply(false, 'sala');
    if (!(room.practiceTimerSec > 0)) return reply(false, 'sin-timer'); // sin timer no hay rebote
    const p = room.practice;
    if (p.phase !== 'answering' || p.idx >= practiceLimit(room)) return reply(false, 'fase');
    if (p.openForAll) return reply(false, 'abierta'); // ya se abrió: contesta en directo
    if (p.answerDeadline === null) return reply(false, 'sin-timer'); // ventana no armada: la apuesta no podría ganar
    const student = room.students[socket.id];
    if (!student) return reply(false, 'sala');
    const holder = practiceTurnName(room);
    if (holder && holder.toLowerCase() === student.name.toLowerCase()) return reply(false, 'turno'); // el del turno contesta, no apuesta
    if (!p.turnQueue.some(n => n.toLowerCase() === student.name.toLowerCase())) return reply(false, 'sala');
    const prev = p.bids.find(b => b.name.toLowerCase() === student.name.toLowerCase());
    if (prev) return reply(false, 'ya-apostaste', { answer: prev.answer }); // primer toque definitivo: devuelve la letra real
    const q = room.questions[p.idx];
    if (qid != null && q.id !== qid) return reply(false, 'pregunta-vieja'); // la apuesta iba a otra pregunta (carrera con Siguiente)
    if (!Object.prototype.hasOwnProperty.call(q.options, answer)) return reply(false, 'opcion');
    p.bids.push({ name: student.name, answer });
    reply(true);
    broadcastPractice(room);
    console.log(`[${roomCode}] Carrusel: apuesta de ${student.name} (${p.bids.length} en fila)`);
  });

  // ── Práctica (Carrusel): el profesor avanza a la siguiente pregunta ──
  socket.on('practiceNext', ({ roomCode }) => {
    const room = rooms.get(roomCode);
    if (!room || room.mode !== 'practice' || !room.practice) return;
    if (room.phase !== 'active') return;
    const p = room.practice;
    const limit = practiceLimit(room);
    if (p.idx < limit) p.idx++;
    p.phase = 'answering';
    p.lastResult = null;
    p.bids = [];
    p.openForAll = false;
    // Si el profe asignó turno a mano y aún no se cumple, la siguiente pregunta
    // la contesta ese alumno (no se rota encima de la asignación).
    if (p.idx < limit) {
      if (p.turnManual) p.turnManual = false;
      else advancePracticeTurn(room);
    }
    schedulePracticeTimer(room);
    broadcastPractice(room);
    console.log(`[${roomCode}] Carrusel: pregunta ${Math.min(p.idx + 1, limit)}/${limit}, turno de ${practiceTurnName(room) || '—'}`);
  });

  // ── Práctica (Carrusel): el profesor reasigna el turno ──
  socket.on('practiceSetTurn', ({ roomCode, name }) => {
    const room = rooms.get(roomCode);
    if (!room || room.mode !== 'practice' || !room.practice) return;
    const p = room.practice;
    const i = p.turnQueue.findIndex(n => n.toLowerCase() === String(name).toLowerCase());
    if (i === -1) return;
    p.turnPos = i;
    p.turnManual = true;
    if (p.phase === 'answering') {
      p.bids = [];                  // el nuevo titular arranca con ventana fresca
      p.openForAll = false;
      schedulePracticeTimer(room);
    }
    broadcastPractice(room);
    console.log(`[${roomCode}] Carrusel: turno reasignado a ${p.turnQueue[i]}`);
  });

  // ── Student switches tab ──
  socket.on('tabSwitch', () => {
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room) return;
    if (room.mode === 'practice') return; // sesión guiada: sin candado de pestañas
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
    if (room.mode === 'practice') { if (typeof ack === 'function') ack({ ok: false, error: 'practice mode' }); return; }
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
    if (room.mode === 'practice' && room.practice) {
      // Corte de equidad: mayor múltiplo de los participantes presentes que
      // cabe en el total de preguntas (todos contestan exactamente lo mismo).
      const p = room.practice;
      const n = p.turnQueue.length;
      const total = room.questions.length;
      const cut = n > 0 ? Math.floor(total / n) * n : total;
      p.limit = cut > 0 ? cut : total;
      if (n > 0) console.log(`[${roomCode}] Carrusel: ${p.limit} de ${total} preguntas (${n} participantes, ${Math.floor(p.limit / n)} c/u)`);
      p.bids = [];
      p.openForAll = false;
      schedulePracticeTimer(room);
      broadcastPractice(room);
    }
    broadcastRoomsList();
    console.log(`[${roomCode}] ${room.mode === 'practice' ? 'Práctica iniciada' : 'Examen iniciado'}`);
  });

  // ── Teacher: close exam ──
  socket.on('closeExam', ({ roomCode }) => {
    const room = rooms.get(roomCode);
    if (!room) return;
    // Práctica: cerrar es solo terminar la sesión — sin auto-entrega, sin
    // comprobantes PDF ni clave. Se envía el marcador final a todos.
    if (room.mode === 'practice') {
      room.phase = 'closed';
      clearPracticeTimer(room);
      // Marcar terminada y vaciar apuestas: si llega un disconnect después, el
      // broadcast no revivirá la pregunta ni apuestas viejas sobre el podio final.
      if (room.practice) { room.practice.phase = 'finished'; room.practice.bids = []; room.practice.openForAll = false; }
      io.to(roomCode).emit('practiceClosed', { scores: room.practice?.scores || {} });
      io.to('teachers').emit('roomClosed', { roomCode, mode: 'practice' });
      broadcastRoomsList();
      console.log(`[${roomCode}] Práctica cerrada`);
      return;
    }
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
    io.to('teachers').emit('roomClosed', { roomCode, mode: 'exam' });
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
    if (room.mode === 'practice' && room.practice) {
      clearPracticeTimer(room);
      room.practice = { idx: 0, phase: 'answering', turnQueue: [], turnPos: 0, turnManual: false, scores: {}, lastResult: null, limit: null, bids: [], openForAll: false, answerDeadline: null, timerToken: 0 };
    }
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
    if (room.mode === 'practice') clearPracticeTimer(room);
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
      mode: room.mode || 'exam',
      title: room.title,
      group: room.group,
      totalQuestions: room.questions.length,
      startTime: room.startTime,
      timeLimit: room.timeLimitMinutes,
    });
    socket.emit('studentsUpdate', getStudentSummary(room));
    if (room.mode === 'practice') socket.emit('practiceTeacherState', buildPracticeTeacherState(room));
  });

  // ── Disconnect ──
  socket.on('disconnect', () => {
    const roomCode = socketRoom.get(socket.id);
    if (roomCode) {
      const room = rooms.get(roomCode);
      if (room && room.students[socket.id]) {
        room.students[socket.id].connected = false;
        io.to(roomCode).emit('studentsUpdate', getStudentSummary(room));
        if (room.mode === 'practice' && room.phase === 'active') broadcastPractice(room); // refresca indicador de turno conectado (no en salas cerradas)
        broadcastRoomsList();
        console.log(`[${roomCode}] ${room.students[socket.id].name} desconectado`);
      }
      socketRoom.delete(socket.id);
    }
  });
});

// ─── Start Server ───────────────────────────────────────────────────────────
// Solo arranca el listener cuando se ejecuta directamente (node server.js).
// Si se hace require() del módulo (p.ej. para pruebas del PDF) no abre el puerto.
if (require.main === module) {
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
}

module.exports = {
  buildComprobanteHTML,
  buildAnswerKeyHTML,
  applyPdfBlankWidths,
  enqueueAnswerKeyPDF,
  getPdfBrowser,
  TERCIAL_PDF_CSS,
};
