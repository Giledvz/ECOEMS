# Qué temas se les están atorando a los alumnos.
#
#   python3 fuentes/scripts/temas-flojos.py                    # todo
#   python3 fuentes/scripts/temas-flojos.py Universidad        # solo un grupo
#   python3 fuentes/scripts/temas-flojos.py Universidad Dana   # y un alumno
#
# Cruza cada resultados_CODIGO_*.csv con su clave_respuestas_CODIGO_*.csv, que trae
# el tema de cada reactivo, y agrega los fallos por tema en vez de por pregunta.
#
# Un tema suele traer UN reactivo por examen, así que con un solo examen el dato no
# dice nada: lo que sirve es acumular todos los que ha presentado el grupo. Por eso
# se reporta "cuántos alumnos-intento" hubo detrás de cada porcentaje, y los temas
# con un solo intento se separan al final: son sospechas, no diagnósticos.
import csv, glob, re, sys, collections, os, json

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MIN_INTENTOS = 3          # por debajo de esto, un tema no es un diagnóstico

def temas_dudosos():
    """Temas de reactivos que el modelo marcó REVISAR al escribir la explicación.

    Importa aquí: si un tema sale con 0 aciertos pero su clave está en duda, el
    problema puede ser del reactivo y no del alumno. Dar clase sobre eso sería
    corregir algo que quizá contestaron bien."""
    rv = os.path.join(RAIZ, 'fuentes/explicaciones/revisar.md')
    if not os.path.exists(rv):
        return {}
    marcados = set()
    for l in open(rv, encoding='utf-8'):
        m = re.match(r'- \*\*([\w.-]+)\.json · id (\d+)\*\*', l)
        if m:
            marcados.add((m.group(1), int(m.group(2))))
    # Se indexa por el nombre del tema, que es lo que trae la clave en CSV
    # (Tema_nombre), para poder cruzarlo con lo que reporta este script.
    dudosos = {}
    for f in glob.glob(os.path.join(RAIZ, '*.json')):
        nombre = os.path.basename(f)[:-5]
        try:
            d = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        if 'exam' not in d:
            continue
        for sec in d['exam']['sections']:
            for q in sec['questions']:
                if (nombre, q['id']) in marcados and q.get('topic_name'):
                    dudosos.setdefault(q['topic_name'], []).append(f'{nombre} id {q["id"]}')
    return dudosos

def pares():
    """Salas que tienen a la vez resultados y clave."""
    pat = re.compile(r'_([A-Z0-9]{6})_')
    res, cla = {}, {}
    for f in glob.glob(os.path.join(RAIZ, 'resultados_*.csv')):
        m = pat.search(os.path.basename(f))
        if m: res[m.group(1)] = f
    for f in glob.glob(os.path.join(RAIZ, 'clave_respuestas_*.csv')):
        m = pat.search(os.path.basename(f))
        if m: cla[m.group(1)] = f
    return {c: (res[c], cla[c]) for c in sorted(res.keys() & cla.keys())}

def recolecta(grupo=None, alumno=None):
    tema = collections.defaultdict(lambda: [0, 0])      # (asignatura, tema) -> [ok, total]
    asig = collections.defaultdict(lambda: [0, 0])
    porAlumno = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    salas, alumnos = 0, set()

    for code, (fr, fk) in pares().items():
        clave = {r['Pregunta'].strip(): (r['Asignatura'], r['Tema_nombre'], r['Respuesta_correcta'].strip())
                 for r in csv.DictReader(open(fk, encoding='utf-8-sig'))}
        filas = list(csv.DictReader(open(fr, encoding='utf-8-sig')))
        usadas = False
        for f in filas:
            if grupo and f.get('Grupo') != grupo: continue
            if alumno and f.get('Alumno') != alumno: continue
            usadas = True
            alumnos.add(f['Alumno'])
            for p, (a, t, corr) in clave.items():
                bien = (f.get(p) or '').strip() == corr
                for d in (tema[(a, t)], asig[a], porAlumno[f['Alumno']][(a, t)]):
                    d[0] += bien; d[1] += 1
        salas += usadas
    return tema, asig, porAlumno, salas, sorted(alumnos)

def barra(p, ancho=18):
    n = round(p * ancho / 100)
    return '█' * n + '·' * (ancho - n)

def main():
    grupo = sys.argv[1] if len(sys.argv) > 1 else None
    alumno = sys.argv[2] if len(sys.argv) > 2 else None
    tema, asig, porAlumno, salas, alumnos = recolecta(grupo, alumno)
    if not tema:
        print('  no hay datos para ese filtro'); return
    dudosos = temas_dudosos()

    print(f"\n  {salas} exámenes · {len(alumnos)} alumno(s): {', '.join(alumnos)}")

    print('\n  POR MATERIA')
    for a, (ok, tot) in sorted(asig.items(), key=lambda kv: kv[1][0] / kv[1][1]):
        p = ok * 100 / tot
        print(f'    {barra(p)} {p:3.0f}%  {a:22s} {ok:3d}/{tot:3d}')

    solidos = {k: v for k, v in tema.items() if v[1] >= MIN_INTENTOS}
    print(f'\n  TEMAS MÁS FLOJOS  (con al menos {MIN_INTENTOS} intentos)')
    orden = sorted(solidos.items(), key=lambda kv: (kv[1][0] / kv[1][1], -kv[1][1]))
    for (a, t), (ok, tot) in orden[:22]:
        if ok / tot >= 0.7: break
        p = ok * 100 / tot
        aviso = '  ⚠' if t in dudosos else ''
        print(f'    {barra(p)} {p:3.0f}%  {t[:38]:38s} {a[:16]:16s} {ok}/{tot}{aviso}')

    # los que fallaron TODOS: son los que más rinde dar en clase
    todos = [(a, t, tot) for (a, t), (ok, tot) in solidos.items() if ok == 0]
    if todos:
        print(f'\n  NADIE ACERTÓ  ({len(todos)} temas)')
        for a, t, tot in sorted(todos, key=lambda x: -x[2]):
            aviso = '  ⚠' if t in dudosos else ''
            print(f'    · {t[:44]:44s} {a[:18]:18s} 0/{tot}{aviso}')

    if not alumno and len(alumnos) > 1:
        print('\n  LO MÁS FLOJO DE CADA QUIEN')
        for al in alumnos:
            d = porAlumno[al]
            malos = [t for (a, t), (ok, tot) in sorted(d.items(), key=lambda kv: kv[1][0] / kv[1][1])
                     if ok == 0][:4]
            print(f'    {al:10s} {", ".join(malos) if malos else "sin temas en cero"}')

    # aviso: no todo fallo es del alumno
    conDuda = sorted({t for (a, t), (ok, tot) in solidos.items()
                      if ok / tot < 0.5 and t in dudosos})
    if conDuda:
        print('\n  ⚠ ANTES DE DAR CLASE SOBRE ESTOS')
        print('    El modelo no coincidió con la clave oficial al explicarlos, así que')
        print('    puede que el reactivo esté mal y los alumnos tuvieran razón.')
        print('    El detalle está en fuentes/explicaciones/revisar.md.')
        for t in conDuda:
            print(f'      · {t[:44]:44s} ({", ".join(dudosos[t])})')

    sueltos = sum(1 for v in tema.values() if v[1] < MIN_INTENTOS and v[0] == 0)
    if sueltos:
        print(f'\n  ({sueltos} temas más fallaron, pero con menos de {MIN_INTENTOS} intentos:')
        print('   no alcanzan para diagnosticar, hacen falta más exámenes.)')

if __name__ == '__main__':
    main()
