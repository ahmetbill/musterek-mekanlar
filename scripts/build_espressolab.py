# Espresso Lab Sisli Esentepe - izometrik diorama (2 kat)
# Calistir:  E:\blender\blender.exe -b -P scripts\build_espressolab.py
# Cikti:     model\espressolab.blend / .glb, model\render_tum.png, model\render_altkat.png
#
# Kokler: "Dis" (teras + cephe), "AltKat", "UstKat" (ust kat + asma kat; sayfada gizlenebilir)
# Her masa "Masa_XX" Empty'si altinda (masa + sandalyeler); ozellikler GLB extras'a gider:
#   masa_id, masa_ad, bolge, kat
#
# Eksenler: x = soldan saga (girise bakarken), y = sokaktan (0) arka bahceye (28), z = yukari.

import bpy, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "model")
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
COL = scene.collection

W, D, H = 14.0, 34.0, 7.4  # bina genislik, derinlik, atriyum yuksekligi
SLAB = 3.8  # ust kat zemin ust kotu


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
    "siva": mat("Siva_Bej", (0.74, 0.70, 0.62), 0.95),
    "zemin": mat("Karo_Bej", (0.66, 0.63, 0.57), 0.5),
    "dis_zemin": mat("Dis_Karo", (0.55, 0.54, 0.52), 0.9),
    "kaide": mat("Kaide", (0.10, 0.10, 0.11), 0.8),
    "cephe": mat("Cephe_Gri", (0.58, 0.60, 0.62), 0.45, 0.3),
    "led": mat("LED_Tabela", (0.92, 0.92, 1.0), 0.3, 0.0, 2.5),
    "led_yazi": mat("LED_Yazi", (0.04, 0.04, 0.04), 0.5),
    "kirmizi": mat("Marka_Kirmizi", (0.75, 0.05, 0.06), 0.5),
    "tik": mat("Tik_Ahsap", (0.42, 0.18, 0.07), 0.5),
    "burl": mat("Kok_Ahsap", (0.62, 0.40, 0.18), 0.45),
    "hasir": mat("Hasir", (0.86, 0.76, 0.55), 0.95),
    "beyaz_metal": mat("Beyaz_Metal", (0.88, 0.88, 0.86), 0.35, 0.3),
    "mermer": mat("Beyaz_Mermer", (0.95, 0.95, 0.93), 0.15),
    "celik": mat("Celik", (0.78, 0.78, 0.80), 0.18, 1.0),
    "ayna": mat("Ayna", (0.92, 0.92, 0.95), 0.03, 1.0),
    "terakota": mat("Terakota", (0.50, 0.24, 0.14), 0.9),
    "gri_minder": mat("Gri_Minder", (0.50, 0.53, 0.53), 0.95),
    "zeytin": mat("Zeytin_Dosemelik", (0.52, 0.52, 0.40), 0.9),
    "fayans": mat("Fayans_Bej", (0.80, 0.74, 0.62), 0.6),
    "turkuaz": mat("Turkuaz", (0.05, 0.42, 0.48), 0.4),
    "kontrplak": mat("Kontrplak_Turuncu", (0.75, 0.38, 0.22), 0.5),
    "bistro": mat("Bistro_Gri", (0.62, 0.63, 0.64), 0.4, 0.5),
    "kumas": mat("Semsiye", (0.93, 0.92, 0.88), 0.9),
    "cam": mat("Cam", (0.70, 0.85, 0.95), 0.05, 0.0, 0.0, 0.2),
    "yaprak": mat("Yaprak", (0.10, 0.30, 0.11), 0.7),
    "yaprak2": mat("Yaprak_Acik", (0.20, 0.42, 0.15), 0.7),
    "toprak": mat("Toprak", (0.20, 0.12, 0.07), 1.0),
    "saksi": mat("Saksi", (0.70, 0.66, 0.60), 0.8),
    "pembe": mat("Pembe", (0.95, 0.35, 0.55), 0.4, 0.0, 0.8),
    "lamba": mat("Lamba", (1.0, 0.85, 0.6), 0.3, 0.0, 6.0),
    "siyah": mat("Siyah", (0.03, 0.03, 0.03), 0.4),
    "ekran_k": mat("Ekran_Kirmizi", (0.85, 0.06, 0.08), 0.3, 0.0, 2.0),
    "ekran_m": mat("Ekran_Mavi", (0.25, 0.45, 0.95), 0.3, 0.0, 2.0),
    "ekran_b": mat("Ekran_Beyaz", (0.9, 0.92, 0.95), 0.3, 0.0, 1.5),
    "ekran_f": mat("Ekran_Foto", (0.45, 0.30, 0.18), 0.3, 0.0, 1.2),
    "granit": mat("Granit", (0.45, 0.44, 0.43), 0.7),
    "merdiven": mat("Merdiven_Ahsap", (0.62, 0.38, 0.22), 0.6),
}


# ================================================================ yardimcilar
def _fin(o, m, parent):
    if m:
        o.data.materials.append(m)
    if parent:
        o.parent = parent
    return o


def box(name, c, s, m, parent=None, bevel=0.0):
    hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
    v = [(x, y, z) for x in (-hx, hx) for y in (-hy, hy) for z in (-hz, hz)]
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    o = bpy.data.objects.new(name, me)
    o.location = c
    COL.objects.link(o)
    if bevel and min(s) > bevel * 2.5:
        b = o.modifiers.new("Bevel", "BEVEL")
        b.width, b.segments, b.limit_method = bevel, 2, "ANGLE"
    return _fin(o, m, parent)


def bx(name, x0, y0, z0, x1, y1, z1, m, parent=None, bevel=0.0):
    """Kose koordinatlariyla kutu."""
    return box(name, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
               (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), m, parent, bevel)


