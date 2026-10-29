# Alocação de Frequências via Coloração de Grafos e Simulated Annealing

Modelagem e resolução do **Problema de Alocação de Frequências** (*Frequency
Assignment Problem* — FAP) em redes de telecomunicações, reduzindo-o a um
problema de **coloração de grafos com k cores fixo** e resolvendo com a
metaheurística **Simulated Annealing (SA)**, usando **DSatur** como solução
inicial (*warm start*).

Testado no benchmark público **DSJC125.5** (DIMACS), com número cromático
conhecido χ(G) = 17.

## O problema

Numa rede de telecomunicações, cada transmissor precisa de uma frequência.
Dois transmissores que podem interferir entre si não podem operar na mesma
frequência. Na variante *co-canal* (a tratada aqui), isso equivale a montar
um **grafo de conflito** G = (V, E) — um vértice por transmissor, uma aresta
entre cada par que pode interferir — e encontrar uma atribuição de cores
(frequências) tal que vértices vizinhos nunca compartilhem cor.

Isso é exatamente **coloração de grafos**, e decidir se um grafo admite uma
k-coloração é **NP-completo** para k ≥ 3 (Karp, 1972). Métodos exatos
(*branch-and-bound*, programação linear inteira) ficam inviáveis conforme a
rede cresce — daí a necessidade de uma metaheurística.

## Abordagem

1. **Modelagem**: solução representada como vetor `s ∈ {1,...,k}ⁿ`; função
   objetivo `f(s)` = número de arestas monocromáticas (conflitos). Uma
   coloração é válida quando `f(s) = 0`.
2. **Solução inicial — DSatur** (Brélaz, 1979): heurística gulosa que, a
   cada passo, colore o vértice de maior *saturação* (mais cores distintas
   já usadas por seus vizinhos), desempatando por grau.
3. **Refinamento — Simulated Annealing**, com quatro otimizações sobre a
   versão canônica:
   - **Calibração automática de T₀**: amostra M movimentos de piora e
     ajusta a temperatura inicial para ~80% de aceitação (Duque-Antón,
     Kunz & Rüber, 1993).
   - **Vizinhança focada**: a cada iteração, escolhe um vértice apenas
     entre os que estão em conflito (`V_conf`), não do grafo inteiro.
   - **Avaliação incremental do custo**: o delta de cada movimento é
     calculado em `O(deg v)`, olhando só os vizinhos do vértice alterado —
     em vez de recontar todas as `O(|E|)` arestas do grafo a cada iteração.
   - **Resfriamento geométrico**: `T ← α·T` a cada `L` iterações.

Detalhamento completo (14 equações, prova de NP-completude, 5 algoritmos em
pseudocódigo, revisão de 15 referências) está no relatório em
[`report/relatorio.pdf`](report/relatorio.pdf).

## Resultados

Benchmark **DSJC125.5**: 125 vértices, 3.891 arestas únicas, densidade
≈ 50,2%, grau médio 62,3. Parâmetros: α = 0,95, M = 500, L = 200,
máximo de 500.000 iterações por execução.

| k  | Conflitos (DSatur) | Conflitos (SA) | Redução | Tempo SA | k-coloração válida? |
|----|--------------------:|----------------:|--------:|---------:|:---:|
| 17 | 139 | 8 | 94,2% | 4,08 s | ✗ |
| 18 | 76 | 5 | 93,4% | 4,4 s | ✗ |
| 19 | 50 | 1 | 98,0% | 3,95 s | ✗ |
| 20 | 36 | 0 | 100%  | 0,18 s | ✓ |

Gráfico de convergência (conflitos e temperatura por iteração, para cada
k): [`results/convergencia_dsjc.png`](results/convergencia_dsjc.png).

**Leitura dos resultados**: o SA reduz conflitos em mais de 90% em todos os
casos, mas só encontra coloração válida a partir de k = 20 dentro do
orçamento de iterações usado. Isso é esperado: para k próximo do número
cromático real (χ = 17), o espaço de colorações válidas é uma fração
minúscula do espaço total `kⁿ`, e o resfriamento geométrico com α = 0,95
esfria rápido demais para essa vizinhança apertada — ajustes como α mais
próximo de 1 (0,98–0,99) ou mais iterações tenderiam a melhorar k = 17–19.

## Estrutura do repositório

```
.
├── src/
│   ├── graph.py                # grafo como lista de adjacência + domínios de cor
│   ├── dsatur.py                # DSatur (solução inicial) + contagem de conflitos
│   ├── simulated_annealing.py   # motor do SA (calibração, delta incremental, resfriamento)
│   ├── parse_dimacs.py          # leitor de instâncias .col (formato DIMACS)
│   └── main_dsjc.py             # ponto de entrada: roda o experimento completo
├── data/
│   └── DSJC125_5.col            # instância de benchmark
├── results/
│   ├── resultados_dsjc.txt      # tabela de resultados (fonte da verdade)
│   └── convergencia_dsjc.png    # gráficos de convergência
├── report/
│   └── FAP.pdf                  # relatório completo (fundamentação, formulação, experimentos)
└── README.md
```

## Como rodar

```bash
cd src
python3 main_dsjc.py
```

Requer Python 3.10+, `numpy` e `matplotlib`. Sem dependências além da
biblioteca padrão para a lógica de grafo/DSatur/SA em si.

### Reprodutibilidade e semente aleatória

O experimento usa uma **semente fixa** (`SEED = 53`, em
`src/main_dsjc.py`) para manter reprodutibilidade entre execuções.
Como o SA é estocástico, ao **variar a seed** é possível explorar outras
trajetórias de busca e eventualmente encontrar a solução ótima para o
problema.

## Autor

Marcos Vinicius Silva dos Santos — Departamento de
Matemática, Universidade Federal de Sergipe.

## Referências principais

Brélaz (1979, DSatur) · Kirkpatrick, Gelatt & Vecchi (1983, Simulated
Annealing) · Duque-Antón, Kunz & Rüber (1993, calibração de T₀ aplicada a
alocação de canais celulares) · Karp (1972, NP-completude de coloração) ·
Eisenblätter, Grötschel & Koster (2002, FAP → coloração de grafos). Lista
completa com as 15 referências em [`report/relatorio.pdf`](report/relatorio.pdf).
