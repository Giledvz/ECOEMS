# Cuadernillo de práctica para el ETS de Geometría y Trigonometría (CECyT 1, IPN).
#
# Los tipos de problema salen de los ocho ETS que tenemos (2009, 2010, 2017, 2018,
# 2019, 2023, 2025 y enero 2026): los reactivos cambian de números año con año pero
# los TIPOS se repiten casi idénticos, así que practicar por tipo es lo que rinde.
#
# Todo se genera con Python resolviendo de verdad cada ejercicio. Ninguna respuesta
# está escrita a mano: así no hay forma de que una salga mal por distracción, y
# verificar.py vuelve a resolver cada una por un camino independiente.
import math

# ── utilidades ──────────────────────────────────────────────────────────────
def num(v, dec=2):
    """Número para imprimir: sin decimales si es entero, si no redondeado."""
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    s = f'{v:.{dec}f}'.rstrip('0').rstrip('.')
    return s

def lin(a, b, var='x'):
    """Expresión lineal ax+b como texto LaTeX, bien signada."""
    p = '' if a == 1 else ('-' if a == -1 else num(a))
    s = f'{p}{var}'
    if b:
        s += f' {"+" if b > 0 else "-"} {num(abs(b))}'
    return s

def gms(grados):
    """Grados decimales a grados-minutos-segundos."""
    g = int(grados)
    m_ = (grados - g) * 60
    m = int(m_)
    s = round((m_ - m) * 60)
    if s == 60:
        s = 0; m += 1
    if m == 60:
        m = 0; g += 1
    return f"{g}^\\circ {m}' {s}''"

def ej(enunciado, pasos, respuesta, figura=None):
    return {'enunciado': enunciado, 'pasos': pasos, 'respuesta': respuesta,
            'figura': figura}

# Parámetros de los bloques que se arman con varias formas. Viven aquí, a la vista,
# para que verificar.py lea EXACTAMENTE los mismos y no puedan desincronizarse.
C1_PARS = [(10, 3, 1, 2), (2, 2, 4, 3), (3, 1, -5, 2), (10, 5, 0, 3),
           (5, 2, 3, 2), (2, 4, -8, 4)]
C2_PARS = [(2, 4, 3, 3), (2, 6, 2, 2), (3, 8, 1, 1), (10, 9, 4, 1)]
C3_PARS = [(5, 3), (4, 6), (7, 12), (3, 8)]
C4_PARS = [(2, 2, 1, 1, 1), (1, 3, 1, 2, 1), (2, 1, 1, 2, 1)]
J_LADOS = (20, 12, 15, 9)
J_ANGULOS = (150, 162, 156, 140)
J_DIAGONALES = (77, 119, 35, 54, 90)
Q1_PARS = [('cos', 2, -1), ('sen', 2, -math.sqrt(3)), ('sen', 2, -1),
           ('cos', 2, math.sqrt(2)), ('tan', 1, -1)]
Q2_PARS = [('sen', 2, 1), ('tan', 2, 1), ('cos', 3, -2), ('sen', 4, -3)]
Q3_PARS = [('cos', 2, -3, 1), ('sen', 2, -1, -1), ('cos', 2, 1, -1)]
S_COSTO = [(200, 8, 375.46), (45, 12, 128.5), (18.5, 3.2, 260)]
S_DIAG = [(5, -2, 13), (1, -6, 17), (-4, -6, 10)]      # cada uno con y entero

# ── A. Ecuaciones exponenciales de base común ───────────────────────────────
# (b^p)^(mx+n) = (b^q)^(rx+s). Se igualan exponentes tras dejar la misma base.
A_PARS = [
    (2, 1, 3, -6, 4, 1, -2), (2, 1, 2, 2, 3, 1, 1), (3, 1, 2, 1, 1, 3, -4),
    (2, 2, 1, 5, 3, 1, -1), (5, 1, 2, -3, 1, 4, 1), (2, 3, 1, 2, 1, 5, 2),
    (3, 2, 1, 4, 4, 1, -3), (2, 1, 5, 1, 2, 3, 4), (7, 1, 3, -2, 1, 2, 5),
    (2, 4, 1, -1, 2, 3, 2), (3, 3, 1, 1, 1, 6, -2), (5, 2, 1, 3, 1, 5, -4),
]

def bloque_A():
    out = []
    for b, p, m, n, q, r, s in A_PARS:
        # p(mx+n) = q(rx+s)  →  (pm - qr)x = qs - pn
        c, d = p * m - q * r, q * s - p * n
        x = d / c
        izq = f'{b**p}^{{{lin(m, n)}}}' if p > 1 else f'{b}^{{{lin(m, n)}}}'
        der = f'{b**q}^{{{lin(r, s)}}}' if q > 1 else f'{b}^{{{lin(r, s)}}}'
        pasos = [
            f'Escribe las dos potencias en la misma base. Como ${b**p} = {b}^{{{p}}}$ y '
            f'${b**q} = {b}^{{{q}}}$:',
            f'$${b}^{{{p}({lin(m, n)})}} = {b}^{{{q}({lin(r, s)})}}$$',
            'Con la misma base, los exponentes tienen que ser iguales:',
            f'$${lin(p*m, p*n)} = {lin(q*r, q*s)}$$',
            f'$${lin(c, 0)} = {num(d)} \\quad\\Rightarrow\\quad x = {num(x, 4)}$$',
        ]
        out.append(ej(f'Resuelve la ecuación exponencial $${izq} = {der}$$',
                      pasos, f'$x = {num(x, 4)}$'))
    return out

# ── B. Ecuaciones exponenciales de bases distintas (con logaritmos) ─────────
B_PARS = [(3, 2, -1, 5, 4, 3), (2, 3, 5, 3, 1, 2), (5, 1, 2, 2, 3, -1),
          (7, 2, 1, 3, 1, 4), (2, 1, -3, 6, 2, 1), (10, 3, 2, 4, 1, -5),
          (3, 1, 1, 7, 2, 2), (5, 4, -2, 2, 1, 3)]

def bloque_B():
    out = []
    for b1, m, n, b2, r, s in B_PARS:
        # (mx+n)·log b1 = (rx+s)·log b2
        L1, L2 = math.log10(b1), math.log10(b2)
        x = (s * L2 - n * L1) / (m * L1 - r * L2)
        pasos = [
            'Las bases no se pueden igualar, así que aplica logaritmo a los dos lados '
            'y baja los exponentes:',
            f'$$({lin(m, n)})\\log {b1} = ({lin(r, s)})\\log {b2}$$',
            f'Sustituye $\\log {b1} = {num(L1, 4)}$ y $\\log {b2} = {num(L2, 4)}$, '
            'desarrolla y agrupa las $x$ de un lado:',
            f'$$x({num(m*L1, 4)} - {num(r*L2, 4)}) = {num(s*L2, 4)} - {num(n*L1, 4)}$$',
            f'$$x = \\frac{{{num(s*L2 - n*L1, 4)}}}{{{num(m*L1 - r*L2, 4)}}} = {num(x, 4)}$$',
        ]
        out.append(ej(f'Resuelve la ecuación exponencial '
                      f'$${b1}^{{{lin(m, n)}}} = {b2}^{{{lin(r, s)}}}$$',
                      pasos, f'$x \\approx {num(x, 4)}$'))
    return out

