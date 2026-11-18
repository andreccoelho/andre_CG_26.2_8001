"""AP2 - "Origens": animação de 15 s (Blender 4.5 LTS).

Uso (a partir da raiz do repositório):
    blender -b AC5/AC05_AndreCosta.blend --python AP2/AP2_AndreCosta.py

Parte de uma cópia da AC05 (o arquivo da AC05 não é alterado) e salva AP2/AP2_AndreCosta.blend com:
câmera animada, letras do Ibmec emergindo do morro, avião em Follow Path, gaivotas em bando com
batida de asas (shape key), nuvens à deriva, luz que esquenta, céu em gradiente e saída MP4/H.264.
"""
import math
from pathlib import Path
import bpy
from mathutils import Vector, Matrix

RAIZ = Path(__file__).resolve().parent.parent if "__file__" in globals() else Path.cwd()
SAIDA = RAIZ / "AP2" / "AP2_AndreCosta.blend"
sc = bpy.context.scene
D = bpy.data.objects
F0, F1 = 1, 360


# ------------------------------------------------------------------ utilidades
def colecao(nome, pai):
    c = bpy.data.collections.get(nome) or bpy.data.collections.new(nome)
    if c.name not in pai.children:
        pai.children.link(c)
    return c


def mover(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def key(alvo, prop, frame, valor=None, interp="BEZIER", easing="AUTO", index=-1):
    if valor is not None:
        setattr(alvo, prop, valor)
    alvo.keyframe_insert(prop, frame=frame, index=index)
    ad = alvo.animation_data if hasattr(alvo, "animation_data") else alvo.id_data.animation_data
    caminho = alvo.path_from_id(prop) if not isinstance(alvo, bpy.types.ID) else prop
    for fc in ad.action.fcurves:
        if fc.data_path == caminho:
            for kp in fc.keyframe_points:
                if abs(kp.co.x - frame) < 0.01:
                    kp.interpolation, kp.easing = interp, easing


def fcurves(id_):
    return id_.animation_data.action.fcurves if id_.animation_data and id_.animation_data.action else []


def curva(nome, pontos, col, ciclica=False, tilts=None):
    cu = bpy.data.curves.get(nome) or bpy.data.curves.new(nome, "CURVE")
    cu.splines.clear()
    cu.dimensions = "3D"
    cu.twist_mode = "Z_UP"
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pontos) - 1)
    for i, p in enumerate(pontos):
        bp = sp.bezier_points[i]
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
        bp.tilt = tilts[i] if tilts else 0.0
    sp.use_cyclic_u = ciclica
    ob = D.get(nome) or bpy.data.objects.new(nome, cu)
    if ob.name not in col.objects:
        col.objects.link(ob)
    ob.hide_render = True
    return ob


def follow_path(obj, caminho, duracao, inicio=F0, fim=F1, eixo="FORWARD_X"):
    """Follow Path com 'Follow Curve': o objeto aponta na tangente. Velocidade constante (LINEAR)."""
    caminho.data.path_duration = duracao
    caminho.data.use_path = True
    c = obj.constraints.new("FOLLOW_PATH")
    c.name = "Follow_Path"
    c.target, c.use_curve_follow, c.forward_axis, c.up_axis = caminho, True, eixo, "UP_Z"
    caminho.data.eval_time = 0
    key(caminho.data, "eval_time", inicio, 0, "LINEAR")
    caminho.data.eval_time = duracao
    key(caminho.data, "eval_time", fim, duracao, "LINEAR")
    return c


# ------------------------------------------------------------------ cena e coleções
sc.frame_start, sc.frame_end = F0, F1
sc.render.fps, sc.render.fps_base = 24, 1.0
sc.frame_current = 180
raiz = bpy.data.collections["AP1_Ibmec_Conceito"]
col_anim = colecao("AP2_Animacao", raiz)
col_traj = colecao("AP2_Trajetos", col_anim)

# Estudos da AC04/AC05 (esferas e câmeras de comparação) ficam no arquivo, mas fora do render final.
for nome in ("Materiais_Referencia", "AC05_Materiais_Texturas", "Cameras_Comparacao"):
    bpy.data.collections[nome].hide_render = True

for m in list(sc.timeline_markers):
    sc.timeline_markers.remove(m)
for nome, f in [("1_Inicio_plano_aberto", 1), ("2_Letras_emergem", 90), ("Pico_logo_AP1", 180),
                ("3_Encerramento", 270), ("Fim", 360)]:
    sc.timeline_markers.new(nome, frame=f)