def _op_obj(name, m, parent, smooth=True):
    o = bpy.context.active_object
    o.name = name
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    return _fin(o, m, parent)


def cyl(name, c, r, h, m, parent=None, verts=28, rot=(0, 0, 0), scale=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=c, rotation=rot)
    o = _op_obj(name, m, parent)
    if scale:
        o.scale = scale
    return o


def ball(name, c, r, m, parent=None, sub=2, scale=None):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=c)
    o = _op_obj(name, m, parent, smooth=False)
    if scale:
        o.scale = scale
    return o


def cone(name, c, r1, r2, h, m, parent=None, verts=4, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=h, location=c, rotation=rot)
    return _op_obj(name, m, parent, smooth=False)


def text(name, body, c, size, m, rot, parent=None, extrude=0.01):
    bpy.ops.object.text_add(location=c, rotation=rot)
    t = bpy.context.active_object
    t.name = name
    t.data.body = body
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.size = size
    t.data.extrude = extrude
    t.data.materials.append(m)
    bpy.ops.object.convert(target="MESH")
    t = bpy.context.active_object
    if parent:
        t.parent = parent
    return t


def empty(name, loc=(0, 0, 0), rot_z=0.0, parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.3
    e.location = loc
    e.rotation_euler = (0, 0, rot_z)
    COL.objects.link(e)
    if parent:
        e.parent = parent
    return e


# ================================================================ mobilya
STIL = {
    #          oturak         sirt           ayak
    "hasir": ("hasir", "tik", "tik"),
    "cita": ("tik", "tik", "beyaz_metal"),
    "eames": ("kontrplak", "kontrplak", "celik"),
    "bistro": ("bistro", "bistro", "bistro"),
    "oval": ("gri_minder", "tik", "tik"),
}


def chair(name, parent, xy, face_to=(0, 0), stil="hasir"):
    dx, dy = xy[0] - face_to[0], xy[1] - face_to[1]
    e = empty(name, (xy[0], xy[1], 0), math.atan2(-dx, dy), parent)
    so, si, ay = (M[k] for k in STIL[stil])
    box(name + "_Oturak", (0, 0, 0.45), (0.44, 0.42, 0.05), so, e)
    if stil == "cita":
        for i in range(4):
            box(f"{name}_Cita{i}", (0, 0.2 + i * 0.012, 0.58 + i * 0.09), (0.42, 0.03, 0.06), si, e)
        for sx in (-0.23, 0.23):
            box(f"{name}_Kol{sx}", (sx, 0.0, 0.65), (0.03, 0.42, 0.03), M["beyaz_metal"], e)
    elif stil == "oval":
        box(name + "_Sirt", (0, 0.2, 0.72), (0.40, 0.04, 0.06), si, e)
    else:
        box(name + "_Sirt", (0, 0.2, 0.68), (0.42, 0.04, 0.3), si, e)
    for i, (lx, ly) in enumerate([(-0.19, -0.18), (0.19, -0.18), (-0.19, 0.18), (0.19, 0.18)]):
        h = 0.95 if (ly > 0 and stil in ("hasir", "oval", "cita")) else 0.43
        box(f"{name}_Ayak{i}", (lx, ly, h / 2), (0.03, 0.03, h), ay, e)
    return e


MASALAR = []


def masa(idx, loc, ad, bolge, kat, parent):
    e = empty(f"Masa_{idx:02d}", loc, 0, parent)
    e["masa_id"], e["masa_ad"], e["bolge"], e["kat"] = idx, ad, bolge, kat
    MASALAR.append(e)
    return e


def round_table(idx, loc, ad, bolge, kat, parent, r=0.36, top="mermer", leg="beyaz_metal",
                n=2, stil="hasir", start=0.0, h=0.74):
    e = masa(idx, loc, ad, bolge, kat, parent)
    n_ = f"Masa_{idx:02d}"
    cyl(n_ + "_Tabla", (0, 0, h), r, 0.035, M[top], e)
    cyl(n_ + "_Ayak", (0, 0, h / 2), 0.035, h, M[leg], e, 12)
    cyl(n_ + "_Taban", (0, 0, 0.015), r * 0.6, 0.03, M[leg], e)
    for i in range(n):
        a = start + i * 2 * math.pi / n
        chair(f"{n_}_Sandalye{i+1}", e, ((r + 0.3) * math.cos(a), (r + 0.3) * math.sin(a)), stil=stil)
    return e


def plant(name, c, size=1.0, parent=None, palm=False):
    e = empty(name, c, 0, parent)
    cyl(name + "_Saksi", (0, 0, 0.25 * size), 0.22 * size, 0.5 * size, M["saksi"], e)
    if palm:
        for i in range(6):
            a = i * math.pi / 3
            ball(f"{name}_Yaprak{i}", (0.35 * size * math.cos(a), 0.35 * size * math.sin(a), 1.1 * size),
                 0.3 * size, M["yaprak2"], e, 1, (1.6, 0.5, 0.25))
            bpy.context.active_object.rotation_euler = (0, 0, a)
        cyl(name + "_Govde", (0, 0, 0.75 * size), 0.03 * size, 0.6 * size, M["tik"], e, 8)
    else:
        ball(name + "_Y1", (0, 0, 0.75 * size), 0.35 * size, M["yaprak"], e)
        ball(name + "_Y2", (0.15 * size, 0.1 * size, 1.05 * size), 0.25 * size, M["yaprak2"], e)
    return e


# ================================================================ kok gruplar
DIS = empty("Dis")
ALT = empty("AltKat")
UST = empty("UstKat")

# ================================================================ DIS: teras + kapali dis alan + cephe
# sira (sokaktan iceri): semsiyeli teras (y -13..-6) -> ustu kapali dis alan (y -6..0) -> ic mekan (y 0..)
KX0, KX1 = 4.7, 11.5  # kapali dis alanin (ve girisin) genisligi
bx("Kaide", -1.5, -13.8, -0.5, W + 1.5, D + 15.5, -0.03, M["kaide"], DIS)
bx("Teras_Zemin", -1.0, -13.2, -0.03, W + 1.0, 0.0, 0.0, M["dis_zemin"], DIS)
bx("Bordur", -1.0, -13.5, -0.03, W + 1.0, -13.2, 0.12, M["granit"], DIS)

# kapali alanin iki yanindaki baska dukkanlar (kapali bloklar) + cephe bandi + LED tabela
bx("Komsu_Sol", -0.3, -6.0, 0, KX0, 0.0, SLAB, M["cephe"], DIS)
bx("Komsu_Sag", KX1, -6.0, 0, W + 0.3, 0.0, SLAB, M["cephe"], DIS)
bx("Komsu_Sol_Vitrin", 0.2, -6.06, 0.3, KX0 - 0.4, -6.0, 3.2, M["siyah"], DIS)
bx("Komsu_Sag_Vitrin", KX1 + 0.4, -6.06, 0.3, W - 0.2, -6.0, 3.2, M["siyah"], DIS)
bx("Cephe_Bant", -0.3, -6.3, SLAB, W + 0.3, -6.0, SLAB + 1.5, M["cephe"], DIS)
bx("Kapali_Yan_Sol", KX0 - 0.2, -6.0, SLAB, KX0, 0.0, H, M["siva"], DIS)
bx("Kapali_Yan_Sag", KX1, -6.0, SLAB, KX1 + 0.2, 0.0, H, M["siva"], DIS)
bx("Kapali_On_Kiris", KX0 - 0.2, -6.3, H - 0.5, KX1 + 0.2, -6.0, H, M["cephe"], DIS)
bx("LED_Panel", 2.2, -6.36, SLAB + 0.25, 11.8, -6.3, SLAB + 1.2, M["led"], DIS)
text("LED_Yazi", "ESPRESSOLAB", (7.0, -6.38, SLAB + 0.72), 0.62, M["led_yazi"], (math.radians(90), 0, 0), DIS)

# ustu kapali dis alan: on kenarda saksi kutulari, citali sandalyeler + ahsap masalar
for i, (x0, x1) in enumerate([(KX0 + 0.15, 7.4), (8.8, KX1 - 0.15)]):
    bx(f"Kapali_Saksi{i}", x0, -5.95, 0, x1, -5.35, 0.6, M["beyaz_metal"], DIS)
    n = int((x1 - x0) / 0.5)
    for k in range(n):
        ball(f"Kapali_Saksi{i}_Cali{k}", (x0 + 0.25 + k * 0.5, -5.65, 0.85), 0.24, M["yaprak2"], DIS, 1, (0.8, 0.8, 1.4))
for idx, (x, y) in zip((32, 33, 34, 35), [(6.0, -3.9), (10.2, -3.9), (6.0, -1.5), (10.2, -1.5)]):
    round_table(idx, (x, y, 0), f"Kapali dis {idx-31}", "Ustu kapali dis alan", "zemin", DIS,
                0.38, "tik", "celik", 3, "cita", 0.3)

# semsiyeli teras
for i, x in enumerate([4.3, 9.8]):
    s = empty(f"Semsiye{i+1}", (x, -9.4, 0), 0, DIS)
    cyl(f"Semsiye{i+1}_Direk", (0, 0, 1.5), 0.05, 3.0, M["beyaz_metal"], s, 12)
    cone(f"Semsiye{i+1}_Kumas", (0, 0, 3.05), 3.1, 0.25, 0.75, M["kumas"], s, 4, (0, 0, math.radians(45)))
    cone(f"Semsiye{i+1}_Tepe", (0, 0, 3.55), 0.6, 0.05, 0.3, M["kumas"], s, 4, (0, 0, math.radians(45)))
    cyl(f"Semsiye{i+1}_Ayak", (0, 0, 0.05), 0.45, 0.1, M["granit"], s)

round_table(1, (2.8, -8.2, 0), "Teras 1", "Dis teras", "zemin", DIS, 0.3, "bistro", "bistro", 2, "bistro", 0.3)
round_table(2, (5.8, -10.6, 0), "Teras 2", "Dis teras", "zemin", DIS, 0.3, "bistro", "bistro", 2, "bistro", 1.2)
round_table(3, (8.4, -8.2, 0), "Teras 3", "Dis teras", "zemin", DIS, 0.3, "bistro", "bistro", 2, "bistro", 0.3)
round_table(4, (11.4, -10.6, 0), "Teras 4", "Dis teras", "zemin", DIS, 0.3, "bistro", "bistro", 2, "bistro", 1.2)

for i, (x0, x1) in enumerate([(-0.6, 2.0), (12.0, 14.6)]):
    bx(f"Dis_Saksi{i}", x0, -12.9, 0, x1, -12.1, 0.55, M["beyaz_metal"], DIS)
    for k in range(4):
        ball(f"Dis_Saksi{i}_Cali{k}", (x0 + 0.35 + k * 0.65, -12.5, 0.85), 0.38, M["yaprak"], DIS)
agac = empty("Agac", (W + 0.2, -10.0, 0), 0, DIS)
bx("Agac_Saksi", -0.8, -0.8, 0, 0.8, 0.8, 0.45, M["granit"], agac)
cyl("Agac_Govde", (0, 0, 1.4), 0.1, 2.0, M["tik"], agac, 10)
ball("Agac_Tepe1", (0, 0, 2.9), 1.1, M["yaprak"], agac)
ball("Agac_Tepe2", (-0.4, 0.3, 3.6), 0.75, M["yaprak2"], agac)

# ================================================================ ALT KAT: kabuk
bx("Zemin", 0, 0, -0.02, W, D, 0.0, M["zemin"], ALT)
bx("Sag_Duvar", W, 0, 0, W + 0.3, D + 0.3, H, M["siva"], ALT)
bx("Sol_Duvar_Kesit", -0.3, 0, 0, 0.0, D + 0.3, 0.7, M["siva"], ALT)
bx("Arka_Duvar_Sol", -0.3, D, 0, 5.0, D + 0.3, 5.3, M["siva"], ALT)
bx("Arka_Duvar_Sag", 12.0, D, 0, W, D + 0.3, 5.3, M["siva"], ALT)
bx("Arka_Duvar_Ust", 5.0, D, 4.5, 12.0, D + 0.3, 5.3, M["siva"], ALT)

# atriyum kirisleri + vantilatorler
for i, y in enumerate([21.0, 24.2, 27.4, 30.6, 33.8]):
    bx(f"Kiris{i}", 5.0, y - 0.18, H - 0.55, W, y + 0.18, H, M["siva"], ALT)
for i, (x, y) in enumerate([(7.6, 24.8), (11.4, 29.6)]):
    f = empty(f"Vantilator{i}", (x, y, 0), 0, ALT)
    cyl(f"Vantilator{i}_Cubuk", (0, 0, 6.3), 0.02, 1.6, M["tik"], f, 8)
    cyl(f"Vantilator{i}_Gobek", (0, 0, 5.5), 0.14, 0.12, M["tik"], f, 16)
    for k in range(3):
        a = k * 2 * math.pi / 3
        b = box(f"Vantilator{i}_Kanat{k}", (0.55 * math.cos(a), 0.55 * math.sin(a), 5.5), (0.9, 0.12, 0.02), M["tik"], f)
        b.rotation_euler = (0, 0, a)

# merdiven (sol, girisin hemen yaninda) - 20 basamak, y 0.6 -> 7.4
for i in range(20):
    y0 = 0.6 + i * 0.34
    bx(f"Basamak{i:02d}", 0.15, y0, 0, 1.45, y0 + 0.34, (i + 1) * 0.19, M["merdiven"], ALT)
bx("Merdiven_Korkuluk", 1.45, 0.6, 0.0, 1.5, 7.4, 1.0, M["cam"], ALT)

# ---------------------------------------------------------------- bar (sag)
bar = empty("Bar", (0, 0, 0), 0, ALT)
bx("Arka_Tezgah", 13.25, 1.5, 0, W, 9.5, 0.92, M["celik"], bar)
bx("Arka_Tezgah_Sirt", 13.92, 1.5, 0.92, W, 9.5, 1.75, M["celik"], bar)
for i in range(4):
    cyl(f"Lavabo{i}", (13.6, 3.0 + i * 0.6, 0.93), 0.17, 0.02, M["siyah"], bar, 16)
for i, mk in enumerate(["ekran_b", "ekran_k", "ekran_k", "ekran_f", "ekran_m"]):
    y = 3.4 + i * 1.0
    bx(f"Menu_Ekran{i}", 13.93, y, 2.1, 13.99, y + 0.9, 3.3, M[mk], bar)
bx("Bar_On", 10.6, 2.0, 0, 11.4, 9.0, 1.04, M["burl"], bar)
bx("Bar_Ust", 10.55, 1.95, 1.04, 11.45, 9.05, 1.08, M["celik"], bar)
bx("Bar_Donus", 11.4, 8.4, 0, 13.25, 9.0, 1.04, M["burl"], bar)
bx("Vitrin", 10.62, 6.6, 1.08, 11.38, 8.9, 1.5, M["cam"], bar)
for i in range(5):
    box(f"Vitrin_Pasta{i}", (11.0, 6.85 + i * 0.42, 1.14), (0.35, 0.25, 0.08), M["burl"], bar)
for i, y in enumerate([3.2, 4.0, 4.8]):
    box(f"Kasa_Ekran{i}", (11.15, y, 1.3), (0.06, 0.45, 0.32), M["ekran_m"], bar)
espm = empty("Espresso_Makinesi", (0, 0, 0), 0, bar)
bx("Espresso_Govde", 11.55, 4.7, 0.92, 12.25, 5.9, 1.45, M["celik"], espm)
bx("Espresso_Tezgah", 11.5, 4.5, 0.0, 12.3, 6.1, 0.92, M["celik"], espm)
for i, y in enumerate([2.5, 2.95]):
    cyl(f"Degirmen{i}", (11.0, y, 1.3), 0.11, 0.45, M["siyah"], bar)
    cyl(f"Degirmen{i}_Hazne", (11.0, y, 1.65), 0.1, 0.25, M["cam"], bar)
# girisin yanindaki yuvarlak urun standlari
for i, (x, y) in enumerate([(8.0, 2.0), (9.3, 3.1)]):
    cyl(f"Urun_Standi{i}", (x, y, 0.4), 0.65, 0.8, M["celik"], ALT)
    for k in range(6):
        a = k * math.pi / 3
        box(f"Urun_Standi{i}_Paket{k}", (x + 0.38 * math.cos(a), y + 0.38 * math.sin(a), 0.9),
            (0.16, 0.1, 0.2), M["kirmizi" if k % 2 else "burl"], ALT)

# ---------------------------------------------------------------- orta salon
round_table(5, (4.0, 2.6, 0), "Giris yani 1", "Giris", "zemin", ALT, 0.36, "mermer", "beyaz_metal", 2, "hasir", 0.0)
round_table(6, (5.8, 4.8, 0), "Giris yani 2", "Giris", "zemin", ALT, 0.36, "mermer", "beyaz_metal", 2, "hasir", 0.0)

# oval ortak masa
ov = masa(7, (7.0, 10.6, 0), "Oval ortak masa", "Orta salon", "zemin", ALT)
cyl("Masa_07_Tabla", (0, 0, 0.75), 1.0, 0.06, M["tik"], ov, 40, scale=(1.0, 2.3, 1.0))
cyl("Masa_07_Delik", (0, 0, 0.785), 0.45, 0.012, M["toprak"], ov, 32, scale=(1.0, 3.0, 1.0))
for i, y in enumerate([-1.3, 1.3]):
    bx(f"Masa_07_Ayak{i}", -0.7, y - 0.05, 0, 0.7, y + 0.05, 0.72, M["tik"], ov)
k = 1
for sx in (-1, 1):
    for y in (-1.6, -0.55, 0.55, 1.6):
        xx = sx * (1.0 * math.sqrt(max(0.0, 1 - (y / 2.3) ** 2)) + 0.28)
        chair(f"Masa_07_Sandalye{k}", ov, (xx, y), (0, y), "oval")
        k += 1
chair(f"Masa_07_Sandalye{k}", ov, (0, -2.6), (0, 0), "oval")
chair(f"Masa_07_Sandalye{k+1}", ov, (0, 2.6), (0, 0), "oval")

# Eames kosesi (sol)
round_table(8, (2.6, 9.6, 0), "Eames 1", "Orta salon - sol", "zemin", ALT, 0.4, "turkuaz", "celik", 3, "eames", 0.3)
round_table(9, (2.6, 12.2, 0), "Eames 2", "Orta salon - sol", "zemin", ALT, 0.4, "turkuaz", "celik", 3, "eames", 0.9)
round_table(10, (2.6, 14.8, 0), "Eames 3", "Orta salon - sol", "zemin", ALT, 0.4, "turkuaz", "celik", 3, "eames", 0.3)

# terakota duvar + bank (sag)
bx("Terakota_Panel", 13.95, 9.8, 0, W, 16.0, 3.4, M["terakota"], ALT)
bx("Bank_Oturak", 13.2, 10.2, 0, 13.95, 15.8, 0.45, M["gri_minder"], ALT)
bx("Bank_Sirt", 13.75, 10.2, 0.45, 13.95, 15.8, 0.95, M["gri_minder"], ALT)
for idx, y in ((11, 11.6), (12, 14.4)):
    e = masa(idx, (12.5, y, 0), f"Terakota bank {idx-10}", "Orta salon - sag", "zemin", ALT)
    box(f"Masa_{idx:02d}_Tabla", (0, 0, 0.74), (0.75, 0.75, 0.04), M["tik"], e)
    cyl(f"Masa_{idx:02d}_Ayak", (0, 0, 0.37), 0.04, 0.72, M["celik"], e, 12)
    chair(f"Masa_{idx:02d}_Sandalye1", e, (-0.7, 0.0), (0, 0), "oval")
plant("Palmiye_Orta", (10.0, 15.3, 0), 1.2, ALT, palm=True)

# ---------------------------------------------------------------- atriyum
for i, y in enumerate([16.6, 20.6, 24.8, 29.0, 33.2]):
    bx(f"Kolon{i}", 4.7, y - 0.3, 0, 5.3, y + 0.3, SLAB - 0.3, M["siva"], ALT)

# friz altindaki masalar (hasir sandalyeler)
round_table(13, (7.0, 17.6, 0), "Friz alti 1", "Atriyum - on", "zemin", ALT, 0.38, "mermer", "beyaz_metal", 4, "hasir", 0.785)
round_table(14, (9.6, 17.6, 0), "Friz alti 2", "Atriyum - on", "zemin", ALT, 0.38, "mermer", "beyaz_metal", 4, "hasir", 0.785)
round_table(15, (12.2, 17.6, 0), "Friz alti 3", "Atriyum - on", "zemin", ALT, 0.38, "mermer", "beyaz_metal", 4, "hasir", 0.785)

# atriyumdan asma kata donen (U) merdiven: manzara acikliginin hemen solundan baslar,
# 1. kol one dogru cikar, sahanlikta doner, 2. kol arka duvara dogru cikip asma kata baglanir
for i in range(10):
    yh = 33.9 - i * 0.32
    bx(f"Asma_Merdiven_A{i:02d}", 5.35, yh - 0.32, 0, 6.55, yh, (i + 1) * 0.19, M["merdiven"], ALT)
bx("Asma_Merdiven_Sahanlik", 5.35, 29.7, 0, 7.75, 30.7, 1.9, M["merdiven"], ALT)
for i in range(10):
    yl = 30.7 + i * 0.32
    bx(f"Asma_Merdiven_B{i:02d}", 6.55, yl, 0, 7.75, yl + 0.32, 1.9 + (i + 1) * 0.19, M["merdiven"], ALT)
bx("Asma_Merdiven_Korkuluk_Dis", 7.75, 29.7, 1.9, 7.8, 34.0, 4.8, M["cam"], ALT)
bx("Asma_Merdiven_Korkuluk_On", 5.35, 29.65, 1.9, 7.8, 29.7, 2.9, M["cam"], ALT)

# yuvarlak saksi adasi + kavisli bank
IX, IY = 9.8, 26.4
ada = empty("Saksi_Adasi", (IX, IY, 0), 0, ALT)
cyl("Ada_Bank_Taban", (0, 0, 0.21), 2.6, 0.42, M["fayans"], ada, 48)
cyl("Ada_Bank_Minder", (0, 0, 0.45), 2.6, 0.06, M["zeytin"], ada, 48)
cyl("Ada_Sirt", (0, 0, 0.48), 2.15, 0.96, M["zeytin"], ada, 48)
cyl("Ada_Kenar", (0, 0, 0.97), 2.05, 0.04, M["celik"], ada, 48)
cyl("Ada_Toprak", (0, 0, 0.95), 2.0, 0.06, M["toprak"], ada, 48)
for k, (r, a, s) in enumerate([(0.0, 0, 1.0), (1.2, 0.5, 0.8), (1.1, 2.3, 0.9), (1.2, 4.2, 0.85), (0.6, 5.5, 0.7)]):
    x, y = r * math.cos(a), r * math.sin(a)
    ball(f"Ada_Bitki{k}a", (x, y, 1.5 + s * 0.4), 0.55 * s, M["yaprak"], ada, 1, (1.3, 1.0, 0.8))
    ball(f"Ada_Bitki{k}b", (x + 0.25, y - 0.2, 2.0 + s * 0.5), 0.4 * s, M["yaprak2"], ada, 1, (1.4, 0.7, 0.5))
for i, adeg in enumerate([45, 135, 225, 315]):
    a = math.radians(adeg)
    idx = 16 + i
    e = masa(idx, (IX + 3.25 * math.cos(a), IY + 3.25 * math.sin(a), 0), f"Ada {i+1}", "Atriyum - saksi adasi", "zemin", ALT)
    cyl(f"Masa_{idx:02d}_Tabla", (0, 0, 0.74), 0.36, 0.035, M["mermer"], e)
    cyl(f"Masa_{idx:02d}_Ayak", (0, 0, 0.37), 0.035, 0.72, M["beyaz_metal"], e, 12)
    cyl(f"Masa_{idx:02d}_Taban", (0, 0, 0.015), 0.25, 0.03, M["beyaz_metal"], e)
    chair(f"Masa_{idx:02d}_Sandalye1", e, (0.7 * math.cos(a), 0.7 * math.sin(a)), (0, 0), "hasir")

# asma kat alti (citali sandalyeler, ahsap masalar)
round_table(20, (2.5, 22.6, 0), "Asma kat alti 1", "Atriyum - asma kat alti", "zemin", ALT, 0.4, "tik", "celik", 3, "cita", 0.0)
round_table(21, (2.5, 26.9, 0), "Asma kat alti 2", "Atriyum - asma kat alti", "zemin", ALT, 0.4, "tik", "celik", 3, "cita", 0.5)
round_table(22, (2.5, 31.1, 0), "Asma kat alti 3", "Atriyum - asma kat alti", "zemin", ALT, 0.4, "tik", "celik", 3, "cita", 0.0)

# LOVE duvari (sag)
bx("Fayans_Duvar", 13.94, 22.0, 0, W, 31.4, 6.6, M["fayans"], ALT)
for i, ch in enumerate("LOVE"):
    y = 24.3 + (3 - i) * 1.35  # iceriden duvara bakinca soldan saga L-O-V-E
    cyl(f"Ayna_{ch}", (13.9, y, 3.6), 0.55, 0.05, M["ayna"], ALT, 40, (0, math.radians(90), 0))
    text(f"Harf_{ch}", ch, (13.86, y, 3.6), 0.7, M["pembe"], (math.radians(90), 0, math.radians(-90)), ALT)
round_table(23, (12.9, 22.6, 0), "LOVE duvari 1", "Atriyum - LOVE duvari", "zemin", ALT, 0.36, "tik", "celik", 2, "cita", 1.57)
round_table(24, (12.9, 31.0, 0), "LOVE duvari 2", "Atriyum - LOVE duvari", "zemin", ALT, 0.36, "tik", "celik", 2, "cita", 1.57)

# arka bahce (aciklik arkasi, basamaklarla yukari)
for i in range(4):
    bx(f"Bahce_Basamak{i}", 5.0, D + 0.3 + i * 0.4, 0, 12.0, D + 0.7 + i * 0.4, 0.2 * (i + 1), M["dis_zemin"], ALT)
bx("Bahce_Zemin", -0.3, D + 1.9, 0, W + 0.3, D + 5.0, 0.8, M["dis_zemin"], ALT)
def prism(name, pts, width, m, parent=None):
    """Yol gibi bir seridi zemine (z=0) kadar dolu prizma olarak uretir."""
    v, f = [], []
    for i, (x, y, z) in enumerate(pts):
        a = pts[min(i + 1, len(pts) - 1)]
        b = pts[max(i - 1, 0)]
        dx, dy = a[0] - b[0], a[1] - b[1]
        n = math.hypot(dx, dy) or 1
        px, py = -dy / n * width / 2, dx / n * width / 2
        v += [(x + px, y + py, z), (x - px, y - py, z), (x + px, y + py, 0), (x - px, y - py, 0)]
    for i in range(len(pts) - 1):
        a, b = i * 4, (i + 1) * 4
        f += [(a, a + 1, b + 1, b), (a + 2, b + 2, b + 3, a + 3), (a, b, b + 2, a + 2), (a + 1, a + 3, b + 3, b + 1)]
    k = (len(pts) - 1) * 4
    f += [(0, 2, 3, 1), (k, k + 1, k + 3, k + 2)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    o = bpy.data.objects.new(name, me)
    COL.objects.link(o)
    return _fin(o, m, parent)


manzara = empty("Manzara", (0, 0, 0), 0, ALT)
yol = [(11.0, D + 2.0, 0.8), (12.2, D + 5.0, 1.6), (12.4, D + 8.0, 2.5), (11.2, D + 11.0, 3.4),
       (8.8, D + 13.2, 4.2), (6.5, D + 14.4, 4.8)]
prism("Yamac", [(x, y, z - 0.15) for x, y, z in yol], 7.5, M["yaprak2"], manzara)
prism("Yokus_Yol", yol, 3.0, M["granit"], manzara)
for i in range(len(yol) - 1):
    (x0, y0, z0), (x1, y1, z1) = yol[i], yol[i + 1]
    box(f"Yol_Cizgi{i}", ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2 + 0.01), (0.12, 0.9, 0.02), M["beyaz_metal"], manzara)
    bpy.context.view_layer.update()
    o = bpy.data.objects[f"Yol_Cizgi{i}"]
    o.rotation_euler = (math.atan2(z1 - z0, math.hypot(x1 - x0, y1 - y0)), 0, math.atan2(-(x1 - x0), y1 - y0))
bx("Komsu_Bina", -0.3, D + 6.0, 0, 6.0, D + 14.0, 13.0, M["cephe"], manzara)
for k in range(4):
    bx(f"Komsu_Bina_Pencere{k}", 0.2, D + 5.94, 1.4 + k * 3.0, 5.5, D + 6.0, 2.6 + k * 3.0, M["siyah"], manzara)
for k in range(12):
    x = 0.3 + k * 1.15
    ball(f"Manzara_Cali{k}", (x, D + 4.3 + (k % 3) * 0.4, 1.3), 0.55 + (k % 2) * 0.15,
         M["yaprak" if k % 2 else "yaprak2"], manzara, 1, (1.0, 1.0, 1.5))
for k in range(7):
    ball(f"Bahce_Cali{k}", (5.4 + k * 1.05, D + 2.6, 1.2), 0.45, M["yaprak2" if k % 2 else "yaprak"], ALT)
plant("Bitki_Arka1", (8.4, D - 0.7, 0), 1.0, ALT)
plant("Bitki_Arka2", (11.0, D - 0.7, 0), 1.1, ALT)

# ================================================================ UST KAT
bx("Kapali_Alan_Tavan", KX0 - 0.2, -6.0, H - 0.3, KX1 + 0.2, 0.0, H, M["siva"], UST)
bx("Ust_Zemin_A", 1.6, 0.0, SLAB - 0.3, W, 16.0, SLAB, M["zemin"], UST)
bx("Ust_Zemin_C", 5.0, 16.0, SLAB - 0.3, W, 19.5, SLAB, M["zemin"], UST)
bx("Ust_Zemin_B", 0.0, 7.4, SLAB - 0.3, 1.6, 16.0, SLAB, M["zemin"], UST)
bx("Asma_Kat_Zemin", 0.0, 16.0, SLAB - 0.3, 5.0, D, SLAB, M["zemin"], UST)
# orta salon tavanindaki oval ayna
cyl("Oval_Ayna_Tavan", (7.0, 10.6, SLAB - 0.34), 1.8, 0.06, M["ayna"], UST, 48, scale=(1.0, 2.2, 1.0))
# atriyuma bakan kenar: parapet (ust kat) + cam korkuluk (asma kat)
bx("Parapet_Atriyum", 5.0, 19.3, SLAB, W, 19.5, SLAB + 1.1, M["siva"], UST)
bx("Friz_Bandi", 5.0, 19.45, SLAB - 0.9, W, 19.55, SLAB - 0.3, M["siva"], UST)
bx("Asma_Kat_Cam_Yan", 4.95, 19.5, SLAB, 5.0, 33.1, SLAB + 1.0, M["cam"], UST)
# merdivenin ust ucunu asma kata baglayan kopru (arka duvar dibinde)
bx("Asma_Kat_Kopru", 5.0, 33.1, SLAB - 0.3, 6.55, D, SLAB, M["zemin"], UST)
bx("Asma_Kat_Kopru_Cam", 5.0, 33.05, SLAB, 6.55, 33.1, SLAB + 1.0, M["cam"], UST)
# ust kat ile asma kat arasi kapali
bx("Asma_Kat_Ayirici_On", 0.0, 15.85, SLAB, 5.0, 16.0, SLAB + 2.6, M["siva"], UST)
bx("Asma_Kat_Ayirici_Yan", 4.95, 16.0, SLAB, 5.1, 19.5, SLAB + 2.6, M["siva"], UST)

bx("Ust_Merdiven_Korkuluk", 1.6, 0.6, SLAB, 1.65, 7.4, SLAB + 1.0, M["cam"], UST)

# lavabolar (merdivenden cikinca sola, biraz ileride)
wc = empty("Lavabolar", (0, 0, 0), 0, UST)
bx("WC_Duvar_On", 0.0, 9.9, SLAB, 3.0, 10.05, SLAB + 2.6, M["siva"], wc)
bx("WC_Duvar_Arka", 0.0, 14.0, SLAB, 3.0, 14.15, SLAB + 2.6, M["siva"], wc)
bx("WC_Duvar_Ara", 0.0, 11.95, SLAB, 3.0, 12.1, SLAB + 2.6, M["siva"], wc)
bx("WC_Duvar_Yan1", 2.95, 10.05, SLAB, 3.1, 10.7, SLAB + 2.6, M["siva"], wc)
bx("WC_Duvar_Yan2", 2.95, 11.6, SLAB, 3.1, 12.6, SLAB + 2.6, M["siva"], wc)
bx("WC_Duvar_Yan3", 2.95, 13.4, SLAB, 3.1, 14.0, SLAB + 2.6, M["siva"], wc)
bx("WC_Kapi1", 3.0, 10.7, SLAB, 3.05, 11.6, SLAB + 2.1, M["tik"], wc)
bx("WC_Kapi2", 3.0, 12.6, SLAB, 3.05, 13.4, SLAB + 2.1, M["tik"], wc)
box("WC_Tabela", (3.12, 12.0, SLAB + 2.3), (0.02, 0.35, 0.18), M["ekran_b"], wc)

# ders calisma alani (merdivenden cikinca sag) - tek uzun masa
e = masa(25, (8.8, 8.0, SLAB), "Calisma masasi", "Ust kat - ders calisma", "ust", UST)
e.rotation_euler = (0, 0, math.radians(90))
box("Masa_25_Tabla", (0, 0, 0.74), (9.0, 1.2, 0.05), M["tik"], e)
for j, lx in enumerate([-4.2, 0.0, 4.2]):
    box(f"Masa_25_Ayak{j}", (lx, 0, 0.36), (0.06, 1.0, 0.72), M["siyah"], e)
k = 1
for side in (-1, 1):
    for lx in (-3.75, -2.5, -1.25, 0.0, 1.25, 2.5, 3.75):
        chair(f"Masa_25_Sandalye{k}", e, (lx, side * 0.9), (lx, 0), "hasir")
        k += 1
for lx in (-3.1, -1.0, 1.0, 3.1):
    cyl(f"Masa_25_Lamba{lx}", (lx, 0, 1.0), 0.015, 0.5, M["siyah"], e, 8)
    cyl(f"Masa_25_Lamba{lx}_Bas", (lx, 0, 1.25), 0.1, 0.08, M["lamba"], e, 16)

# uzun masanin ilerisinde (merdivenden cikinca sag taraf) birkac masa
for idx, y in ((36, 3.2), (37, 6.6), (38, 10.0), (39, 13.4)):
    round_table(idx, (12.2, y, SLAB), f"Ust kat sag {idx-35}", "Ust kat - ders calisma", "ust", UST,
                0.4, "tik", "celik", 3, "hasir", 0.3)

# atriyuma bakan parapet kenarindaki kucuk masalar
for idx, x in ((26, 7.0), (27, 9.6), (28, 12.2)):
    round_table(idx, (x, 18.6, SLAB), f"Atriyuma bakan {idx-25}", "Ust kat - atriyum kenari", "ust", UST,
                0.34, "mermer", "beyaz_metal", 2, "hasir", 0.0)
# asma kat masalari
round_table(29, (2.6, 20.5, SLAB), "Asma kat 1", "Asma kat", "ust", UST, 0.42, "tik", "celik", 3, "hasir", 0.0)
round_table(30, (2.6, 25.5, SLAB), "Asma kat 2", "Asma kat", "ust", UST, 0.42, "tik", "celik", 3, "hasir", 0.5)
round_table(31, (2.6, 30.5, SLAB), "Asma kat 3", "Asma kat", "ust", UST, 0.42, "tik", "celik", 3, "hasir", 0.0)
plant("Bitki_Asma", (4.3, 17.0, SLAB), 0.9, UST)

# ================================================================ isik + kamera
sun_d = bpy.data.lights.new("Gunes", "SUN")
sun_d.energy = 2.6
sun_d.angle = math.radians(10)
sun = bpy.data.objects.new("Gunes", sun_d)
sun.rotation_euler = (math.radians(48), math.radians(-12), math.radians(-150))
COL.objects.link(sun)
for i, (x, y, z, e) in enumerate([(7, 5, 3.2, 250), (7, 12, 3.2, 250), (9, 26, 6.0, 600), (3, 26, 3.2, 200),
                                  (8, 7, SLAB + 2.6, 300), (2.6, 26, SLAB + 2.6, 200)]):
    ld = bpy.data.lights.new(f"Ic_Isik{i}", "POINT")
    ld.energy, ld.color, ld.shadow_soft_size = e, (1.0, 0.86, 0.68), 1.0
    lo = bpy.data.objects.new(f"Ic_Isik{i}", ld)
    lo.location = (x, y, z)
    COL.objects.link(lo)

world = bpy.data.worlds.new("Dunya")
scene.world = world
try:
    world.use_nodes = True
except Exception:
    pass
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.78, 0.82, 0.9, 1)
bg.inputs[1].default_value = 0.55
scene.view_settings.view_transform = "Standard"
scene.view_settings.exposure = -0.2

cam_d = bpy.data.cameras.new("Kamera")
cam_d.type = "ORTHO"
cam_d.ortho_scale = 52.0
cam_d.clip_end = 500
cam = bpy.data.objects.new("Kamera", cam_d)
target = (7.0, 15.5, 3.0)
dirv = (-0.542, -0.542, 0.643)  # on-sol ustten bakis
cam.location = tuple(target[i] + dirv[i] * 80 for i in range(3))
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
scene.render.resolution_y = 1600
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"

# ================================================================ kaydet / disa aktar / render
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "espressolab.blend"))
bpy.ops.export_scene.gltf(
    filepath=os.path.join(OUT, "espressolab.glb"),
    export_format="GLB", export_extras=True, export_apply=True, export_yup=True,
    export_cameras=False, export_lights=False,
)

scene.render.filepath = os.path.join(OUT, "render_tum.png")
bpy.ops.render.render(write_still=True)

for o in [UST] + list(UST.children_recursive):
    o.hide_render = True
scene.render.filepath = os.path.join(OUT, "render_altkat.png")
bpy.ops.render.render(write_still=True)

print("TAMAM:", OUT, "masa sayisi:", len(MASALAR))
