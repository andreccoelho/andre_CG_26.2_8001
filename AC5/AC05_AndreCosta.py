"""AC05 - Materiais PBR e texturas (Blender 4.5 LTS).

Uso (a partir da raiz do repositório):
    blender -b AC4/AC04_AndreCosta.blend --python AC5/AC05_AndreCosta.py

Parte da cópia da AC04, aplica materiais Principled BSDF e salva AC5/AC05_AndreCosta.blend.
Pré-requisito: python AC5/AC05_gerar_texturas.py <pasta do cristo extraído> AC5/texturas
"""
import math
from pathlib import Path
import bpy

RAIZ = Path(bpy.data.filepath).resolve().parent.parent if bpy.data.filepath else Path.cwd()
AC5 = Path(__file__).resolve().parent if "__file__" in globals() else RAIZ / "AC5"
TEX = AC5 / "texturas"
SAIDA = AC5 / "AC05_AndreCosta.blend"
scene = bpy.context.scene


# ---------------------------------------------------------------- utilidades
def img(nome_arquivo, data):
    """Carrega a imagem, define o espaço de cor e EMPACOTA no .blend."""
    i = bpy.data.images.load(str(TEX / nome_arquivo), check_existing=True)
    i.colorspace_settings.name = "Non-Color" if data else "sRGB"
    i.pack()
    return i


