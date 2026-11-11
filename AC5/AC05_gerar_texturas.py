"""AC05 - gera as texturas procedurais (metal escovado e madeira) e prepara a do Cristo.

Uso (Python com numpy + pillow):
    python AC05_gerar_texturas.py <pasta_do_cristo_extraido> <pasta_de_saida>

Todos os mapas gerados são TILEÁVEIS (ruído periódico via FFT), então podem repetir
no UV sem emendas visíveis.
Convenção do mapa normal: tangente, OpenGL (Y+), como o Blender espera.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def pnoise(n, sx, sy, seed):
    """Ruído periódico 2D normalizado em [0,1]. sx/sy = escala do filtro nas duas direções
    (maior = mais detalhe nessa direção)."""
    rng = np.random.default_rng(seed)
    f = np.fft.fft2(rng.standard_normal((n, n)))
    ky = np.fft.fftfreq(n)[:, None] * n
    kx = np.fft.fftfreq(n)[None, :] * n
    filt = np.exp(-((kx / sx) ** 2 + (ky / sy) ** 2))
    a = np.real(np.fft.ifft2(f * filt))
    a -= a.min()
    return a / a.max()


def normal_from_height(h, strength):
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5
    dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5  # d/d(linha); v cresce para cima -> -d/dv = +d/dlinha
    nx, ny, nz = -dx * strength, dy * strength, np.ones_like(h)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    return np.stack([nx / l, ny / l, nz / l], -1) * 0.5 + 0.5


def save_rgb(a, path, jpg=False):
    img = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")
    img.save(path, quality=92) if jpg else img.save(path, optimize=True)


def save_gray(a, path):
    Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "L").save(path, optimize=True)


def metal_escovado(out, n=2048):
    # estrias longas na horizontal: filtro estreito em kx (variação lenta em X) e largo em ky
    fino = pnoise(n, 6, 420, 1)
    medio = pnoise(n, 14, 220, 2)
    risco = pnoise(n, 3, 700, 3)
    streak = 0.55 * fino + 0.30 * medio + 0.15 * risco
    streak = (streak - streak.min()) / (streak.max() - streak.min())
    mancha = pnoise(n, 5, 5, 4)  # variação suave de oxidação/tinta
    base = np.array([0.62, 0.045, 0.04])  # vermelho do avião da AP1/AC04, agora metal anodizado
    k = (0.80 + 0.35 * (streak - 0.5) + 0.10 * (mancha - 0.5))[..., None]
    save_rgb(base * k, out / "metal_escovado_basecolor.jpg", jpg=True)
    save_gray(0.22 + 0.30 * streak + 0.08 * mancha, out / "metal_escovado_roughness.png")
    save_rgb(normal_from_height(streak, 7.0), out / "metal_escovado_normal.png")


def madeira(out, n=2048):
    warp = pnoise(n, 5, 30, 10)
    grao = pnoise(n, 280, 5, 11)  # fibras longas na vertical
    poro = pnoise(n, 120, 14, 12)
    x = np.arange(n)[None, :] / n * np.ones((n, 1))
    r = x * 7 + 0.55 * (warp - 0.5)  # 7 anéis: inteiro => tileável em U
    anel = (np.sin(r * 2 * np.pi) * 0.5 + 0.5) ** 1.3
    t = np.clip(0.55 * anel + 0.30 * grao + 0.15 * poro, 0, 1)[..., None]
    claro, escuro = np.array([0.58, 0.38, 0.19]), np.array([0.27, 0.14, 0.06])
    save_rgb(claro * (1 - t) + escuro * t, out / "madeira_basecolor.jpg", jpg=True)
    save_gray(0.52 + 0.22 * grao + 0.14 * anel + 0.08 * poro, out / "madeira_roughness.png")
    h = 0.45 * anel + 0.40 * grao + 0.15 * poro
    save_rgb(normal_from_height(h, 3.5), out / "madeira_normal.png")


def cristo(src_dir, out, lado=4096):
    """O JPEG original tem 8192x8192 (36 MB). Reduzido para 4096 para o .blend caber nos
    limites do GitHub (100 MB por arquivo)."""
    src = next(Path(src_dir).rglob("a-ChristTheRedeemer.jp*g"))
    Image.open(src).convert("RGB").resize((lado, lado), Image.LANCZOS).save(
        out / "cristo_basecolor_4k.jpg", quality=90, optimize=True)


if __name__ == "__main__":
    cristo_dir, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    metal_escovado(out)
    madeira(out)
    cristo(cristo_dir, out)
    print("ok", sorted(p.name for p in out.iterdir()))