# ------------------------------------------------------------------ CÂMERA (dolly-in com alvo)
cam = D["Camera_Principal"]
C180 = cam.matrix_world.translation.copy()               # posição da AP1 = enquadramento do frame 180
fwd = (cam.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
fwd_h = Vector((fwd.x, fwd.y, 0)).normalized()
dir_r = Vector((fwd_h.y, -fwd_h.x, 0))                  # direita do quadro (horizontal)
UP = Vector((0, 0, 1))
DIST = 24.6
T180 = C180 + fwd * DIST                                 # ponto que a câmera da AP1 olha (centro do logo)

alvo = D.get("Camera_Alvo") or bpy.data.objects.new("Camera_Alvo", None)
alvo.empty_display_type, alvo.empty_display_size = "SPHERE", 0.6
if alvo.name not in col_anim.objects:
    col_anim.objects.link(alvo)
cam.constraints.clear()
tt = cam.constraints.new("TRACK_TO")
tt.name, tt.target, tt.track_axis, tt.up_axis = "Track_Alvo", alvo, "TRACK_NEGATIVE_Z", "UP_Y"
cam.data.lens = 50
cam.data.dof.use_dof = False

poses_cam = [  # frame, posição da câmera, alvo
    (1,   T180 - fwd * 46 - dir_r * 7 + UP * 7.0, T180 + UP * 3.2),   # plano aberto: morro inteiro + Cristo
    (180, C180,                                    T180),              # composição da AP1
    (300, T180 - fwd * 21.8 + UP * 0.2, T180 + UP * 0.45),           # quadro frontal: logo + Cristo
    (360, T180 - fwd * 21.2 + UP * 0.2, T180 + UP * 0.45),           # respiro: drift mínimo
]
for f, p, a in poses_cam:
    key(cam, "location", f, p, "BEZIER")
    key(alvo, "location", f, a, "BEZIER")
for fc in list(fcurves(cam)) + list(fcurves(alvo)):
    for kp in fc.keyframe_points:
        kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"

# ------------------------------------------------------------------ PALAVRA IBMEC: letras emergem da rocha
texto = D["Text"]
texto.name = "Ibmec_Palavra_Pivo"          # pivô (não renderiza); as letras são objetos filhos
mat_ib = bpy.data.materials["MAT_Ibmec_PBR"]
mat_inv = bpy.data.materials.get("MAT_Invisivel") or bpy.data.materials.new("MAT_Invisivel")
mat_inv.use_nodes = True
nt = mat_inv.node_tree
nt.nodes.clear()
o_ = nt.nodes.new("ShaderNodeOutputMaterial")
t_ = nt.nodes.new("ShaderNodeBsdfTransparent")
nt.links.new(t_.outputs[0], o_.inputs[0])
mat_inv.surface_render_method = "DITHERED"

letras = []
for i, ch in enumerate(texto.data.body):
    nome = f"Ibmec_Letra_{ch}"
    ob = D.get(nome)
    if ob is None:
        ob = texto.copy()
        ob.data = texto.data.copy()
        ob.name = ob.data.name = nome
        ob.animation_data_clear()
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    for c in texto.users_collection:
        c.objects.link(ob)
    ob.parent = texto
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.location, ob.rotation_euler, ob.scale = (0, 0, 0), (0, 0, 0), (1, 1, 1)
    ob.data.materials.clear()
    ob.data.materials.append(mat_ib)   # slot 0: letra visível
    ob.data.materials.append(mat_inv)  # slot 1: demais letras
    for j, fmt in enumerate(ob.data.body_format):
        fmt.material_index = 0 if j == i else 1
    ob.hide_render = ob.hide_viewport = False
    letras.append(ob)
texto.hide_render = True
texto.hide_viewport = True

PROF = -3.0        # deslocamento (eixo Z local, normal da rocha) que esconde a letra dentro do morro
DUR = 34           # duração da subida de cada letra (≈1,4 s)


def emergir(ob, inicio, z_final):
    ob.location.z = z_final + PROF
    key(ob, "location", inicio, None, "BACK", "EASE_OUT", index=2)
    ob.location.z = z_final
    key(ob, "location", inicio + DUR, None, "BEZIER", "AUTO", index=2)
    for fc in fcurves(ob):
        for kp in fc.keyframe_points:
            if kp.interpolation == "BACK":
                kp.back = 1.1


# I (com as serifas) primeiro, depois b, m, e, c a cada 14 frames (defasagem = "construção")
I, serif, ponto = D["IBMEC_I"], D["IBMEC_Serifas_b"], D["IBMEC_Esfera"]
emergir(I, 92, I.location.z)
emergir(serif, 92, serif.location.z)
for k, ob in enumerate(letras):
    # Cada objeto-letra contém a palavra inteira (as outras letras com MAT_Invisivel). Um recuo mínimo
    # (0.004 no eixo Z local) evita faces coplanares entre a letra visível e as cópias invisíveis.
    emergir(ob, 106 + 14 * k, 0.004 * k)

# pingo do i: cai do alto e quica no lugar (BOUNCE)
y0, s0 = ponto.location.y, ponto.scale.copy()
ponto.location.y = y0 + 3.0
ponto.scale = (0, 0, 0)
key(ponto, "scale", 188, None, "BEZIER")
key(ponto, "location", 188, None, "BOUNCE", "EASE_OUT", index=1)
ponto.scale = s0
key(ponto, "scale", 194, None, "BEZIER")
ponto.location.y = y0
key(ponto, "location", 216, None, "BEZIER", index=1)

# Material da marca: azul Ibmec liso (sem textura, para não prejudicar a leitura) com verniz leve.
b = mat_ib.node_tree.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.004, 0.06, 0.25, 1)   # ≈ #0B4489 em sRGB
b.inputs["Metallic"].default_value = 0.0
b.inputs["Roughness"].default_value = 0.32
b.inputs["Coat Weight"].default_value = 0.35
b.inputs["Coat Roughness"].default_value = 0.12