# ── C. Ecuaciones logarítmicas ──────────────────────────────────────────────
def bloque_C():
    out = []
    # C1: log_b(mx+n) = k
    for b, m, n, k in C1_PARS:
        val = b ** k
        x = (val - n) / m
        base = '' if b == 10 else f'_{{{b}}}'
        pasos = [
            f'Por definición, $\\log{base}(N) = {k}$ significa $N = {b}^{{{k}}} = {val}$:',
            f'$${lin(m, n)} = {val}$$',
            f'$$x = \\frac{{{val} - {num(n)}}}{{{m}}} = {num(x, 4)}$$',
            f'Comprueba que el argumento quede positivo: '
            f'${lin(m, n)} = {num(val)} > 0$. Sí sirve.',
        ]
        out.append(ej(f'Resuelve la ecuación logarítmica '
                      f'$$\\log{base}({lin(m, n)}) = {k}$$', pasos, f'$x = {num(x, 4)}$'))
    # C2: log_b(x+a) - log_b(x-c) = k   →  (x+a)/(x-c) = b^k
    for b, a, c, k in C2_PARS:
        R = b ** k
        x = (R * c + a) / (R - 1)
        base = '' if b == 10 else f'_{{{b}}}'
        pasos = [
            'Resta de logaritmos con la misma base es el logaritmo del cociente:',
            f'$$\\log{base}\\left(\\frac{{{lin(1, a)}}}{{{lin(1, -c)}}}\\right) = {k}$$',
            f'Por definición el cociente vale ${b}^{{{k}}} = {R}$:',
            f'$${lin(1, a)} = {R}({lin(1, -c)})$$',
            f'$$x + {a} = {R}x - {R*c} \\quad\\Rightarrow\\quad x = {num(x, 4)}$$',
            f'Los dos argumentos quedan positivos ($x + {a} = {num(x+a, 2)}$ y '
            f'$x - {c} = {num(x-c, 2)}$), así que la solución sirve.',
        ]
        out.append(ej(f'Resuelve la ecuación logarítmica '
                      f'$$\\log{base}({lin(1, a)}) - \\log{base}({lin(1, -c)}) = {k}$$',
                      pasos, f'$x = {num(x, 4)}$'))
    # C3: log(mx) - log(x+c) = 0  →  mx = x+c
    for m, c in C3_PARS:
        x = c / (m - 1)
        pasos = [
            'Pasa la resta a cociente y usa que $\\log(N) = 0$ obliga a $N = 1$:',
            f'$$\\frac{{{m}x}}{{{lin(1, c)}}} = 1$$',
            f'$${m}x = x + {c} \\quad\\Rightarrow\\quad {m-1}x = {c} '
            f'\\quad\\Rightarrow\\quad x = {num(x, 4)}$$',
        ]
        out.append(ej(f'Resuelve la ecuación logarítmica '
                      f'$$\\log({m}x) - \\log({lin(1, c)}) = 0$$', pasos,
                      f'$x = {num(x, 4)}$'))
    # C4: log(ax+b) + log(cx+d) = k  (cuadrática)
    for a, b_, c_, d, k in C4_PARS:
        # (ax+b)(cx+d) = 10^k
        A, B, C = a * c_, a * d + b_ * c_, b_ * d - 10 ** k
        disc = B * B - 4 * A * C
        r1 = (-B + math.sqrt(disc)) / (2 * A)
        r2 = (-B - math.sqrt(disc)) / (2 * A)
        buenas = [r for r in (r1, r2) if a * r + b_ > 0 and c_ * r + d > 0]
        x = buenas[0]
        pasos = [
            'Suma de logaritmos con la misma base es el logaritmo del producto:',
            f'$$\\log\\big(({lin(a, b_)})({lin(c_, d)})\\big) = {k}$$',
            f'El producto vale $10^{{{k}}} = {10**k}$:',
            f'$${num(A)}x^2 {"+" if B >= 0 else "-"} {num(abs(B))}x '
            f'{"+" if (b_*d - 10**k) >= 0 else "-"} {num(abs(b_*d - 10**k))} = 0$$',
            f'Con la fórmula general salen $x = {num(r1, 4)}$ y $x = {num(r2, 4)}$.',
            f'Se descarta $x = {num(r2, 4)}$ porque deja un argumento negativo, y el '
            'logaritmo de un número negativo no existe.',
        ]
        out.append(ej(f'Resuelve la ecuación logarítmica '
                      f'$$\\log({lin(a, b_)}) + \\log({lin(c_, d)}) = {k}$$', pasos,
                      f'$x = {num(x, 4)}$'))
    return out

# ── D. Modelos exponenciales aplicados ──────────────────────────────────────
D_PARS = [
    ('truchas', 'En un estanque se sueltan {N0} truchas adultas. Se espera que el número '
     'que siga vivo después de $t$ años sea $N(t) = {N0}({r})^t$. ¿Cuándo quedarán {meta}?',
     1000, 0.9, 500),
    ('bacterias', 'Un cultivo empieza con {N0} bacterias y se duplica cada hora, de modo '
     'que $N(t) = {N0}({r})^t$ con $t$ en horas. ¿Cuántas horas pasan para llegar a {meta}?',
     500, 2, 32000),
    ('medicamento', 'La cantidad de medicamento en la sangre sigue $N(t) = {N0}({r})^t$, '
     'con $t$ en horas. ¿En cuántas horas quedan {meta} mg?', 240, 0.85, 60),
    ('inversión', 'Una inversión de $\\${N0}$ crece según $N(t) = {N0}({r})^t$, con $t$ '
     'en años. ¿En cuántos años llega a $\\${meta}$?', 15000, 1.08, 30000),
    ('población', 'La población de un pueblo sigue $N(t) = {N0}({r})^t$, con $t$ en años. '
     '¿En cuántos años llega a {meta} habitantes?', 8000, 1.035, 12000),
    ('enfriamiento', 'Un objeto se enfría según $N(t) = {N0}({r})^t$ grados, con $t$ en '
     'minutos. ¿En cuántos minutos llega a {meta} grados?', 90, 0.93, 25),
]

def bloque_D():
    out = []
    for _, plantilla, N0, r, meta in D_PARS:
        t = math.log(meta / N0) / math.log(r)
        pasos = [
            'Iguala la fórmula al valor que te piden y despeja la potencia:',
            f'$${num(N0)}({num(r)})^t = {num(meta)} \\quad\\Rightarrow\\quad '
            f'({num(r)})^t = {num(meta/N0, 4)}$$',
            'Aplica logaritmo a los dos lados y baja el exponente:',
            f'$$t\\log({num(r)}) = \\log({num(meta/N0, 4)})$$',
            f'$$t = \\frac{{{num(math.log10(meta/N0), 4)}}}{{{num(math.log10(r), 4)}}} '
            f'= {num(t, 3)}$$',
        ]
        out.append(ej(plantilla.format(N0=num(N0), r=num(r), meta=num(meta)),
                      pasos, f'$t \\approx {num(t, 3)}$'))
    return out

# ── figuras ─────────────────────────────────────────────────────────────────
FONT = "'Latin Modern Roman', Georgia, serif"

def svg_paralelas(rotA, rotB, tipo):
    """Dos paralelas cortadas por una secante, con dos ángulos rotulados.
    tipo dice en qué posición va cada rótulo."""
    W, H = 340, 210
    y1, y2 = 62, 148
    # la secante cruza inclinada
    x1, x2 = 96, 244
    pos = {                       # (punto de corte, desplazamiento del rótulo)
        'alternos internos':  ((x1, y1, 30, 26), (x2, y2, -34, -12)),
        'alternos externos':  ((x1, y1, -34, -12), (x2, y2, 30, 26)),
        'correspondientes':   ((x1, y1, 30, -12), (x2, y2, 30, -12)),
        'colaterales':        ((x1, y1, 30, 26), (x2, y2, 30, -12)),
    }[tipo]
    c = [f'<line x1="24" y1="{y1}" x2="{W-24}" y2="{y1}" stroke="currentColor" stroke-width="2"/>',
         f'<line x1="24" y1="{y2}" x2="{W-24}" y2="{y2}" stroke="currentColor" stroke-width="2"/>',
         f'<line x1="{x1-52}" y1="{y1-32}" x2="{x2+52}" y2="{y2+32}" stroke="currentColor" stroke-width="2"/>']
    for (px, py, dx, dy), rot in zip(pos, (rotA, rotB)):
        c.append(f'<text x="{px+dx}" y="{py+dy}" font-size="15" text-anchor="middle">{rot}</text>')
    c.append(f'<text x="{W-18}" y="{y1-8}" font-size="13" font-style="italic">m</text>')
    c.append(f'<text x="{W-18}" y="{y2-8}" font-size="13" font-style="italic">n</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
            f'height="{H}" fill="currentColor" font-family="{FONT}">' + ''.join(c) + '</svg>')

def svg_tales(ad, db, ae, ec, inc):
    """Triángulo ABC con DE paralelo a BC. inc dice qué segmento es la incógnita."""
    W, H = 320, 240
    A, B, C = (56, 216), (284, 216), (128, 34)
    t = 0.46                                   # dónde cae D sobre AB… (visual)
    D = (A[0] + (C[0]-A[0])*t, A[1] + (C[1]-A[1])*t)
    E = (A[0] + (B[0]-A[0])*t, A[1] + (B[1]-A[1])*t)
    et = {'AD': ad, 'DB': db, 'AE': ae, 'EC': ec}
    c = [f'<path d="M {A[0]} {A[1]} L {B[0]} {B[1]} L {C[0]} {C[1]} Z" fill="currentColor" '
         f'fill-opacity="0.07" stroke="currentColor" stroke-width="2"/>',
         f'<line x1="{D[0]:.0f}" y1="{D[1]:.0f}" x2="{E[0]:.0f}" y2="{E[1]:.0f}" '
         f'stroke="currentColor" stroke-width="2" stroke-dasharray="6 4"/>']
    for p, t_, dx, dy in ((A, 'A', -14, 8), (B, 'B', 14, 8), (C, 'C', -6, -12),
                          (D, 'D', -16, 0), (E, 'E', 16, 6)):
        c.append(f'<text x="{p[0]+dx:.0f}" y="{p[1]+dy:.0f}" font-size="16" '
                 f'font-style="italic" text-anchor="middle">{t_}</text>')
    # rótulos de los cuatro segmentos, a media distancia
    for (p, q), k, dx, dy in (((A, D), 'AD', -22, 4), ((D, C), 'DB', -22, 4),
                              ((A, E), 'AE', 6, 20), ((E, B), 'EC', 6, 20)):
        mx, my = (p[0]+q[0])/2, (p[1]+q[1])/2
        c.append(f'<text x="{mx+dx:.0f}" y="{my+dy:.0f}" font-size="14" '
                 f'text-anchor="middle">{et[k]}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
            f'height="{H}" fill="currentColor" font-family="{FONT}">' + ''.join(c) + '</svg>')

