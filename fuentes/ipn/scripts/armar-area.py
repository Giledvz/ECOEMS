# Arma un examen IPN de un área a partir de los bloques transcritos.
#   python3 build_area.py cmb|csya
# Los bloques de Conocimientos generales (matemáticas, competencias, reading,
# historia) los comparten las tres áreas; solo cambian Biología, Química y Física.
import json, os, sys, collections

BQ = '/Users/giledvz/Documents/ECOEMS/fuentes/ipn/bloques'
RAIZ = '/Users/giledvz/Documents/ECOEMS'

AREAS = {
    'cmb': {
        'slug': 'ipn-cmb-1',
        'titulo': 'Simulacro IPN — Ciencias Médico Biológicas',
        # materia -> (cuántos, [(archivo, código)])
        'dist': [
            ('Matemáticas', 33, None),          # None = reparto entre los 7 bloques
            ('Competencia escrita', 20, [('competencia-escrita', 'CE')]),
            ('Competencia lectora', 20, None),
            ('Química', 17, [('quimica-cmb', 'QUI')]),
            ('Física', 13, [('fisica-cmb', 'FIS')]),
            ('Historia', 10, [('historia', 'HIS')]),
            ('Reading comprehension', 10, None),
            ('Biología', 17, [('biologia-cmb', 'BIO')]),
        ],
    },
    'csya': {
        'slug': 'ipn-csya-1',
        'titulo': 'Simulacro IPN — Ciencias Sociales y Administrativas',
        'dist': [
            ('Matemáticas', 37, None),
            ('Competencia escrita', 20, [('competencia-escrita', 'CE')]),
            ('Competencia lectora', 20, None),
            ('Química', 17, [('quimica-csya', 'QUI')]),
            ('Física', 17, [('fisica-csya', 'FIS')]),
            ('Historia', 10, [('historia', 'HIS')]),
            ('Reading comprehension', 10, None),
            ('Biología', 9, [('biologia-csya', 'BIO')]),
        ],
    },
}

MATE_BLOQUES = [
    ('pensamiento-matematico', 'PM'), ('algebra', 'ALG'),
    ('geometria-trigonometria', 'GT'), ('geometria-analitica', 'GA'),
    ('calculo-diferencial', 'CD'), ('calculo-integral', 'CI'),
    ('probabilidad-estadistica', 'PE'),
]

def load(name):
    with open(os.path.join(BQ, name + '.json'), encoding='utf-8') as f:
        return json.load(f)

def usable(q):
    """Reactivo aprovechable: texto propio, 4 opciones y sin figura pendiente."""
    if q.get('figura'):
        return False
    o = q.get('options') or {}
    return bool(q.get('text', '').strip()) and sorted(o) == ['A', 'B', 'C', 'D'] \
        and all(str(v).strip() for v in o.values()) and q.get('answer') in o

def ya_usados():
    """Reactivos que ya ocupa otro examen IPN, para no repetirlos si se puede."""
    usados = set()
    for f in os.listdir(RAIZ):
        if f.startswith('ipn-') and f.endswith('.json'):
            d = json.load(open(os.path.join(RAIZ, f), encoding='utf-8'))
            for sec in d.get('exam', {}).get('sections', []):
                for q in sec['questions']:
                    if q.get('_src'):
                        usados.add(q['_src'])
    return usados

def elegir(pool, n, usados):
    """Prefiere lo no usado antes; si no alcanza, completa con lo repetido."""
    frescos = [q for q in pool if q['_src'] not in usados]
    if len(frescos) >= n:
        return frescos[:n]
    return frescos + [q for q in pool if q['_src'] in usados][:n - len(frescos)]

def pool_de(bloques):
    out = []
    for fname, code in bloques:
        blk = load(fname)
        nom = blk['_meta']['bloque']
        for q in blk['questions']:
            if usable(q):
                out.append({**q, '_code': f"{code}.{q['n']}",
                            '_tn': q.get('subtema', nom),
                            '_src': f"{fname} · reactivo {q['n']}"})
    return out