# Pingo do i em amarelo (cor de destaque da marca): mesma receita PBR do azul, só muda a cor base.
mat_pt = bpy.data.materials.get("MAT_Ibmec_Ponto_Amarelo") or mat_ib.copy()
mat_pt.name = "MAT_Ibmec_Ponto_Amarelo"
mat_pt.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.93, 0.48, 0.0, 1)  # ≈ #F7B800
ponto.data.materials.clear()
ponto.data.materials.append(mat_pt)

# ------------------------------------------------------------------ AVIÃO: Follow Path da esquerda p/ direita
av = D["Aviao"]


def pto(u, z, d):  # ponto no espaço do enquadramento da AP1: u = lateral, d = profundidade, z = altura
    p = C180 + fwd_h * d + dir_r * u
    return Vector((p.x, p.y, z))


traj_av = curva("Trajeto_Aviao", [pto(-22, 16.0, 37), pto(-11, 15.2, 36), pto(0, 14.0, 34),
                                  pto(10, 13.0, 33), pto(21, 12.6, 33)], col_traj,
                tilts=[0.0, -0.18, -0.10, -0.22, -0.05])
av.location, av.rotation_euler = (0, 0, 0), (0, 0, 0)
follow_path(av, traj_av, 360)

# ------------------------------------------------------------------ GAIVOTAS: bando + batida de asas
CR = Vector((0.08, -0.1, 11.6))   # topo do Cristo (centróide dos vértices altos do modelo)
cs = C180 - fwd_h * 21  # posição aproximada da câmera no frame 1 (para o voo de primeiro plano)
CO = Vector((CR.x, CR.y, 10.9))   # centro da órbita (altura dos braços do Cristo)
RO = 4.5
pts_g = [
    cs + fwd_h * 14 - dir_r * 8 + UP * 5.0,      # entra pela esquerda, em primeiro plano
    cs + fwd_h * 20 - dir_r * 1 + UP * 5.0,
    CO - fwd_h * 8 + dir_r * 3,                  # aproxima-se do Cristo pela frente
    CO + dir_r * RO + UP * 0.3,                  # e passa a circulá-lo
    CO + fwd_h * RO + UP * 0.5,
    CO - dir_r * RO + UP * 0.2,
    CO - fwd_h * RO - UP * 0.2,
    CO + dir_r * RO + UP * 0.3,
    CO + fwd_h * RO + UP * 0.5,
    CO - dir_r * RO + UP * 0.2,
    CO - fwd_h * RO - UP * 0.2,
]
traj_g = curva("Trajeto_Gaivotas", pts_g, col_traj,
               tilts=[0, 0.1, 0.2, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3])
