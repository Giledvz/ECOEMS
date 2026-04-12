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

// ─── Exam State ─────────────────────────────────────────────────────────────
let exam = {
  phase: 'waiting',
  title: '',
  group: '',
  studentList: [],       // names from JSON
  questions: [],
  answerKey: {},
  students: {},
  timeLimitMinutes: 180,
  startTime: null,
};

function resetExam() {
  exam = {
    phase: 'waiting',
    title: '',
    group: '',
    studentList: [],
    questions: [],
    answerKey: {},
    students: {},
    timeLimitMinutes: 180,
    startTime: null,
  };
}

function getStudentSummary() {
  return Object.entries(exam.students).map(([id, s]) => {
    let correct = 0;
    if (s.submitted) {
      exam.questions.forEach(q => {
        const key = s.answerKey?.[q.id] ?? exam.answerKey[q.id];
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
      total: exam.questions.length,
      marked: s.marked.length,
      submitted: s.submitted,
      connected: s.connected,
      correct: s.submitted ? correct : null,
      timeUsed,
      tabSwitches: s.tabSwitches || 0,
    };
  });
}

function generateCSV() {
  if (exam.questions.length === 0) return '';
  
  const questionIds = exam.questions.map(q => q.id);
  const fecha = exam.date || new Date().toISOString().split('T')[0];
  let header = 'Fecha,Alumno,Grupo,Tiempo_min,Salidas_pestaña';
  questionIds.forEach(id => { header += `,P${id}`; });
  header += '\n';

  let rows = '';
  Object.values(exam.students).forEach(s => {
    const timeMin = s.submitted && s.submitTime && s.startTime
      ? Math.round((s.submitTime - s.startTime) / 60000)
      : '';
    let row = `${fecha},${s.name},${s.group},${timeMin},${s.tabSwitches || 0}`;
    questionIds.forEach(id => {
      const ans = s.answers[id];
      if (!ans || !s.optionOrders?.[id]) {
        row += `,${ans || ''}`;
      } else {
        // Convert shuffled letter back to original letter for consistent CSV
        const origLetters = Object.keys(exam.questions.find(q => q.id === id).options);
        row += `,${s.optionOrders[id][origLetters.indexOf(ans)] || ''}`;
      }
    });
    rows += row + '\n';
  });

  return header + rows;
}

function generateAnswerKeyCSV() {
  if (exam.questions.length === 0) return '';
  let header = 'Pregunta,Asignatura,Tema,Tema_nombre,Respuesta_correcta\n';
  let rows = '';
  exam.questions.forEach(q => {
    rows += `P${q.id},${q.subject},${q.topic},"${q.topic_name}",${exam.answerKey[q.id]}\n`;
  });
  return header + rows;
}

// ─── API Endpoints ──────────────────────────────────────────────────────────

// Teacher uploads exam JSON
app.post('/api/upload-exam', (req, res) => {
  try {
    const data = req.body;
    resetExam();
    io.emit('examReset');
    
    exam.title = data.exam?.title || 'Examen';
    exam.group = data.exam?.group || 'Sin grupo';
    exam.date = data.exam?.date || new Date().toISOString().split('T')[0];
    exam.studentList = data.exam?.students || [];
    exam.timeLimitMinutes = data.timeLimitMinutes || 180;
    
    const sections = data.exam?.sections || [];
    sections.forEach(section => {
      section.questions.forEach(q => {
        exam.questions.push({
          id: q.id,
          text: q.text,
          options: q.options,
          image: q.image || null,
          topic: q.topic,
          topic_name: q.topic_name || '',
          subject: section.subject,
        });
        exam.answerKey[q.id] = q.answer;
      });
    });

    exam.phase = 'waiting';
    io.emit('examLoaded', { title: exam.title, group: exam.group, studentList: exam.studentList, totalQuestions: exam.questions.length });
    res.json({ success: true, totalQuestions: exam.questions.length });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Download CSV results
app.get('/api/download-csv', (req, res) => {
  const csv = generateCSV();
  const [y, m, d] = (exam.date || new Date().toISOString().split('T')[0]).split('-');
  const filename = `resultados_${d}${m}${y.slice(2)}.csv`;
  const filePath = path.join(__dirname, filename);
  fs.writeFileSync(filePath, '\uFEFF' + csv, 'utf8');
  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', `attachment; filename=${filename}`);
  res.send('\uFEFF' + csv);
});

// Download answer key CSV
app.get('/api/download-key', (req, res) => {
  const csv = generateAnswerKeyCSV();
  const fecha = (exam.date || new Date().toISOString().split('T')[0]).replace(/-/g, '');
  const filename = `clave_respuestas_${fecha}.csv`;
  const filePath = path.join(__dirname, filename);
  fs.writeFileSync(filePath, '\uFEFF' + csv, 'utf8');
  res.setHeader('Content-Type', 'text/csv; charset=utf-8');
  res.setHeader('Content-Disposition', `attachment; filename=${filename}`);
  res.send('\uFEFF' + csv);
});

// QR code for student URL
app.get('/api/qr', async (req, res) => {
  const nets = os.networkInterfaces();
  let localIP = 'localhost';
  outer: for (const ifaces of Object.values(nets)) {
    for (const iface of ifaces) {
      if (iface.family === 'IPv4' && !iface.internal) {
        localIP = iface.address;
        break outer;
      }
    }
  }
  const url = `http://${localIP}:${PORT}`;
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
  
  // Send current state
  socket.emit('state', {
    phase: exam.phase,
    title: exam.title,
    group: exam.group,
    studentList: exam.studentList,
    totalQuestions: exam.questions.length,
    startTime: exam.startTime,
    timeLimit: exam.timeLimitMinutes,
  });

  // ── Student joins ──
  socket.on('joinExam', ({ name }) => {
    if (exam.phase === 'closed') { socket.emit('joinError', 'El examen ya fue cerrado'); return; }

    const cleanName = String(name).trim().substring(0, 30);
    if (!cleanName) { socket.emit('joinError', 'Selecciona tu nombre'); return; }

    // Validate name is in the student list (if list exists)
    if (exam.studentList.length > 0) {
      const validName = exam.studentList.find(s => s.toLowerCase() === cleanName.toLowerCase());
      if (!validName) { socket.emit('joinError', 'Tu nombre no está en la lista'); return; }
    }

    const nameExists = Object.values(exam.students).some(
      s => s.name.toLowerCase() === cleanName.toLowerCase() && s.connected
    );
    if (nameExists) { socket.emit('joinError', 'Ese nombre ya está en uso'); return; }

    // Check if reconnecting (same name, previously disconnected)
    const prevEntry = Object.entries(exam.students).find(
      ([id, s]) => s.name.toLowerCase() === cleanName.toLowerCase() && !s.connected
    );

    if (prevEntry) {
      // Transfer old data to new socket
      const [oldId, oldData] = prevEntry;
      oldData.connected = true;
      exam.students[socket.id] = oldData;
      delete exam.students[oldId];
      console.log(`${cleanName} reconectado`);
    } else {
      // Force clear any stale client state before sending new data
      socket.emit('examReset');

      // Generate shuffled question order for this student
      const questionsBySubject = {};
      exam.questions.forEach(q => {
        if (!questionsBySubject[q.subject]) questionsBySubject[q.subject] = [];
        questionsBySubject[q.subject].push(q.id);
      });
      const shuffledSubjects = shuffle(Object.keys(questionsBySubject));
      const questionOrder = [];
      shuffledSubjects.forEach(subj => {
        questionsBySubject[subj].forEach(id => questionOrder.push(id));
      });

      const optionOrders = {};
      exam.questions.forEach(q => {
        optionOrders[q.id] = shuffle(Object.keys(q.options));
      });

      exam.students[socket.id] = {
        name: cleanName,
        group: exam.group,
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

    // Build questions in the student's stored order with shuffled options
    const student = exam.students[socket.id];
    const questionsForStudent = student.questionOrder.map(qid => {
      const q = exam.questions.find(x => x.id === qid);
      const origLetters = Object.keys(q.options);       // ['A','B','C','D']
      const srcLetters  = student.optionOrders[qid];    // e.g. ['C','A','D','B']

      const newOptions = {};
      origLetters.forEach((newLetter, i) => {
        newOptions[newLetter] = q.options[srcLetters[i]];
      });

      // Which new letter maps to the globally correct answer?
      const correctOrig = exam.answerKey[qid];
      student.answerKey[qid] = origLetters[srcLetters.indexOf(correctOrig)];

      return { id: q.id, text: q.text, options: newOptions, image: q.image, subject: q.subject };
    });

    socket.emit('joined', {
      name: cleanName,
      group: exam.group,
      questions: questionsForStudent,
      timeLimit: exam.timeLimitMinutes,
      examActive: exam.phase === 'active',
      startTime: exam.startTime,
    });

    io.emit('studentsUpdate', getStudentSummary());
    console.log(`${cleanName} (${exam.group}) se unió`);
  });

  // ── Student answers a question ──
  socket.on('answer', ({ questionId, answer }) => {
    const student = exam.students[socket.id];
    if (!student || student.submitted) return;
    if (exam.phase !== 'active') return;
    // Block bulk answer re-sends from cached client JS (old localStorage restore)
    if (student.joinedAt && Date.now() - student.joinedAt < 3000) return;

    student.answers[questionId] = answer;
    io.emit('studentsUpdate', getStudentSummary());
  });

  // ── Student switches tab ──
  socket.on('tabSwitch', () => {
    const student = exam.students[socket.id];
    if (!student || student.submitted) return;
    student.tabSwitches = (student.tabSwitches || 0) + 1;
    io.emit('studentsUpdate', getStudentSummary());
  });

  // ── Student marks/unmarks question for review ──
  socket.on('toggleMark', ({ questionId }) => {
    const student = exam.students[socket.id];
    if (!student || student.submitted) return;
    
    const idx = student.marked.indexOf(questionId);
    if (idx === -1) student.marked.push(questionId);
    else student.marked.splice(idx, 1);
    
    socket.emit('markedUpdate', student.marked);
  });

  // ── Student submits exam ──
  socket.on('submitExam', () => {
    const student = exam.students[socket.id];
    if (!student || student.submitted) return;
    
    student.submitted = true;
    student.submitTime = Date.now();
    
    // Calculate score
    let correct = 0;
    exam.questions.forEach(q => {
      const key = student.answerKey?.[q.id] ?? exam.answerKey[q.id];
      if (student.answers[q.id] === key) correct++;
    });

    socket.emit('examSubmitted', {
      correct,
      total: exam.questions.length,
      answerKey: student.answerKey ?? exam.answerKey,
    });
    
    io.emit('studentsUpdate', getStudentSummary());
    console.log(`${student.name} entregó: ${correct}/${exam.questions.length}`);
  });

  // ── Teacher controls ──
  socket.on('startExam', () => {
    exam.phase = 'active';
    exam.startTime = Date.now();
    // Set startTime for all connected students
    Object.values(exam.students).forEach(s => { s.startTime = exam.startTime; });
    io.emit('examStarted', { startTime: exam.startTime, timeLimit: exam.timeLimitMinutes });
    console.log('Examen iniciado');
  });

  socket.on('closeExam', () => {
    exam.phase = 'closed';
    // Auto-submit for students who haven't submitted
    Object.entries(exam.students).forEach(([id, s]) => {
      if (!s.submitted) {
        s.submitted = true;
        s.submitTime = Date.now();
        const sock = io.sockets.sockets.get(id);
        if (sock) {
          let correct = 0;
          exam.questions.forEach(q => {
            const key = s.answerKey?.[q.id] ?? exam.answerKey[q.id];
            if (s.answers[q.id] === key) correct++;
          });
          sock.emit('examSubmitted', {
            correct,
            total: exam.questions.length,
            answerKey: s.answerKey ?? exam.answerKey,
          });
        }
      }
    });
    io.emit('examClosed');
    console.log('Examen cerrado');
  });

  socket.on('resetExam', () => {
    resetExam();
    io.emit('examReset');
    console.log('Examen reseteado');
  });

  socket.on('getStudents', () => {
    socket.emit('studentsUpdate', getStudentSummary());
  });

  // ── Disconnect ──
  socket.on('disconnect', () => {
    if (exam.students[socket.id]) {
      exam.students[socket.id].connected = false;
      io.emit('studentsUpdate', getStudentSummary());
      console.log(`${exam.students[socket.id].name} desconectado`);
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
  
  const nets = os.networkInterfaces();
  Object.values(nets).forEach(ifaces => {
    ifaces.forEach(iface => {
      if (iface.family === 'IPv4' && !iface.internal) {
        console.log(`\n  Los alumnos se conectan a:`);
        console.log(`  → http://${iface.address}:${PORT}`);
        console.log(`\n  Panel del profesor (desde otro dispositivo):`);
        console.log(`  → http://${iface.address}:${PORT}/teacher`);
      }
    });
  });
  console.log(`\n══════════════════════════════════════════\n`);
});
