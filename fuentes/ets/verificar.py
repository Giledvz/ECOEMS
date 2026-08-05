# Verifica el cuadernillo por un camino DISTINTO al que lo generó.
#
# generar.py despeja cada ejercicio con su fórmula; aquí se hace al revés: se toma el
# número que va a leer el alumno, se sustituye en la ecuación ORIGINAL y se comprueba
# que la cumpla (o se busca la raíz por bisección y se compara). Si las dos vías
# coinciden, el error tendría que estar en las dos a la vez y de la misma forma.
import math, re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import generar as G

TOL = 5e-3
fallos, revisados = [], 0

def nums(s):
    """Todos los números que aparecen en un texto (para leer la respuesta impresa)."""
    return [float(x) for x in re.findall(r'-?\d+\.?\d*', s.replace('^\\circ', ''))]

def check(nombre, ok, detalle=''):
    global revisados
    revisados += 1
    if not ok:
        fallos.append(f'{nombre}: {detalle}')

# ── A: sustituir x en b^(p(mx+n)) = b^(q(rx+s)) ────────────────────────────
for i, (b, p, m, n, q, r, s) in enumerate(G.A_PARS):
    x = nums(G.bloque_A()[i]['respuesta'])[0]
    izq, der = (b**p)**(m*x + n), (b**q)**(r*x + s)
    check(f'A{i+1}', abs(izq - der) / max(abs(izq), 1) < TOL,
          f'{izq:.6g} ≠ {der:.6g}')

# ── B: lo mismo con bases distintas ────────────────────────────────────────
for i, (b1, m, n, b2, r, s) in enumerate(G.B_PARS):
    x = nums(G.bloque_B()[i]['respuesta'])[0]
    izq, der = b1**(m*x + n), b2**(r*x + s)
    check(f'B{i+1}', abs(izq - der) / max(abs(izq), 1e-9) < 1e-2, f'{izq:.6g} ≠ {der:.6g}')

# ── C: sustituir en cada forma logarítmica ─────────────────────────────────
C = G.bloque_C()
k = 0
for b, m, n, kk in G.C1_PARS:
    x = nums(C[k]['respuesta'])[0]; k += 1
    check(f'C1.{k}', abs(math.log(m*x + n, b) - kk) < TOL)
for b, a, c, kk in G.C2_PARS:
    x = nums(C[k]['respuesta'])[0]; k += 1
    check(f'C2.{k}', abs(math.log(x + a, b) - math.log(x - c, b) - kk) < TOL)
for m, c in G.C3_PARS:
    x = nums(C[k]['respuesta'])[0]; k += 1
    check(f'C3.{k}', abs(math.log10(m*x) - math.log10(x + c)) < TOL)
for a, b_, c_, d, kk in G.C4_PARS:
    x = nums(C[k]['respuesta'])[0]; k += 1
    check(f'C4.{k}', abs(math.log10(a*x + b_) + math.log10(c_*x + d) - kk) < TOL,
          'no cumple la ecuación')
    check(f'C4.{k}-dom', a*x + b_ > 0 and c_*x + d > 0, 'argumento no positivo')

# ── D: N0·r^t debe dar la meta ─────────────────────────────────────────────
for i, (_, _, N0, r, meta) in enumerate(G.D_PARS):
    t = nums(G.bloque_D()[i]['respuesta'])[0]
    check(f'D{i+1}', abs(N0 * r**t - meta) / meta < 1e-2, f'{N0*r**t:.6g} ≠ {meta}')

# ── E: los ángulos deben cumplir la relación y el suplemento sumar 180 ─────
E = G.bloque_E()
for i, (tipo, a, b, c_, d) in enumerate(G.E_PARS):
    v = nums(E[i]['respuesta'])
    x, ang, sup = v[0], v[1], v[2]
    check(f'E{i+1}-igual', abs((a*x + b) - (c_*x + d)) < TOL, 'los ángulos no coinciden')
    check(f'E{i+1}-ang', abs((a*x + b) - ang) < 0.02)
    check(f'E{i+1}-sup', abs(ang + sup - 180) < 0.02)
