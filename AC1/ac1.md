# Computação Visual: Síntese de Imagens, Processamento de Imagens, Visão Computacional e Visualização Computacional

## Objetivo

Demonstrar as diferenças e principais características das áreas relacionadas à Computação Visual — Síntese de Imagens (Computação Gráfica), Processamento de Imagens, Visão Computacional (Artificial) e Visualização Computacional — selecionando, para cada uma, uma aplicação com código disponível em repositório público, executável e explicado.

---

## 1. Síntese de Imagens (Computação Gráfica)

**Aplicação:** ray tracing / path tracing — geração de imagem fotorrealista a partir de um modelo matemático de luz.

**Repositório:** [smallpt](https://github.com/lzn27/smallpt) (Kevin Beason) — path tracer Monte Carlo em apenas 99 linhas de C++, clássico usado em cursos de CG por caber inteiro em uma apresentação.

```bash
g++ -O3 -fopenmp smallpt.cpp -o smallpt
./smallpt 100   # gera image.ppm
```

**Aspectos a explicar:**
- O pipeline Universo Físico → Matemático → Representação → Implementação.
- A equação de rendering resolvida por Monte Carlo.
- Reflexão difusa, especular e dielétrica.
- Por que isso é "síntese" (dados numéricos → imagem), e não o caminho inverso da Visão Computacional.

**Alternativa/complemento:** renderizar uma cena simples no próprio **Blender (Cycles)** e comparar rasterização vs. path tracing lado a lado.

---

## 2. Processamento de Imagens

**Aplicação:** operações clássicas sobre pixels — escala de cinza, blur, detecção de bordas.

**Repositório:** exemplos oficiais do [OpenCV](https://github.com/opencv/opencv) (`samples/python`), ou script direto com `opencv-python`:

```python
import cv2
img = cv2.imread("foto.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(img, (15, 15), 0)
edges = cv2.Canny(gray, 100, 200)
```

**Aspectos a explicar:**
- Entrada e saída são ambas imagens (imagem → imagem).
- Diferente de CG (dados → imagem) e de Visão Computacional (imagem → informação).
- Operações locais de convolução (kernel de blur) vs. operações de gradiente (Canny).

---

## 3. Visão Computacional (Artificial)

**Aplicação:** detecção de objetos em imagem/vídeo.

**Repositório:** [ultralytics/ultralytics (YOLOv8)](https://github.com/ultralytics/ultralytics) — instalação e inferência em uma linha, ótimo para demonstração ao vivo:

```bash
pip install ultralytics
yolo predict model=yolov8n.pt source='https://ultralytics.com/images/bus.jpg'
```

**Aspectos a explicar:**
- Entrada é imagem, saída é informação simbólica (classe + bounding box) — o inverso da síntese de imagens.
- Rede neural convolucional por trás da detecção.
- Paralelo histórico: exemplo do "Juiz Virtual" (Tecgraf/PUC-Rio) como aplicação da mesma área.

---

## 4. Visualização Computacional

**Aplicação:** visualização científica de dados volumétricos.

**Repositório:** [Kitware/VTK](https://github.com/Kitware/VTK), ou `pyvista` (wrapper mais simples do VTK, roda fácil em notebook):

```bash
pip install pyvista
```

```python
import pyvista as pv
grid = pv.examples.load_uniform()  # dataset volumétrico de exemplo
grid.plot(volume=True)
```

**Aspectos a explicar:**
- Entrada é dado (não necessariamente imagem) — um campo escalar 3D (ex.: tomografia, simulação).
- Saída é uma representação visual para interpretação humana.
- Diferença da Visão Computacional: não há "reconhecimento", é mapeamento direto dado → visual (isosuperfície, ray casting volumétrico, transfer function de cor/opacidade).

---

## Resumo comparativo

| Área | Entrada | Saída |
|---|---|---|
| Síntese de Imagens | modelo/dados matemáticos | imagem |
| Processamento de Imagens | imagem | imagem |
| Visão Computacional | imagem | informação/símbolo |
| Visualização Computacional | dado (não necessariamente imagem) | imagem/representação visual |

---

## Ferramenta de apoio

Este material foi organizado com apoio do **Claude (Anthropic)**, usado para pesquisar e selecionar aplicações e repositórios públicos correspondentes a cada área, a partir do material da disciplina (slides de introdução, bibliotecas gráficas e Blender).

**Prompt de pesquisa utilizado:**

```
Objetivo: Demonstrar as diferenças e principais características das áreas
relacionadas a Computação Visual: Síntese de Imagens (Computação Gráfica),
Processamento de Imagens, Visão Computacional (Artificial) e Visualização
Computacional.

Considerações adicionais: Para cada uma das áreas deve-se selecionar uma
aplicação, apresentar os principais aspectos e executar a aplicação ou
código disponível em repositórios públicos com a devida explicação de
aspectos específicos de cada área.
```