def pool_matematicas(n, usados):
    """Reparte proporcionalmente entre los 7 sub-bloques de matemáticas."""
    pools = {}
    for fname, code in MATE_BLOQUES:
        pools[fname] = pool_de([(fname, code)])
    # cuántos de cada uno: reparto lo más parejo posible, respetando disponibilidad
    orden = [f for f, _ in MATE_BLOQUES]
    cuota = {f: n // len(orden) for f in orden}
    for i in range(n - sum(cuota.values())):
        cuota[orden[i % len(orden)]] += 1
    elegidos, faltan = [], 0
    for f in orden:
        got = elegir(pools[f], cuota[f], usados)
        elegidos += got
        faltan += cuota[f] - len(got)
    if faltan:  # rellena de donde quede material
        resto = [q for f in orden for q in pools[f] if q not in elegidos]
        elegidos += elegir(resto, faltan, usados | {q['_src'] for q in elegidos})
    return elegidos

def lecturas(fname, cuantos, tipo, usados):
    """Toma lecturas COMPLETAS, prefiriendo las que ningún otro examen usó.
    Si al final falta un resto para llegar al total, lo completa con las primeras
    preguntas de otra lectura (parcial): en un simulacro es aceptable usar solo
    parte de un texto, y evita repetir una lectura entera entre exámenes."""
    blk = load(fname)
    nom = blk['_meta']['bloque']

    def envolver(L, qs):
        titulo = L.get('titulo') or L.get('tema')
        return [{**q,
                 '_code': f"{tipo}.{L['id']}.{q['n']}",
                 '_tn': f"Lectura: {titulo}",
                 '_src': f"{fname} · lectura {L['id']} · reactivo {q['n']}",
                 '_ctx': L['texto']} for q in qs]

    disponibles = []
    for L in blk['lecturas']:
        qs = envolver(L, [q for q in L['questions'] if usable(q)])
        if qs:
            repetidas = sum(1 for q in qs if q['_src'] in usados)
            disponibles.append((repetidas, L, qs))
    # primero las intactas, y entre ellas las más grandes (para llegar al total
    # con lecturas enteras y dejar el resto chico)
    disponibles.sort(key=lambda t: (t[0], -len(t[2])))

    out, restantes = [], list(disponibles)
    for rep, L, qs in disponibles:
        if len(out) + len(qs) <= cuantos:
            out += qs
            restantes = [t for t in restantes if t[1]['id'] != L['id']]
        if len(out) == cuantos:
            return out
    # completar el resto con un trozo de la siguiente lectura disponible
    for rep, L, qs in restantes:
        falta = cuantos - len(out)
        if falta <= 0:
            break
        out += qs[:falta]
    return out

def construir(area):
    cfg = AREAS[area]
    usados = ya_usados()
    qid = 0
    secciones = []
    for materia, n, bloques in cfg['dist']:
        if materia == 'Matemáticas':
            elegidos = pool_matematicas(n, usados)
        elif materia == 'Competencia lectora':
            elegidos = lecturas('competencia-lectora', n, 'CL', usados)
        elif materia == 'Reading comprehension':
            elegidos = lecturas('reading-comprehension', n, 'RC', usados)
        else:
            elegidos = elegir(pool_de(bloques), n, usados)
        if len(elegidos) != n:
            print(f'  ! {materia}: alcanzaron {len(elegidos)} de {n} — falta transcribir más')
        qs = []
        for q in elegidos:
            qid += 1
            nq = {'id': qid, 'topic': q['_code'], 'topic_name': q['_tn'], 'text': q['text']}
            if q.get('_ctx'):
                nq['context'] = q['_ctx']
            nq['options'] = q['options']
            nq['answer'] = q['answer']
            nq['_src'] = q['_src']
            qs.append(nq)
        secciones.append((materia, qs))

    total = sum(len(q) for _, q in secciones)
    exam = {'exam': {
        'title': cfg['titulo'],
        'group': 'IPN',
        'date': '2026-07-30',
        'version': '1.0',
        'total_questions': total,
        'students': ['Gil'],
        'instructions': ('Examen de 140 reactivos de opción múltiple con la distribución oficial '
                         'del IPN para esta área. Selecciona la opción correcta para cada pregunta. '
                         'No se permite el uso de calculadora.'),
        'source': ('Reactivos tomados del Material de Apoyo al Aprendizaje 2026, Instituto '
                   'Politécnico Nacional. Respuestas verificadas contra las tablas de Respuestas '
                   'Correctas (RC) de la propia guía.'),
        'sections': [{'subject': m, 'questions_count': len(qs), 'questions': qs}
                     for m, qs in secciones],
    }}
    out = os.path.join(RAIZ, cfg['slug'] + '.json')
    json.dump(exam, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f"{out}  —  {total} reactivos")
    for m, qs in secciones:
        print(f'  {len(qs):3d}  {m}')
    dist = collections.Counter(q['answer'] for _, qs in secciones for q in qs)
    print('  respuestas:', dict(sorted(dist.items())))
    rep = sum(1 for _, qs in secciones for q in qs if q['_src'] in usados)
    print(f'  reactivos repetidos con otro examen IPN: {rep}')
    return total

if __name__ == '__main__':
    construir(sys.argv[1])