# ── E. Ángulos entre paralelas cortadas por una secante ─────────────────────
E_PARS = [
    ('alternos internos', 8, -30, 2, 24), ('alternos externos', 3, 10, 4, -20),
    ('correspondientes', 4, 20, 6, -10),  ('alternos internos', 12, 8, 17, -4),
    ('alternos externos', 2, 40, 3, -35), ('correspondientes', 5, 12, 7, -18),
    ('alternos internos', 9, -6, 5, 2),   ('alternos externos', 6, 15, 11, -35),
    ('correspondientes', 7, 4, 3, 40),    ('alternos internos', 10, -12, 4, 30),
]
E_COLAT = [('colaterales', 5, 10, 4, 35), ('colaterales', 7, -5, 8, 22)]

def bloque_E():
    out = []
    for tipo, a, b, c_, d in E_PARS:
        x = (d - b) / (a - c_)                 # iguales
        ang = a * x + b
        sup = 180 - ang
        fig = svg_paralelas(f'A = {lin(a, b)}', f'B = {lin(c_, d)}', tipo)
        pasos = [
            f'Los ángulos {tipo} entre paralelas son **iguales**, así que iguala las '
            'dos expresiones:',
            f'$${lin(a, b)} = {lin(c_, d)}$$',
            f'$${lin(a - c_, 0)} = {num(d - b)} \\quad\\Rightarrow\\quad x = {num(x, 4)}$$',
            f'Sustituye para obtener el ángulo: $A = {a}({num(x, 4)}) {"+" if b >= 0 else "-"} '
            f'{abs(b)} = {num(ang, 2)}^\\circ$. El otro mide lo mismo.',
            f'El **suplementario** es lo que le falta para $180^\\circ$: '
            f'$180^\\circ - {num(ang, 2)}^\\circ = {num(sup, 2)}^\\circ$.',
        ]
        out.append(ej(f'Dos rectas paralelas cortadas por una secante forman los ángulos '
                      f'{tipo} $A = {lin(a, b)}$ y $B = {lin(c_, d)}$. Determina el valor '
                      f'de $x$, cuánto mide cada ángulo y cuánto mide el suplementario '
                      f'de $A$.', pasos,
                      f'$x = {num(x, 4)}$, $A = B = {num(ang, 2)}^\\circ$, '
                      f'suplementario $= {num(sup, 2)}^\\circ$', fig))
    for tipo, a, b, c_, d in E_COLAT:
        x = (180 - b - d) / (a + c_)           # suman 180
        ang1, ang2 = a * x + b, c_ * x + d
        fig = svg_paralelas(f'A = {lin(a, b)}', f'B = {lin(c_, d)}', tipo)
        pasos = [
            'Los ángulos **colaterales** (del mismo lado de la secante) son '
            'suplementarios: suman $180^\\circ$.',
            f'$$({lin(a, b)}) + ({lin(c_, d)}) = 180$$',
            f'$${lin(a + c_, b + d)} = 180 \\quad\\Rightarrow\\quad x = {num(x, 4)}$$',
            f'$A = {num(ang1, 2)}^\\circ$ y $B = {num(ang2, 2)}^\\circ$. '
            f'Verifica: ${num(ang1, 2)} + {num(ang2, 2)} = 180$. ✓',
        ]
        out.append(ej(f'Dos rectas paralelas cortadas por una secante forman los ángulos '
                      f'colaterales internos $A = {lin(a, b)}$ y $B = {lin(c_, d)}$. '
                      f'Determina el valor de $x$ y cuánto mide cada ángulo.', pasos,
                      f'$x = {num(x, 4)}$, $A = {num(ang1, 2)}^\\circ$, '
                      f'$B = {num(ang2, 2)}^\\circ$', fig))
    return out

# ── F. Ángulos internos y externos de un triángulo ──────────────────────────
F_INT = [(5, 5, 8, 42, 9, 1), (2, 10, 3, -14, 2, 0), (4, 12, 6, -8, 5, 16),
         (3, 20, 7, -5, 2, 15), (6, -4, 5, 30, 4, 8), (8, 2, 3, 26, 7, -4)]
F_EXT = [(2, 10, 3, -14, 2, 0), (5, 8, 4, 22, 3, -6), (7, -10, 6, 15, 4, 5),
         (3, 25, 2, 18, 4, -8)]

def bloque_F():
    out = []
    for a1, b1, a2, b2, a3, b3 in F_INT:
        x = (180 - b1 - b2 - b3) / (a1 + a2 + a3)
        A, B, C = a1*x + b1, a2*x + b2, a3*x + b3
        pasos = [
            'Los tres ángulos internos de cualquier triángulo suman $180^\\circ$:',
            f'$$({lin(a1, b1)}) + ({lin(a2, b2)}) + ({lin(a3, b3)}) = 180$$',
            f'$${lin(a1+a2+a3, b1+b2+b3)} = 180 \\quad\\Rightarrow\\quad x = {num(x, 4)}$$',
            f'$A = {num(A, 2)}^\\circ$, $B = {num(B, 2)}^\\circ$, $C = {num(C, 2)}^\\circ$. '
            f'Comprueba que sumen $180^\\circ$. ✓',
        ]
        out.append(ej(f'Los ángulos internos de un triángulo miden $A = {lin(a1, b1)}$, '
                      f'$B = {lin(a2, b2)}$ y $C = {lin(a3, b3)}$. Obtén el valor '
                      f'numérico de los tres ángulos.', pasos,
                      f'$x = {num(x, 4)}$; $A = {num(A, 2)}^\\circ$, $B = {num(B, 2)}^\\circ$, '
                      f'$C = {num(C, 2)}^\\circ$'))
    for ae, be, a2, b2, a3, b3 in F_EXT:
        # ángulo externo = suma de los dos internos no adyacentes
        x = (b2 + b3 - be) / (ae - a2 - a3)
        E, B, C = ae*x + be, a2*x + b2, a3*x + b3
        A = 180 - E
        pasos = [
            'Un ángulo **externo** vale lo mismo que la suma de los dos internos que no '
            'están junto a él:',
            f'$${lin(ae, be)} = ({lin(a2, b2)}) + ({lin(a3, b3)})$$',
            f'$${lin(ae, be)} = {lin(a2+a3, b2+b3)} \\quad\\Rightarrow\\quad x = {num(x, 4)}$$',
            f'Externo $= {num(E, 2)}^\\circ$; los internos no adyacentes miden '
            f'${num(B, 2)}^\\circ$ y ${num(C, 2)}^\\circ$.',
            f'El interno adyacente al externo es su suplemento: '
            f'$180^\\circ - {num(E, 2)}^\\circ = {num(A, 2)}^\\circ$.',
        ]
        out.append(ej(f'Un triángulo tiene un ángulo externo que mide ${lin(ae, be)}$, '
                      f'mientras que los dos internos no adyacentes a él miden '
                      f'${lin(a2, b2)}$ y ${lin(a3, b3)}$. Determina el valor numérico de '
                      f'los tres ángulos internos.', pasos,
                      f'$x = {num(x, 4)}$; internos: ${num(B, 2)}^\\circ$, '
                      f'${num(C, 2)}^\\circ$ y ${num(A, 2)}^\\circ$'))
    return out

# ── G. Triángulo rectángulo con lados en x (Pitágoras) ──────────────────────
# Cada terna (a, b, h) está elegida para que la ecuación de Pitágoras dé una x
# ENTERA: si no, el alumno acaba con catetos de cuatro decimales y el ejercicio
# deja de parecerse a los del ETS.
G_PARS = [(0, 7, 13), (-2, 3, 25), (1, -1, 10), (-6, -5, 5), (-4, -6, 10),
          (-3, -6, 15), (-2, -6, 20), (-1, -6, 25), (1, -6, 17), (8, -6, 26),
          (0, -6, 30), (8, -6, 34)]

def bloque_G():
    out = []
    for a, b, h in G_PARS:
        A_, B_, C_ = 2, 2*(a+b), a*a + b*b - h*h
        d = B_*B_ - 4*A_*C_
        x = (-B_ + math.sqrt(d)) / (2*A_)
        c1, c2 = x + a, x + b
        per = c1 + c2 + h
        pasos = [
            'Aplica el teorema de Pitágoras: la suma de los cuadrados de los catetos es '
            'el cuadrado de la hipotenusa.',
            f'$$({lin(1, a)})^2 + ({lin(1, b)})^2 = {h}^2$$',
            'Desarrolla los dos binomios al cuadrado y junta términos:',
            f'$$2x^2 {"+" if B_ >= 0 else "-"} {abs(B_)}x + {a*a + b*b} = {h*h}$$',
            f'$$2x^2 {"+" if B_ >= 0 else "-"} {abs(B_)}x {"+" if C_ >= 0 else "-"} '
            f'{abs(C_)} = 0$$',
            f'Por la fórmula general, la raíz positiva es $x = {num(x)}$ (la negativa se '
            'descarta: una longitud no puede ser negativa).',
            f'Los catetos miden ${num(c1)}$ y ${num(c2)}$, así que el perímetro es '
            f'${num(c1)} + {num(c2)} + {h} = {num(per)}$.',
        ]
        out.append(ej(f'Un triángulo rectángulo tiene por catetos ${lin(1, a)}$ y '
                      f'${lin(1, b)}$, y por hipotenusa $h = {h}$. Determina el valor '
                      f'numérico del perímetro.', pasos,
                      f'$x = {num(x)}$; catetos ${num(c1)}$ y ${num(c2)}$; '
                      f'perímetro $= {num(per)}$'))
    return out

