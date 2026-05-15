#!/usr/bin/env python3
"""Generate examen_ecoems_2015_versionA_con_respuestas.html from V.A JSON."""
import json
import re
import html as html_lib

VA_PATH = '/Users/giledvz/Documents/ECOEMS/examen_ecoems_2015_versionA.json'
OUT_PATH = '/Users/giledvz/Documents/ECOEMS/public/examen_ecoems_2015_versionA_con_respuestas.html'


def md_table_to_html(text):
    """Convert simple markdown tables in text to HTML <table>."""
    lines = text.split('\n')
    out = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Detect a markdown table: header row, separator row, then data rows
        if '|' in line and i + 1 < len(lines) and re.match(r'^\s*\|?(\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$', lines[i + 1]):
            header = [c.strip() for c in line.strip('|').split('|')]
            rows = []
            j = i + 2
            while j < len(lines) and '|' in lines[j]:
                rows.append([c.strip() for c in lines[j].strip().strip('|').split('|')])
                j += 1
            tbl = '<table class="qtable"><thead><tr>'
            tbl += ''.join(f'<th>{h}</th>' for h in header)
            tbl += '</tr></thead><tbody>'
            for r in rows:
                tbl += '<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>'
            tbl += '</tbody></table>'
            out.append(tbl)
            i = j
        else:
            out.append(lines[i])
            i += 1
    return '\n'.join(out)


def render_inline(text):
    """Apply minimal markdown: **bold**, line breaks, tables."""
    if not text:
        return ''
    text = md_table_to_html(text)
    # Bold **x** y *x* (ambos renderizados como negrita)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<strong>\1</strong>', text)
    # Replace remaining newlines (outside tables) with <br>
    parts = re.split(r'(<table.*?</table>)', text, flags=re.DOTALL)
    new_parts = []
    for p in parts:
        if p.startswith('<table'):
            new_parts.append(p)
        else:
            new_parts.append(p.replace('\n', '<br>'))
    return ''.join(new_parts)


def is_placeholder(q):
    return (
        q.get('_to_replace') or
        'PENDIENTE' in str(q.get('topic_name', '')) or
        'PLACEHOLDER' in str(q.get('text', ''))
    )


def render_option_value(val):
    """Render an option value — could be plain text or HTML (e.g. <img>)."""
    if val is None:
        return ''
    s = str(val)
    # Fix absolute web paths in any embedded <img src="/..."> so <base> resolves them
    s = re.sub(r'src="/(imagenes_)', r'src="\1', s)
    return render_inline(s)


def render_question(q):
    qid = q.get('id', '?')
    topic = q.get('topic', '')
    name = q.get('topic_name', '')
    text = q.get('text', '')
    img = q.get('image')
    options = q.get('options', {})
    answer = q.get('answer', '')
    explanation = q.get('explanation', '')
    ph = is_placeholder(q)

    klass = "question placeholder" if ph else "question"
    header = f"Pregunta {qid}"
    if topic:
        header += f" · {topic}"
    if name:
        header += f" — {name}"
    if ph:
        reason = q.get('_replace_reason', '')
        header += f" ⚠️ PENDIENTE" + (f" ({reason})" if reason else "")

    parts = [f'<div class="{klass}">']
    parts.append(f'<div class="qheader">{html_lib.escape(header)}</div>')
    context = q.get('context')
    if context:
        parts.append(f'<div class="qcontext">{render_inline(context)}</div>')
    parts.append(f'<div class="qtext">{render_inline(text)}</div>')
    if img:
        # Strip leading / so <base> tag resolves it within /public/
        img_src = img.lstrip('/')
        parts.append(f'<img class="qimage" src="{html_lib.escape(img_src)}" alt=""/>')
    parts.append('<div class="options">')
    for letter in ('A', 'B', 'C', 'D'):
        if letter not in options:
            continue
        correct = (letter == answer)
        opt_class = 'option correct' if correct else 'option'
        parts.append(
            f'<div class="{opt_class}"><b>{letter})</b> {render_option_value(options[letter])}</div>'
        )
    parts.append('</div>')
    if explanation:
        parts.append(f'<div class="qexplanation"><b>Explicación:</b> {render_inline(explanation)}</div>')
    parts.append('</div>')
    return '\n'.join(parts)


