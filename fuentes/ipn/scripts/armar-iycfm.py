# Arma ipn-iycfm-1.json a partir de los bloques transcritos de la guía oficial.
import json, os, collections

BQ = '/Users/giledvz/Documents/ECOEMS/fuentes/ipn/bloques'
OUT = '/Users/giledvz/Documents/ECOEMS/ipn-iycfm-1.json'
IMG = '/imagenes_ipn-iycfm-1'

def load(name):
    return json.load(open(os.path.join(BQ, name + '.json'), encoding='utf-8'))

def index(blk):
    return {q['n']: q for q in blk['questions']}

# ------------------------------------------------------------------ selección
# (archivo, código, [números de reactivo]) — todos sin figura pendiente.
MATE = [
    ('pensamiento-matematico', 'PM',  [1, 5, 11, 29, 34, 37]),
    ('algebra',                'ALG', [4, 5, 12, 24, 33, 40]),
    ('geometria-trigonometria','GT',  [1, 12, 17, 19, 23, 39]),
    ('geometria-analitica',    'GA',  [2, 7, 9, 13, 26, 34]),
    ('calculo-diferencial',    'CD',  [1, 11, 20, 22, 38]),
    ('calculo-integral',       'CI',  [1, 6, 13, 36]),
    ('probabilidad-estadistica','PE', [26, 37, 39, 40]),
]
ESCRITA = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 14, 15, 16, 17, 20, 22, 23, 25, 26, 29]
QUIMICA = [1, 2, 3, 6, 7, 9, 10, 12, 14, 15, 16, 17, 19, 23, 24, 28, 29]
FISICA  = [1, 2, 5, 6, 7, 8, 9, 10, 11, 13, 14, 16, 17, 19, 20, 21, 23]
HISTORIA = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
BIOLOGIA = [1, 3, 6, 9, 13, 14, 18, 20, 21]

# ------------------------------------------------------------------ lectura 1 con figuras
# Va en HTML crudo a propósito: markdown-render devuelve el bloque tal cual
# cuando contiene <img>, así que aquí mandan <b>/<br>/<img> y no el markdown.
def fig(f, w):
    return (f'<img src="{IMG}/{f}" width="{w}" '
            f'style="display:block;margin:14px auto;max-width:100%">')

LECTURA1 = (
    '<b>LA PROPORCIÓN ÁUREA Y LA NATURALEZA</b><br><br>'
    '<b>[1]</b> En el corazón de la naturaleza se encuentra una elegante y misteriosa huella '
    'matemática llamada proporción áurea. Debido a la belleza y particularidad de esta proporción, '
    'ha llamado la atención de matemáticos, artistas, filósofos y científicos a lo largo de la '
    'historia. Pero para poder apreciar plenamente la proporción áurea es necesario comenzar con '
    'la explicación del número áureo.<br><br>'
    '<b>[2]</b> El número dorado, el número divino, phi (φ) o el número áureo es uno de los más '
    'importantes y emblemáticos de las matemáticas. Es un número con una representación decimal '
    'infinita y sin periodo, es decir, es un número algebraico irracional cuyo valor numérico '
    'corresponde a φ = (1+√5)/2 ≈ 1.618 033 988 749 894… Hay registros de este número desde la '
    'Antigüedad; pero no como la expresión algebraica antes expuesta, sino como una construcción '
    'geométrica llamada razón áurea, la cual es la relación entre dos segmentos.<br><br>'
    '<b>[3]</b>' + fig('lectura1_construccion.svg', 280) +
    'Los segmentos AB y BC son perpendiculares e iguales a uno. Con centro en O trazamos la '
    'circunferencia de radio 1/2. Finalmente, uniendo A con O y prolongando obtenemos P. La '
    'relación entre AP y AB da como resultado el número áureo.<br><br>'
    '<b>[4]</b> Al aplicar la proporcionalidad áurea a distintos objetos geométricos, obtenemos '
    'objetos con equilibrio y belleza en su forma, como el rectángulo dorado, cuyos lados guardan '
    'una proporción igual al número áureo, o sea, la relación entre la longitud de su base y su '
    'altura es igual a 1.618…, por lo tanto, si se traza un cuadrado inscrito al rectángulo dorado, '
    'el rectángulo resultante es semejante al original.<br><br>'
    '<b>[5]</b>' + fig('lectura1_rectangulo.svg', 300) +
    '<b>[6]</b> Ahora, es posible seguir trazando un cuadrado en cada rectángulo resultante '
    'siguiendo la proporción áurea y si se trazan arcos de circunferencia a partir de las esquinas '
    'de cada cuadrado, cuando estos se unan, formarán una espiral llamada espiral dorada o espiral '
    'áurea, la cual es una forma excepcional.<br><br>'
    '<b>[7]</b>' + fig('lectura1_espiral.svg', 320) +
    '<b>[8]</b> Pero quizá lo más extraordinario de la espiral áurea no radique en su aspecto '
    'matemático, sino en la forma en la que se encuentra de manera constante en la naturaleza: el '
    'interior de la concha de cualquier caracol, las galaxias espirales, las olas del mar, la '
    'disposición de las hojas de las alcachofas o la distribución de las semillas de los girasoles. '
    'Incluso, los seres humanos estamos regidos por la proporción áurea, ya que se observa en la '
    'distancia entre el ombligo y la planta de los pies de una persona con respecto a su altura '
    'total, por lo que algunos le han atribuido propiedades místicas a esta proporción, mismas que '
    'no han podido confirmarse; pero lo que sí es posible confirmar es que este número guarda en su '
    'interior gran belleza, armonía y elegancia.<br><br>'
    '<i>Texto adaptado de Freire, N. (2023). La proporción áurea: explicación de los patrones en la '
    'naturaleza. National Geographic.</i>'
)

