"""AC05 - renders, layout UV e diagrama dos nós. Uso:
    python AC05_renderizar.py      (python do módulo bpy 4.5, a partir da raiz do repositório)
Não grava nada no .blend: CPU/amostras/fonte substituta valem só nesta sessão.
"""
import os
from pathlib import Path
import bpy
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

AC5 = Path("AC5").resolve()
bpy.ops.wm.open_mainfile(filepath=str(AC5 / "AC05_AndreCosta.blend"))
sc = bpy.context.scene
sc.cycles.device = "CPU"
sc.cycles.samples = int(os.environ.get("AMOSTRAS", 96))

# Fonte Lagu Sans está no PC do autor; se faltar (ex.: servidor), usa substituta só para este render.
for f in bpy.data.fonts:
    if not Path(bpy.path.abspath(f.filepath)).exists():
        sub = "/usr/share/fonts/truetype/liberation/LiberationSans-" + ("Bold" if "Bold" in f.name else "Regular") + ".ttf"
        if Path(sub).exists():
            f.filepath = sub
            print("fonte substituta:", f.name, "->", sub)


def render(cam, nome, w=1920, h=1080, amostras=None):
    sc.camera = bpy.data.objects[cam]
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
    if amostras:
        sc.cycles.samples = amostras
    sc.render.filepath = str(AC5 / nome)
    bpy.ops.render.render(write_still=True)


