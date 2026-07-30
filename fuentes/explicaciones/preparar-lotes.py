# Parte en lotes las preguntas que no tienen explicación, para repartirlas entre
# agentes. Cada lote es un JSON pequeño y autocontenido: el agente lo lee, escribe
# su archivo de salida y nunca toca los exámenes.
#
#   python3 fuentes/explicaciones/preparar-lotes.py ipn      # solo los IPN
#   python3 fuentes/explicaciones/preparar-lotes.py todos
import json, os, re, sys, glob

RAIZ = '/Users/giledvz/Documents/ECOEMS'
LOTES = os.path.join(RAIZ, 'fuentes/explicaciones/lotes')
# Preguntas por lote. Con la autovalidación del agente quitada, cada agente da ~3
# turnos, así que el costo ya casi no depende del tamaño del contexto y sí del número
# de agentes: conviene el lote grande para pagar una sola vez las instrucciones.
TAM = 40

GRUPOS = {
    'ipn':          lambda f: f.startswith('ipn-'),
    'unam':         lambda f: f.startswith('unam-'),
    'ecoems':       lambda f: f.startswith('ecoems-'),
    'diagnosticos': lambda f: f.startswith('diag'),
    'todos':        lambda f: True,
}

def slug(s):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return s or 'x'

def main(grupo):
    cond = GRUPOS[grupo]
    os.makedirs(LOTES, exist_ok=True)
    total = 0
    lotes = []
    for path in sorted(glob.glob(os.path.join(RAIZ, '*.json'))):
        f = os.path.basename(path)
        if not cond(f):
            continue
        try:
            d = json.load(open(path, encoding='utf-8'))
        except Exception:
            continue
        e = d.get('exam')
        if not e:
            continue
        for sec in e['sections']:
            faltan = [q for q in sec['questions']
                      if not (q.get('explanation') or '').strip()]
            if not faltan:
                continue
            for i in range(0, len(faltan), TAM):
                trozo = faltan[i:i + TAM]
                nombre = f"{f[:-5]}__{slug(sec['subject'])}__{i//TAM + 1:02d}"

                # Las lecturas compartidas se guardan UNA vez y cada pregunta las
                # referencia. Repetir el texto en cada pregunta inflaba el lote (en
                # los IPN, 84% del texto de lecturas era la misma repetida) y ese
                # peso se vuelve a leer en cada turno del agente.
                lecturas, orden = {}, []
                for q in trozo:
                    c = q.get('context')
                    if c and c not in lecturas:
                        lecturas[c] = f'L{len(lecturas) + 1}'
                        orden.append(c)

                def limpia(q):
                    d = {'id': q['id'], 'texto': q['text'],
                         'opciones': q['options'], 'clave': q['answer']}
                    if q.get('topic_name'):    d['tema'] = q['topic_name']
                    if q.get('context'):       d['lectura'] = lecturas[q['context']]
                    if q.get('image'):         d['figura'] = q['image']
                    if q.get('option_images'): d['figuras_opciones'] = q['option_images']
                    return d

                lote = {
                    'lote': nombre,
                    'examen': f,
                    'titulo': e['title'],
                    'materia': sec['subject'],
                    'lecturas': {lecturas[c]: c for c in orden},
                    'preguntas': [limpia(q) for q in trozo],
                }
                if not lecturas:
                    del lote['lecturas']
                json.dump(lote, open(os.path.join(LOTES, nombre + '.json'), 'w',
                                     encoding='utf-8'), ensure_ascii=False, indent=1)
                lotes.append((nombre, len(trozo), sum(1 for q in trozo
                              if q.get('image') or q.get('option_images'))))
                total += len(trozo)
    print(f'{len(lotes)} lotes · {total} explicaciones por escribir')
    confi = sum(1 for _, _, fg in lotes if fg)
    print(f'{confi} lotes incluyen alguna pregunta con figura')
    return lotes

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'todos')
