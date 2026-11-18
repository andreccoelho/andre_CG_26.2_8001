"""AP2 - render da sequência em PNG + montagem do MP4 (H.264) com ffmpeg.

Uso (python do módulo bpy 4.5, a partir da raiz do repositório):
    python AP2/AP2_renderizar.py <pasta_dos_quadros> [amostras]

No Blender com interface basta abrir AP2_AndreCosta.blend e usar Render > Render Animation (Ctrl+F12):
a saída já está configurada como FFMPEG / MPEG-4 / H.264 em //AP2_AndreCosta.mp4.
Este script existe para renderizar em servidor (sem GPU) e retomar o render se ele for interrompido.
Nada é gravado no .blend: CPU, amostras e fonte substituta valem só nesta sessão.
"""
import subprocess
import sys
from pathlib import Path
import bpy

AP2 = Path("AP2").resolve()
QUADROS = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else AP2 / "quadros"
AMOSTRAS = int(sys.argv[2]) if len(sys.argv) > 2 else 32
QUADROS.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=str(AP2 / "AP2_AndreCosta.blend"))
sc = bpy.context.scene

# Fonte Lagu Sans está no PC do autor; se faltar (ex.: servidor), usa substituta só para este render.
for f in bpy.data.fonts:
    if f.packed_file is None and not Path(bpy.path.abspath(f.filepath)).exists():
        sub = "/usr/share/fonts/truetype/liberation/LiberationSans-" + ("Bold" if "Bold" in f.name else "Regular") + ".ttf"
        if Path(sub).exists():
            f.filepath = sub
            print("fonte substituta:", f.name, "->", sub)

sc.cycles.device = "CPU"
sc.cycles.samples = AMOSTRAS
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGB"
sc.render.image_settings.compression = 30
sc.render.filepath = str(QUADROS / "f_####")
sc.render.use_overwrite = False      # retoma de onde parou
sc.render.use_placeholder = True
bpy.ops.render.render(animation=True)

mp4 = AP2 / "AP2_AndreCosta.mp4"
subprocess.run(["ffmpeg", "-y", "-framerate", "24", "-start_number", "1", "-i", str(QUADROS / "f_%04d.png"),
                "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "24",
                "-movflags", "+faststart", str(mp4)], check=True)
print("VIDEO", mp4)