# ── H. Semejanza: sombras, fotografías y planos ─────────────────────────────
H_PARS = [
    ('Un poste proyecta una sombra de {s2} m mientras que una persona de {h1} m proyecta '
     'una sombra de {s1} m al mismo tiempo. ¿Cuál es la altura del poste?', 1.8, 3, 12),
    ('¿Qué altura tiene un poste que proyecta una sombra de {s2} m, al mismo tiempo que '
     'un observador de {h1} m de estatura proyecta una sombra de {s1} m?', 1.8, 1.2, 16),
    ('Luis mide {h1} m y proyecta una sombra de {s1} m; al mismo tiempo un poste proyecta '
     'una sombra de {s2} m. Obtén la altura del poste.', 1.6, 3.35, 9.72),
    ('David mide {h1} m y proyecta una sombra de {s1} m. Un árbol junto a él proyecta una '
     'sombra de {s2} m. ¿Qué altura tiene el árbol?', 1.68, 2.5, 3.8),
    ('Una antena proyecta una sombra de {s2} m en el momento en que una barda de {h1} m '
     'proyecta una sombra de {s1} m. ¿Cuánto mide la antena?', 2.4, 1.5, 21),
    ('Un edificio proyecta una sombra de {s2} m mientras que una señal de tránsito de '
     '{h1} m proyecta una sombra de {s1} m. ¿Qué altura tiene el edificio?', 2.1, 0.7, 14),
    ('En una fotografía están Pablo y su padre. Pablo mide en la realidad {h1} m y en la '
     'foto {s1} cm; su padre mide {s2} cm en la foto. ¿Cuánto mide el padre en la '
     'realidad?', 1.5, 6, 7.2),
    ('En una maqueta, una torre de {h1} m aparece con {s1} cm de alto. Otro edificio '
     'aparece con {s2} cm. ¿Cuánto mide ese edificio en la realidad?', 45, 9, 13.4),
    ('Adán mide {h1} m y proyecta una sombra de {s1} m; la sombra de Eva mide {s2} m al '
     'mismo tiempo. Determina la altura de Eva.', 1.77, 1.62, 1.44),
    ('Una escalera apoyada en una pared llega a {h1} m de altura con la base a {s1} m del '
     'muro. Si se aleja la base hasta {s2} m manteniendo la misma inclinación de la '
     'diagonal del dibujo a escala, ¿a qué altura llegaría?', 3.2, 1.6, 2.4),
]

def bloque_H():
    out = []
    for plantilla, h1, s1, s2 in H_PARS:
        h2 = h1 * s2 / s1
        pasos = [
            'Los dos objetos y sus sombras forman **triángulos semejantes**, así que sus '
            'lados guardan la misma proporción:',
            f'$$\\frac{{\\text{{altura conocida}}}}{{\\text{{su sombra}}}} = '
            f'\\frac{{\\text{{altura buscada}}}}{{\\text{{su sombra}}}}$$',
            f'$$\\frac{{{num(h1)}}}{{{num(s1)}}} = \\frac{{H}}{{{num(s2)}}}$$',
            f'$$H = \\frac{{{num(h1)} \\times {num(s2)}}}{{{num(s1)}}} = {num(h2, 3)}$$',
        ]
        out.append(ej(plantilla.format(h1=num(h1), s1=num(s1), s2=num(s2)), pasos,
                      f'${num(h2, 3)}$'))
    return out

# ── I. Semejanza con un segmento paralelo a un lado (Tales) ─────────────────
I_PARS = [(4, 6, 6, None), (5, 3, 10, None), (3, 9, 4, None), (6, 4, 9, None),
          (8, 12, 10, None), (2, 7, 6, None), (9, 6, 12, None), (5, 8, 7.5, None)]

def bloque_I():
    out = []
    for ad, db, ae, _ in I_PARS:
        ec = ae * db / ad
        fig = svg_tales(f'{num(ad)}', f'{num(db)}', f'{num(ae)}', 'x', 'EC')
        pasos = [
            'Como $DE \\parallel BC$, el triángulo $ADE$ es semejante al $ABC$ '
            '(teorema de Tales), así que los segmentos que quedan sobre los dos lados '
            'son proporcionales:',
            f'$$\\frac{{AD}}{{DB}} = \\frac{{AE}}{{EC}}$$',
            f'$$\\frac{{{num(ad)}}}{{{num(db)}}} = \\frac{{{num(ae)}}}{{x}}$$',
            f'Multiplica en cruz: $${num(ad)}\\,x = {num(db)} \\times {num(ae)} = '
            f'{num(db*ae)}$$',
            f'$$x = {num(ec, 3)}$$',
        ]
        out.append(ej(f'En el triángulo $ABC$ el segmento $DE$ es paralelo a $BC$. Si '
                      f'$AD = {num(ad)}$, $DB = {num(db)}$ y $AE = {num(ae)}$, determina '
                      f'el valor de $x = EC$.', pasos, f'$x = {num(ec, 3)}$', fig))
    return out

# ── J. Polígonos regulares ──────────────────────────────────────────────────
def bloque_J():
    out = []
    for n in J_LADOS:
        i = 180 * (n - 2) / n
        pasos = [
            'La suma de los ángulos internos de un polígono de $n$ lados es '
            '$180^\\circ(n-2)$. Como el polígono es regular, todos miden lo mismo:',
            f'$$i = \\frac{{180^\\circ({n} - 2)}}{{{n}}} = '
            f'\\frac{{180^\\circ \\times {n-2}}}{{{n}}} = {num(i, 2)}^\\circ$$',
        ]
        out.append(ej(f'Determina el valor del ángulo interno de un polígono regular de '
                      f'{n} lados.', pasos, f'${num(i, 2)}^\\circ$'))
    for i in J_ANGULOS:
        n = 360 / (180 - i)
        pasos = [
            'Parte del ángulo interno y despeja $n$:',
            f'$$\\frac{{180^\\circ(n-2)}}{{n}} = {i}^\\circ$$',
            f'$$180n - 360 = {i}n \\quad\\Rightarrow\\quad {180-i}n = 360$$',
            f'$$n = \\frac{{360}}{{{180-i}}} = {num(n)}$$',
            f'Atajo: el ángulo **externo** mide $180^\\circ - {i}^\\circ = {180-i}^\\circ$, '
            f'y como todos los externos suman $360^\\circ$, hay $360 \\div {180-i} = '
            f'{num(n)}$ lados.',
        ]
        out.append(ej(f'Calcula analíticamente el número de lados del polígono regular '
                      f'cuyos ángulos internos miden ${i}^\\circ$.', pasos,
                      f'$n = {num(n)}$ lados'))
    for D in J_DIAGONALES:
        n = (3 + math.sqrt(9 + 8 * D)) / 2
        pasos = [
            'El número total de diagonales de un polígono de $n$ lados es:',
            f'$$D = \\frac{{n(n-3)}}{{2}} = {D}$$',
            f'$$n^2 - 3n - {2*D} = 0$$',
            f'Con la fórmula general: $n = \\dfrac{{3 + \\sqrt{{9 + {8*D}}}}}{{2}} = '
            f'\\dfrac{{3 + {num(math.sqrt(9+8*D))}}}{{2}} = {num(n)}$',
            '(La raíz negativa se descarta: no existe un polígono con un número negativo '
            'de lados.)',
        ]
        out.append(ej(f'Calcula el número de lados del polígono regular que tiene {D} '
                      f'diagonales en total.', pasos, f'$n = {num(n)}$ lados'))
    return out

# ── K. Ángulos de elevación y depresión ─────────────────────────────────────
K_PARS = [
    ('altura', 'El ángulo de elevación desde un punto del suelo hasta la cima de una '
     'torre es de ${A}^\\circ$. Si la distancia horizontal al pie de la torre es de {d} m, '
     '¿cuál es la altura de la torre?', 30, 40),
    ('altura', 'A una distancia de {d} m de la base de un árbol, la punta se observa bajo '
     'un ángulo de ${A}^\\circ$. Calcula la altura del árbol.', 23, 10),
    ('altura', 'Ana está a {d} m de la base de una antena y observa su parte más alta con '
     'un ángulo de elevación de ${A}^\\circ$. ¿Qué altura tiene la antena?', 60, 4),
    ('altura', 'Desde {d} m de la base de un edificio, su azotea se ve con un ángulo de '
     'elevación de ${A}^\\circ$. ¿Cuánto mide el edificio?', 52, 25),
    ('distancia', 'Una torre mide {h} m de alto y su punta se observa con un ángulo de '
     'elevación de ${A}^\\circ$. ¿A qué distancia horizontal está el observador?', 38, 60),
    ('distancia', 'Desde lo alto de un faro de {h} m se ve un barco con un ángulo de '
     'depresión de ${A}^\\circ$. ¿A qué distancia del faro está el barco?', 27, 45),
    ('angulo', 'Determina el ángulo de elevación del sol en el momento en que un poste de '
     '{h} m proyecta una sombra de {d} m.', None, None),
    ('angulo', 'Una rampa sube {h} m a lo largo de una base horizontal de {d} m. ¿Qué '
     'ángulo forma la rampa con el piso?', None, None),
    ('angulo', 'Un cometa está a {h} m de altura y el hilo, tenso, toca el suelo a {d} m '
     'del punto justo debajo del cometa. ¿Qué ángulo forma el hilo con el suelo?',
     None, None),
]
K_ANG = [(3, 1.8), (1.5, 6), (48, 36)]