def main():
    with open(VA_PATH) as f:
        data = json.load(f)

    # Walk all questions, preserving order and grouping by subject
    sections = []  # list of (subject_name, [questions])

    def walk(node):
        if isinstance(node, dict):
            if 'subject' in node and isinstance(node.get('questions'), list):
                sections.append((node['subject'], node['questions']))
                return
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)

    total = sum(len(qs) for _, qs in sections)
    placeholders = sum(1 for _, qs in sections for q in qs if is_placeholder(q))

    html = f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>Examen ECOEMS 2015 — Versión A (con respuestas)</title>
<base href="file:///Users/giledvz/Documents/ECOEMS/public/">

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<style>
  body {{ font-family: 'Latin Modern Roman', Georgia, 'Times New Roman', serif; max-width: 850px; margin: 20px auto; padding: 0 20px; line-height: 1.4; }}
  h1 {{ text-align: center; margin-bottom: 4px; }}
  .summary {{ text-align: center; color: #666; margin-bottom: 20px; }}
  h2.subject {{ background: #2c3e50; color: white; padding: 8px 12px; margin: 32px 0 12px 0; border-radius: 4px; page-break-before: auto; }}
  .question {{ margin-bottom: 20px; padding: 12px; border: 1px solid #ddd; page-break-inside: avoid; border-radius: 4px; }}
  .question.placeholder {{ border-color: #d97706; background: #fef3c7; }}
  .qheader {{ color: #666; font-size: 13px; margin-bottom: 6px; font-style: italic; }}
  .question.placeholder .qheader {{ color: #92400e; font-weight: bold; }}
  .qtext {{ margin-bottom: 8px; }}
  .qimage {{ max-width: 400px; max-height: 280px; display: block; margin: 8px 0; }}
  .options {{ margin-left: 16px; }}
  .option {{ padding: 4px 8px; margin: 2px 0; border-radius: 4px; }}
  .option.correct {{ background: #c8f0c8; font-weight: bold; }}
  .option.correct::before {{ content: "✓ "; }}
  .option img {{ max-width: 200px; max-height: 200px; vertical-align: middle; }}
  .qexplanation {{ margin-top: 8px; padding: 6px 10px; background: #f5f5f5; font-size: 13px; border-left: 3px solid #999; }}
  .qcontext {{ background: #f8f4e8; border-left: 4px solid #b08d57; padding: 10px 14px; margin: 8px 0 12px 0; font-size: 14px; text-align: justify; }}
  .qcontext strong {{ color: #6b4423; }}
  .qtable {{ border-collapse: collapse; margin: 8px 0; }}
  .qtable th, .qtable td {{ border: 1px solid #ccc; padding: 4px 8px; text-align: center; }}
  .qtable th {{ background: #eee; }}
  @media print {{
    body {{ margin: 0; max-width: none; }}
    .question {{ page-break-inside: avoid; }}
    h2.subject {{ page-break-after: avoid; }}
  }}
</style>
</head><body>
<h1>Examen ECOEMS 2015 — Versión A</h1>
<p class="summary">{total} preguntas con respuestas marcadas (✓) — <b>{placeholders} pendientes</b> resaltadas en amarillo</p>
"""

    for subj, qs in sections:
        html += f'\n<h2 class="subject">{html_lib.escape(subj)} ({len(qs)} preguntas)</h2>\n'
        for q in qs:
            html += render_question(q) + '\n'

    html += """
<script>
document.addEventListener('DOMContentLoaded', () => {
  renderMathInElement(document.body, {
    delimiters: [
      {left: '$$', right: '$$', display: true},
      {left: '$',  right: '$',  display: false}
    ],
    throwOnError: false
  });
});
</script>
</body></html>
"""

    with open(OUT_PATH, 'w') as f:
        f.write(html)
    print(f"✓ HTML escrito: {OUT_PATH}")
    print(f"  Total: {total} preguntas | Pendientes: {placeholders}")


if __name__ == '__main__':
    main()
