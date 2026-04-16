const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const fs = require('fs');
const os = require('os');
const QRCode = require('qrcode');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

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

function createRoom(data) {
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
  };

  const sections = data.exam?.sections || [];
  sections.forEach(section => {
    section.questions.forEach(q => {
      room.questions.push({
        id: q.id,
        text: q.text,
        options: q.options,
        image: q.image || null,
        topic: q.topic,
        topic_name: q.topic_name || '',
        subject: section.subject,
      });
      room.answerKey[q.id] = q.answer;
    });
  });

  rooms.set(roomCode, room);
  return room;
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
app.post('/api/upload-exam', (req, res) => {
  try {
    const room = createRoom(req.body);
    console.log(`Sala ${room.roomCode} creada: "${room.title}" (${room.questions.length} preguntas)`);
    res.json({ success: true, totalQuestions: room.questions.length, roomCode: room.roomCode });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
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
        joinedAt: Date.now(),
      };
    }

    const student = room.students[socket.id];
    const questionsForStudent = student.questionOrder.map(qid => {
      const q = room.questions.find(x => x.id === qid);
      const origLetters = Object.keys(q.options);
      const srcLetters = student.optionOrders[qid];

      const newOptions = {};
      origLetters.forEach((newLetter, i) => {
        newOptions[newLetter] = q.options[srcLetters[i]];
      });

      const correctOrig = room.answerKey[qid];
      student.answerKey[qid] = origLetters[srcLetters.indexOf(correctOrig)];

      return { id: q.id, text: q.text, options: newOptions, image: q.image, subject: q.subject };
    });

    socket.emit('joined', {
      name: cleanName,
      group: room.group,
      title: room.title,
      questions: questionsForStudent,
      timeLimit: room.timeLimitMinutes,
      examActive: room.phase === 'active',
      startTime: room.startTime,
      roomCode,
    });

    io.to(roomCode).emit('studentsUpdate', getStudentSummary(room));
    console.log(`[${roomCode}] ${cleanName} (${room.group}) se unió`);
  });

  // ── Student answers a question ──
  socket.on('answer', ({ questionId, answer }) => {
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room) return;
    const student = room.students[socket.id];
    if (!student || student.submitted) return;
    if (room.phase !== 'active') return;
    if (student.joinedAt && Date.now() - student.joinedAt < 3000) return;
    student.answers[questionId] = answer;
    io.to(roomCode).emit('studentsUpdate', getStudentSummary(room));
  });

  // ── Student switches tab ──
  socket.on('tabSwitch', () => {
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room) return;
    const student = room.students[socket.id];
    if (!student || student.submitted) return;
    student.tabSwitches = (student.tabSwitches || 0) + 1;
    io.to(roomCode).emit('studentsUpdate', getStudentSummary(room));
  });

  // ── Student marks/unmarks question ──
  socket.on('toggleMark', ({ questionId }) => {
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room) return;
    const student = room.students[socket.id];
    if (!student || student.submitted) return;
    const idx = student.marked.indexOf(questionId);
    if (idx === -1) student.marked.push(questionId);
    else student.marked.splice(idx, 1);
    socket.emit('markedUpdate', student.marked);
  });

  // ── Student submits exam ──
  socket.on('submitExam', () => {
    const roomCode = socketRoom.get(socket.id);
    const room = roomCode && rooms.get(roomCode);
    if (!room) return;
    const student = room.students[socket.id];
    if (!student || student.submitted) return;

    student.submitted = true;
    student.submitTime = Date.now();

    let correct = 0;
    room.questions.forEach(q => {
      const key = student.answerKey?.[q.id] ?? room.answerKey[q.id];
      if (student.answers[q.id] === key) correct++;
    });

    socket.emit('examSubmitted', {
      correct,
      total: room.questions.length,
      answerKey: student.answerKey ?? room.answerKey,
    });

    io.to(roomCode).emit('studentsUpdate', getStudentSummary(room));
    console.log(`[${roomCode}] ${student.name} entregó: ${correct}/${room.questions.length}`);
  });

  // ── Teacher: start exam ──
  socket.on('startExam', ({ roomCode }) => {
    const room = rooms.get(roomCode);
    if (!room) return;
    room.phase = 'active';
    room.startTime = Date.now();
    Object.values(room.students).forEach(s => { s.startTime = room.startTime; });
    io.to(roomCode).emit('examStarted', { startTime: room.startTime, timeLimit: room.timeLimitMinutes });
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
          });
        }
      }
    });
    io.to(roomCode).emit('examClosed');
    console.log(`[${roomCode}] Examen cerrado`);
  });

  // ── Teacher: reset exam (keep room, clear students) ──
  socket.on('resetExam', ({ roomCode }) => {
    const room = rooms.get(roomCode);
    if (!room) return;
    room.phase = 'waiting';
    room.students = {};
    room.startTime = null;
    io.to(roomCode).emit('examReset');
    console.log(`[${roomCode}] Examen reiniciado`);
  });

  // ── Teacher: delete room entirely ──
  socket.on('deleteRoom', ({ roomCode }) => {
    const room = rooms.get(roomCode);
    if (!room) return;
    io.to(roomCode).emit('roomDeleted');
    rooms.delete(roomCode);
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
    socket.emit('roomsList', list);
  });

  // ── Teacher: watch a room (join for live updates) ──
  socket.on('watchRoom', ({ roomCode }) => {
    for (const r of socket.rooms) {
      if (r !== socket.id) socket.leave(r);
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
        console.log(`[${roomCode}] ${room.students[socket.id].name} desconectado`);
      }
      socketRoom.delete(socket.id);
    }
  });
});

// ─── Start Server ───────────────────────────────────────────────────────────
const PORT = 3000;
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
