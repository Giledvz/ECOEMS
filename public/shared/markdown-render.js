// Renderer compartido entre el cliente (browser) y el server (Node).
// Cada contexto define las variables CSS --md-* (text, border, table-bg, th-bg, font)
// con sus propios valores; el HTML generado es el mismo en ambos lados.

(function(global) {
  // En Node tenemos katex como dependencia directa; en browser viene como global.
  var katexLib = (typeof require !== 'undefined' && typeof window === 'undefined')
    ? require('katex')
    : (typeof katex !== 'undefined' ? katex : null);

  function renderInlineMath(text) {
    var parts = String(text).split(/(\$\$[\s\S]+?\$\$|\$[^$\n]+?\$)/g);
    return parts.map(function(p) {
      var isDisplay = p.indexOf('$$') === 0 && p.lastIndexOf('$$') === p.length - 2 && p.length >= 4;
      var isInline = !isDisplay && p.length >= 2 && p.charAt(0) === '$' && p.charAt(p.length - 1) === '$' && p.indexOf('\n') === -1;
      if (isDisplay || isInline) {
        var inner = isDisplay ? p.slice(2, -2) : p.slice(1, -1);
        if (katexLib) {
          try { return katexLib.renderToString(inner, { throwOnError: false, displayMode: false, macros: { "\\sen": "\\operatorname{sen}", "\\tg": "\\operatorname{tg}" } }); } catch(e) {}
        }
        return inner.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      }
      return p.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/&lt;(\/?(u|b|i|strong|em))&gt;/g, '<$1>')
        .replace(/&lt;br\s*\/?&gt;/g, '<br>')
        .replace(/&lt;img\s+([^&]*?)\/?&gt;/g, '<img $1>')
        .replace(/_{3,}/g, function(m) {
          return '<span class="md-blank" style="display:inline-block;border-bottom:1px solid currentColor;width:' + (m.length * 1.3) + 'em;height:1.5px;background-color:currentColor;vertical-align:0.18em;"></span>';
        })
        .replace(/\*\*([^*\n]+?)\*\*/g, '<b>$1</b>')
        .replace(/(^|[^*])\*([^*\n]+?)\*(?!\*)/g, '$1<b>$2</b>');
    }).join('');
  }

  function renderMarkdownTable(block) {
    var lines = block.split('\n').map(function(l){ return l.trim(); }).filter(function(l){ return l.length > 0; });
    if (lines.length < 2) return block;
    var parseCells = function(line) {
      return line.replace(/^\||\|$/g, '').split('|').map(function(c){ return c.trim(); });
    };
    var header = parseCells(lines[0]);
    var separator = parseCells(lines[1]);
    var body = lines.slice(2).map(parseCells);

    // Alineación por columna desde la fila separadora del markdown.
    // :-  = left, :-: = center, -: = right, - = default (center, convención ECOEMS).
    var aligns = separator.map(function(s) {
      var t = s.trim();
      var startsCol = t.charAt(0) === ':';
      var endsCol = t.charAt(t.length - 1) === ':';
      if (startsCol && endsCol) return 'center';
      if (endsCol) return 'right';
      if (startsCol) return 'left';
      return 'center';
    });

    // Si todos los cells del header están vacíos, omitimos el <thead>.
    var headerless = header.every(function(c){ return c === ''; });
    // Si hay celdas vacías en el cuerpo, omitimos las líneas horizontales entre
    // filas (las verticales y el separador del header se mantienen).
    var hasEmptyBodyCells = body.some(function(row){ return row.some(function(c){ return c === ''; }); });

    // Detectar columnas con "trailing empty cells": items contiguos al principio
    // seguidos de celdas vacías al final. En esas columnas fusionamos los items
    // en una sola celda con rowspan que abarca todo el body, y los centramos
    // verticalmente (visualmente queda como un grupo centrado en lugar de
    // alineado arriba con espacio vacío abajo).
    var nCols = aligns.length;
    var nRows = body.length;
    var mergedCol = [];
    for (var ci = 0; ci < nCols; ci++) {
      var items = [];
      var sawEmpty = false;
      var skipMerge = false;
      for (var ri = 0; ri < nRows; ri++) {
        var v = body[ri][ci];
        if (v === '') sawEmpty = true;
        else {
          if (sawEmpty) { skipMerge = true; break; } // empty intercalado: no fusionar
          items.push(v);
        }
      }
      mergedCol[ci] = (!skipMerge && sawEmpty && items.length > 0) ? items : null;
    }

    function makeCellStyle(i, isHeader) {
      var s = 'padding:10px 14px; font-variant-numeric:tabular-nums; color:var(--md-text); text-align:' + aligns[i] + '; vertical-align:middle;';
      if (i > 0) s += ' border-left:1px solid var(--md-border);';
      if (!isHeader && !hasEmptyBodyCells) {
        s += ' border-bottom:1px solid var(--md-border);';
      }
      return s;
    }
    function makeHeadStyle(i) {
      // Headers siempre centrados (convención editorial), independientemente
      // de la alineación del body especificada en el markdown.
      var base = makeCellStyle(i, true).replace(/text-align:[^;]+;/, 'text-align:center;');
      return base + ' background-color:var(--md-th-bg); font-weight:500; letter-spacing:0.02em; border-bottom:1px solid var(--md-border);';
    }
    var tableStyle = 'border-collapse:collapse; margin:14px 0; font-size:inherit; font-family:var(--md-font); background-color:var(--md-table-bg); border:1px solid var(--md-border);';

    var thead = headerless ? '' :
      '<thead><tr>' + header.map(function(c, i){ return '<th style="'+makeHeadStyle(i)+'">'+renderInlineMath(c)+'</th>'; }).join('') + '</tr></thead>';

    var bodyRowsHtml = body.map(function(row, ri) {
      var cells = row.map(function(c, i) {
        if (mergedCol[i]) {
          if (ri === 0) {
            // Render una sola vez como rowspan; vertical-align:middle centra
            // el bloque de items verticalmente en la altura combinada.
            var inner = mergedCol[i].map(function(it){
              return '<div>' + renderInlineMath(it) + '</div>';
            }).join('<div style="height:22px"></div>');
            return '<td rowspan="' + nRows + '" style="' + makeCellStyle(i, false) + '">' + inner + '</td>';
          }
          return ''; // las demás filas no renderizan esta columna (cubierta por rowspan)
        }
        return '<td style="' + makeCellStyle(i, false) + '">' + renderInlineMath(c) + '</td>';
      }).join('');
      return '<tr>' + cells + '</tr>';
    }).join('');

    return '<table style="'+tableStyle+'">'+thead+'<tbody>'+bodyRowsHtml+'</tbody></table>';
  }

  function renderMath(text) {
    if (!text) return '';
    try {
      // Protect escaped \$ (literal dollar signs) from LaTeX parsing
      text = String(text).replace(/\\\$/g, '\x00DOLLAR\x00');
      // Extract Markdown tables before any other processing
      var tables = [];
      text = text.replace(/(?:^|\n)(\|[^\n]+\|[ \t]*\n\|[-:\s|]+\|[ \t]*\n(?:\|[^\n]+\|[ \t]*(?:\n|$))+)/g, function(match, block) {
        var html = renderMarkdownTable(block);
        var idx = tables.push(html) - 1;
        return '\n\x00TBL' + idx + '\x00\n';
      });
      var parts = text.split(/(\$\$[\s\S]+?\$\$|\$[^$\n]+?\$)/g);
      var out = parts.map(function(part) {
        var isDisplay = part.indexOf('$$') === 0 && part.lastIndexOf('$$') === part.length - 2 && part.length >= 4;
        var isInline = !isDisplay && part.length >= 2 && part.charAt(0) === '$' && part.charAt(part.length - 1) === '$' && part.indexOf('\n') === -1;
        if (isDisplay || isInline) {
          // Restaurar placeholder a "\$" antes de pasar a KaTeX (KaTeX entiende
          // \$ como signo de peso literal). Sin esto, el placeholder queda dentro
          // del math expression y KaTeX falla con error visible en rojo.
          var inner = (isDisplay ? part.slice(2, -2) : part.slice(1, -1)).replace(/\x00DOLLAR\x00/g, '\\$');
          if (katexLib) {
            try { return katexLib.renderToString(inner, { throwOnError: false, displayMode: isDisplay, macros: { "\\sen": "\\operatorname{sen}", "\\tg": "\\operatorname{tg}" } }); } catch(e) {}
          }
          return inner.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        }
        if (/<img\s/.test(part)) return part;
        return part
          .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
          .replace(/&lt;(\/?(u|b|i|strong|em))&gt;/g, '<$1>')
          // Fill-in-the-blank: 3+ underscores seguidos → línea continua justo
          // sobre la baseline. Color del mismo token que usa el texto.
          // Ancho: 0.85em por underscore.
          .replace(/_{3,}/g, function(m){
            var w = (m.length * 0.85).toFixed(2);
            return '<span class="md-blank" style="display:inline-block; width:' + w + 'em; height:1.5px; background-color:var(--md-text); vertical-align:0; margin:0 0.18em;"></span>';
          })
          .replace(/\*\*([^*\n]+?)\*\*/g, '<b>$1</b>')
          .replace(/(^|[^*])\*([^*\n]+?)\*(?!\*)/g, '$1<i>$2</i>')
          .replace(/\n/g, '<br>');
      }).join('');
      out = out.replace(/(?:<br>)?\x00TBL(\d+)\x00(?:<br>)?/g, function(m, i){ return tables[Number(i)]; });
      return out.replace(/\x00DOLLAR\x00/g, '$');
    } catch(e) {
      return String(text).replace(/\$\$/g, '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\x00DOLLAR\x00/g, '$');
    }
  }

  var api = { renderInlineMath: renderInlineMath, renderMarkdownTable: renderMarkdownTable, renderMath: renderMath };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  } else if (typeof window !== 'undefined') {
    window.MdRender = api;
  }
})(this);
