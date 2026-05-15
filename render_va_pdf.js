#!/usr/bin/env node
// Render examen_ecoems_2015_versionA_con_respuestas.html → PDF using Puppeteer.
const path = require('path');
const fs = require('fs');
const puppeteer = require('puppeteer');

const HTML_PATH = path.join(__dirname, 'public', 'examen_ecoems_2015_versionA_con_respuestas.html');
const PDF_PATH = path.join(__dirname, 'Examen ECOEMS 2015 — Versión A (con respuestas).pdf');

(async () => {
  if (!fs.existsSync(HTML_PATH)) {
    console.error('❌ HTML no encontrado:', HTML_PATH);
    process.exit(1);
  }
  console.log('Iniciando Puppeteer...');
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();

  // file:// URL so the page can resolve local images
  const fileUrl = 'file://' + HTML_PATH;
  console.log('Cargando', fileUrl);
  await page.goto(fileUrl, { waitUntil: 'networkidle0', timeout: 60000 });

  // Give KaTeX a moment to render after networkidle
  await new Promise(r => setTimeout(r, 1500));

  console.log('Generando PDF...');
  await page.pdf({
    path: PDF_PATH,
    format: 'Letter',
    margin: { top: '15mm', right: '12mm', bottom: '15mm', left: '12mm' },
    printBackground: true,
  });

  await browser.close();
  const sizeKB = (fs.statSync(PDF_PATH).size / 1024).toFixed(0);
  console.log(`✓ PDF generado: ${PDF_PATH} (${sizeKB} KB)`);
})().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