for j, (tipo, a, b, c_, d) in enumerate(G.E_COLAT):
    v = nums(E[len(G.E_PARS) + j]['respuesta'])
    x, A, B = v[0], v[1], v[2]
    check(f'Ec{j+1}', abs((a*x + b) + (c_*x + d) - 180) < TOL, 'no suman 180°')
    check(f'Ec{j+1}-val', abs(A + B - 180) < 0.02)

# ── F: internos suman 180; externo = suma de los dos no adyacentes ─────────
F = G.bloque_F()
for i, (a1, b1, a2, b2, a3, b3) in enumerate(G.F_INT):
    v = nums(F[i]['respuesta'])
    x, A, B, C_ = v[0], v[1], v[2], v[3]
    check(f'F{i+1}-suma', abs(A + B + C_ - 180) < 0.05, f'suman {A+B+C_}')
    check(f'F{i+1}-expr', abs(a1*x + b1 - A) < 0.02)
for j, (ae, be, a2, b2, a3, b3) in enumerate(G.F_EXT):
    v = nums(F[len(G.F_INT) + j]['respuesta'])
    x, B, C_, A = v[0], v[1], v[2], v[3]
    check(f'Fe{j+1}-ext', abs((ae*x + be) - ((a2*x + b2) + (a3*x + b3))) < TOL)
    check(f'Fe{j+1}-suma', abs(A + B + C_ - 180) < 0.05, f'suman {A+B+C_}')

# ── G: los catetos deben cumplir Pitágoras y dar el perímetro ─────────────
G_ = G.bloque_G()
for i, (a, b, h) in enumerate(G.G_PARS):
    v = nums(G_[i]['respuesta'])
    x, c1, c2, per = v[0], v[1], v[2], v[3]
    check(f'G{i+1}-ent', abs(x - round(x)) < 1e-9, 'x no es entero')
    check(f'G{i+1}-pit', abs(c1*c1 + c2*c2 - h*h) < 1e-6, f'{c1}²+{c2}² ≠ {h}²')
    check(f'G{i+1}-expr', abs(x + a - c1) < 1e-9 and abs(x + b - c2) < 1e-9)
    check(f'G{i+1}-per', abs(c1 + c2 + h - per) < 1e-6)

# ── H: la proporción de semejanza ──────────────────────────────────────────
H = G.bloque_H()
for i, (_, h1, s1, s2) in enumerate(G.H_PARS):
    h2 = nums(H[i]['respuesta'])[0]
    check(f'H{i+1}', abs(h1/s1 - h2/s2) < 1e-3, f'{h1}/{s1} ≠ {h2}/{s2}')

# ── I: Tales ───────────────────────────────────────────────────────────────
I = G.bloque_I()
for i, (ad, db, ae, _) in enumerate(G.I_PARS):
    ec = nums(I[i]['respuesta'])[0]
    check(f'I{i+1}', abs(ad/db - ae/ec) < 1e-3)

# ── J: polígonos ───────────────────────────────────────────────────────────
J = G.bloque_J()
k = 0
for n in G.J_LADOS:
    ang = nums(J[k]['respuesta'])[0]; k += 1
    check(f'J1.{k}', abs(180*(n-2)/n - ang) < 0.02)
for ii in G.J_ANGULOS:
    n = nums(J[k]['respuesta'])[0]; k += 1
    check(f'J2.{k}', abs(180*(n-2)/n - ii) < 0.02, f'ángulo interno da {180*(n-2)/n}')
    check(f'J2.{k}-ent', abs(n - round(n)) < 1e-9, 'n no es entero')
for D in G.J_DIAGONALES:
    n = nums(J[k]['respuesta'])[0]; k += 1
    check(f'J3.{k}', abs(n*(n-3)/2 - D) < 1e-6, f'da {n*(n-3)/2} diagonales')
    check(f'J3.{k}-ent', abs(n - round(n)) < 1e-9, 'n no es entero')