bando = D.get("Gaivotas_Bando") or bpy.data.objects.new("Gaivotas_Bando", None)
bando.empty_display_type, bando.empty_display_size = "ARROWS", 0.8
if bando.name not in col_anim.objects:
    col_anim.objects.link(bando)
bando.location = (0, 0, 0)
bando.constraints.clear()
follow_path(bando, traj_g, 360)

formacao = {"Gaivota": (0, 0, 0), "Gaivota.001": (-0.9, 0.8, 0.25), "Gaivota.002": (-0.8, -0.9, -0.2)}
fase = {"Gaivota": 0, "Gaivota.001": 3, "Gaivota.002": 6}
for nome, off in formacao.items():
    g = D[nome]
    g.parent = bando
    g.matrix_parent_inverse = Matrix.Identity(4)
    g.location, g.rotation_euler, g.scale = off, (0, 0, 0), (0.6, 0.6, 0.6)
    me = g.data
    if me.shape_keys is None:
        g.shape_key_add(name="Basis", from_mix=False)
    sk = me.shape_keys.key_blocks.get("Asas_Cima") or g.shape_key_add(name="Asas_Cima", from_mix=False)
    sk.slider_min, sk.slider_max = -1.0, 1.0
    base = me.shape_keys.key_blocks["Basis"]
    ANG, Y0 = math.radians(38), 0.06       # asas giram em torno do eixo do corpo (X local)
    for i, v in enumerate(base.data):
        co = v.co.copy()
        if abs(co.y) > Y0:
            s = 1 if co.y > 0 else -1
            dy, dz = abs(co.y) - Y0, co.z
            a = ANG
            co.y = s * (Y0 + dy * math.cos(a) - dz * math.sin(a) * 0)
            co.z = dz + dy * math.sin(a)
        sk.data[i].co = co
    # ciclo de 10 frames (2,4 batidas/s): cima (1) -> baixo (-0.7) -> cima, com modificador Cycles
    p0 = 1 + fase[nome]
    for f, v in [(p0, 1.0), (p0 + 5, -0.7), (p0 + 10, 1.0)]:
        sk.value = v
        sk.keyframe_insert("value", frame=f)
    for fc in me.shape_keys.animation_data.action.fcurves:
        fc.modifiers.new("CYCLES")

# ------------------------------------------------------------------ NUVENS: deriva lenta (paralaxe)
for nome, desloc in (("Nuvem", 2.2), ("Nuvem.001", 1.3)):
    n = D[nome]
    p = n.location.copy()
    key(n, "location", F0, p - dir_r * desloc / 2, "LINEAR")
    key(n, "location", F1, p + dir_r * desloc / 2, "LINEAR")

# ------------------------------------------------------------------ ILUMINAÇÃO
sol = D["Luz_Principal"]
key(sol.data, "color", 1, (1.0, 0.95, 0.88))
key(sol.data, "color", 300, (1.0, 0.80, 0.60))
key(sol.data, "energy", 1, 2.2)
key(sol.data, "energy", 300, 2.6)
key(sol, "rotation_euler", 1, sol.rotation_euler.copy())
r = sol.rotation_euler.copy(); r.x += math.radians(6)        # sol desce ~6° ao longo da peça
key(sol, "rotation_euler", 360, r)

# Luz de destaque do logo (Area), acende quando as letras emergem
col_luz = bpy.data.collections["Iluminacao"]
ld = bpy.data.lights.get("Luz_Destaque_Ibmec") or bpy.data.lights.new("Luz_Destaque_Ibmec", "AREA")
ld.shape, ld.size, ld.size_y = "RECTANGLE", 7.0, 3.0
ld.color = (1.0, 0.90, 0.78)
ld.use_shadow = True
lo = D.get("Luz_Destaque_Ibmec") or bpy.data.objects.new("Luz_Destaque_Ibmec", ld)
if lo.name not in col_luz.objects:
    col_luz.objects.link(lo)
lo.location = T180 - fwd_h * 9 - dir_r * 3 + UP * 4
d = (T180 - lo.location).normalized()
lo.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
key(ld, "energy", 80, 0.0)
key(ld, "energy", 170, 900.0)
key(ld, "energy", 360, 750.0)