def bloque_K():
    out = []
    for tipo, plantilla, A, v in K_PARS:
        if tipo == 'altura':
            h = v * math.tan(math.radians(A))
            pasos = [
                'Haz el dibujo: la altura es el cateto **opuesto** al ángulo y la '
                'distancia al pie es el cateto **adyacente**. Eso pide tangente:',
                f'$$\\tan {A}^\\circ = \\frac{{h}}{{{num(v)}}}$$',
                f'$$h = {num(v)} \\tan {A}^\\circ = {num(v)}({num(math.tan(math.radians(A)), 4)}) '
                f'= {num(h, 3)}$$',
            ]
            out.append(ej(plantilla.format(A=A, d=num(v)), pasos, f'${num(h, 3)}$ m'))
        elif tipo == 'distancia':
            d = v / math.tan(math.radians(A))
            pasos = [
                'La altura es el cateto opuesto y la distancia el adyacente, así que otra '
                'vez es tangente, pero ahora despejas el denominador:',
                f'$$\\tan {A}^\\circ = \\frac{{{num(v)}}}{{d}} \\quad\\Rightarrow\\quad '
                f'd = \\frac{{{num(v)}}}{{\\tan {A}^\\circ}}$$',
                f'$$d = \\frac{{{num(v)}}}{{{num(math.tan(math.radians(A)), 4)}}} = '
                f'{num(d, 3)}$$',
            ]
            out.append(ej(plantilla.format(A=A, h=num(v)), pasos, f'${num(d, 3)}$ m'))
    for h, d in K_ANG:
        ang = math.degrees(math.atan(h / d))
        idx = [i for i, k in enumerate(K_PARS) if k[0] == 'angulo'][K_ANG.index((h, d))]
        pasos = [
            'Conoces los dos catetos, así que usa tangente y despeja el ángulo con la '
            'función inversa:',
            f'$$\\tan \\theta = \\frac{{{num(h)}}}{{{num(d)}}} = {num(h/d, 4)}$$',
            f'$$\\theta = \\tan^{{-1}}({num(h/d, 4)}) = {num(ang, 2)}^\\circ = {gms(ang)}$$',
        ]
        out.append(ej(K_PARS[idx][1].format(h=num(h), d=num(d)), pasos,
                      f'${num(ang, 2)}^\\circ \\approx {gms(ang)}$'))
    return out

# ── L. Escaleras y planos inclinados ────────────────────────────────────────
L_PARS = [('angulo', 20.4, 4.75, 'pies'), ('angulo', 5, 1.4, 'm'),
          ('altura', 6, 60, 'm'), ('altura', 8.5, 55, 'm'),
          ('longitud', 4.2, 65, 'm'), ('angulo', 12, 3.6, 'm')]

def bloque_L():
    out = []
    for tipo, L, v, u in L_PARS:
        if tipo == 'angulo':
            ang = math.degrees(math.acos(v / L))
            alt = math.sqrt(L*L - v*v)
            pasos = [
                'La escalera es la **hipotenusa** y la separación desde el muro es el '
                'cateto **adyacente** al ángulo del piso. Eso es coseno:',
                f'$$\\cos \\theta = \\frac{{{num(v)}}}{{{num(L)}}} = {num(v/L, 4)}$$',
                f'$$\\theta = \\cos^{{-1}}({num(v/L, 4)}) = {num(ang, 2)}^\\circ$$',
                f'De paso, por Pitágoras la escalera llega a $\\sqrt{{{num(L)}^2 - '
                f'{num(v)}^2}} = {num(alt, 3)}$ {u} de altura.',
            ]
            out.append(ej(f'Se coloca una escalera de {num(L)} {u} contra un edificio de '
                          f'modo que el extremo inferior queda a {num(v)} {u} de la base. '
                          f'¿Qué ángulo forma la escalera con el piso?', pasos,
                          f'${num(ang, 2)}^\\circ$'))
        elif tipo == 'altura':
            h = L * math.sin(math.radians(v))
            pasos = [
                'La altura del muro es el cateto **opuesto** al ángulo y la escalera es la '
                'hipotenusa: eso es seno.',
                f'$$\\mathrm{{sen}}\\, {v}^\\circ = \\frac{{h}}{{{num(L)}}}$$',
                f'$$h = {num(L)}\\,\\mathrm{{sen}}\\, {v}^\\circ = '
                f'{num(L)}({num(math.sin(math.radians(v)), 4)}) = {num(h, 3)}$$',
            ]
            out.append(ej(f'Una escalera de {num(L)} {u} se recarga sobre la parte '
                          f'superior de un muro vertical formando con la banqueta un '
                          f'ángulo de ${v}^\\circ$. Determina la altura del muro.', pasos,
                          f'${num(h, 3)}$ {u}'))
        else:
            Lg = L / math.sin(math.radians(v))
            pasos = [
                'La altura es el cateto opuesto y la escalera la hipotenusa; despeja la '
                'hipotenusa:',
                f'$$\\mathrm{{sen}}\\, {v}^\\circ = \\frac{{{num(L)}}}{{L}} '
                f'\\quad\\Rightarrow\\quad L = \\frac{{{num(L)}}}{{\\mathrm{{sen}}\\, {v}^\\circ}}$$',
                f'$$L = \\frac{{{num(L)}}}{{{num(math.sin(math.radians(v)), 4)}}} = '
                f'{num(Lg, 3)}$$',
            ]
            out.append(ej(f'¿Qué longitud debe tener una escalera para alcanzar una '
                          f'ventana a {num(L)} {u} de altura si debe formar un ángulo de '
                          f'${v}^\\circ$ con el piso?', pasos, f'${num(Lg, 3)}$ {u}'))
    return out

# ── M. Doble observación (dos ángulos de elevación) ─────────────────────────
M_PARS = [(30, 45, 50), (25, 40, 80), (32, 58, 45), (20, 35, 120),
          (28, 47, 65), (35, 50, 30)]

def bloque_M():
    out = []
    for a1, a2, d in M_PARS:
        t1, t2 = math.tan(math.radians(a1)), math.tan(math.radians(a2))
        # h = d / (1/t1 - 1/t2)
        x = d * t1 / (t2 - t1)          # distancia que le falta desde el 2º punto
        h = x * t2
        pasos = [
            'Llama $x$ a la distancia que **falta** desde el segundo punto hasta la base, '
            'y $h$ a la altura. Se arman dos triángulos rectángulos con la misma altura:',
            f'$$\\tan {a2}^\\circ = \\frac{{h}}{{x}} \\qquad '
            f'\\tan {a1}^\\circ = \\frac{{h}}{{x + {d}}}$$',
            'Despeja $h$ en las dos e iguala:',
            f'$$x\\tan {a2}^\\circ = (x + {d})\\tan {a1}^\\circ$$',
            f'$$x({num(t2, 4)} - {num(t1, 4)}) = {d}({num(t1, 4)}) '
            f'\\quad\\Rightarrow\\quad x = {num(x, 3)}$$',
            f'Y la altura: $h = {num(x, 3)} \\tan {a2}^\\circ = {num(h, 3)}$.',
        ]
        out.append(ej(f'Una persona observa la punta de una torre con un ángulo de '
                      f'elevación de ${a1}^\\circ$; se acerca {d} m hacia la torre y ahora '
                      f'la observa con ${a2}^\\circ$. Determina la altura de la torre y la '
                      f'distancia que le faltaría caminar para llegar a la base.', pasos,
                      f'falta caminar ${num(x, 3)}$ m; altura $= {num(h, 3)}$ m'))
    return out

# ── N. Ley de senos ─────────────────────────────────────────────────────────
N_PARS = [(8, 50, 70), (15, 42, 76), (24, 35, 65), (12, 105, 30),
          (30, 48, 62), (18, 27, 98), (9.5, 61, 44), (40, 33, 87)]

def bloque_N():
    out = []
    for a, B, C in N_PARS:
        A = 180 - B - C
        b = a * math.sin(math.radians(B)) / math.sin(math.radians(A))
        c = a * math.sin(math.radians(C)) / math.sin(math.radians(A))
        pasos = [
            f'Primero saca el ángulo que falta: $A = 180^\\circ - {B}^\\circ - {C}^\\circ '
            f'= {num(A)}^\\circ$.',
            'Ahora la ley de senos, que relaciona cada lado con el seno de su ángulo '
            'opuesto:',
            f'$$\\frac{{a}}{{\\mathrm{{sen}}\\,A}} = \\frac{{b}}{{\\mathrm{{sen}}\\,B}} = '
            f'\\frac{{c}}{{\\mathrm{{sen}}\\,C}}$$',
            f'$$b = \\frac{{a\\,\\mathrm{{sen}}\\,B}}{{\\mathrm{{sen}}\\,A}} = '
            f'\\frac{{{num(a)}\\,\\mathrm{{sen}}\\,{B}^\\circ}}{{\\mathrm{{sen}}\\,{num(A)}^\\circ}} '
            f'= {num(b, 3)}$$',
            f'$$c = \\frac{{a\\,\\mathrm{{sen}}\\,C}}{{\\mathrm{{sen}}\\,A}} = {num(c, 3)}$$',
        ]
        out.append(ej(f'En un triángulo se sabe que $a = {num(a)}$, $B = {B}^\\circ$ y '
                      f'$C = {C}^\\circ$. Determina el ángulo $A$ y los lados $b$ y $c$.',
                      pasos, f'$A = {num(A)}^\\circ$, $b = {num(b, 3)}$, $c = {num(c, 3)}$'))
    return out

