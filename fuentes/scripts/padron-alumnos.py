# Arma el padrón de alumnos a partir del historial de git.
#
#   python3 fuentes/scripts/padron-alumnos.py
#
# Cada examen lleva su lista en exam.students, pero esa lista solo dice quién está
# HOY. Cuando un alumno se va, su nombre desaparece y no queda rastro de que estuvo.
# Ahora que empiezan a regresar a repetir el examen hace falta saber quién estuvo,
# en qué grupo y cuándo. El historial sí lo guarda: este script lo recorre y deja el
# padrón en fuentes/alumnos/padron.json.
import json, os, re, subprocess, collections

RAIZ = '/Users/giledvz/Documents/ECOEMS'
SALIDA = os.path.join(RAIZ, 'fuentes/alumnos')

# De qué grupo es cada examen. Se deduce del nombre del archivo.
def grupo_de(examen):
    """A qué curso pertenece un examen. Contempla también los nombres viejos: el
    repo pasó por dos renombres masivos y sin esto la mitad del padrón cae en un
    cajón de sastre."""
    e = examen.lower()
    # Prefijos que solo se usan para universidad: el número que sigue es el área.
    m = re.search(r'(?:unam-a|diag-uni-a|diagnostico-a|universidad_area|examen_area)(\d)', e)
    if m:
        return f'UNAM · Área {m.group(1)}'
    # "area<N>" suelto es ambiguo, así que solo cuenta si el nombre ya habla de
    # universidad (p. ej. diagnostico_matematicas_area1).
    m = re.search(r'area(\d)', e)
    if m and not any(k in e for k in ('ecoems', 'comipems', 'bachillerato')):
        return f'UNAM · Área {m.group(1)}'
    if 'unam' in e or 'eval_matfis' in e or 'universidad' in e:
        return 'UNAM · varios'
    # bachillerato: ECOEMS y su predecesor COMIPEMS
    if any(k in e for k in ('ecoems', 'comipems', 'bachillerato', 'diag-bach')):
        return 'ECOEMS (bachillerato)'
    if 'ipn' in e:
        return 'IPN'
    return 'sin clasificar'

# Nombres que son la misma persona escrita distinto. Se unifican al primero.
ALIAS = {'Oscar': 'Óscar', 'Danna': 'Dana'}

def listas_en(commit):
    """{examen: [alumnos]} en ese commit."""
    out = {}
    files = subprocess.run(['git', 'ls-tree', '-r', '--name-only', commit],
                           capture_output=True, text=True, cwd=RAIZ).stdout.split('\n')
    for f in files:
        if not f.endswith('.json') or '/' in f:
            continue
        blob = subprocess.run(['git', 'show', f'{commit}:{f}'],
                              capture_output=True, text=True, cwd=RAIZ).stdout
        if '"students"' not in blob:
            continue
        m = re.search(r'"students"\s*:\s*\[(.*?)\]', blob, re.S)
        if not m:
            continue
        al = [ALIAS.get(n, n) for n in re.findall(r'"([^"]+)"', m.group(1))]
        if al:
            out[f[:-5]] = al
    return out