SO_DIAGRAMAS = os.environ.get("SO_DIAGRAMAS") == "1"  # pula os renders
if not SO_DIAGRAMAS:
    render("Camera_Principal", "AC05_AndreCosta_render_final.png")
    for cam, nome in [("Cam_Comp_Aviao", "aviao"), ("Cam_Comp_Gaivota", "gaivota"), ("Cam_Comp_Nuvem", "nuvem"),
                      ("Cam_AC05_Esferas", "esferas")]:
        render(cam, f"_tmp_{nome}.png", 960, 540, 64)

    # montagem 2x2 dos close-ups
    ims = [Image.open(AC5 / f"_tmp_{n}.png").convert("RGB") for n in ("aviao", "gaivota", "nuvem", "esferas")]
    M = Image.new("RGB", (1920, 1080))
    for i, im in enumerate(ims):
        M.paste(im, ((i % 2) * 960, (i // 2) * 540))
    M.save(AC5 / "AC05_AndreCosta_closeups_materiais.png")
    for n in ("aviao", "gaivota", "nuvem", "esferas"):
        (AC5 / f"_tmp_{n}.png").unlink()

# layout UV do Aviao, desenhado a partir dos dados reais da malha
# (bpy.ops.uv.export_layout exige GPU e não roda em modo background)
import numpy as np
from matplotlib.collections import LineCollection
av = bpy.data.objects["Aviao"]
me = av.data
uv = me.uv_layers["UVMap"].data
arestas = []
for p in me.polygons:
    pts = [tuple(uv[i].uv) for i in p.loop_indices]
    arestas += [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
fig.patch.set_facecolor("#282828"); ax.set_facecolor("#282828")
ax.imshow(Image.open(AC5 / "texturas" / "metal_escovado_basecolor.jpg").convert("RGB"), extent=(0, 1, 0, 1), alpha=0.55)
ax.add_collection(LineCollection(arestas, colors="#ffffff", linewidths=0.5))
ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color="#ff9f1a", lw=1.5)
ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.05); ax.set_aspect("equal")
ax.set_title(f"UV Editor - Aviao (UVMap): Smart UV Project 66 deg, margem 0.02, escala média das ilhas\n{len(me.polygons)} faces, textura Base Color ao fundo", color="white", fontsize=9)
ax.tick_params(colors="#bbb")
fig.tight_layout(); fig.savefig(AC5 / "AC05_AndreCosta_uv_aviao.png", facecolor=fig.get_facecolor()); plt.close(fig)
um = np.array([(c.uv[0], c.uv[1]) for c in uv])
print("UV min/max", um.min(0), um.max(0))


# --- diagrama do Shader Editor, desenhado a partir da árvore REAL de nós de MAT_Metal_Escovado_PBR
def diagrama(mat, destino):
    nt = bpy.data.materials[mat].node_tree
    fig, ax = plt.subplots(figsize=(16, 8.5), dpi=120)
    ax.set_facecolor("#282828"); fig.patch.set_facecolor("#282828")
    pos, alt = {}, {}
    mostrar = {"TEX_IMAGE": ["Vector"], "MAPPING": ["Vector", "Scale"], "NORMAL_MAP": ["Strength", "Color"],
               "BSDF_PRINCIPLED": ["Base Color", "Metallic", "Roughness", "Normal"], "OUTPUT_MATERIAL": ["Surface"],
               "TEX_COORD": []}
    saidas = {"TEX_COORD": ["UV"], "MAPPING": ["Vector"], "TEX_IMAGE": ["Color"], "NORMAL_MAP": ["Normal"],
              "BSDF_PRINCIPLED": ["BSDF"], "OUTPUT_MATERIAL": []}
    cores = {"TEX_IMAGE": "#7a3f3f", "BSDF_PRINCIPLED": "#2f6f4f", "OUTPUT_MATERIAL": "#6b2f2f",
             "NORMAL_MAP": "#2f4f7a", "MAPPING": "#4a4a6a", "TEX_COORD": "#4a4a6a"}
    soc = {}
    for n in nt.nodes:
        x, y = n.location
        ins = mostrar.get(n.type, [])
        outs = saidas.get(n.type, [])
        extra = 0.0
        titulo = n.label or n.name
        if n.type == "TEX_IMAGE":
            titulo += f"\n[{n.image.colorspace_settings.name}]  {n.image.name}"
            extra = 40
        if n.type == "BSDF_PRINCIPLED":
            titulo += "\n(Principled BSDF)"
        linhas = max(len(ins), len(outs), 1)
        w, h = 230, 50 + extra + 24 * linhas
        ax.add_patch(FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0,rounding_size=8", fc="#3c3c3c", ec="#111", lw=1.2))
        ax.add_patch(FancyBboxPatch((x, y - 42 - extra), w, 42 + extra, boxstyle="round,pad=0,rounding_size=8", fc=cores.get(n.type, "#555"), ec="#111", lw=1.2))
        ax.text(x + 8, y - 8 - extra / 2, titulo, color="white", fontsize=7.2, va="top", fontweight="bold")
        for i, s in enumerate(ins):
            sy = y - 52 - extra - 24 * i
            val = ""
            sk = n.inputs[s]
            if n.type == "BSDF_PRINCIPLED" and not sk.is_linked and hasattr(sk, "default_value") and isinstance(sk.default_value, float):
                val = f" = {sk.default_value:.2f}"
            ax.text(x + 14, sy, s + val, color="#ddd", fontsize=7, va="center")
            soc[(n.name, "in", s)] = (x, sy)
            ax.plot(x, sy, "o", ms=5, color="#c7c729")
        for i, s in enumerate(outs):
            sy = y - 52 - extra - 24 * i
            ax.text(x + w - 14, sy, s, color="#ddd", fontsize=7, va="center", ha="right")
            soc[(n.name, "out", s)] = (x + w, sy)
            ax.plot(x + w, sy, "o", ms=5, color="#c7c729")
    for l in nt.links:
        a = soc.get((l.from_node.name, "out", l.from_socket.name)); b = soc.get((l.to_node.name, "in", l.to_socket.name))
        if a and b:
            import numpy as np
            t = np.linspace(0, 1, 40); k = (1 - np.cos(t * np.pi)) / 2
            ax.plot(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * k, color="#e0e0e0", lw=1.3, alpha=.9)
    ax.set_xlim(-1100, 700 + 260); ax.set_ylim(-640, 360); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(f"{mat} - árvore de nós (Shader Editor)", color="white", fontsize=11)
    fig.tight_layout(); fig.savefig(destino, facecolor=fig.get_facecolor()); plt.close(fig)


diagrama("MAT_Metal_Escovado_PBR", AC5 / "AC05_AndreCosta_shader_editor_metal.png")
print("PRONTO")