# ── K y L: razones trigonométricas ─────────────────────────────────────────
K = G.bloque_K()
k = 0
for tipo, _, A, v in G.K_PARS:
    if tipo == 'altura':
        h = nums(K[k]['respuesta'])[0]; k += 1
        check(f'K{k}', abs(math.degrees(math.atan(h/v)) - A) < 0.05)
    elif tipo == 'distancia':
        d = nums(K[k]['respuesta'])[0]; k += 1
        check(f'K{k}', abs(math.degrees(math.atan(v/d)) - A) < 0.05)
for j, (h, d) in enumerate(G.K_ANG):
    ang = nums(K[k]['respuesta'])[0]; k += 1
    check(f'Ka{j+1}', abs(math.tan(math.radians(ang)) - h/d) < 1e-3)

L = G.bloque_L()
for i, (tipo, Lg, v, u) in enumerate(G.L_PARS):
    r = nums(L[i]['respuesta'])[0]
    if tipo == 'angulo':
        check(f'L{i+1}', abs(math.cos(math.radians(r)) - v/Lg) < 1e-3)
    elif tipo == 'altura':
        check(f'L{i+1}', abs(math.asin(r/Lg) - math.radians(v)) < 1e-3)
    else:
        check(f'L{i+1}', abs(r*math.sin(math.radians(v)) - Lg) < 1e-2)

# ── M: los dos triángulos deben dar la misma altura ────────────────────────
M = G.bloque_M()
for i, (a1, a2, d) in enumerate(G.M_PARS):
    v = nums(M[i]['respuesta'])
    x, h = v[0], v[1]
    check(f'M{i+1}-cerca', abs(x*math.tan(math.radians(a2)) - h) < 1e-2)
    check(f'M{i+1}-lejos', abs((x + d)*math.tan(math.radians(a1)) - h) < 1e-2,
          'el triángulo lejano no da la misma altura')

# ── N: la ley de senos debe dar la misma razón para los tres lados ─────────
N = G.bloque_N()
for i, (a, B, C_) in enumerate(G.N_PARS):
    v = nums(N[i]['respuesta'])
    A, b, c = v[0], v[1], v[2]
    check(f'N{i+1}-suma', abs(A + B + C_ - 180) < 0.02)
    r1 = a / math.sin(math.radians(A))
    check(f'N{i+1}-b', abs(b/math.sin(math.radians(B)) - r1) / r1 < 1e-3)
    check(f'N{i+1}-c', abs(c/math.sin(math.radians(C_)) - r1) / r1 < 1e-3)

# ── O: ley de cosenos, en los dos sentidos ─────────────────────────────────
O = G.bloque_O()
for i, (b, c, A, _) in enumerate(G.O_LADO):
    a = nums(O[i]['respuesta'])[0]
    # se compara sobre el lado, no sobre su cuadrado: la respuesta viene redondeada
    # a 3 decimales y al elevarla al cuadrado ese redondeo se amplifica
    esperado = math.sqrt(b*b + c*c - 2*b*c*math.cos(math.radians(A)))
    check(f'O{i+1}', abs(a - esperado)/esperado < 1e-4, f'{a} ≠ {esperado:.6g}')
for j, (a, b, c) in enumerate(G.O_ANG):
    v = nums(O[len(G.O_LADO) + j]['respuesta'])
    A, rad = v[0], v[1]
    esperado = math.degrees(math.acos((b*b + c*c - a*a)/(2*b*c)))
    check(f'Oa{j+1}', abs(A - esperado) < 0.02, f'{A}° ≠ {esperado:.4f}°')
    check(f'Oa{j+1}-rad', abs(math.radians(A) - rad) < 1e-3)
    check(f'Oa{j+1}-tri', a < b + c and b < a + c and c < a + b, 'no es un triángulo válido')

