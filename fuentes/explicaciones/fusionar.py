# Mete las explicaciones de salida/ en los exámenes, validando antes de tocar nada.
#
#   python3 fuentes/explicaciones/fusionar.py --dry     # solo revisa y reporta
#   python3 fuentes/explicaciones/fusionar.py           # escribe los exámenes
#
# Las líneas que empiezan con REVISAR: son notas del modelo cuando su resolución no
# coincide con la clave oficial. NO deben llegar al alumno: se recortan de la
# explicación y se juntan en revisar.md para revisarlas a mano.
import json, os, re, sys, glob, collections

RAIZ = '/Users/giledvz/Documents/ECOEMS'
BASE = os.path.join(RAIZ, 'fuentes/explicaciones')
LOTES, SALIDA = os.path.join(BASE, 'lotes'), os.path.join(BASE, 'salida')

# lo único que el renderizador desescapa; cualquier otra etiqueta sale literal
TAGS_OK = {'b', 'i', 'u', 'em', 'strong', 'br', 'img'}

def revisa_texto(t):
    """Devuelve la lista de problemas de una explicación."""
    prob = []
    if not t.strip():
        prob.append('vacía')
    # Una etiqueta de verdad cierra con ">". Sin exigirlo, un "menor que" dentro de
    # LaTeX se confunde con HTML: la ordenación de electronegatividades
    # $Sc<Be<Cr<As<Cl$ se leía como cuatro etiquetas <Be> <Cr> <As> <Cl>.
    for tag in re.findall(r'<\s*/?\s*([a-zA-Z][a-zA-Z0-9]*)(?:\s[^<>]*)?\s*/?>', t):
        if tag.lower() not in TAGS_OK:
            prob.append(f'etiqueta HTML <{tag}>')
    if t.count('$') % 2:
        prob.append('signos de pesos impares (LaTeX sin cerrar)')
    if re.match(r'^\s*(la\s+)?respuesta\s+correcta\s+es', t, re.I):
        prob.append('empieza con "la respuesta correcta es"')
    if len(t) > 1800:
        prob.append(f'muy larga ({len(t)} car.)')
    return prob

def parte_revisar(t):
    """Separa la explicación de sus notas REVISAR:."""
    lineas = t.split('\n')
    notas = [l.strip() for l in lineas if l.strip().upper().startswith('REVISAR:')]
    limpio = '\n'.join(l for l in lineas if not l.strip().upper().startswith('REVISAR:'))
    return limpio.strip(), notas

def main(dry):
    porExamen = collections.defaultdict(dict)   # examen -> {id: explicación}
    revisar, problemas, faltantes = [], [], []
    lotes = sorted(glob.glob(os.path.join(LOTES, '*.json')))

    for lp in lotes:
        nombre = os.path.basename(lp)[:-5]
        sp = os.path.join(SALIDA, nombre + '.json')
        lote = json.load(open(lp, encoding='utf-8'))
        esperados = [q['id'] for q in lote['preguntas']]
        if not os.path.exists(sp):
            faltantes.append(f'{nombre} ({len(esperados)} preguntas)')
            continue
        try:
            sal = json.load(open(sp, encoding='utf-8'))
        except Exception as ex:
            problemas.append(f'{nombre}: JSON inválido — {ex}')
            continue
        got = {e['id']: e.get('explanation', '') for e in sal if isinstance(e, dict)}
        sobran = set(got) - set(esperados)
        faltan = set(esperados) - set(got)
        if faltan:  problemas.append(f'{nombre}: faltan ids {sorted(faltan)[:8]}')
        if sobran:  problemas.append(f'{nombre}: ids que no son del lote {sorted(sobran)[:8]}')
        clave = {q['id']: q['clave'] for q in lote['preguntas']}
        for qid in esperados:
            if qid not in got:
                continue
            limpio, notas = parte_revisar(got[qid])
            for p in revisa_texto(limpio):
                problemas.append(f'{nombre} id {qid}: {p}')
            for n in notas:
                revisar.append({'examen': lote['examen'], 'id': qid, 'materia': lote['materia'],
                                'clave': clave[qid], 'nota': n})
            porExamen[lote['examen']][qid] = limpio

    print(f'lotes: {len(lotes)} · con salida: {len(lotes) - len(faltantes)}')
    print(f'explicaciones listas: {sum(len(v) for v in porExamen.values())}')
    print(f'marcadas REVISAR: {len(revisar)}')
    if faltantes:
        print(f'\nSIN SALIDA ({len(faltantes)}):'); [print('  ·', x) for x in faltantes[:20]]
    if problemas:
        print(f'\nPROBLEMAS ({len(problemas)}):'); [print('  !', x) for x in problemas[:25]]

    if dry:
        print('\n(dry run: no se escribió nada)')
        return

    if problemas:
        print('\nNO se escribe nada mientras haya problemas. Corrígelos y vuelve a correr.')
        return

    for examen, mapa in sorted(porExamen.items()):
        p = os.path.join(RAIZ, examen)
        d = json.load(open(p, encoding='utf-8'))
        n = 0
        for sec in d['exam']['sections']:
            for q in sec['questions']:
                if q['id'] in mapa:
                    q['explanation'] = mapa[q['id']]
                    n += 1
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f'  {examen:28s} +{n} explicaciones')

    if revisar:
        md = ['# Reactivos marcados REVISAR por el modelo', '',
              'El modelo resolvió el reactivo por su cuenta y no le dio la clave oficial.',
              'La explicación que ve el alumno sigue siendo la de la clave oficial; estas',
              'notas se recortaron y se juntaron aquí para revisarlas a mano.', '']
        for r in revisar:
            md.append(f"- **{r['examen']} · id {r['id']}** ({r['materia']}, clave {r['clave']}) — "
                      f"{r['nota'][len('REVISAR:'):].strip()}")
        open(os.path.join(BASE, 'revisar.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
        print(f"\nrevisar.md: {len(revisar)} notas")

if __name__ == '__main__':
    main('--dry' in sys.argv)
