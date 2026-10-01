Nome# AP1 – Relatório da cena-conceito

**Aluno:** [André Costa] | **Disciplina:** [disciplina] | **Blender 4.5 LTS**
**Arquivo:** `AP1_AndreCosta.blend` | **Coleção principal:** `AP1_Ibmec_Conceito`

## 1. Conceito e título

**Título: "Origens"**

A palavra **Ibmec** aparece gravada no morro do Corcovado, aos pés do Cristo Redentor, para representar as origens da instituição: nascida no Rio de Janeiro e construída sobre uma base sólida. Um avião atravessa o céu ao fundo, sugerindo futuro, inovação e empreendedorismo. A rocha transmite solidez, o voo transmite futuridade, e as letras que se erguem do morro transmitem construção e criatividade.

## 2. Entrada, transformação e apresentação da palavra

- **Entrada:** plano aberto do morro e do Cristo. O logo ainda está discreto, integrado à rocha.
- **Transformação:** as letras se erguem do morro, uma a uma, como uma construção, enquanto a câmera se aproxima lentamente.
- **Apresentação:** a câmera assenta num quadro frontal estável e o logo fica nítido e legível, com o avião saindo de quadro ao fundo.

A marca é preservada: o logo é o modelo original do aluno, sem alteração de fonte ou proporção. As cores da marca serão aplicadas na AP2.

## 3. Objetos autorais (exatamente três)

| Objeto (Outliner) | Função na cena | Modelagem |
|---|---|---|
| `Aviao` | Protagonista secundário. Cruza o céu ao fundo durante os 15 s, simbolizando inovação, empreendedorismo e a jornada da instituição. | Fuselagem a partir de esfera com afunilamento proporcional da cauda; asa com diedro e ponta afilada; cabine com inset + extrusão; hélice e trem de pouso; Bevel. |
| `Gaivota` | Vida e identidade carioca. Cria camada de profundidade entre câmera e morro e movimento secundário. | Corpo, cabeça e bico a partir de primitivas; asas em "M" construídas vértice a vértice como prismas (composição de malhas). |
| `Nuvem` | Atmosfera e profundidade de fundo, com deslocamento lento para dar paralaxe ao céu. | Esferas compostas, base achatada, modificadores Remesh (voxel), Displace com textura Clouds e Subdivision Surface. |

Elementos de apoio (não contam como autorais): modelo do **Cristo Redentor/morro** importado (`ChristTheRedeemer.002`) – fonte/licença: [preencher] – e o **logo Ibmec**, modelado pelo aluno.

## 4. Técnicas de modelagem e transformações

- **Modelagem:** inset, extrusão, deformação com falloff (equivalente à edição proporcional), composição de malhas, construção de faces por vértices, modificadores (Bevel, Remesh, Displace, Subdivision Surface).
- **Translação:** logo mantido na face do morro, abaixo do Cristo; objetos colocados no quadro por posição de tela e profundidade.
- **Rotação:** logo girado em Z para encarar a câmera; avião e gaivota com rumo em relação ao quadro.
- **Escala:** logo e objetos dimensionados pela largura do quadro na profundidade de cada um, o que cria camadas de perspectiva (gaivota perto, morro no meio, avião e nuvem ao fundo).
- **Organização:** subcoleções `Logo_Ibmec`, `Cenario_Cristo`, `Objetos_Autorais` e `Camera`; nomes coerentes no Outliner.
- **Câmera:** `Camera_Principal` (50 mm), 1920×1080, pronta para animar. Cena configurada para **360 frames a 24 fps (15 s)**, com marcadores em 1, 180 e 360.

## 5. Storyboard

| Momento | Frames / tempo | Descrição | Câmera |
|---|---|---|---|
| **1. Início** | 1–90 (0–3,75 s) | Plano aberto do morro e do Cristo. Logo discreto na rocha. O avião entra pela esquerda, ao fundo, e a gaivota cruza o primeiro plano. | Aberta, quase parada. |
| **2. Destaque / transformação** | 90–270 (≈3,75–11,25 s; pico no frame 180) | As letras se erguem do morro em sequência. O avião cruza o céu e a nuvem se desloca. A luz esquenta. | Dolly-in lento em direção ao logo. |
| **3. Encerramento** | 270–360 (≈11,25–15 s) | O logo fica nítido e legível em quadro frontal. O avião sai à direita e a cena respira por cerca de 1 s. | Estável, enquadramento final. |

## 6. Plano para a AP2

- **Animação:** dolly-in da câmera (keyframes 1→360); letras do logo emergindo por escala/posição com defasagem; avião percorrendo uma curva (Follow Path) com leve inclinação; gaivota com bater de asas (asas separadas da malha); nuvem em deslocamento lento.
- **Iluminação:** luz de fim de tarde/nascer do sol, com luz de contorno para destacar o logo.
- **Materiais e texturas:** rocha do morro, branco do Cristo, cores e acabamento oficiais da marca no logo, materiais simples para avião, gaivota e nuvem.
- **Renderização:** 1920×1080, 24 fps, 360 frames; exportação em MP4 (H.264).