def main():
    commits = subprocess.run(
        ['git', 'log', '--all', '--reverse', '--format=%h|%ad', '--date=short'],
        capture_output=True, text=True, cwd=RAIZ).stdout.strip().split('\n')

    # alumno -> {grupo -> {'desde':fecha, 'hasta':fecha, 'examenes':set}}
    reg = collections.defaultdict(lambda: collections.defaultdict(
        lambda: {'desde': None, 'hasta': None, 'examenes': set()}))

    for linea in commits:
        h, fecha = linea.split('|')
        for examen, alumnos in listas_en(h).items():
            g = grupo_de(examen)
            for a in alumnos:
                r = reg[a][g]
                if r['desde'] is None:
                    r['desde'] = fecha
                r['hasta'] = fecha
                r['examenes'].add(examen)

    actuales = listas_en('HEAD')
    vigentes = {a for al in actuales.values() for a in al}

    # grupo al que pertenece HOY cada alumno, según las listas vigentes
    hoy = collections.defaultdict(set)
    for examen, alumnos in actuales.items():
        for a in alumnos:
            hoy[a].add(grupo_de(examen))

    padron = []
    for alumno in sorted(reg, key=lambda s: s.lower()):
        grupos = [{'grupo': g, 'desde': r['desde'], 'hasta': r['hasta'],
                   'examenes': sorted(r['examenes'])}
                  for g, r in sorted(reg[alumno].items())]
        primera = min(g['desde'] for g in grupos)
        ultima = max(g['hasta'] for g in grupos)
        padron.append({
            'nombre': alumno,
            # La generación es el año en que el alumno cursó. Si alguna vez alguien
            # abarca dos años, aquí aparecerán los dos y hay que decidir a mano.
            'generaciones': sorted({primera[:4], ultima[:4]}),
            'vigente': alumno in vigentes,
            'grupo_actual': sorted(hoy.get(alumno, [])),
            'primera_vez': primera,
            'ultima_vez': ultima,
            'historial': grupos,
        })

    os.makedirs(SALIDA, exist_ok=True)
    doc = {
        '_meta': {
            'que_es': 'Padrón de alumnos reconstruido del historial de git. Cada '
                      'examen guarda en exam.students quién está hoy; esto guarda '
                      'quién estuvo y cuándo, para cuando alguien regresa a repetir.',
            'como_se_hizo': 'fuentes/scripts/padron-alumnos.py recorre todos los '
                            'commits y anota, por alumno y grupo, la primera y la '
                            'última fecha en que aparece en una lista.',
            'ojo': 'Las fechas son de commit, no de inscripción: marcan cuándo el '
                   'nombre estaba en el material, que es lo más cercano que hay.',
            'alias': ALIAS,
            'alumnos': len(padron),
            'vigentes': sum(1 for a in padron if a['vigente']),
        },
        'alumnos': padron,
    }
    json.dump(doc, open(os.path.join(SALIDA, 'padron.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    # agrupado por generación y grupo, que es como se consulta en la práctica
    porGen = collections.defaultdict(lambda: collections.defaultdict(list))
    for a in padron:
        for gen in a['generaciones']:
            for g in (a['grupo_actual'] or [h['grupo'] for h in a['historial']]):
                if a['nombre'] not in porGen[gen][g]:
                    porGen[gen][g].append(a['nombre'])

    md = ['# Padrón de alumnos', '',
          'Quién estuvo, en qué grupo y en qué generación. Cada examen guarda en',
          '`exam.students` quién está **hoy**; esto guarda quién **estuvo**, para',
          'cuando alguien regresa a repetir el examen.', '',
          'Se regenera con `python3 fuentes/scripts/padron-alumnos.py`, que recorre el',
          'historial de git. Las fechas son de commit, no de inscripción: marcan cuándo',
          'el nombre estaba en el material, que es lo más cercano que hay.', '']
    for gen in sorted(porGen):
        md += [f'## Generación {gen}', '']
        for g in sorted(porGen[gen]):
            if g == 'UNAM · varios':
                continue          # redundante: son los mismos de las áreas
            md.append(f"- **{g}** — {', '.join(sorted(porGen[gen][g]))}")
        md.append('')
    md += ['## Detalle', '',
           '| Alumno | Generación | Grupo actual | Primera vez | Última vez | Vigente |',
           '|---|:-:|---|---|---|:-:|']
    for a in padron:
        g = ' · '.join(x for x in a['grupo_actual'] if x != 'UNAM · varios') or '—'
        md.append(f"| {a['nombre']} | {', '.join(a['generaciones'])} | {g} | "
                  f"{a['primera_vez']} | {a['ultima_vez']} | "
                  f"{'sí' if a['vigente'] else '**no**'} |")
    md += ['', '## Cuando entre una generación nueva', '',
           'No hay que hacer nada especial: se agregan los nombres a `exam.students`',
           'de los exámenes que les toquen y se vuelve a correr el script. Las fechas',
           'de commit los colocan solos en su año, y los de generaciones anteriores',
           'se quedan registrados aunque ya no estén en ninguna lista.', '']
    md += ['', '## Nombres unificados', '',
           'Aparecieron escritos de dos formas y son la misma persona:', '']
    for viejo, nuevo in ALIAS.items():
        md.append(f'- `{viejo}` → **{nuevo}**')
    open(os.path.join(SALIDA, 'PADRON.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')

    print(f"{len(padron)} alumnos · {doc['_meta']['vigentes']} vigentes")
    for a in padron:
        g = ' · '.join(a['grupo_actual']) or '(ya no está en ningún examen)'
        print(f"  {'●' if a['vigente'] else '○'} {a['nombre']:16s} "
              f"{a['primera_vez']} → {a['ultima_vez']}   {g}")

if __name__ == '__main__':
    main()
