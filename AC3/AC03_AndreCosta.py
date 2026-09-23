"""
AC03 - Parque Geometrico | Transformacoes 2D e 3D no Blender 4.5 LTS
Executar na aba Scripting (Run Script / Alt+P).

Atencao: ao rodar de novo, o script apaga e recria tudo que esta na colecao
AC03_transformacoes. Faca os ajustes manuais (G/R/S) DEPOIS da ultima execucao.
"""
import bpy
import math
from mathutils import Vector

NOME_COLECAO = "AC03_transformacoes"
NOME_ARQUIVO = "AC03_AndreCosta"  
FPS, FRAME_INI, FRAME_FIM = 24, 1, 120  # 120 frames / 24 fps = 5 s

scene = bpy.context.scene


# ---------------------------------------------------------------- utilitarios
def preparar_colecao(nome):
    """Cria a colecao (ou limpa se ja existir) para o script ser reexecutavel."""
    col = bpy.data.collections.get(nome)
    if col is None:
        col = bpy.data.collections.new(nome)
        scene.collection.children.link(col)
    else:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    return col


def mover_para(obj, col):
    """Tira o objeto da colecao atual e coloca na colecao da atividade."""
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def material(nome, rgba):
    mat = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
    mat.diffuse_color = rgba  # cor tambem no modo Solid do viewport
    return mat


def aplicar_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def fcurves_de(obj):
    """F-curves do objeto. No Blender 4.4+ as actions sao em camadas/slots."""
    ad = obj.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "layers") and len(act.layers):
        for layer in act.layers:
            for strip in layer.strips:
                cb = strip.channelbag(ad.action_slot)
                if cb:
                    return cb.fcurves
    return act.fcurves


def definir_interpolacao(obj, interp="BEZIER", easing="EASE_IN_OUT"):
    for fc in fcurves_de(obj):
        for kp in fc.keyframe_points:
            kp.interpolation = interp
            kp.easing = easing


def key(obj, frame, loc=None, rot_graus=None, esc=None):
    """Define transformacoes e grava keyframe. Rotacao em graus -> radianos."""
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert(data_path="location", frame=frame)
    if rot_graus is not None:
        obj.rotation_euler = [math.radians(g) for g in rot_graus]
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    if esc is not None:
        obj.scale = esc
        obj.keyframe_insert(data_path="scale", frame=frame)


# ---------------------------------------------------------------- cena
scene.render.fps = FPS
scene.frame_start = FRAME_INI
scene.frame_end = FRAME_FIM

col = preparar_colecao(NOME_COLECAO)

mat_2d = material("mat_2d", (0.95, 0.55, 0.15, 1))
mat_tri = material("mat_triangulo", (0.90, 0.25, 0.30, 1))
mat_3d = material("mat_3d", (0.20, 0.50, 0.90, 1))
mat_sat = material("mat_satelite", (0.95, 0.85, 0.20, 1))

# ================= ELEMENTOS 2D (todos em z = 0, plano XY) =================
# 2D: translacao em X/Y, rotacao so em Z, escala so em X/Y

# Quadrado
bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
quad = bpy.context.active_object
quad.name = "obj2d_quadrado"
mover_para(quad, col)
quad.location = (-5, 0, 0)                        # translacao em X
quad.rotation_euler = (0, 0, math.radians(45))    # rotacao em Z (graus -> rad)
quad.scale = (0.8, 0.8, 1)                        # escala uniforme em XY
aplicar_mat(quad, mat_2d)

# Triangulo: malha criada direto pelos 3 vertices (equilatero, raio 1)
verts = [(0, 1, 0), (-math.sqrt(3) / 2, -0.5, 0), (math.sqrt(3) / 2, -0.5, 0)]
malha = bpy.data.meshes.new("malha_triangulo")
malha.from_pydata(verts, [], [(0, 1, 2)])
malha.update()
tri = bpy.data.objects.new("obj2d_triangulo", malha)
col.objects.link(tri)
tri.location = (-2, 0, 0)
tri.scale = (1.3, 1.3, 1)
aplicar_mat(tri, mat_tri)

# Circulo (preenchido para aparecer no render)
bpy.ops.mesh.primitive_circle_add(vertices=48, radius=1, fill_type='NGON',
                                  location=(2, 0, 0))
circ = bpy.context.active_object
circ.name = "obj2d_circulo"
mover_para(circ, col)
circ.location.y = 0.5                             # translacao em Y
circ.scale = (1.4, 1.0, 1)                        # escala nao uniforme -> elipse
aplicar_mat(circ, mat_2d)

