# Saca las lecturas compartidas del enunciado y las pone en "context".
#
#   python3 fuentes/scripts/extraer-lecturas.py --dry     # reporta, no escribe
#   python3 fuentes/scripts/extraer-lecturas.py           # aplica
#
# En varios exámenes la lectura viene incrustada dentro de "text" y REPETIDA en cada
# reactivo del bloque. El alumno la ve con la misma tipografía que el enunciado, sin
# el recuadro que la separa, y tiene que bajar hasta el final para dar con la
# pregunta. La convención (ya usada en los exámenes *-1) es dejar la lectura en
# "context" —el cliente la pinta en su recuadro y la muestra una sola vez por
# bloque— y en "text" solo la pregunta.
import json, os, re, sys, glob, collections

RAIZ = '/Users/giledvz/Documents/ECOEMS'

# Renglones de instrucción que pierden sentido dentro del recuadro de lectura:
# el recuadro ya dice visualmente "esto es la lectura", y el rango de preguntas
# ("de la 77 a la 81") no le sirve al alumno, que navega por su propio índice.
INSTRUCCION = re.compile(
    r'^\s*(lee|leer|lea)\b.{0,120}?(texto|lectura|fragmento|poema|siguiente)\b.{0,80}$'
    r'|^\s*con base en (el|la) (siguiente )?(texto|lectura)\b.{0,80}$',
    re.I | re.S)

def parrafos(t):
    """Parte por renglones en blanco, conservando el orden."""
    return [p.strip() for p in re.split(r'\n\s*\n', t) if p.strip()]

def procesar(path, dry):
    d = json.load(open(path, encoding='utf-8'))
    qs = [q for s in d['exam']['sections'] for q in s['questions']]

    # cuántas veces aparece cada párrafo entre los reactivos SIN context
    cuenta = collections.Counter()
    for q in qs:
        if q.get('context'):
            continue
        for p in parrafos(q.get('text') or ''):
            cuenta[p] += 1

    cambios, avisos = [], []
    for q in qs:
        if q.get('context'):
            continue
        ps = parrafos(q.get('text') or '')
        compartidos = [i for i, p in enumerate(ps) if cuenta[p] > 1]
        # el bloque tiene que estar anclado por un párrafo largo repetido; si no,
        # lo repetido puede ser una coincidencia (un pie, una instrucción suelta)
        if not any(len(ps[i]) > 180 for i in compartidos):
            continue

        corte = max(compartidos)
        lectura, pregunta = ps[:corte + 1], ps[corte + 1:]
        if not pregunta:
            avisos.append(f'  {os.path.basename(path)} id {q["id"]}: la pregunta no '
                          f'queda después de la lectura; se deja como está')
            continue

        while lectura and INSTRUCCION.match(lectura[0]):
            lectura.pop(0)
        if not lectura:
            continue

        nuevo_ctx, nuevo_txt = '\n\n'.join(lectura), '\n\n'.join(pregunta)
        # nada se pierde: todo párrafo original sigue en la lectura o en la pregunta
        faltan = [p for p in ps if p not in lectura and p not in pregunta
                  and not INSTRUCCION.match(p)]
        if faltan:
            avisos.append(f'  {os.path.basename(path)} id {q["id"]}: se perdería '
                          f'contenido; se deja como está')
            continue

        cambios.append((q, nuevo_ctx, nuevo_txt))

    if not dry:
        for q, ctx, txt in cambios:
            q['context'], q['text'] = ctx, txt
        if cambios:
            json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    return cambios, avisos

def main(dry):
    tot = 0
    todos_avisos = []
    lecturas = collections.Counter()
    for path in sorted(glob.glob(os.path.join(RAIZ, 'unam-*.json')) +
                       glob.glob(os.path.join(RAIZ, 'diag-uni-*.json')) +
                       glob.glob(os.path.join(RAIZ, 'diagnostico-a1.json'))):
        cambios, avisos = procesar(path, dry)
        todos_avisos += avisos
        if cambios:
            grupos = len({c[1] for c in cambios})
            ahorro = sum(len(c[0].get('text', '')) for c in cambios)
            print(f'  {os.path.basename(path)[:-5]:16s} {len(cambios):3d} reactivos '
                  f'· {grupos:2d} lecturas')
            tot += len(cambios)
            for c in cambios:
                lecturas[c[1][:60]] += 1
    print(f'\n{tot} reactivos convertidos · {len(lecturas)} lecturas distintas')
    if todos_avisos:
        print(f'\nCASOS QUE NO SE TOCAN ({len(todos_avisos)}):')
        for a in todos_avisos[:15]:
            print(a)
    if dry:
        print('\n(prueba: no se escribió nada)')

if __name__ == '__main__':
    main('--dry' in sys.argv)