def novo_material(nome):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (700, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (400, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m, nt, bsdf


def tex_node(nt, nome, imagem, x, y, label, uv_scale=(1, 1), mapping=None, coord=None):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.name, n.label, n.image, n.location = nome, label, imagem, (x, y)
    n.interpolation, n.extension = "Linear", "REPEAT"
    nt.links.new(mapping.outputs["Vector"], n.inputs["Vector"])
    return n


def cadeia_pbr(nt, bsdf, prefixo, base, rough, normal, uv_scale, forca_normal, uv_name="UVMap"):
    """Texture Coordinate(UV) -> Mapping -> 3 Image Textures -> Principled BSDF."""
    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-1050, 0); tc.label = "UV"
    mp = nt.nodes.new("ShaderNodeMapping"); mp.location = (-700, 0); mp.label = "Tiling"
    mp.inputs["Scale"].default_value = (uv_scale, uv_scale, 1)
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    nb = tex_node(nt, f"{prefixo}_BaseColor", base, -420, 280, "Base Color (sRGB)", mapping=mp)
    nr = tex_node(nt, f"{prefixo}_Roughness", rough, -420, 0, "Roughness (Non-Color)", mapping=mp)
    nn = tex_node(nt, f"{prefixo}_Normal", normal, -420, -280, "Normal (Non-Color)", mapping=mp)
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.location = (-100, -280)
    nm.space, nm.uv_map = "TANGENT", uv_name
    nm.inputs["Strength"].default_value = forca_normal
    nt.links.new(nb.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(nr.outputs["Color"], bsdf.inputs["Roughness"])
    nt.links.new(nn.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])


def aplicar(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


# ---------------------------------------------------------------- coleção
col = bpy.data.collections.get("AC05_Materiais_Texturas") or bpy.data.collections.new("AC05_Materiais_Texturas")
if col.name not in scene.collection.children:
    scene.collection.children.link(col)

# ---------------------------------------------------------------- materiais
# 1) Aviao: metal escovado (3 mapas)
m_metal, nt, b = novo_material("MAT_Metal_Escovado_PBR")
b.inputs["Metallic"].default_value = 1.0
b.inputs["Base Color"].default_value = (0.62, 0.045, 0.04, 1)
b.inputs["Roughness"].default_value = 0.35
cadeia_pbr(nt, b, "Metal", img("metal_escovado_basecolor.jpg", False),
           img("metal_escovado_roughness.png", True), img("metal_escovado_normal.png", True),
           uv_scale=2.0, forca_normal=0.6)

# 2) Gaivota: madeira (3 mapas), dielétrico
m_mad, nt, b = novo_material("MAT_Madeira_PBR")
b.inputs["Metallic"].default_value = 0.0
b.inputs["Base Color"].default_value = (0.45, 0.27, 0.12, 1)
b.inputs["Roughness"].default_value = 0.6
cadeia_pbr(nt, b, "Madeira", img("madeira_basecolor.jpg", False),
           img("madeira_roughness.png", True), img("madeira_normal.png", True),
           uv_scale=1.0, forca_normal=0.8)

# 3) Nuvem: espelho (cor sólida, sem textura)
m_esp, nt, b = novo_material("MAT_Espelho_PBR")
b.inputs["Base Color"].default_value = (0.78, 0.88, 1.0, 1)  # leve azul: preserva a identidade da nuvem
b.inputs["Metallic"].default_value = 1.0
b.inputs["Roughness"].default_value = 0.06

# 4) Cristo + montanha: textura de cor do modelo original (Sketchfab), pedra não metálica
m_cri, nt, b = novo_material("MAT_Cristo_Pedra_PBR")
tc = nt.nodes.new("ShaderNodeTexCoord"); tc.location = (-700, 0)
nb = nt.nodes.new("ShaderNodeTexImage"); nb.location = (-400, 0)
nb.name, nb.label, nb.image = "Cristo_BaseColor", "Base Color (sRGB)", img("cristo_basecolor_4k.jpg", False)
nt.links.new(tc.outputs["UV"], nb.inputs["Vector"])
nt.links.new(nb.outputs["Color"], b.inputs["Base Color"])
b.inputs["Metallic"].default_value = 0.0
b.inputs["Roughness"].default_value = 0.85
b.inputs["Specular IOR Level"].default_value = 0.3

# 5) Palavra Ibmec: cor lisa, sem textura nem relevo (legibilidade)
m_ib, nt, b = novo_material("MAT_Ibmec_PBR")
b.inputs["Base Color"].default_value = (0.80, 0.80, 0.80, 1)  # mesmo cinza-claro da AC04
b.inputs["Metallic"].default_value = 0.0
b.inputs["Roughness"].default_value = 0.5

# ---------------------------------------------------------------- aplicação
for o in bpy.data.objects:
    if o.name.startswith("Aviao"):
        aplicar(o, m_metal)
    elif o.name.startswith("Gaivota"):
        aplicar(o, m_mad)
    elif o.name.startswith("Nuvem"):
        aplicar(o, m_esp)
aplicar(bpy.data.objects["ChristTheRedeemer.002"], m_cri)
for n in ("IBMEC_Esfera", "IBMEC_I", "IBMEC_Serifas_b"):
    aplicar(bpy.data.objects[n], m_ib)
bpy.data.objects["Text"].data.materials.clear()
bpy.data.objects["Text"].data.materials.append(m_ib)

# ---------------------------------------------------------------- World
# Ajuste de iluminação (registrado no relatório): o espelho só mostra o que reflete, e o World da AC04
# (strength 0.18) é escuro. A força do World passa a valer 0.90 APENAS para raios glossy (reflexos);
# para raios de câmera e difusos continua 0.18, então a iluminação dos outros objetos fica igual à AC04.
w = scene.world.node_tree
bg = w.nodes["Background"]
for n in [n for n in w.nodes if n.type == "TEX_ENVIRONMENT"]:  # HDRI desconectado (caminho D:/ quebrado)
    if n.image:
        bpy.data.images.remove(n.image)
    w.nodes.remove(n)
lp = w.nodes.new("ShaderNodeLightPath"); lp.location = (-500, -200)
ma = w.nodes.new("ShaderNodeMath"); ma.operation = "MULTIPLY_ADD"; ma.location = (-250, -200)
ma.label = "0.18 + 0.72 * Is Glossy Ray"
ma.inputs[1].default_value, ma.inputs[2].default_value = 0.72, 0.18
w.links.new(lp.outputs["Is Glossy Ray"], ma.inputs[0])
w.links.new(ma.outputs["Value"], bg.inputs["Strength"])

# ---------------------------------------------------------------- UVs
def unwrap(obj):
    """Smart UV Project + escala média das ilhas (densidade de texel uniforme)."""
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if "UVMap" not in obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02, scale_to_bounds=False)
    bpy.ops.uv.select_all(action="SELECT")
    try:
        bpy.ops.uv.average_islands_scale()
        bpy.ops.uv.pack_islands(margin=0.02)
    except RuntimeError as e:
        print("aviso UV:", e)
    bpy.ops.object.mode_set(mode="OBJECT")

for o in bpy.data.objects:
    if o.name.startswith(("Aviao", "Gaivota")):
        unwrap(o)

# ---------------------------------------------------------------- esferas de referência PBR (coleção AC05)
ref = bpy.data.objects["Ref_Phong"]
cam_ref = bpy.data.objects["Cam_Comp_Esferas"]
dz = -6.0
pares = [("Ref_PBR_Metal", m_metal, -62.07, 38.6), ("Ref_PBR_Madeira", m_mad, -60.0, 40.0), ("Ref_PBR_Espelho", m_esp, -57.93, 41.4)]
for nome, mat, x, y in pares:
    e = ref.copy(); e.data = ref.data.copy(); e.name = nome
    e.location = (x, y, 30 + dz)
    e.data.materials.clear(); e.data.materials.append(mat)
    for c in list(e.users_collection):
        c.objects.unlink(e)
    col.objects.link(e)
cam = cam_ref.copy(); cam.data = cam_ref.data.copy(); cam.name = "Cam_AC05_Esferas"
cam.location = (cam_ref.location.x, cam_ref.location.y, cam_ref.location.z + dz)
for c in list(cam.users_collection):
    c.objects.unlink(cam)
col.objects.link(cam)

bpy.ops.file.pack_all() if False else None
bpy.ops.wm.save_as_mainfile(filepath=str(SAIDA), compress=True)
print("SALVO", SAIDA)