# Céu: gradiente quente no horizonte, visto só pelos raios de câmera.
# Raios de luz difusa/glossy continuam com o World da AC05 (0.18 / 0.90), então os materiais
# recebem a mesma iluminação ambiente da AC05.
w = sc.world.node_tree
bg = w.nodes["Background"]
saida = w.nodes["World Output"]
if "Ceu_Gradiente" not in w.nodes:
    tc = w.nodes.new("ShaderNodeTexCoord"); tc.location = (-1300, 300)
    sep = w.nodes.new("ShaderNodeSeparateXYZ"); sep.location = (-1100, 300)
    w.links.new(tc.outputs["Generated"], sep.inputs[0])
    rampa_fria = w.nodes.new("ShaderNodeValToRGB"); rampa_fria.location = (-900, 450); rampa_fria.label = "Céu frio (início)"
    rampa_quente = w.nodes.new("ShaderNodeValToRGB"); rampa_quente.location = (-900, 200); rampa_quente.label = "Céu quente (fim)"
    for rp, hor, zen in ((rampa_fria, (0.62, 0.70, 0.82, 1), (0.16, 0.30, 0.58, 1)),
                         (rampa_quente, (0.98, 0.62, 0.38, 1), (0.20, 0.30, 0.58, 1))):
        rp.color_ramp.elements[0].position, rp.color_ramp.elements[0].color = 0.0, hor
        rp.color_ramp.elements[1].position, rp.color_ramp.elements[1].color = 0.35, zen
        w.links.new(sep.outputs["Z"], rp.inputs["Fac"])
    mix = w.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.name = "Ceu_Mix"; mix.location = (-600, 350)
    w.links.new(rampa_fria.outputs["Color"], mix.inputs[6])
    w.links.new(rampa_quente.outputs["Color"], mix.inputs[7])
    ceu = w.nodes.new("ShaderNodeBackground"); ceu.name = "Ceu_Gradiente"; ceu.location = (-350, 350)
    ceu.inputs["Strength"].default_value = 1.0
    w.links.new(mix.outputs[2], ceu.inputs["Color"])
    lp = w.nodes.new("ShaderNodeLightPath"); lp.location = (-350, 600)
    ms = w.nodes.new("ShaderNodeMixShader"); ms.location = (-100, 300)
    w.links.new(lp.outputs["Is Camera Ray"], ms.inputs[0])
    w.links.new(bg.outputs[0], ms.inputs[1])
    w.links.new(ceu.outputs[0], ms.inputs[2])
    w.links.new(ms.outputs[0], saida.inputs["Surface"])
mix = w.nodes["Ceu_Mix"]
mix.inputs[0].default_value = 0.0
mix.inputs[0].keyframe_insert("default_value", frame=40)
mix.inputs[0].default_value = 1.0
mix.inputs[0].keyframe_insert("default_value", frame=300)

# ------------------------------------------------------------------ RENDER E SAÍDA
r = sc.render
sc.render.engine = "CYCLES"
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPENIMAGEDENOISE"
sc.cycles.use_adaptive_sampling = True
sc.cycles.transparent_max_bounces = 16   # raios atravessam as cópias invisíveis das letras
r.use_persistent_data = True
r.resolution_x, r.resolution_y, r.resolution_percentage = 1920, 1080, 100
r.use_motion_blur = False
r.image_settings.file_format = "FFMPEG"
r.ffmpeg.format = "MPEG4"
r.ffmpeg.codec = "H264"
r.ffmpeg.constant_rate_factor = "HIGH"
r.ffmpeg.ffmpeg_preset = "GOOD"
r.ffmpeg.audio_codec = "NONE"
r.filepath = "//AP2_AndreCosta.mp4"
sc.camera = cam

# Fonte Lagu Sans empacotada no .blend (o "I" e as serifas foram modelados nas medidas dela).
# Se o caminho original (PC do autor) não existir, procura o mesmo arquivo em LAGU_SANS_DIR.
import os
pasta_fonte = os.environ.get("LAGU_SANS_DIR")
for f in bpy.data.fonts:
    if f.packed_file is not None or f.filepath == "<builtin>":
        continue
    if not Path(bpy.path.abspath(f.filepath)).exists() and pasta_fonte:
        alt = Path(pasta_fonte) / Path(f.filepath.replace("\\", "/")).name
        if alt.exists():
            f.filepath = str(alt)
    if Path(bpy.path.abspath(f.filepath)).exists():
        f.pack()
        print("fonte empacotada:", f.name)
    else:
        print("AVISO: fonte não encontrada, não empacotada:", f.name, f.filepath)

bpy.ops.wm.save_as_mainfile(filepath=str(SAIDA), compress=True, relative_remap=True)
print("SALVO", SAIDA)
