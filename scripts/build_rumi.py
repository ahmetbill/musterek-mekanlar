# Rumi Mehmet Pasa Camii (Uskudar) - izometrik diorama
# Calistir:  E:\blender\blender.exe -b -P scripts\build_rumi.py
# Cikti:     model\rumi.blend / .glb, model\rumi_render.png
#
# Tek "masa": revak yukseltisinin sol ucundaki manzara banki (Masa_01), yan kemerden Bogaza bakar. Revak onundeki bank dekor. Ozellikler GLB extras'a gider: masa_id, masa_ad, bolge, kat
# Eksenler: x = soldan saga (revaktan camiye girerken; sol = Bogaz), y = on bahce/sadirvan (y<0) -> cami (arka), z = yukari.
# Kaynak: Google Maps fotograflari (revak, minare, sadirvan kameriyesi, turbe, manzara). Olcular yaklasik.

import bpy, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "model")
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
COL = scene.collection


# ================================================================ malzemeler
def _set(node, names, val):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = val
            return


def mat(name, rgb, rough=0.6, metal=0.0, emit=0.0, alpha=1.0):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = m.node_tree.nodes.get("Principled BSDF")
    _set(b, ["Base Color"], (*rgb, 1))
    _set(b, ["Roughness"], rough)
    _set(b, ["Metallic"], metal)
    if emit:
        _set(b, ["Emission Color", "Emission"], (*rgb, 1))
        _set(b, ["Emission Strength"], emit)
    if alpha < 1:
        _set(b, ["Alpha"], alpha)
        for attr, v in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
            try:
                setattr(m, attr, v)
            except Exception:
                pass
    m.diffuse_color = (*rgb, alpha)
    return m


M = {
    "tas": mat("Kesme_Tas", (0.78, 0.66, 0.45), 0.85),
    "tas_koyu": mat("Kaide_Tasi", (0.25, 0.23, 0.19), 0.9),
    "tugla": mat("Tugla", (0.50, 0.09, 0.03), 0.8),
    "siva": mat("Beyaz_Siva", (0.90, 0.88, 0.84), 0.9),
    "kursun": mat("Kursun_Kubbe", (0.20, 0.27, 0.38), 0.55, 0.25),
    "mermer": mat("Mermer", (0.82, 0.82, 0.80), 0.3),
    "alem": mat("Alem_Altin", (0.95, 0.62, 0.12), 0.25, 1.0),
    "pencere": mat("Pencere", (0.012, 0.03, 0.08), 0.35),
    "kapi": mat("Ahsap_Kapi", (0.45, 0.20, 0.06), 0.6),
    "avlu": mat("Avlu_Tasi", (0.30, 0.27, 0.22), 0.9),
    "derz": mat("Derz", (0.17, 0.15, 0.12), 0.95),
    "patika": mat("Patika", (0.43, 0.38, 0.30), 0.9),
    "cimen": mat("Cimen", (0.27, 0.48, 0.18), 0.95),
    "yaprak": mat("Yaprak", (0.12, 0.32, 0.12), 0.8),
    "yaprak2": mat("Yaprak_Acik", (0.24, 0.45, 0.16), 0.8),
    "selvi": mat("Selvi", (0.07, 0.20, 0.10), 0.8),
    "govde": mat("Govde", (0.30, 0.20, 0.13), 0.9),
    "kiremit": mat("Kiremit", (0.62, 0.16, 0.06), 0.8),
    "kameriye": mat("Kameriye_Ahsap", (0.25, 0.08, 0.03), 0.6),
    "saksi": mat("Saksi_Ahsap", (0.62, 0.48, 0.32), 0.8),
    "cicek": mat("Cicek_Kirmizi", (0.80, 0.10, 0.12), 0.6),
    "demir": mat("Demir", (0.10, 0.10, 0.11), 0.5, 0.6),
    "bank_ahsap": mat("Bank_Ahsap", (0.66, 0.42, 0.22), 0.55),
    "deniz": mat("Bogaz", (0.16, 0.38, 0.62), 0.15),
    "yamac": mat("Yamac", (0.30, 0.42, 0.20), 0.95),
    "ev": mat("Ev_Cephe", (0.62, 0.56, 0.45), 0.9),
    "ev2": mat("Ev_Ahsap", (0.55, 0.30, 0.18), 0.8),
    "kopru": mat("Kopru", (0.55, 0.55, 0.55), 0.5, 0.2),
    "lamba": mat("Fener", (1.0, 0.86, 0.6), 0.3, 0.0, 4.0),
}


# ================================================================ yardimcilar
def _fin(o, m, parent, smooth=False):
    if m:
        o.data.materials.append(m)
    if parent:
        o.parent = parent
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    return o