# ── O. Ley de cosenos ───────────────────────────────────────────────────────
O_LADO = [(225, 300, 74 + 23/60, 'Dos aviones parten de una ciudad y sus direcciones '
           'forman un ángulo de ${A}$. Después de una hora uno está a {b} km de la ciudad '
           'y el otro a {c} km. ¿Cuál es la distancia entre ambos aviones?'),
          (18, 25, 47, 'Dos caminos salen de un mismo punto formando un ángulo de '
           '${A}^\\circ$. Un pueblo está a {b} km por el primero y otro a {c} km por el '
           'segundo. ¿Qué distancia hay entre los dos pueblos?'),
          (40, 32, 118, 'Un terreno triangular tiene dos lados de {b} m y {c} m que '
           'forman un ángulo de ${A}^\\circ$. ¿Cuánto mide el tercer lado?'),
          (7.5, 11, 63, 'Dos barcos salen del puerto con rumbos que forman ${A}^\\circ$. '
           'Uno navega {b} km y el otro {c} km. ¿A qué distancia quedan uno del otro?')]
O_ANG = [(41, 19.5, 32.48), (7, 20, 14), (50, 45, 32), (12, 15, 9), (26, 18, 31)]

def bloque_O():
    out = []
    for b, c, A, plantilla in O_LADO:
        a = math.sqrt(b*b + c*c - 2*b*c*math.cos(math.radians(A)))
        txt = plantilla.format(A=(gms(A) if A != int(A) else num(A)), b=num(b), c=num(c))
        pasos = [
            'Conoces dos lados y el ángulo **entre** ellos: ése es el caso de la ley de '
            'cosenos.',
            '$$a^2 = b^2 + c^2 - 2bc\\cos A$$',
            f'$$a^2 = {num(b)}^2 + {num(c)}^2 - 2({num(b)})({num(c)})'
            f'\\cos {num(A, 4)}^\\circ$$',
            f'$$a^2 = {num(b*b + c*c)} - {num(2*b*c, 2)}({num(math.cos(math.radians(A)), 4)}) '
            f'= {num(a*a, 3)}$$',
            f'$$a = {num(a, 3)}$$',
        ]
        out.append(ej(txt, pasos, f'${num(a, 3)}$'))
    for a, b, c in O_ANG:
        cosA = (b*b + c*c - a*a) / (2*b*c)
        A = math.degrees(math.acos(cosA))
        pasos = [
            'Conoces los tres lados, así que despeja el coseno del ángulo que te piden:',
            '$$a^2 = b^2 + c^2 - 2bc\\cos A \\quad\\Rightarrow\\quad '
            '\\cos A = \\frac{b^2 + c^2 - a^2}{2bc}$$',
            f'$$\\cos A = \\frac{{{num(b)}^2 + {num(c)}^2 - {num(a)}^2}}'
            f'{{2({num(b)})({num(c)})}} = {num(cosA, 4)}$$',
            f'$$A = \\cos^{{-1}}({num(cosA, 4)}) = {num(A, 2)}^\\circ$$',
            f'En sistema circular: $A = {num(A, 2)}^\\circ \\times '
            f'\\dfrac{{\\pi}}{{180^\\circ}} = {num(math.radians(A), 4)}$ rad.',
        ]
        out.append(ej(f'Un triángulo oblicuángulo tiene lados $a = {num(a)}$, '
                      f'$b = {num(b)}$ y $c = {num(c)}$. Calcula el ángulo $A$ (el opuesto '
                      f'al lado $a$) en grados y en radianes.', pasos,
                      f'$A = {num(A, 2)}^\\circ = {num(math.radians(A), 4)}$ rad'))
    return out

# ── P. Funciones trigonométricas restantes ──────────────────────────────────
P_PARS = [('sen', 2, 3), ('sen', 0.13, 1), ('cos', 5, 13), ('sen', 3, 5),
          ('cos', 8, 17), ('tan', 3, 4), ('sen', 7, 25), ('cos', 12, 13),
          ('tan', 5, 12), ('sen', 1, 2)]

def bloque_P():
    out = []
    for f, p, q in P_PARS:
        v = p / q
        if f == 'sen':
            sen = v; cos = math.sqrt(1 - v*v)
        elif f == 'cos':
            cos = v; sen = math.sqrt(1 - v*v)
        else:
            tan = v; cos = 1/math.sqrt(1 + v*v); sen = tan*cos
        tan = sen / cos
        ang = math.degrees(math.asin(sen))
        dado = f'\\frac{{{num(p)}}}{{{num(q)}}}' if q != 1 else num(p)
        nombre = {'sen': '\\mathrm{sen}', 'cos': '\\cos', 'tan': '\\tan'}[f]
        pasos = [
            'Dibuja el triángulo rectángulo que corresponde al dato y saca el lado que '
            'falta con Pitágoras; de ahí salen todas las demás razones.',
            f'$$\\mathrm{{sen}}\\,\\alpha = {num(sen, 4)} \\qquad '
            f'\\cos\\alpha = {num(cos, 4)} \\qquad \\tan\\alpha = {num(tan, 4)}$$',
            'Las tres restantes son las recíprocas:',
            f'$$\\csc\\alpha = \\frac{{1}}{{\\mathrm{{sen}}\\,\\alpha}} = {num(1/sen, 4)} '
            f'\\qquad \\sec\\alpha = \\frac{{1}}{{\\cos\\alpha}} = {num(1/cos, 4)} '
            f'\\qquad \\cot\\alpha = \\frac{{1}}{{\\tan\\alpha}} = {num(1/tan, 4)}$$',
            f'El ángulo sale con la inversa: $\\alpha = \\mathrm{{sen}}^{{-1}}'
            f'({num(sen, 4)}) = {num(ang, 2)}^\\circ = {gms(ang)}$.',
        ]
        out.append(ej(f'Sabiendo que ${nombre}\\,\\alpha = {dado}$ y que $\\alpha$ es un '
                      f'ángulo agudo, calcula las cinco funciones trigonométricas '
                      f'restantes y el valor del ángulo.', pasos,
                      f'$\\mathrm{{sen}} = {num(sen, 4)}$, $\\cos = {num(cos, 4)}$, '
                      f'$\\tan = {num(tan, 4)}$, $\\csc = {num(1/sen, 4)}$, '
                      f'$\\sec = {num(1/cos, 4)}$, $\\cot = {num(1/tan, 4)}$; '
                      f'$\\alpha = {num(ang, 2)}^\\circ$'))
    return out

# ── Q. Ecuaciones trigonométricas ───────────────────────────────────────────
def _sols_sen(v):
    """Soluciones en [0°,360°) de sen θ = v."""
    if abs(v) > 1: return []
    a = math.degrees(math.asin(v))
    s = sorted({round(a % 360, 4), round((180 - a) % 360, 4)})
    return s

def _sols_cos(v):
    if abs(v) > 1: return []
    a = math.degrees(math.acos(v))
    return sorted({round(a % 360, 4), round((360 - a) % 360, 4)})

def _sols_tan(v):
    a = math.degrees(math.atan(v))
    return sorted({round(a % 360, 4), round((a + 180) % 360, 4)})