# ================= ELEMENTOS 3D (fileira atras dos 2D, y = 5) ===============

# Cubo
bpy.ops.mesh.primitive_cube_add(size=1.6, location=(-4, 5, 1))
cubo = bpy.context.active_object
cubo.name = "obj3d_cubo"
mover_para(cubo, col)
aplicar_mat(cubo, mat_3d)

# Cilindro: demonstra espaco GLOBAL x LOCAL
bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=2, location=(0, 5, 1))
cil = bpy.context.active_object
cil.name = "obj3d_cilindro"
mover_para(cil, col)
bpy.ops.object.shade_smooth()
cil.rotation_euler = (math.radians(45), 0, 0)     # rotacao em X
cil.scale = (0.8, 0.8, 1.2)
# Translacao GLOBAL: soma direto no eixo Z do mundo
cil.location += Vector((0, 0, 0.5))
# Translacao LOCAL: 0.5 no eixo Z do proprio objeto (que esta inclinado 45 graus).
# A direcao local e convertida para o mundo pela matriz de rotacao do objeto.
cil.location += cil.rotation_euler.to_matrix() @ Vector((0, 0, 0.5))
aplicar_mat(cil, mat_3d)

# Esfera UV
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9, location=(4, 5, 1.2))
esf = bpy.context.active_object
esf.name = "obj3d_esfera"
mover_para(esf, col)
bpy.ops.object.shade_smooth()
aplicar_mat(esf, mat_3d)

# BONUS - hierarquia: satelite filho da esfera (transformacao composta)
bpy.ops.mesh.primitive_cube_add(size=0.35)
sat = bpy.context.active_object
sat.name = "obj3d_satelite"
mover_para(sat, col)
sat.parent = esf
sat.location = (1.8, 0, 0)   # coordenada LOCAL, relativa a esfera
aplicar_mat(sat, mat_sat)

# ================= ANIMACAO (frames 1 a 120) ================================

# 2D: triangulo translada (Y) e rotaciona (Z), com etapa intermediaria no frame 60
key(tri, 1,   loc=(-2, 0, 0),    rot_graus=(0, 0, 0))
key(tri, 60,  loc=(-2, -2.5, 0), rot_graus=(0, 0, 180))
key(tri, 120, loc=(-2, 0, 0),    rot_graus=(0, 0, 360))
definir_interpolacao(tri, "SINE", "EASE_IN_OUT")        # bonus: easing

# 3D: cubo escala e rotaciona em X e Y
key(cubo, 1,   rot_graus=(0, 0, 0),    esc=(1, 1, 1))
key(cubo, 120, rot_graus=(90, 180, 0), esc=(1.5, 1.5, 0.6))
definir_interpolacao(cubo, "BACK", "EASE_OUT")          # bonus: overshoot

# Esfera gira em Z; o satelite orbita junto (rotacao do pai + posicao do filho)
key(esf, 1,   rot_graus=(0, 0, 0))
key(esf, 120, rot_graus=(0, 0, 360))
definir_interpolacao(esf, "LINEAR", "AUTO")

# ================= CAMERA, LUZ E RENDER =====================================
alvo = bpy.data.objects.new("alvo_camera", None)
col.objects.link(alvo)
alvo.location = (0, 2.5, 0.5)

cam = bpy.data.objects.new("camera_cena", bpy.data.cameras.new("camera_cena"))
col.objects.link(cam)
cam.location = (0, -13, 11)
cam.data.lens = 35
mira = cam.constraints.new('TRACK_TO')
mira.target = alvo
mira.track_axis = 'TRACK_NEGATIVE_Z'
mira.up_axis = 'UP_Y'
scene.camera = cam

sol = bpy.data.objects.new("luz_sol", bpy.data.lights.new("luz_sol", 'SUN'))
col.objects.link(sol)
sol.data.energy = 3
sol.rotation_euler = (math.radians(50), 0, math.radians(30))

try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'   # nome do EEVEE no 4.2-4.5
except TypeError:
    scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.filepath = f"//{NOME_ARQUIVO}.png"   # salva ao lado do .blend

scene.frame_set(60)   # frame do render estatico (meio da animacao)
# Para renderizar pelo script (salve o .blend antes), descomente:
# bpy.ops.render.render(write_still=True)

print("Cena AC03 criada:", [o.name for o in col.objects])