def mesh(name, v, f, m, parent=None, loc=(0, 0, 0), smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.validate()
    me.update()
    o = bpy.data.objects.new(name, me)
    o.location = loc
    COL.objects.link(o)
    return _fin(o, m, parent, smooth)


def box(name, c, s, m, parent=None):
    hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
    v = [(x, y, z) for x in (-hx, hx) for y in (-hy, hy) for z in (-hz, hz)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return mesh(name, v, f, m, parent, c)


def bx(name, x0, y0, z0, x1, y1, z1, m, parent=None):
    return box(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
               (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), m, parent)


def lathe(name, prof, c, m, parent=None, n=32, rib=0, rib_amp=0.0, rot=0.0, smooth=True):
    """Profil (r, z) noktalarini z ekseni etrafinda dondurur. r=0 olan nokta tek kose olur."""
    v, rings = [], []
    for r, z in prof:
        if r == 0:
            rings.append([len(v)])
            v.append((0, 0, z))
        else:
            ring = []
            for i in range(n):
                a = rot + 2 * math.pi * i / n
                rr = r * (1 + rib_amp * math.cos(rib * a)) if rib else r
                ring.append(len(v))
                v.append((rr * math.cos(a), rr * math.sin(a), z))
            rings.append(ring)
    f = []
    for A, B in zip(rings, rings[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
        if len(A) == 1:
            f += [(A[0], B[i], B[(i + 1) % n]) for i in range(n)]
        elif len(B) == 1:
            f += [(A[i], B[0], A[(i + 1) % n]) for i in range(n)]
        else:
            f += [(A[i], A[(i + 1) % n], B[(i + 1) % n], B[i]) for i in range(n)]
    if len(rings[0]) > 1:
        f.append(tuple(reversed(rings[0])))
    if len(rings[-1]) > 1:
        f.append(tuple(rings[-1]))
    return mesh(name, v, f, m, parent, c, smooth)


def cyl(name, c, r, h, m, parent=None, n=24, smooth=True, rot=0.0):
    x, y, z = c
    return lathe(name, [(r, -h / 2), (r, h / 2)], c, m, parent, n, smooth=smooth, rot=rot)


def dome(name, c, r, h, m, parent=None, n=40, rib=0, rib_amp=0.0, steps=10):
    prof = [(r * math.cos(t), h * math.sin(t)) for t in (i * math.pi / 2 / steps for i in range(steps))] + [(0, h)]
    return lathe(name, [(r, -0.01)] + prof, c, m, parent, n, rib, rib_amp)


def ball(name, c, r, m, parent=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=c)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    return _fin(o, m, parent)


def empty(name, loc=(0, 0, 0), rot_z=0.0, parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.3
    e.location = loc
    e.rotation_euler = (0, 0, rot_z)
    COL.objects.link(e)
    if parent:
        e.parent = parent
    return e


def arch_curve(cx, span, zs, rise, k=14, off=0.0):
    """Hafif sivri kemer egrisi: soldan saga (u, z) noktalari. off: disa dogru kalinlik."""
    pts = []
    for i in range(k + 1):
        t = math.pi * i / k
        u = -math.cos(t)
        z = math.sin(t) ** 0.85
        pts.append((cx + u * (span / 2 + off), zs + z * (rise + off)))
    return pts


def _plane(axis, u, w, z):
    # axis "x": duvar x boyunca uzanir, kalinlik y'de; "y": duvar y boyunca, kalinlik x'te
    return (u, w, z) if axis == "x" else (w, u, z)


def spandrel(name, axis, w0, w1, u0, u1, zs, zt, rise, m, parent=None, k=14):
    """u0..u1 genisliginde, zs'de baslayan kemer acikligi olan, zt'ye kadar dolu duvar parcasi."""
    span = u1 - u0
    cur = arch_curve((u0 + u1) / 2, span, zs, rise, k)
    outline = [(u0, zt), (u1, zt)] + list(reversed(cur))  # ust sol, ust sag, sonra kemer sagdan sola
    n = len(outline)
    v = [_plane(axis, u, w0, z) for u, z in outline] + [_plane(axis, u, w1, z) for u, z in outline]
    f = [tuple(range(n)), tuple(reversed(range(n, 2 * n)))]
    f += [(i, n + i, n + (i + 1) % n, (i + 1) % n) for i in range(n)]
    return mesh(name, v, f, m, parent)


def arch_band(name, axis, w0, w1, u0, u1, zs, rise, th, m, parent=None, k=14):
    """Kemerin ic kenarini izleyen tugla serit (kalinlik th)."""
    cx, span = (u0 + u1) / 2, u1 - u0
    a = arch_curve(cx, span, zs, rise, k, -0.03)  # kemer icine hafif tasar, duvarla ayni yuzeyde kalmasin
    b = arch_curve(cx, span, zs, rise, k, th)
    v, f = [], []
    for (ua, za), (ub, zb) in zip(a, b):
        v += [_plane(axis, ua, w0, za), _plane(axis, ub, w0, zb), _plane(axis, ua, w1, za), _plane(axis, ub, w1, zb)]
    for i in range(k):
        p, q = i * 4, (i + 1) * 4
        f += [(p, q, q + 1, p + 1), (p + 2, p + 3, q + 3, q + 2), (p, p + 2, q + 2, q), (p + 1, q + 1, q + 3, p + 3)]
    return mesh(name, v, f, m, parent)


def half_disc(name, axis, w0, w1, uc, zc, r, m, parent=None, k=24):
    """Yarim daire alinlik (timpan) duvari."""
    outline = [(uc + r * math.cos(math.pi * i / k), zc + r * math.sin(math.pi * i / k)) for i in range(k + 1)]
    n = len(outline)
    v = [_plane(axis, u, w0, z) for u, z in outline] + [_plane(axis, u, w1, z) for u, z in outline]
    f = [tuple(range(n)), tuple(reversed(range(n, 2 * n)))]
    f += [(i, n + i, n + (i + 1) % n, (i + 1) % n) for i in range(n)]
    return mesh(name, v, f, m, parent)


def window(name, axis, w, u, z0, wd, ht, parent, m=None, out=1):
    """Duvar yuzune oturan kemerli koyu pencere. w: duvar yuzu, out: disa dogru yon (+1/-1)."""
    m = m or M["pencere"]
    pts = [(u - wd / 2, z0), (u + wd / 2, z0)] + list(reversed(arch_curve(u, wd, z0 + ht - wd / 2, wd / 2 * 1.1, 8)))
    n = len(pts)
    v = [_plane(axis, pu, w, pz) for pu, pz in pts] + [_plane(axis, pu, w + 0.06 * out, pz) for pu, pz in pts]
    f = [tuple(range(n)), tuple(reversed(range(n, 2 * n)))]
    f += [(i, n + i, n + (i + 1) % n, (i + 1) % n) for i in range(n)]
    return mesh(name, v, f, m, parent)


def striped_box(name, x0, y0, z0, x1, y1, z1, parent, step=0.95):
    """Tas govde + aralikli tugla seritler (almasik orgu)."""
    g = empty(name, (0, 0, 0), 0, parent)
    bx(name + "_Govde", x0, y0, z0, x1, y1, z1, M["tas"], g)
    z, i = z0 + step * 0.7, 0
    while z < z1 - 0.25:
        bx(f"{name}_Tugla{i}", x0 - 0.02, y0 - 0.02, z, x1 + 0.02, y1 + 0.02, z + 0.32, M["tugla"], g)
        z += step
        i += 1
    return g


def tree(name, c, s=1.0, parent=None):
    e = empty(name, c, 0, parent)
    cyl(name + "_Govde", (0, 0, 1.2 * s), 0.16 * s, 2.4 * s, M["govde"], e, 10)
    ball(name + "_Tepe1", (0, 0, 3.1 * s), 1.5 * s, M["yaprak"], e, (1.0, 1.0, 0.85))
    ball(name + "_Tepe2", (0.6 * s, -0.4 * s, 3.8 * s), 1.0 * s, M["yaprak2"], e)
    ball(name + "_Tepe3", (-0.7 * s, 0.5 * s, 3.6 * s), 0.9 * s, M["yaprak2"], e)
    return e


def cypress(name, c, s=1.0, parent=None):
    e = empty(name, c, 0, parent)
    cyl(name + "_Govde", (0, 0, 0.6 * s), 0.18 * s, 1.2 * s, M["govde"], e, 10)
    lathe(name + "_Tepe", [(0.0, 0.8 * s), (1.1 * s, 1.6 * s), (1.25 * s, 4.0 * s), (0.9 * s, 7.0 * s), (0, 9.0 * s)],
          (0, 0, 0), M["selvi"], e, 14)
    return e


def lamp(name, c, parent=None):
    e = empty(name, c, 0, parent)
    cyl(name + "_Direk", (0, 0, 1.6), 0.05, 3.2, M["demir"], e, 8)
    for sx in (-0.28, 0.28):
        bx(f"{name}_Kol{sx}", min(0, sx), -0.03, 3.05, max(0, sx), 0.03, 3.1, M["demir"], e)
        cyl(f"{name}_Fener{sx}", (sx, 0, 3.0), 0.11, 0.3, M["lamba"], e, 6, smooth=False)
    return e


# ================================================================ kok
ROOT_E = empty("Cami_Avlu")

# ---------------------------------------------------------------- arazi
# Gercek yonler: revaktan camiye giren kisinin SOLU (-x) Bogaz/manzara tarafi; revakin ONU (-y) bahce + sadirvan.
X0, X1 = -18.0, 20.0      # sol (manzara duvari) .. sag
Y0, Y1 = -12.0, 31.0      # on (bahce ucu) .. arka
bx("Avlu_Zemin", X0, Y0, -0.4, X1, Y1, 0.0, M["avlu"], ROOT_E)
# tas doseme derzleri (duz bir yuzey gibi durmasin)
for i, x in enumerate(range(-17, 14, 2)):
    bx(f"Derz_X{i:02d}", x - 0.03, 0.4, 0.0, x + 0.03, 9.2, 0.012, M["derz"], ROOT_E)
for i, y in enumerate(range(1, 10, 2)):
    bx(f"Derz_Y{i:02d}", X0 + 0.5, y - 0.03, 0.0, 13.6, y + 0.03, 0.012, M["derz"], ROOT_E)
# on bahce (revakin onu) + sadirvana giden patika
bx("On_Bahce", X0 + 0.5, Y0 + 0.5, 0.0, X1 - 0.5, -0.3, 0.08, M["cimen"], ROOT_E)
bx("Patika", -3.7, -3.4, 0.0, -1.3, -0.3, 0.1, M["patika"], ROOT_E)
bx("Sol_Arka_Cimen", X0 + 0.5, 16.5, 0.0, -11.6, 30.4, 0.08, M["cimen"], ROOT_E)
bx("Sag_Cimen", 13.6, 9.0, 0.0, X1 - 0.5, 30.4, 0.08, M["cimen"], ROOT_E)


def wall_y(name, x, ya, yb, parent):
    """y boyunca alcak tas duvar + demir parmaklik (sol, manzara kenari)."""
    bx(name, x - 0.5, ya, 0.0, x, yb, 0.75, M["tas_koyu"], parent)
    bx(name + "_Kapak", x - 0.54, ya, 0.75, x + 0.04, yb, 0.85, M["tas"], parent)
    bx(name + "_PUst", x - 0.28, ya, 1.9, x - 0.22, yb, 1.96, M["demir"], parent)
    bx(name + "_PAlt", x - 0.28, ya, 1.0, x - 0.22, yb, 1.05, M["demir"], parent)
    y, k = ya + 0.15, 0
    while y < yb:
        bx(f"{name}_Cubuk{k:02d}", x - 0.275, y - 0.025, 0.85, x - 0.225, y + 0.025, 2.05, M["demir"], parent)
        y += 0.45
        k += 1


def wall_x(name, xa, xb, y, parent):
    """x boyunca alcak tas duvar (bahcenin on ucu)."""
    bx(name, xa, y, 0.0, xb, y + 0.5, 0.6, M["tas_koyu"], parent)
    bx(name + "_Kapak", xa, y - 0.04, 0.6, xb, y + 0.54, 0.7, M["tas"], parent)


# manzara tarafi (sol): duvarin otesinde yamac, evler, Bogaz, kopru
man = empty("Manzara", (0, 0, 0), 0, ROOT_E)
XS = X0 - 0.5            # yamacin ust kenari
v = [(XS, Y0, -0.4), (XS, Y1, -0.4), (XS - 5.0, Y1, -3.4), (XS - 5.0, Y0, -3.4),
     (XS, Y0, -3.6), (XS, Y1, -3.6), (XS - 5.0, Y1, -3.6), (XS - 5.0, Y0, -3.6)]
f = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (2, 6, 7, 3), (0, 3, 7, 4), (1, 5, 6, 2)]
mesh("Yamac", v, f, M["yamac"], man)
bx("Bogaz", XS - 13.0, Y0, -3.9, XS - 5.0, Y1, -3.6, M["deniz"], man)
for i, (y, w, h, mm) in enumerate([(-7.0, 3.2, 2.2, "ev"), (14.5, 2.6, 2.6, "ev2"), (25.0, 3.4, 2.0, "ev")]):
    e = empty(f"Ev{i}", (XS - 3.0, y, -2.6), 0, man)
    bx(f"Ev{i}_Govde", -1.2, -w / 2, 0, 1.2, w / 2, h, M[mm], e)
    lathe(f"Ev{i}_Cati", [(w * 0.78, h), (0, h + 1.0)], (0, 0, 0), M["kiremit"], e, 4, rot=math.pi / 4, smooth=False).scale = (2.7 / (w * 1.1), 1, 1)
# kopru (15 Temmuz Sehitler) - uzakta silueti, y boyunca uzanir
kop = empty("Kopru", (XS - 10.0, 0, -3.6), 0, man)
YA, YB = -6.0, 22.0
for y in (YA, YB):
    bx(f"Kopru_Kule{y}", -0.3, y - 0.25, 0, 0.3, y + 0.25, 7.0, M["kopru"], kop)
    bx(f"Kopru_Kule{y}_Kiris", -0.3, y - 0.25, 6.2, 0.3, y + 0.25, 6.5, M["kopru"], kop)
bx("Kopru_Tabliye", -0.45, Y0, 2.2, 0.45, Y1, 2.55, M["kopru"], kop)
pts = []
for i in range(25):
    t = i / 24
    pts.append((YA + (YB - YA) * t, 7.0 - 4.2 * (1 - (2 * t - 1) ** 2)))
pts = [(Y0, 2.6)] + pts + [(Y1, 2.6)]
for i in range(len(pts) - 1):
    (ya, za), (yb, zb) = pts[i], pts[i + 1]
    L = math.hypot(yb - ya, zb - za)
    o = box(f"Kopru_Kablo{i:02d}", (0, (ya + yb) / 2, (za + zb) / 2), (0.08, L, 0.08), M["kopru"], kop)
    o.rotation_euler = (math.atan2(zb - za, yb - ya), 0, 0)

# sol duvar + parmaklik + Bogaz'a inen bahce kapisi
GY0, GY1 = 3.0, 5.6
wall_y("Sol_Duvar0", X0, Y0, GY0 - 0.5, ROOT_E)
wall_y("Sol_Duvar1", X0, GY1 + 0.5, Y1, ROOT_E)
for i, y in enumerate([GY0 - 0.5, GY1]):
    bx(f"Kapi_Ayak{i}", X0 - 0.55, y, 0.0, X0 + 0.05, y + 0.5, 2.3, M["tugla"], ROOT_E)
    bx(f"Kapi_Ayak{i}_Kapak", X0 - 0.6, y - 0.05, 2.3, X0 + 0.1, y + 0.55, 2.42, M["tas"], ROOT_E)
for k in range(6):
    y = GY0 + 0.2 + k * 0.42
    bx(f"Kapi_Kanat_Cubuk{k}", X0 - 0.28, y - 0.025, 0.0, X0 - 0.22, y + 0.025, 2.0, M["demir"], ROOT_E)
bx("Kapi_Kanat_Ust", X0 - 0.28, GY0, 1.95, X0 - 0.22, GY1, 2.02, M["demir"], ROOT_E)
for i in range(5):  # kapidan asagi inen merdiven
    bx(f"Kapi_Merdiven{i}", XS - 0.6 * (i + 1), GY0, -0.4 - 0.55 * (i + 1), XS - 0.6 * i, GY1, -0.4 - 0.55 * i, M["tas"], man)
# bahcenin on ucu
wall_x("On_Duvar", X0, X1, Y0, ROOT_E)

# fener direkleri
for i, (x, y) in enumerate([(-16.6, 1.0), (-16.6, 13.5), (9.5, 0.8), (-9.0, -6.5), (5.0, -6.5), (-16.6, 24.0)]):
    lamp(f"Fener{i}", (x, y, 0), ROOT_E)

# ---------------------------------------------------------------- CAMI
cami = empty("Cami", (0, 0, 0), 0, ROOT_E)
FL = 1.0                       # harim zemin kotu (avludan yuksek kaide)
HX0, HX1, HY0, HY1 = -6.5, 6.5, 15.0, 28.0
WT = 9.0                       # duvar ust kotu

# yuksek tas kaide (bina sokulu)
bx("Cami_Sokulu", -10.9, HY0, 0.0, 10.9, 28.4, FL, M["tas_koyu"], cami)  # revak kaidesiyle cakismasin
bx("Mihrap_Sokulu", -3.4, 28.0, 0.0, 3.4, 30.4, FL, M["tas_koyu"], cami)

# harim govdesi (almasik)
striped_box("Harim", HX0, HY0, FL, HX1, HY1, WT, cami)
bx("Harim_Cati", HX0 - 0.15, HY0 - 0.15, WT, HX1 + 0.15, HY1 + 0.15, WT + 0.25, M["kursun"], cami)
# dort cephede yarim daire alinlik + tugla kemer
CX, CY = 0.0, (HY0 + HY1) / 2
for side, (axis, w0, w1, uc) in {"On": ("x", HY0, HY0 + 0.9, CX), "Arka": ("x", HY1 - 0.9, HY1, CX),
                                  "Sol": ("y", HX0, HX0 + 0.9, CY), "Sag": ("y", HX1 - 0.9, HX1, CY)}.items():
    half_disc(f"Alinlik_{side}", axis, w0, w1, uc, WT, 5.2, M["tas"], cami)
    # tugla kemer bandi (alinligin cevresinde)
    rr0, rr1, k = 5.0, 5.5, 24
    vv, ff = [], []
    ws = (w0 - 0.03, w1 + 0.03)
    for i in range(k + 1):
        t = math.pi * i / k
        for r in (rr0, rr1):
            for w in ws:
                vv.append(_plane(axis, uc + r * math.cos(t), w, WT + r * math.sin(t)))
    for i in range(k):
        p, q = i * 4, (i + 1) * 4
        ff += [(p + 1, q + 1, q + 3, p + 3), (p, p + 2, q + 2, q), (p + 2, p + 3, q + 3, q + 2), (p, q, q + 1, p + 1)]
    mesh(f"Alinlik_{side}_Kemer", vv, ff, M["tugla"], cami)
    # alinlik pencereleri (3 kemerli)
    wface = w0 - 0.01 if side in ("On", "Sol") else w1 + 0.01
    out = -1 if side in ("On", "Sol") else 1
    for j, du in enumerate((-2.0, 0.0, 2.0)):
        window(f"Alinlik_{side}_Pencere{j}", axis, wface, uc + du, WT + 0.8 + (0.6 if du == 0 else 0), 0.75, 1.6, cami, out=out)
    # alt kat pencereleri
    for j, du in enumerate((-3.6, 3.6)):
        if side == "On":
            continue
        window(f"Harim_{side}_Pencere{j}", axis, wface, uc + du, FL + 1.4, 1.0, 2.3, cami, out=out)

# kubbe kasnagi + kubbe + alem
bx("Kasnak_Kaidesi", -5.5, CY - 5.5, WT + 0.25, 5.5, CY + 5.5, WT + 2.0, M["tas"], cami)
lathe("Kasnak", [(5.2, WT + 2.0), (5.2, WT + 4.4)], (0, CY, 0), M["tas"], cami, 32)
for i, z in enumerate([WT + 2.6, WT + 3.4]):
    lathe(f"Kasnak_Tugla{i}", [(5.23, z), (5.23, z + 0.22)], (0, CY, 0), M["tugla"], cami, 32)
lathe("Kasnak_Sacak", [(5.25, WT + 4.4), (5.6, WT + 4.55), (5.6, WT + 4.7), (5.0, WT + 4.7)], (0, CY, 0), M["kursun"], cami, 32)
for j in range(12):  # kasnak pencereleri
    a = 2 * math.pi * j / 12 + math.pi / 12
    e = empty(f"Kasnak_Pencere{j}", (5.21 * math.cos(a), CY + 5.21 * math.sin(a), WT + 2.7), a - math.pi / 2, cami)
    window(f"Kasnak_Pencere{j}_P", "x", 0.0, 0.0, 0.0, 0.6, 1.3, e)
dome("Kubbe", (0, CY, WT + 4.6), 5.45, 4.4, M["kursun"], cami, 48, rib=24, rib_amp=0.012)
ZT = WT + 4.6 + 4.4
lathe("Alem", [(0.12, ZT - 0.1), (0.12, ZT + 0.3), (0.2, ZT + 0.45), (0.06, ZT + 0.6), (0.18, ZT + 0.8), (0.0, ZT + 1.1)],
      (0, CY, 0), M["alem"], cami, 12)

# yan kanatlar (tabhane) + kucuk kubbeler
for s, (a, b) in (("Sol", (-10.6, HX0)), ("Sag", (HX1, 10.6))):
    striped_box(f"Kanat_{s}", a, HY0, FL, b, 24.5, 6.6, cami)
    bx(f"Kanat_{s}_Cati", a - 0.12, HY0 - 0.12, 6.6, b + 0.12, 24.62, 6.8, M["kursun"], cami)
    xm = (a + b) / 2
    for j, y in enumerate((17.4, 22.1)):
        bx(f"Kanat_{s}_Kasnak{j}", xm - 1.5, y - 1.5, 6.8, xm + 1.5, y + 1.5, 7.5, M["tas"], cami)
        dome(f"Kanat_{s}_Kubbe{j}", (xm, y, 7.5), 1.65, 1.35, M["kursun"], cami, 28, rib=12, rib_amp=0.02)
        lathe(f"Kanat_{s}_Alem{j}", [(0.05, 8.8), (0.05, 9.3), (0, 9.4)], (xm, y, 0), M["alem"], cami, 8)
    wface = a - 0.04 if s == "Sol" else b + 0.04  # tugla seritlerin onunde
    for j, y in enumerate((17.4, 22.1)):
        window(f"Kanat_{s}_Pencere{j}", "y", wface, y, FL + 1.2, 1.0, 2.3, cami, out=-1 if s == "Sol" else 1)
    # bacalar (fotodaki kulahli bacalar)
    xc = a + 0.6 if s == "Sol" else b - 0.6
    bx(f"Kanat_{s}_Baca", xc - 0.3, 15.4, 6.8, xc + 0.3, 16.0, 8.4, M["tugla"], cami)
    lathe(f"Kanat_{s}_Baca_Kulah", [(0.5, 8.4), (0, 9.1)], (xc, 15.7, 0), M["kursun"], cami, 4, rot=math.pi / 4, smooth=False)

# mihrap cikintisi (arka) + yarim kubbe
bx("Mihrap_Govde", -3.0, HY1, FL, 3.0, 30.0, 7.2, M["tas"], cami)
bx("Mihrap_Tugla", -3.02, HY1, 4.2, 3.02, 30.02, 4.42, M["tugla"], cami)
bx("Mihrap_Cati", -3.15, HY1, 7.2, 3.15, 30.15, 7.4, M["kursun"], cami)

# ---------------------------------------------------------------- son cemaat yeri (revak)
PY0, PY1 = 9.6, HY0              # revak derinligi
bx("Revak_Kaide", -10.9, PY0 - 0.2, 0.0, 10.9, PY1, FL, M["tas"], cami)
bx("Revak_Zemin", -10.6, PY0, FL, 10.6, PY1, FL + 0.03, M["mermer"], cami)
for i in range(3):  # orta basamaklar
    bx(f"Revak_Basamak{i}", -2.4 - i * 0.3, PY0 - 0.2 - (i + 1) * 0.42, 0.0, 2.4 + i * 0.3, PY0 - 0.2 - i * 0.42,
       FL - (i + 1) * 0.25, M["tas"], cami)
CXS = [-10.0, -6.0, -2.0, 2.0, 6.0, 10.0]
ZS, RISE, ZTOP = FL + 4.3, 2.0, FL + 7.3   # kemer baslangici, yukseklik, revak duvar ustu
CW = 0.38                                  # sutun basligi yarim genisligi
CYC = PY0 + 0.35                            # sutun hatti
for i, x in enumerate(CXS):
    e = empty(f"Sutun{i}", (x, CYC, FL), 0, cami)
    lathe(f"Sutun{i}_Kaide", [(0.42, 0.0), (0.42, 0.25), (0.32, 0.35)], (0, 0, 0), M["mermer"], e, 20)
    cyl(f"Sutun{i}_Govde", (0, 0, 0.35 + (ZS - FL - 0.75) / 2), 0.3, ZS - FL - 0.75, M["mermer"], e, 20)
    lathe(f"Sutun{i}_Baslik", [(0.3, ZS - FL - 0.4), (0.45, ZS - FL - 0.15), (CW + 0.05, ZS - FL - 0.15)], (0, 0, 0), M["mermer"], e, 4, rot=math.pi / 4, smooth=False)
    bx(f"Sutun{i}_Abakus", -CW - 0.05, -CW - 0.05, ZS - FL - 0.15, CW + 0.05, CW + 0.05, ZS - FL, M["mermer"], e)
# on cephe: kemerli duvar parcalari + tugla kemer bantlari
W0, W1 = CYC - 0.35, CYC + 0.35
for i in range(5):
    u0, u1 = CXS[i] + CW, CXS[i + 1] - CW
    spandrel(f"Revak_On_Kemer{i}", "x", W0, W1, u0, u1, ZS, ZTOP, RISE, M["tas"], cami)
    arch_band(f"Revak_On_Tugla{i}", "x", W0 - 0.03, W1 + 0.03, u0, u1, ZS, RISE, 0.38, M["tugla"], cami)
    bx(f"Revak_On_Ayak{i}", CXS[i] - CW, W0, ZS, CXS[i] + CW, W1, ZTOP, M["tas"], cami)
bx("Revak_On_Ayak5", CXS[5] - CW, W0, ZS, CXS[5] + CW, W1, ZTOP, M["tas"], cami)
# yan cepheler (kisa kenar) tek kemer
for s, x in (("Sol", CXS[0]), ("Sag", CXS[5])):
    spandrel(f"Revak_{s}_Kemer", "y", x - 0.35, x + 0.35, CYC + CW, PY1, ZS, ZTOP, RISE + 0.3, M["tas"], cami)
    arch_band(f"Revak_{s}_Tugla", "y", x - 0.38, x + 0.38, CYC + CW, PY1, ZS, RISE + 0.3, 0.38, M["tugla"], cami)
# tasiyici demir gergiler
for i, x in enumerate(CXS):
    bx(f"Gergi{i}", x - 0.04, CYC, ZS - 0.1, x + 0.04, PY1, ZS - 0.02, M["demir"], cami)
bx("Gergi_On", CXS[0], CYC - 0.04, ZS - 0.1, CXS[5], CYC + 0.04, ZS - 0.02, M["demir"], cami)
# revak cati (kursun, hafif kirma)
bx("Revak_Cati", -10.55, CYC - 0.5, ZTOP, 10.55, PY1 + 0.1, ZTOP + 0.22, M["kursun"], cami)
bx("Revak_Cati_Sirt", -10.2, CYC - 0.1, ZTOP + 0.22, 10.2, PY1 - 0.2, ZTOP + 0.42, M["kursun"], cami)
bx("Revak_Silme", -10.6, CYC - 0.42, ZTOP - 0.3, 10.6, CYC + 0.4, ZTOP, M["tugla"], cami)
# revak ici: tac kapi + pencereler (harim on duvari, beyaz sivali)
bx("Revak_Ic_Siva", -10.55, HY0 - 0.06, FL, 10.55, HY0, ZTOP, M["siva"], cami)
bx("Tac_Kapi", -1.8, HY0 - 0.3, FL, 1.8, HY0 - 0.05, FL + 5.6, M["tas"], cami)
window("Tac_Kapi_Kapi", "x", HY0 - 0.31, 0.0, FL + 0.03, 1.4, 3.0, cami, M["kapi"], out=-1)
for j, x in enumerate((-4.6, 4.6, -8.6, 8.6)):
    window(f"Revak_Pencere{j}", "x", HY0 - 0.07, x, FL + 1.0, 1.1, 2.4, cami, out=-1)
# revak kenarindaki ahsap saksilar
for i in range(5):
    if i == 2:
        continue
    xc = (CXS[i] + CXS[i + 1]) / 2
    for j, dx in enumerate((-0.85, 0.85)):
        e = empty(f"Saksi{i}{j}", (xc + dx, CYC + 0.45, FL), 0, cami)
        bx(f"Saksi{i}{j}_Kasa", -0.65, -0.3, 0.0, 0.65, 0.3, 0.55, M["saksi"], e)
        for k in range(3):
            ball(f"Saksi{i}{j}_Bitki{k}", (-0.42 + k * 0.42, 0, 0.75), 0.26, M["yaprak2"], e, (1, 0.8, 1.1))

# ---------------------------------------------------------------- minare (sag on kose)
mn = empty("Minare", (12.1, 13.0, 0), 0, cami)
bx("Minare_Kaide", -1.25, -1.25, 0.0, 1.25, 1.25, 6.0, M["tas"], mn)
lathe("Minare_Pabuc", [(1.77, 6.0), (1.35, 7.2)], (0, 0, 0), M["tas"], mn, 4, rot=math.pi / 4, smooth=False)
lathe("Minare_Govde", [(1.2, 7.2), (1.02, 7.6), (1.0, 18.0)], (0, 0, 0), M["tas"], mn, 16, smooth=False)
lathe("Minare_Serefe_Alt", [(1.0, 18.0), (1.15, 18.4), (1.35, 18.8), (1.5, 19.2)], (0, 0, 0), M["tas"], mn, 16, smooth=False)
lathe("Minare_Serefe", [(1.5, 19.2), (1.5, 20.1), (1.4, 20.1)], (0, 0, 0), M["tas"], mn, 16, smooth=False)
lathe("Minare_Ust_Govde", [(0.82, 19.2), (0.82, 23.0), (0.92, 23.2), (0.92, 23.4)], (0, 0, 0), M["tas"], mn, 16, smooth=False)
lathe("Minare_Kulah", [(0.98, 23.4), (0.0, 28.4)], (0, 0, 0), M["kursun"], mn, 16, smooth=False)
lathe("Minare_Alem", [(0.06, 28.3), (0.06, 28.9), (0.14, 29.0), (0, 29.3)], (0, 0, 0), M["alem"], mn, 8)
window("Minare_Kapi", "x", -1.26, 0.0, 0.0, 0.9, 2.2, mn, M["kapi"], out=-1)

# ---------------------------------------------------------------- turbe (sekizgen, kubbeli)
tb = empty("Turbe", (16.8, 24.0, 0), 0, ROOT_E)
lathe("Turbe_Govde", [(2.2, 0.0), (2.2, 4.6)], (0, 0, 0), M["tas"], tb, 8, rot=math.pi / 8, smooth=False)
lathe("Turbe_Sacak", [(2.25, 4.6), (2.45, 4.75), (2.0, 4.85)], (0, 0, 0), M["kursun"], tb, 8, rot=math.pi / 8, smooth=False)
dome("Turbe_Kubbe", (0, 0, 4.8), 1.85, 1.5, M["kursun"], tb, 28)
lathe("Turbe_Alem", [(0.05, 6.2), (0.05, 6.7), (0, 6.8)], (0, 0, 0), M["alem"], tb, 8)
for j in range(8):
    a = math.pi / 8 + 2 * math.pi * j / 8 + math.pi / 8
    r = 2.2 * math.cos(math.pi / 8)
    e = empty(f"Turbe_Pencere{j}", (r * math.cos(a), r * math.sin(a), 0), 0, tb)
    e.rotation_euler = (0, 0, a - math.pi / 2)
    window(f"Turbe_Pencere{j}_P", "x", 0.0, 0.0, 2.5, 0.6, 1.4, e)
    if j % 2 == 0:
        window(f"Turbe_Pencere{j}_A", "x", 0.0, 0.0, 0.4, 0.8, 1.6, e)

# ---------------------------------------------------------------- sadirvan kameriyesi (bahcede)
sd = empty("Sadirvan", (-2.5, -6.6, 0), 0, ROOT_E)
R8 = 3.0
lathe("Sadirvan_Platform", [(R8, 0.0), (R8, 0.3)], (0, 0, 0), M["mermer"], sd, 8, rot=math.pi / 8, smooth=False)
for j in range(8):
    a = math.pi / 8 + 2 * math.pi * j / 8
    x, y = (R8 - 0.3) * math.cos(a), (R8 - 0.3) * math.sin(a)
    bx(f"Sadirvan_Direk{j}", x - 0.11, y - 0.11, 0.3, x + 0.11, y + 0.11, 3.0, M["kameriye"], sd)
    if j != 1:  # giris (patika, +y tarafi) acik
        a2 = a + 2 * math.pi / 8
        x2, y2 = (R8 - 0.3) * math.cos(a2), (R8 - 0.3) * math.sin(a2)
        L = math.hypot(x2 - x, y2 - y)
        o = box(f"Sadirvan_Korkuluk{j}", ((x + x2) / 2, (y + y2) / 2, 1.2), (L, 0.07, 0.08), M["kameriye"], sd)
        o.rotation_euler = (0, 0, math.atan2(y2 - y, x2 - x))
        for k in range(1, 6):
            t = k / 6
            bx(f"Sadirvan_Korkuluk{j}_Cubuk{k}", x + (x2 - x) * t - 0.03, y + (y2 - y) * t - 0.03, 0.3,
               x + (x2 - x) * t + 0.03, y + (y2 - y) * t + 0.03, 1.2, M["kameriye"], sd)
lathe("Sadirvan_Kusak", [(R8 - 0.1, 2.85), (R8 - 0.1, 3.1), (R8 - 0.5, 3.1)], (0, 0, 0), M["kameriye"], sd, 8, rot=math.pi / 8, smooth=False)
lathe("Sadirvan_Cati", [(R8 + 0.6, 3.05), (0.35, 4.6), (0, 4.75)], (0, 0, 0), M["kiremit"], sd, 8, rot=math.pi / 8, smooth=False)
lathe("Sadirvan_Havuz", [(1.25, 0.3), (1.25, 0.55), (1.05, 0.55), (1.05, 0.4)], (0, 0, 0), M["mermer"], sd, 8, rot=math.pi / 8, smooth=False)
lathe("Sadirvan_Tas", [(0.8, 0.3), (0.8, 1.55), (0.85, 1.6), (0.3, 1.95), (0.08, 2.15), (0, 2.25)], (0, 0, 0), M["mermer"], sd, 8, rot=math.pi / 8, smooth=False)
for j in range(6):
    a = 2 * math.pi * j / 6
    cyl(f"Sadirvan_Tabure{j}", (1.75 * math.cos(a), 1.75 * math.sin(a), 0.55), 0.2, 0.5, M["mermer"], sd, 12)

# ---------------------------------------------------------------- agaclar
for i, (x, y, s) in enumerate([(-15.0, -9.0, 1.0), (-9.5, -3.0, 0.85), (5.5, -9.0, 1.1), (11.0, -3.5, 0.9),
                               (16.5, -8.5, 1.0), (-14.5, 20.0, 1.0), (-14.0, 28.0, 1.1), (17.0, 12.0, 0.85)]):
    tree(f"Agac{i}", (x, y, 0.08), s, ROOT_E)
cypress("Selvi0", (18.6, 18.5, 0.08), 1.4, ROOT_E)
cypress("Selvi1", (18.4, 29.0, 0.08), 1.1, ROOT_E)
# cicekli tarh (bahcenin on duvari dibinde)
for i in range(9):
    x = -15.5 + i * 3.4
    ball(f"Tarh_Cali{i}", (x, Y0 + 1.0, 0.35), 0.48, M["yaprak2"], ROOT_E, (1, 0.8, 0.8))
    ball(f"Tarh_Cicek{i}", (x + 0.3, Y0 + 0.8, 0.7), 0.16, M["cicek"], ROOT_E)

# ================================================================ BANKLAR
def bench(name, loc, rot, parent):
    """Ahsap citali, dokum demir ayakli bank. Yerel: yuzu -y, sirti +y."""
    bank = empty(name, loc, rot, parent)
    BL = 1.9
    for i in range(4):  # oturak citalari
        y = -0.22 + i * 0.15
        bx(f"{name}_Oturak{i}", -BL / 2, y - 0.06, 0.44, BL / 2, y + 0.06, 0.48, M["bank_ahsap"], bank)
    for i in range(3):  # sirt citalari (hafif yatik)
        o = bx(f"{name}_Sirt{i}", -BL / 2, -0.03, 0.0, BL / 2, 0.03, 0.11, M["bank_ahsap"], bank)
        o.location = (0, 0.3 + i * 0.03, 0.62 + i * 0.15)
        o.rotation_euler = (math.radians(-12), 0, 0)
    for k, sx in enumerate((-BL / 2 + 0.12, BL / 2 - 0.12)):  # dokum demir yanlar
        bx(f"{name}_Ayak_On{k}", sx - 0.04, -0.28, 0.0, sx + 0.04, -0.2, 0.46, M["demir"], bank)
        bx(f"{name}_Ayak_Arka{k}", sx - 0.04, 0.22, 0.0, sx + 0.04, 0.3, 0.46, M["demir"], bank)
        bx(f"{name}_Yan{k}", sx - 0.04, -0.28, 0.4, sx + 0.04, 0.3, 0.44, M["demir"], bank)
        o = bx(f"{name}_Sirt_Dikme{k}", sx - 0.04, -0.035, 0.0, sx + 0.04, 0.035, 0.6, M["demir"], bank)
        o.location = (0, 0.3, 0.44)
        o.rotation_euler = (math.radians(-12), 0, 0)
        bx(f"{name}_Kol{k}", sx - 0.05, -0.25, 0.66, sx + 0.05, 0.25, 0.7, M["demir"], bank)
        bx(f"{name}_Kol_Dikme{k}", sx - 0.035, -0.24, 0.44, sx + 0.035, -0.17, 0.68, M["demir"], bank)
    return bank


MASALAR = []
# asil manzara banki: revakin yukseltisinde (cami kapisi seviyesi), sol ucta; yan kemerden Bogaz'a bakar (-x)
mb = bench("Masa_01", (-9.3, 12.4, FL + 0.03), -math.pi / 2, ROOT_E)
mb["masa_id"], mb["masa_ad"], mb["bolge"], mb["kat"] = 1, "Manzara bankı", "Revak · Boğaz tarafı", "Zemin"
MASALAR.append(mb)
# revakin onundeki bank (sadirvana ve bahceye bakar) - sadece dekor
bench("Avlu_Banki", (-4.5, 7.9, 0), 0.0, ROOT_E)

# ================================================================ isik + kamera
sun_d = bpy.data.lights.new("Gunes", "SUN")
sun_d.energy = 3.0
sun_d.angle = math.radians(8)
sun = bpy.data.objects.new("Gunes", sun_d)
sun.rotation_euler = (math.radians(50), math.radians(-15), math.radians(-140))
COL.objects.link(sun)

world = bpy.data.worlds.new("Dunya")
scene.world = world
try:
    world.use_nodes = True
except Exception:
    pass
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.80, 0.85, 0.95, 1)
bg.inputs[1].default_value = 0.6
scene.view_settings.view_transform = "Standard"
scene.view_settings.exposure = -0.1

cam_d = bpy.data.cameras.new("Kamera")
cam_d.type = "ORTHO"
cam_d.ortho_scale = 66.0
cam_d.clip_end = 500
cam = bpy.data.objects.new("Kamera", cam_d)
target = (-3.0, 9.0, 6.0)
dirv = (-0.542, -0.542, 0.643)
cam.location = tuple(target[i] + dirv[i] * 90 for i in range(3))
cam.rotation_euler = (math.radians(50), 0, math.radians(-45))
COL.objects.link(cam)
scene.camera = cam

for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        scene.render.engine = eng
        break
    except Exception:
        continue
scene.render.resolution_x = 1800
scene.render.resolution_y = 1450
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"

# ================================================================ kaydet / disa aktar / render
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "rumi.blend"))
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT, "rumi.glb"),
    export_format="GLB", export_extras=True, export_apply=True, export_yup=True,
    export_cameras=False, export_lights=False,
)
scene.render.filepath = os.path.join(OUT, "rumi_render.png")
bpy.ops.render.render(write_still=True)

# sayfadaki mekan seciciye kucuk gorsel
scene.render.resolution_x, scene.render.resolution_y = 720, 580
cam_d.ortho_scale = 68.0
scene.render.filepath = os.path.join(ROOT, "assets", "thumbs", "rumi.png")
bpy.ops.render.render(write_still=True)
print("TAMAM:", OUT, "masa sayisi:", len(MASALAR))
