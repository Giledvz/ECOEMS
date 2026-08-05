// Imprime cuadernillo.html a PDF conservando los hipervínculos internos.
//
// Chrome sí convierte los anclajes (#id) en enlaces reales dentro del PDF, así que el
// "ver respuesta →" de cada ejercicio funciona con clic en cualquier lector.
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const RAIZ = '/Users/giledvz/Documents/ECOEMS';
const ENTRADA = path.join(RAIZ, 'fuentes/ets/cuadernillo.html');
const SALIDA = path.join(RAIZ, 'ETS-Geometria-y-Trigonometria-practica.pdf');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  const errores = [];
  page.on('pageerror', (e) => errores.push(String(e)));

  await page.goto('file://' + ENTRADA, { waitUntil: 'networkidle0', timeout: 120000 });
  // esperar a que KaTeX termine de componer todas las fórmulas
  await page.waitForFunction(() => document.body.dataset.listo === '1', { timeout: 120000 });

  const stats = await page.evaluate(() => ({
    formulas: document.querySelectorAll('.katex').length,
    // se mira solo el texto que KaTeX NO tocó: dentro de .katex los signos de
    // pesos son glifos legítimos de cantidades en dinero, no delimitadores
    sinRenderizar: (() => {
      const c = document.body.cloneNode(true);
      c.querySelectorAll('.katex, .katex-display, script, style').forEach((e) => e.remove());
      return (c.innerText.match(/\$[^$\n]{1,80}\$/g) || []);
    })(),
    enlaces: document.querySelectorAll('a[href^="#"]').length,
    huerfanos: [...document.querySelectorAll('a[href^="#"]')]
      .filter((a) => !document.getElementById(a.getAttribute('href').slice(1)))
      .map((a) => a.getAttribute('href')),
  }));

  await page.pdf({
    path: SALIDA,
    format: 'Letter',
    printBackground: true,
    margin: { top: '16mm', bottom: '18mm', left: '16mm', right: '16mm' },
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate:
      `<div style="width:100%;font:8pt Georgia,serif;color:#a89c92;
        padding:0 16mm;display:flex;justify-content:space-between">
        <span>ETS · Geometría y Trigonometría · cuadernillo de práctica</span>
        <span class="pageNumber"></span>
      </div>`,
  });

  await browser.close();

  // Copia servida, para poder abrirlo desde el navegador sin buscar el archivo.
  // public/_pdf/ va en .gitignore: el PDF bueno es el de la raíz del repo.
  const publico = path.join(RAIZ, 'public/_pdf', path.basename(SALIDA));
  fs.mkdirSync(path.dirname(publico), { recursive: true });
  fs.copyFileSync(SALIDA, publico);
  const url = 'http://localhost:3000/_pdf/' + encodeURIComponent(path.basename(SALIDA));

  console.log(JSON.stringify({ salida: SALIDA, url, ...stats, errores }, null, 1));
})();
