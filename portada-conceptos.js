// Genera 3 conceptos de "portada puntaje protagonista" (anillo de progreso) para
// el comprobante PDF, con datos y fuentes reales. NO toca server.js — solo crea
// PDFs de muestra en /tmp para comparar y decidir cuál implementar.
//
// Uso (desde la raíz del repo):
//   1) node server.js            # sirve las fuentes en :3000
//   2) node portada-conceptos.js # genera /tmp/portada_*.pdf
//
// Variantes: A (anillo centrado coñac) · B (editorial) · C (anillo por nivel).
const puppeteer = require('puppeteer');
const O = process.env.ORIGIN || 'http://localhost:3000';

// Datos de muestra (ajusta a gusto para previsualizar otros casos)
const correct = 91, total = 128, pct = 71, tiempo = '2h 0m', domina = 6, materias = 10;
const RING_R = 62, C = 2 * Math.PI * RING_R;
const arc = (p) => (p / 100 * C).toFixed(1) + ' ' + C.toFixed(1);

function ring(color, big, small) {
  return `<div style="position:relative;width:160px;height:160px">
    <svg width="160" height="160" viewBox="0 0 160 160">
      <circle cx="80" cy="80" r="${RING_R}" fill="none" stroke="#ede2c5" stroke-width="11"/>
      <circle cx="80" cy="80" r="${RING_R}" fill="none" stroke="${color}" stroke-width="11" stroke-linecap="round"
        stroke-dasharray="${arc(pct)}" transform="rotate(-90 80 80)"/>
    </svg>
    <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:1">
      <div style="font-family:'Fraunces',serif;font-style:italic;font-weight:500;font-size:38pt;color:${color}">${big}</div>
      <div style="font-size:9pt;color:#8c7556;margin-top:2pt;letter-spacing:.02em">${small}</div>
    </div></div>`;
}
const metric = (label, val) => `<div style="text-align:center"><div style="font-family:'Fraunces',serif;font-size:19pt;color:#4a3f33;line-height:1">${val}</div><div style="font-size:8pt;letter-spacing:.1em;text-transform:uppercase;color:#8c7556;margin-top:4pt">${label}</div></div>`;
const metricRow = (gap) => `<div style="display:flex;justify-content:center;gap:${gap}">${metric('Aciertos', correct + ' / ' + total)}${metric('Tiempo', tiempo)}${metric('Dominadas', domina + ' / ' + materias)}</div>`;

const A = `<section style="text-align:center;padding:26pt 0;border-top:1px solid #8c7556;border-bottom:1px solid #8c7556">
  <p style="font-size:9pt;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:#8c7556;margin:0 0 16pt">Resultado</p>
  <div style="display:flex;justify-content:center;margin-bottom:18pt">${ring('#6b3a2e', pct + '%', correct + '/' + total)}</div>
  ${metricRow('48pt')}
</section>`;

const B = `<section style="padding:26pt 0;border-top:1px solid #8c7556;border-bottom:1px solid #8c7556;display:flex;align-items:center;gap:40pt">
  ${ring('#6b3a2e', pct + '%', correct + '/' + total)}
  <div style="flex:1">
    <p style="font-size:9pt;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:#8c7556;margin:0 0 14pt">Resultado</p>
    <div style="display:flex;flex-direction:column;gap:10pt">
      <div style="display:flex;justify-content:space-between;border-bottom:1px solid #ede2c5;padding-bottom:7pt"><span style="color:#7a6448;font-size:10.5pt">Aciertos</span><span style="font-family:'Fraunces',serif;font-size:14pt;color:#4a3f33">${correct} / ${total}</span></div>
      <div style="display:flex;justify-content:space-between;border-bottom:1px solid #ede2c5;padding-bottom:7pt"><span style="color:#7a6448;font-size:10.5pt">Tiempo</span><span style="font-family:'Fraunces',serif;font-size:14pt;color:#4a3f33">${tiempo}</span></div>
      <div style="display:flex;justify-content:space-between"><span style="color:#7a6448;font-size:10.5pt">Materias dominadas</span><span style="font-family:'Fraunces',serif;font-size:14pt;color:#4a3f33">${domina} / ${materias}</span></div>
    </div>
  </div>
</section>`;

const levelColor = pct >= 70 ? '#1D9E75' : pct >= 50 ? '#EF9F27' : '#E24B4A';
const levelLabel = pct >= 70 ? 'Domina' : pct >= 50 ? 'En proceso' : 'Requiere atención';
const Cv = `<section style="text-align:center;padding:26pt 0;border-top:1px solid #8c7556;border-bottom:1px solid #8c7556">
  <p style="font-size:9pt;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:#8c7556;margin:0 0 16pt">Resultado</p>
  <div style="display:flex;justify-content:center;margin-bottom:8pt">${ring(levelColor, pct + '%', correct + '/' + total)}</div>
  <div style="font-size:9pt;letter-spacing:.08em;text-transform:uppercase;color:${levelColor};font-weight:500;margin-bottom:16pt">Nivel: ${levelLabel}</div>
  ${metricRow('48pt')}
</section>`;

function page(block, label) {
  return `<div style="width:6.7in;margin:0 auto;padding:0.5in 0">
    <header style="border-top:3px solid #8c4a3a;padding-top:0.34in;margin-bottom:0.3in">
      <p style="font-size:10pt;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:#8c7556;margin:0 0 12pt">Comprobante de examen · Ingreso a Nivel Medio Superior</p>
      <h1 style="font-family:'Fraunces',serif;font-weight:500;font-size:32pt;letter-spacing:-.02em;color:#1f1a16;margin:0 0 12pt;font-variation-settings:'opsz' 96">ECOEMS 9</h1>
      <p style="font-size:11pt;color:#7a6448;margin:0"><strong style="font-weight:500;color:#4a3f33">Muestra Diseño</strong> · 19 de junio de 2026 · Tiempo: ${tiempo}</p>
    </header>
    ${block}
    <p style="text-align:center;font-size:9pt;color:#8c7556;margin-top:14pt">${label}</p>
  </div>`;
}

(async () => {
  const b = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  for (const [name, block] of [['A_anillo_centrado', A], ['B_anillo_editorial', B], ['C_anillo_nivel', Cv]]) {
    const p = await b.newPage();
    await p.setContent(`<html><head><base href="${O}/"><link rel="stylesheet" href="${O}/fonts/tercial-fonts.css">
      <style>*{margin:0;padding:0;box-sizing:border-box}body{background:#f4ecd8;font-family:'IBM Plex Sans',sans-serif}</style></head>
      <body>${page(block, 'Variante ' + name.split('_')[0])}</body></html>`, { waitUntil: 'networkidle0' });
    await p.evaluate(async () => { await document.fonts.ready; });
    await p.pdf({ path: `/tmp/portada_${name}.pdf`, format: 'letter', margin: { top: '0', bottom: '0', left: '0', right: '0' }, printBackground: true });
    await p.close();
    console.log('OK', `/tmp/portada_${name}.pdf`);
  }
  await b.close();
})();
