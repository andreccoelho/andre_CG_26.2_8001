# AC03 — Transformações Geométricas 2D e 3D no Blender 4.5 LTS

**Aluno:** NomeSobrenome
**Cena:** Parque Geométrico

---

## 1. Entregáveis

| Arquivo | Conteúdo |
|---|---|
| `AC03_NomeSobrenome.blend` | Cena completa na coleção `AC03_transformacoes`: 3 objetos 2D, 3 objetos 3D, satélite (filho da esfera), câmera, luz e animação de 120 frames a 24 fps (5 s). |
| `AC03_NomeSobrenome.py` | Script que cria a cena, aplica as transformações, insere os keyframes e configura câmera, luz e render. É reexecutável: limpa e recria a coleção a cada execução. |
| `AC03_NomeSobrenome.png` | Render estático da cena no frame 60 (meio da animação), 1920x1080, EEVEE. |
| Este documento | Texto explicativo e respostas às questões teóricas. |

### Objetos da cena

| Objeto | Tipo | Transformações |
|---|---|---|
| `obj2d_quadrado` | Plane | Translação em X, rotação em Z, escala uniforme (script + ajuste manual) |
| `obj2d_triangulo` | Malha de 3 vértices | Escala; **animado** com translação em Y e rotação em Z |
| `obj2d_circulo` | Mesh Circle (preenchido) | Translação em Y, escala não uniforme (vira elipse) |
| `obj3d_cubo` | Cube | **Animado** com escala e rotação em X e Y |
| `obj3d_cilindro` | Cylinder | Rotação em X, escala, translação no Z global e no Z local |
| `obj3d_esfera` | UV Sphere | Translação manual em Z; **animada** com rotação em Z |
| `obj3d_satelite` | Cube (filho da esfera) | Posição local relativa à esfera; orbita por herança da rotação do pai |

### Cobertura dos requisitos técnicos

Os objetos seguem a nomenclatura `obj2d_` / `obj3d_` e ficam na coleção `AC03_transformacoes`. Todas as rotações do script são definidas em graus e convertidas com `math.radians()`. Há transformações nos três eixos: translação em X (quadrado), Y (círculo, triângulo) e Z (cilindro, esfera); rotação em X (cilindro, cubo), Y (cubo) e Z (quadrado, triângulo, esfera). O triângulo e o cubo têm keyframes nos frames inicial (1) e final (120).

Bônus: hierarquia parent/child (satélite filho da esfera, gerando transformação composta), etapa intermediária no frame 60 da animação do triângulo e interpolações com easing (`SINE` com ease in/out no triângulo, `BACK` com overshoot no cubo).

---

## 2. Texto explicativo

Na cena "Parque Geométrico" apliquei transformações 2D nos objetos planos, todos no plano XY. O quadrado recebeu translação em X, rotação em Z e escala uniforme. O círculo foi transladado em Y e escalado de forma não uniforme. O triângulo foi animado com translação em Y e rotação em Z, com uma etapa intermediária no frame 60.

Nos sólidos, o cubo foi animado com escala e rotação em X e Y. O cilindro foi rotacionado em X e depois transladado uma vez no eixo Z global e outra no seu Z local, mostrando a diferença entre os dois espaços. A esfera gira em Z e carrega um satélite filho, o que gera uma transformação composta.

Por Python criei toda a cena, os keyframes, a câmera e a luz, com rotações em graus convertidas para radianos. Manualmente, transladei o quadrado em X (G), rotacionei em Z (R) e escalei (S); subi a esfera em Z (G) e ajustei o enquadramento da câmera antes do render.

---

## 3. Questões teóricas

### 1. Diferença entre translação, rotação e escala

**Translação** desloca o objeto sem alterar sua forma nem sua orientação: equivale a somar um vetor à posição. **Rotação** gira o objeto em torno de um eixo e de um ponto pivô, mantendo tamanho e forma. **Escala** multiplica as dimensões do objeto por fatores em cada eixo; se os fatores forem iguais (uniforme), as proporções se mantêm, e se forem diferentes (não uniforme), o objeto se deforma. Em computação gráfica as três são representadas por matrizes 4x4 em coordenadas homogêneas, o que permite combiná-las em uma única matriz por multiplicação.

### 2. Espaço local x espaço global

No **espaço global** (World), os eixos são os do mundo, fixos e iguais para toda a cena. No **espaço local**, os eixos pertencem ao próprio objeto e acompanham sua rotação e escala. Em um objeto sem rotação os dois coincidem; em um objeto rotacionado, "mover 1 unidade em Z" leva a posições diferentes em cada espaço. No script, o cilindro inclinado 45° em X demonstra isso: a translação global o faz subir na vertical, enquanto a local o desloca na diagonal, na direção do seu próprio eixo Z.

### 3. Por que rotações em eixos diferentes geram resultados distintos

Cada eixo define um plano de giro diferente, então o mesmo ângulo produz orientações diferentes conforme o eixo. Além disso, rotações não são comutativas: girar em X e depois em Y gera um resultado diferente de girar em Y e depois em X. Por isso o Blender usa uma ordem de Euler definida (XYZ por padrão). Algumas combinações ainda podem alinhar dois eixos e causar *gimbal lock*, com perda de um grau de liberdade.

### 4. Por que usar `math.radians()` em `rotation_euler`

A API Python do Blender armazena `rotation_euler` em **radianos**, embora a interface exiba graus. Se o script atribuir `45`, o Blender interpreta como 45 radianos (cerca de 2578°). A função `math.radians()` converte o valor pensado em graus para a unidade que a API espera, o que deixa o código legível e correto.

### 5. Quando vale mais a pena usar Python

Quando a tarefa envolve repetição, precisão ou reprodutibilidade. Um exemplo é distribuir 200 árvores em uma grade, variando posição, rotação e escala por fórmula ou aleatoriamente: pela interface seria lento e sujeito a erro, enquanto no script é um laço de poucas linhas. O mesmo vale para aplicar a mesma animação a dezenas de objetos ou recriar a cena com outros parâmetros. Nesta atividade, o script permitiu apagar e reconstruir toda a cena de forma idêntica a cada execução.