# ── P: identidad pitagórica y recíprocas ───────────────────────────────────
P = G.bloque_P()
for i, (f, p, q) in enumerate(G.P_PARS):
    v = nums(P[i]['respuesta'])
    sen, cos, tan, csc, sec, cot, ang = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
    check(f'P{i+1}-pit', abs(sen*sen + cos*cos - 1) < 1e-3, f'sen²+cos² = {sen*sen+cos*cos}')
    check(f'P{i+1}-tan', abs(tan - sen/cos) < 1e-3)
    check(f'P{i+1}-rec', abs(csc - 1/sen) < 1e-3 and abs(sec - 1/cos) < 1e-3
                        and abs(cot - 1/tan) < 1e-3)
    check(f'P{i+1}-ang', abs(math.sin(math.radians(ang)) - sen) < 1e-3)
    dado = {'sen': sen, 'cos': cos, 'tan': tan}[f]
    check(f'P{i+1}-dato', abs(dado - p/q) < 1e-3, f'no respeta el dato {p}/{q}')

# ── Q: sustituir CADA solución en la ecuación original ─────────────────────
Q = G.bloque_Q()
k = 0
FN = {'sen': math.sin, 'cos': math.cos, 'tan': math.tan}
for f, a, b in G.Q1_PARS:
    sols = nums(Q[k]['respuesta']); k += 1
    for s in sols:
        check(f'Q1.{k}@{s}', abs(a*FN[f](math.radians(s)) + b) < 1e-3)
    check(f'Q1.{k}-n', len(sols) >= 1, 'sin soluciones')
for f, a, b in G.Q2_PARS:
    sols = nums(Q[k]['respuesta']); k += 1
    for s in sols:
        u = FN[f](math.radians(s))
        check(f'Q2.{k}@{s}', abs(a*u*u + b*u) < 1e-3)
    check(f'Q2.{k}-n', len(sols) >= 2, 'faltan soluciones (¿dividiste entre la función?)')
for f, a, b, c in G.Q3_PARS:
    sols = nums(Q[k]['respuesta']); k += 1
    for s in sols:
        u = FN[f](math.radians(s))
        check(f'Q3.{k}@{s}', abs(a*u*u + b*u + c) < 1e-3)

# ── S: costos y perímetros ─────────────────────────────────────────────────
S = G.bloque_S()
k = 0
for largo, alto, precio in G.S_COSTO:
    t = nums(S[k]['respuesta'])[0]; k += 1
    check(f'S1.{k}', abs(t - largo*alto*precio) < 0.02)
for a, b, diag in G.S_DIAG:
    v = nums(S[k]['respuesta']); k += 1
    y, L1, L2, per = v[0], v[1], v[2], v[3]
    check(f'S2.{k}-ent', abs(y - round(y)) < 1e-9, 'y no es entero')
    check(f'S2.{k}-pit', abs(L1*L1 + L2*L2 - diag*diag) < 1e-6)
    check(f'S2.{k}-per', abs(2*(L1 + L2) - per) < 1e-6)

# ── revisión de forma sobre TODOS los ejercicios ───────────────────────────
datos = G.construir()
for b in datos:
    for i, e in enumerate(b['ejercicios'], 1):
        n = f"{b['clave']}{i}"
        texto = e['enunciado'] + ' ' + ' '.join(e['pasos']) + ' ' + e['respuesta']
        check(f'{n}-dolares', texto.replace('\\$', '').count('$') % 2 == 0,
              'LaTeX sin cerrar')
        check(f'{n}-vacio', e['enunciado'].strip() and e['respuesta'].strip(), 'vacío')
        # con \b, para que "inferior" no se confunda con un infinito
        check(f'{n}-nan', not re.search(r'\b(nan|inf)\b', texto), 'número inválido')

print(f'  {revisados} comprobaciones sobre {sum(len(b["ejercicios"]) for b in datos)} ejercicios')
if fallos:
    print(f'\n  {len(fallos)} FALLOS:')
    for f in fallos[:30]:
        print('   !', f)
    sys.exit(1)
print('  todo cuadra')
