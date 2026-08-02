# Arma un examen unam-a{N}-5.json a partir de los tramos transcritos de la Guía 2025.
#
#   python3 fuentes/unam-2025/armar.py 2
#
# La verificación de respuestas es DETERMINISTA: la clave de la guía se extrae como
# texto (claves/clave-a{N}-2025.json) y aquí se compara reactivo por reactivo. Si algo
# no cuadra, no se escribe nada.
import json, glob, os, re, sys, collections

RAIZ = '/Users/giledvz/Documents/ECOEMS'
ORDEN = ['Física', 'Literatura', 'Química', 'Geografía', 'Matemáticas', 'Español',
         'Biología', 'Historia Universal', 'Historia de México', 'Filosofía']
NOMBRE = {1: 'Ciencias Físico Matemáticas y de las Ingenierías',
          2: 'Ciencias Biológicas, Químicas y de la Salud',
          3: 'Ciencias Sociales',
          4: 'Humanidades y Artes'}
ALUMNOS = {1: ['Óscar', 'Alfredo', 'Dana'], 2: ['Lupita'],
           3: ['Ángeles'], 4: ['Yuri', 'Esme']}
# Dónde vive el examen muestra dentro de cada guía, para poder volver al original.
PAGINAS = {1: ' (páginas 61-82; clave en las 83-86).'}

# El renglón de instrucción sobra dentro del recuadro de lectura: el recuadro ya dice
# visualmente que eso es la lectura, y el rango de preguntas no le sirve al alumno.
INSTR = re.compile(r'^\s*Lee (el|los|la) siguiente[^\n]*\n+', re.I)

RUTA = lambda a: f'/imagenes_unam-a{a}-5'

def main(a):
    qs = {}
    for f in sorted(glob.glob(f'{RAIZ}/fuentes/unam-2025/a{a}-2025-*.json')):
        for q in json.load(open(f, encoding='utf-8'))['questions']:
            qs[q['n']] = q
    clave = json.load(open(f'{RAIZ}/fuentes/unam-2025/claves/clave-a{a}-2025.json',
                           encoding='utf-8'))
    # Registro de figuras ya dibujadas, para que rearmar el examen no las borre.
    figs = json.load(open(f'{RAIZ}/fuentes/unam-2025/figuras/figuras.json',
                          encoding='utf-8'))[str(a)]
    archivos = []
    for v in figs.values():
        archivos += [v] if isinstance(v, str) else \
            ([v['enunciado']] if 'enunciado' in v else []) + list(v.get('opciones', {}).values())
    if faltan_svg := [f for f in archivos
                      if not os.path.exists(f'{RAIZ}/public{RUTA(a)}/{f}')]:
        print(f'  ! figuras registradas que no existen en disco: {faltan_svg}')
        return

    faltan = [n for n in range(1, 121) if n not in qs]
    if faltan:
        print(f'  ! faltan reactivos: {faltan}')
        return
    mal = [n for n in range(1, 121)
           if qs[n]['answer'] != clave[str(n)]['answer']
           or qs[n]['asignatura'] != clave[str(n)]['asignatura']]
    if mal:
        print(f'  ! no cuadran con la clave oficial: {mal}')
        return

    secs = collections.OrderedDict((s, []) for s in ORDEN)
    pend = []
    for n in range(1, 121):
        q = qs[n]
        nq = {'id': n, 'topic': q['tema'], 'topic_name': q['asignatura'], 'text': q['text']}
        ctx = q.get('lectura') or (qs[q['comparte_lectura_con']].get('lectura')
                                   if q.get('comparte_lectura_con') else None)
        if ctx:
            nq['context'] = INSTR.sub('', ctx).strip()
        if q.get('figura') or q.get('figuras_opciones'):
            if str(n) in figs:
                # Ya dibujada: entra como imagen y la descripción deja de hacer falta.
                # El valor es un nombre de archivo suelto, o un dict cuando además
                # hay una imagen por opción.
                v = figs[str(n)]
                v = v if isinstance(v, dict) else {'enunciado': v}
                if 'enunciado' in v:
                    nq['image'] = f'{RUTA(a)}/{v["enunciado"]}'
                if 'opciones' in v:
                    nq['option_images'] = {k: f'{RUTA(a)}/{f}'
                                           for k, f in v['opciones'].items()}
            else:
                # La descripción queda registrada pero FUERA de lo que ve el alumno,
                # hasta que la figura exista como SVG.
                nq['_figura_pendiente'] = {k: v for k, v in
                    (('enunciado', q.get('figura')), ('opciones', q.get('figuras_opciones'))) if v}
                pend.append(n)
        nq['options'] = q['options']
        nq['answer'] = q['answer']
        secs[q['asignatura']].append(nq)
    secs = {s: v for s, v in secs.items() if v}

    exam = {'exam': {
        'title': f'UNAM Área {a} - 5', 'group': 'Universidad', 'date': '2026-08-01',
        'version': '1.0', 'total_questions': 120, 'students': ALUMNOS[a],
        'instructions': 'Selecciona la opción correcta para cada pregunta. '
                        'No se permite el uso de calculadora.',
        'source': {'guia': f'Guia UNAM 2025 Area {a}.pdf', 'anio': 2025,
                   'descripcion': f'Examen muestra de la Guía oficial UNAM 2025, '
                                  f'Área de las {NOMBRE[a]}' + PAGINAS.get(a, '.'),
                   'ubicacion': f'fuentes/unam-guias/guia-unam-a{a}-2025.pdf '
                                '(en disco, fuera de git por peso)'},
        'sections': [{'subject': s, 'questions_count': len(v), 'questions': v}
                     for s, v in secs.items()]}}

    json.dump(exam, open(f'{RAIZ}/unam-a{a}-5.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    print(f'  unam-a{a}-5.json · 120 reactivos · '
          + ' · '.join(f'{s} {len(v)}' for s, v in secs.items()))
    print(f'     figuras pendientes: {pend}')

if __name__ == '__main__':
    main(int(sys.argv[1]))