def bloque_Q():
    out = []
    # Q1: lineales   a·f(θ) + b = 0
    for f, a, b in Q1_PARS:
        v = -b / a
        sols = {'sen': _sols_sen, 'cos': _sols_cos, 'tan': _sols_tan}[f](v)
        nombre = {'sen': '\\mathrm{sen}', 'cos': '\\cos', 'tan': '\\tan'}[f]
        bt = num(b, 4) if abs(b - round(b)) > 1e-9 else num(b)
        izq = f'{a if a != 1 else ""}{nombre}\\,\\theta {"+" if b >= 0 else "-"} {bt.lstrip("-")}'
        pasos = [
            'Despeja la función trigonométrica:',
            f'$${nombre}\\,\\theta = {num(v, 4)}$$',
            f'Busca **todos** los ángulos del intervalo $[0^\\circ, 360^\\circ)$ que la '
            f'cumplen, no solo el que da la calculadora:',
            '$$\\theta = ' + ',\\quad '.join(f'{num(s, 2)}^\\circ' for s in sols) + '$$',
        ]
        out.append(ej(f'Resuelve la ecuación trigonométrica $${izq} = 0$$ '
                      f'para $0^\\circ \\le \\theta < 360^\\circ$.', pasos,
                      '$\\theta = ' + ',\\ '.join(f'{num(s, 2)}^\\circ' for s in sols) + '$'))
    # Q2: factorizables   a·f²(θ) + b·f(θ) = 0
    for f, a, b in Q2_PARS:
        nombre = {'sen': '\\mathrm{sen}', 'cos': '\\cos', 'tan': '\\tan'}[f]
        fn = {'sen': _sols_sen, 'cos': _sols_cos, 'tan': _sols_tan}[f]
        sols = sorted(set(fn(0) + fn(-b / a)))
        pasos = [
            f'No dividas entre ${nombre}\\,\\theta$: perderías soluciones. **Factoriza**:',
            f'$${nombre}\\,\\theta\\,({a}\\,{nombre}\\,\\theta {"+" if b >= 0 else "-"} '
            f'{abs(b)}) = 0$$',
            'Un producto es cero cuando alguno de sus factores lo es, así que hay dos '
            'casos:',
            f'$${nombre}\\,\\theta = 0 \\qquad\\text{{o}}\\qquad '
            f'{nombre}\\,\\theta = {num(-b/a, 4)}$$',
            '$$\\theta = ' + ',\\quad '.join(f'{num(s, 2)}^\\circ' for s in sols) + '$$',
        ]
        out.append(ej(f'Resuelve la ecuación trigonométrica '
                      f'$${a}\\,{nombre}^2\\theta {"+" if b >= 0 else "-"} {abs(b)}\\,'
                      f'{nombre}\\,\\theta = 0$$ para '
                      f'$0^\\circ \\le \\theta < 360^\\circ$.', pasos,
                      '$\\theta = ' + ',\\ '.join(f'{num(s, 2)}^\\circ' for s in sols) + '$'))
    # Q3: cuadráticas factorizables   a·f² + b·f + c = 0
    for f, a, b, c in Q3_PARS:
        nombre = {'sen': '\\mathrm{sen}', 'cos': '\\cos', 'tan': '\\tan'}[f]
        fn = {'sen': _sols_sen, 'cos': _sols_cos}[f]
        d = b*b - 4*a*c
        r1, r2 = (-b + math.sqrt(d)) / (2*a), (-b - math.sqrt(d)) / (2*a)
        sols = sorted(set(fn(r1) + fn(r2)))
        desc = [r for r in (r1, r2) if abs(r) > 1]
        pasos = [
            f'Trátala como una ecuación de segundo grado en ${nombre}\\,\\theta$. Con la '
            'fórmula general:',
            f'$${nombre}\\,\\theta = {num(r1, 4)} \\qquad\\text{{o}}\\qquad '
            f'{nombre}\\,\\theta = {num(r2, 4)}$$',
        ]
        if desc:
            pasos.append(f'Descarta ${nombre}\\,\\theta = {num(desc[0], 4)}$: el seno y el '
                         'coseno nunca salen del intervalo $[-1, 1]$.')
        pasos.append('Los ángulos que quedan en $[0^\\circ, 360^\\circ)$ son:')
        pasos.append('$$\\theta = ' + ',\\quad '.join(f'{num(s, 2)}^\\circ' for s in sols) + '$$')
        out.append(ej(f'Resuelve la ecuación trigonométrica '
                      f'$${a}\\,{nombre}^2\\theta {"+" if b >= 0 else "-"} {abs(b)}\\,'
                      f'{nombre}\\,\\theta {"+" if c >= 0 else "-"} {abs(c)} = 0$$ para '
                      f'$0^\\circ \\le \\theta < 360^\\circ$.', pasos,
                      '$\\theta = ' + ',\\ '.join(f'{num(s, 2)}^\\circ' for s in sols) + '$'))
    return out

# ── R. Identidades trigonométricas ──────────────────────────────────────────
R_IDS = [
    ('\\frac{1}{1 + \\cot^2\\theta} = \\mathrm{sen}^2\\theta',
     ['Parte del lado izquierdo y usa la identidad pitagórica $1 + \\cot^2\\theta = '
      '\\csc^2\\theta$:',
      '$$\\frac{1}{1 + \\cot^2\\theta} = \\frac{1}{\\csc^2\\theta}$$',
      'Y como $\\csc\\theta$ es el recíproco de $\\mathrm{sen}\\,\\theta$:',
      '$$\\frac{1}{\\csc^2\\theta} = \\mathrm{sen}^2\\theta \\quad\\blacksquare$$']),
    ('\\frac{\\tan\\theta \\cos\\theta}{\\mathrm{sen}\\,\\theta} = \\sec\\theta\\cot\\theta',
     ['Trabaja cada lado por separado. En el izquierdo sustituye '
      '$\\tan\\theta = \\dfrac{\\mathrm{sen}\\,\\theta}{\\cos\\theta}$:',
      '$$\\frac{\\frac{\\mathrm{sen}\\,\\theta}{\\cos\\theta}\\cos\\theta}'
      '{\\mathrm{sen}\\,\\theta} = \\frac{\\mathrm{sen}\\,\\theta}{\\mathrm{sen}\\,\\theta} = 1$$',
      'En el derecho, escribe todo en senos y cosenos:',
      '$$\\sec\\theta\\cot\\theta = \\frac{1}{\\cos\\theta}\\cdot'
      '\\frac{\\cos\\theta}{\\mathrm{sen}\\,\\theta} = \\frac{1}{\\mathrm{sen}\\,\\theta} '
      '= \\csc\\theta$$',
      'Ojo: los dos lados **no** coinciden. Tal como está escrita, la igualdad solo se '
      'cumple si $\\csc\\theta = 1$, o sea $\\theta = 90^\\circ$. La identidad correcta '
      'sería $\\dfrac{\\tan\\theta\\cos\\theta}{\\mathrm{sen}\\,\\theta} = 1$. Este '
      'reactivo aparece así en los ETS de 2019 y 2025: si te lo ponen, demuestra que el '
      'lado izquierdo vale 1 y señala la discrepancia.']),
    ('(1 + \\cos\\theta)(1 - \\cos\\theta) = \\mathrm{sen}^2\\theta',
     ['El lado izquierdo es una diferencia de cuadrados:',
      '$$(1 + \\cos\\theta)(1 - \\cos\\theta) = 1 - \\cos^2\\theta$$',
      'Y de la identidad pitagórica $\\mathrm{sen}^2\\theta + \\cos^2\\theta = 1$ se '
      'despeja $1 - \\cos^2\\theta = \\mathrm{sen}^2\\theta$. $\\blacksquare$']),
    ('\\sec\\theta - \\cos\\theta = \\mathrm{sen}\\,\\theta\\tan\\theta',
     ['Escribe $\\sec\\theta$ como recíproco y saca común denominador:',
      '$$\\frac{1}{\\cos\\theta} - \\cos\\theta = \\frac{1 - \\cos^2\\theta}{\\cos\\theta}$$',
      'El numerador es $\\mathrm{sen}^2\\theta$:',
      '$$\\frac{\\mathrm{sen}^2\\theta}{\\cos\\theta} = \\mathrm{sen}\\,\\theta\\cdot'
      '\\frac{\\mathrm{sen}\\,\\theta}{\\cos\\theta} = \\mathrm{sen}\\,\\theta\\tan\\theta '
      '\\quad\\blacksquare$$']),
    ('\\frac{\\cos\\theta}{1 - \\mathrm{sen}\\,\\theta} = \\sec\\theta + \\tan\\theta',
     ['Multiplica arriba y abajo por el conjugado $1 + \\mathrm{sen}\\,\\theta$:',
      '$$\\frac{\\cos\\theta(1 + \\mathrm{sen}\\,\\theta)}{(1 - \\mathrm{sen}\\,\\theta)'
      '(1 + \\mathrm{sen}\\,\\theta)} = \\frac{\\cos\\theta(1 + \\mathrm{sen}\\,\\theta)}'
      '{1 - \\mathrm{sen}^2\\theta}$$',
      'El denominador es $\\cos^2\\theta$, así que se cancela un coseno:',
      '$$\\frac{1 + \\mathrm{sen}\\,\\theta}{\\cos\\theta} = \\frac{1}{\\cos\\theta} + '
      '\\frac{\\mathrm{sen}\\,\\theta}{\\cos\\theta} = \\sec\\theta + \\tan\\theta '
      '\\quad\\blacksquare$$']),
    ('\\cot\\theta\\,\\mathrm{sen}\\,\\theta = \\cos\\theta',
     ['Sustituye la cotangente por su cociente:',
      '$$\\frac{\\cos\\theta}{\\mathrm{sen}\\,\\theta}\\cdot\\mathrm{sen}\\,\\theta = '
      '\\cos\\theta \\quad\\blacksquare$$']),
    ('\\frac{\\mathrm{sen}\\,\\theta}{\\csc\\theta} + \\frac{\\cos\\theta}{\\sec\\theta} = 1',
     ['Dividir entre un recíproco es multiplicar:',
      '$$\\frac{\\mathrm{sen}\\,\\theta}{\\frac{1}{\\mathrm{sen}\\,\\theta}} + '
      '\\frac{\\cos\\theta}{\\frac{1}{\\cos\\theta}} = \\mathrm{sen}^2\\theta + \\cos^2\\theta$$',
      'Que por la identidad pitagórica vale 1. $\\blacksquare$']),
    ('\\tan^2\\theta - \\mathrm{sen}^2\\theta = \\tan^2\\theta\\,\\mathrm{sen}^2\\theta',
     ['Factoriza $\\tan^2\\theta$ en el lado derecho… mejor empieza por el izquierdo '
      'escribiendo la tangente como cociente:',
      '$$\\frac{\\mathrm{sen}^2\\theta}{\\cos^2\\theta} - \\mathrm{sen}^2\\theta = '
      '\\mathrm{sen}^2\\theta\\left(\\frac{1}{\\cos^2\\theta} - 1\\right)$$',
      '$$= \\mathrm{sen}^2\\theta\\cdot\\frac{1 - \\cos^2\\theta}{\\cos^2\\theta} = '
      '\\mathrm{sen}^2\\theta\\cdot\\frac{\\mathrm{sen}^2\\theta}{\\cos^2\\theta} = '
      '\\mathrm{sen}^2\\theta\\tan^2\\theta \\quad\\blacksquare$$']),
    ('\\frac{1 + \\tan^2\\theta}{\\csc^2\\theta} = \\tan^2\\theta',
     ['El numerador es la identidad pitagórica $1 + \\tan^2\\theta = \\sec^2\\theta$:',
      '$$\\frac{\\sec^2\\theta}{\\csc^2\\theta} = \\frac{\\frac{1}{\\cos^2\\theta}}'
      '{\\frac{1}{\\mathrm{sen}^2\\theta}} = \\frac{\\mathrm{sen}^2\\theta}{\\cos^2\\theta} '
      '= \\tan^2\\theta \\quad\\blacksquare$$']),
    ('\\csc\\theta - \\mathrm{sen}\\,\\theta = \\cos\\theta\\cot\\theta',
     ['Igual que en la de secante: recíproco y común denominador.',
      '$$\\frac{1}{\\mathrm{sen}\\,\\theta} - \\mathrm{sen}\\,\\theta = '
      '\\frac{1 - \\mathrm{sen}^2\\theta}{\\mathrm{sen}\\,\\theta} = '
      '\\frac{\\cos^2\\theta}{\\mathrm{sen}\\,\\theta}$$',
      '$$= \\cos\\theta\\cdot\\frac{\\cos\\theta}{\\mathrm{sen}\\,\\theta} = '
      '\\cos\\theta\\cot\\theta \\quad\\blacksquare$$']),
]