# ------------------------------------------------------------------ armado
qid = 0
def mk(text, options, answer, topic, topic_name, src, context=None, image=None):
    global qid
    qid += 1
    q = {'id': qid, 'topic': topic, 'topic_name': topic_name, 'text': text}
    if context: q['context'] = context
    if image:   q['image'] = image
    q['options'] = options
    q['answer'] = answer
    q['_src'] = src
    return q

sections = []

# --- Matemáticas (37)
qs = []
for fname, code, nums in MATE:
    blk = load(fname); idx = index(blk)
    for n in nums:
        s = idx[n]
        assert 'text' in s and 'options' in s, (fname, n)
        qs.append(mk(s['text'], s['options'], s['answer'],
                     f'{code}.{n}', s.get('subtema', blk['_meta']['bloque']),
                     f"{fname} · reactivo {n}"))
sections.append(('Matemáticas', qs))

# --- Competencia escrita (20)
blk = load('competencia-escrita'); idx = index(blk); qs = []
for n in ESCRITA:
    s = idx[n]
    qs.append(mk(s['text'], s['options'], s['answer'], f'CE.{n}',
                 s.get('subtema', 'Competencia escrita'),
                 f"competencia-escrita · reactivo {n}"))
sections.append(('Competencia escrita', qs))

# --- Competencia lectora (20): dos lecturas completas
blk = load('competencia-lectora'); qs = []
lec = {l['id']: l for l in blk['lecturas']}
for lid, ctx in ((1, LECTURA1), (2, None)):
    L = lec[lid]
    texto = ctx if ctx else L['texto']
    for s in L['questions']:
        qs.append(mk(s['text'], s['options'], s['answer'], f'CL.{lid}.{s["n"]}',
                     f"Lectura: {L['titulo'].title()}",
                     f"competencia-lectora · lectura {lid} · reactivo {s['n']}",
                     context=texto))
sections.append(('Competencia lectora', qs))

# --- Química (17)
blk = load('quimica-iycfm'); idx = index(blk); qs = []
for n in QUIMICA:
    s = idx[n]
    qs.append(mk(s['text'], s['options'], s['answer'], f'QUI.{n}', 'Química',
                 f"quimica-iycfm · reactivo {n}"))
sections.append(('Química', qs))

# --- Física (17)
blk = load('fisica-iycfm'); idx = index(blk); qs = []
for n in FISICA:
    s = idx[n]
    qs.append(mk(s['text'], s['options'], s['answer'], f'FIS.{n}', 'Física',
                 f"fisica-iycfm · reactivo {n}"))
sections.append(('Física', qs))

# --- Historia (10)
blk = load('historia'); idx = index(blk); qs = []
for n in HISTORIA:
    s = idx[n]
    qs.append(mk(s['text'], s['options'], s['answer'], f'HIS.{n}', 'Historia',
                 f"historia · reactivo {n}"))
sections.append(('Historia', qs))

# --- Reading comprehension (10): Family life + Fake News
blk = load('reading-comprehension'); qs = []
for L in blk['lecturas']:
    if L['id'] not in (1, 6): continue
    for s in L['questions']:
        qs.append(mk(s['text'], s['options'], s['answer'], f'RC.{L["id"]}.{s["n"]}',
                     f"Reading: {L['tema']}",
                     f"reading-comprehension · lectura {L['id']} · reactivo {s['n']}",
                     context=L['texto']))
sections.append(('Reading comprehension', qs))

# --- Biología (9)
blk = load('biologia-iycfm'); idx = index(blk); qs = []
for n in BIOLOGIA:
    s = idx[n]
    qs.append(mk(s['text'], s['options'], s['answer'], f'BIO.{n}', 'Biología',
                 f"biologia-iycfm · reactivo {n}"))
sections.append(('Biología', qs))

total = sum(len(q) for _, q in sections)
exam = {'exam': {
    'title': 'Simulacro IPN — Ingeniería y Ciencias Físico Matemáticas',
    'group': 'IPN',
    'date': '2026-07-29',
    'version': '1.0',
    'total_questions': total,
    'students': ['Danna Belem'],
    'instructions': ('Examen de 140 reactivos de opción múltiple con la distribución oficial del '
                     'IPN para el área de Ingeniería y Ciencias Físico Matemáticas. Selecciona la '
                     'opción correcta para cada pregunta. No se permite el uso de calculadora.'),
    'source': ('Reactivos tomados del Material de Apoyo al Aprendizaje 2026, Instituto Politécnico '
               'Nacional. Respuestas verificadas contra las tablas de Respuestas Correctas (RC) de '
               'la propia guía.'),
    'sections': [{'subject': name, 'questions_count': len(qs), 'questions': qs}
                 for name, qs in sections],
}}

json.dump(exam, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

print(f'{OUT}  —  {total} reactivos')
for name, qs in sections:
    print(f'  {len(qs):3d}  {name}')
dist = collections.Counter(q['answer'] for _, qs in sections for q in qs)
print('  respuestas:', dict(sorted(dist.items())))