def bloque_R():
    return [ej(f'Demuestra la identidad $${idn}$$', pasos, 'Ver el desarrollo.')
            for idn, pasos in R_IDS]

# ── S. Área, perímetro y costo con expresiones algebraicas ──────────────────
def bloque_S():
    out = []
    for largo, alto, precio in S_COSTO:
        area = largo * alto
        total = area * precio
        pasos = [
            f'Primero el área de la pared: $A = {num(largo)} \\times {num(alto)} = '
            f'{num(area)}\\ \\mathrm{{m}}^2$.',
            f'Después multiplica por el precio por metro cuadrado:',
            f'$${num(area)} \\times \\$ {num(precio)} = \\$ {num(total, 2)}$$',
        ]
        out.append(ej(f'Una pared rectangular ha de ser pintada. Mide {num(largo)} m de '
                      f'largo y {num(alto)} m de alto, y quien la pinte cobra '
                      f'$\\${num(precio)}$ por $\\mathrm{{m}}^2$. Determina el monto a '
                      f'pagar.', pasos, f'$\\${num(total, 2)}$'))
    for a, b, diag in S_DIAG:
        # (y+a)² + (y+b)² = diag²
        A_, B_, C_ = 2, 2*(a+b), a*a + b*b - diag*diag
        d = B_*B_ - 4*A_*C_
        y = (-B_ + math.sqrt(d)) / (2*A_)
        L, W_ = y + a, y + b
        per = 2*(L + W_)
        pasos = [
            'La diagonal de un rectángulo lo parte en dos triángulos rectángulos, así que '
            'aplica Pitágoras con los dos lados:',
            f'$$({lin(1, a, "y")})^2 + ({lin(1, b, "y")})^2 = {diag}^2$$',
            f'$$2y^2 {"+" if B_ >= 0 else "-"} {abs(B_)}y {"+" if C_ >= 0 else "-"} '
            f'{abs(C_)} = 0 \\quad\\Rightarrow\\quad y = {num(y)}$$',
            f'Los lados miden ${num(L)}$ y ${num(W_)}$, así que el perímetro es '
            f'$2({num(L)} + {num(W_)}) = {num(per)}$.',
        ]
        out.append(ej(f'Una alberca rectangular tiene de largo ${lin(1, a, "y")}$ y de '
                      f'ancho ${lin(1, b, "y")}$; su diagonal mide {diag} metros. ¿Qué '
                      f'valor numérico tiene el perímetro?', pasos,
                      f'$y = {num(y)}$; lados ${num(L)}$ y ${num(W_)}$; '
                      f'perímetro $= {num(per)}$'))
    return out

# ── índice de bloques ───────────────────────────────────────────────────────
BLOQUES = [
    ('A', 'Ecuaciones exponenciales de base común',
     'Cuando los dos lados se pueden escribir con la misma base, basta igualar los '
     'exponentes. Aparece en los ocho ETS.', bloque_A),
    ('B', 'Ecuaciones exponenciales con logaritmos',
     'Si las bases no se pueden igualar, se aplica logaritmo a los dos lados y se baja '
     'el exponente. ETS 2018, 2019 y 2023.', bloque_B),
    ('C', 'Ecuaciones logarítmicas',
     'Se juntan los logaritmos en uno solo con las propiedades y se pasa a la forma '
     'exponencial. Siempre hay que verificar que los argumentos queden positivos.', bloque_C),
    ('D', 'Modelos exponenciales aplicados',
     'La incógnita está en el exponente y se despeja con logaritmos. ETS 2009 y 2017.',
     bloque_D),
    ('E', 'Ángulos entre paralelas cortadas por una secante',
     'Alternos internos, alternos externos y correspondientes son iguales; los '
     'colaterales suman 180°. Aparece en los ocho ETS.', bloque_E),
    ('F', 'Ángulos internos y externos de un triángulo',
     'Los internos suman 180° y un externo vale la suma de los dos internos no '
     'adyacentes. ETS 2017 y 2023.', bloque_F),
    ('G', 'Triángulo rectángulo con lados en x',
     'Pitágoras con expresiones algebraicas, y de ahí el perímetro. Aparece en casi '
     'todos los ETS.', bloque_G),
    ('H', 'Semejanza: sombras, fotografías y escalas',
     'Dos triángulos semejantes tienen lados proporcionales. Aparece en los ocho ETS.',
     bloque_H),
    ('I', 'Segmento paralelo a un lado del triángulo',
     'Teorema de Tales. Es el reactivo de "hallar el valor de x" con figura.', bloque_I),
    ('J', 'Polígonos regulares',
     'Ángulo interno, ángulo externo y número de diagonales. Aparece en casi todos.',
     bloque_J),
    ('K', 'Ángulos de elevación y de depresión',
     'Un triángulo rectángulo y la razón que relacione lo que tienes con lo que buscas. '
     'Aparece en los ocho ETS.', bloque_K),
    ('L', 'Escaleras y planos inclinados',
     'La escalera es la hipotenusa; según el dato, toca seno, coseno o tangente.', bloque_L),
    ('M', 'Doble observación desde dos puntos',
     'Dos triángulos con la misma altura; se igualan las dos expresiones de la altura. '
     'ETS 2010.', bloque_M),
    ('N', 'Ley de senos',
     'Cuando conoces un lado y dos ángulos, o dos lados y el ángulo opuesto a uno de '
     'ellos. ETS 2018 y 2026.', bloque_N),
    ('O', 'Ley de cosenos',
     'Cuando conoces dos lados y el ángulo entre ellos, o los tres lados. ETS 2009, '
     '2019, 2023 y 2025.', bloque_O),
    ('P', 'Funciones trigonométricas restantes',
     'Con una razón se arma el triángulo, se saca el lado que falta con Pitágoras y de '
     'ahí salen todas. ETS 2009 y 2017.', bloque_P),
    ('Q', 'Ecuaciones trigonométricas',
     'Despejar, factorizar o resolver como cuadrática, y dar TODAS las soluciones del '
     'intervalo. Aparece en los ocho ETS.', bloque_Q),
    ('R', 'Identidades trigonométricas',
     'Se toma un lado y se transforma hasta llegar al otro, escribiendo todo en senos y '
     'cosenos. ETS 2019, 2025 y 2026.', bloque_R),
    ('S', 'Área, perímetro y costo',
     'Combina álgebra con geometría elemental. ETS 2009 y 2017.', bloque_S),
]

def construir():
    datos = []
    for clave, titulo, intro, fn in BLOQUES:
        datos.append({'clave': clave, 'titulo': titulo, 'intro': intro,
                      'ejercicios': fn()})
    return datos

if __name__ == '__main__':
    d = construir()
    tot = sum(len(b['ejercicios']) for b in d)
    for b in d:
        print(f"  {b['clave']}. {b['titulo']:52s} {len(b['ejercicios']):3d}")
    print(f'\n  {len(d)} bloques · {tot} ejercicios')
