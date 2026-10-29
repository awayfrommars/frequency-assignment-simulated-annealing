# main_dsjc.py
"""
Ponto de entrada para os experimentos com DSJC125.5.

Executa o SA para k = K_MIN .. K_MAX e reporta:
  - Conflitos após DSatur (warm start)
  - Conflitos após SA
  - Tempo de execução

Também gera:
  - Gráfico de convergência para cada k
  - Tabela resumo salva em resultados_dsjc.txt
"""

import os
import random
import sys
import time

import matplotlib

matplotlib.use("Agg")  # renderização sem display
import matplotlib.pyplot as plt

from dsatur import count_conflicts, run_dsatur
from parse_dimacs import parse_dimacs
from simulated_annealing import SimulatedAnnealing

# ──────────────────────────────────────────────
# Parâmetros do experimento
# ──────────────────────────────────────────────
ARQUIVO = "../data/DSJC125_5.col"
K_MIN = 17  # χ(DSJC125.5) conhecido = 17
K_MAX = 20  # valores acima de 17 devem ser trivialmente resolvidos
ALPHA = 0.95  # taxa de resfriamento
M_AMOSTRAS = 500  # amostras para calibrar T0
MAX_ITER = 500_000  # iterações máximas por execução
L = 200  # iterações por nível de temperatura
SEED = (
    53  # semente fixa para reprodutibilidade (varie para explorar outras trajetórias)
)
"""
import time
Gera uma seed com base no timestamp atual
SEED = int(time.time())
"""

random.seed(SEED)

# ──────────────────────────────────────────────
# Experimento
# ──────────────────────────────────────────────
print(f"{'=' * 60}")
print(f"  Experimento: DSJC125.5  |  α={ALPHA}  |  max_iter={MAX_ITER:,}")
print(f"{'=' * 60}\n")

resultados = []

for k in range(K_MIN, K_MAX + 1):
    print(f"\n{'─' * 50}")
    print(f"  k = {k} cores")
    print(f"{'─' * 50}")

    # 1. Carregar grafo
    graph, n, m = parse_dimacs(ARQUIVO, k)
    print(f"  Grafo: {n} vértices, {m} arestas  (grau médio {2 * m / n:.1f})")

    # 2. DSatur (warm start)
    t0 = time.time()
    coloring_dsatur = run_dsatur(graph)
    custo_dsatur = count_conflicts(graph, coloring_dsatur)
    t_dsatur = time.time() - t0
    print(f"  DSatur  → {custo_dsatur:4d} conflitos  ({t_dsatur:.2f}s)")

    # 3. Simulated Annealing
    sa = SimulatedAnnealing(
        graph=graph,
        alpha=ALPHA,
        M=M_AMOSTRAS,
        max_iter=MAX_ITER,
        L=L,
    )

    t0 = time.time()
    best_coloring, best_cost = sa.run(coloring_dsatur)
    t_sa = time.time() - t0
    print(f"  SA      → {best_cost:4d} conflitos  ({t_sa:.2f}s)")

    status = (
        "✓ SOLUÇÃO VÁLIDA" if best_cost == 0 else f"✗ {best_cost} conflitos residuais"
    )
    print(f"  Resultado: {status}")

    resultados.append(
        {
            "k": k,
            "dsatur": custo_dsatur,
            "sa": best_cost,
            "t_dsatur": t_dsatur,
            "t_sa": t_sa,
            "history_cost": sa.history_cost[:],
            "history_temp": sa.history_temp[:],
            "valido": best_cost == 0,
        }
    )

# ──────────────────────────────────────────────
# Tabela resumo
# ──────────────────────────────────────────────
print(f"\n\n{'=' * 60}")
print("  RESUMO")
print(f"{'=' * 60}")
print(f"{'k':>4}  {'DSatur':>8}  {'SA':>8}  {'Válido':>8}  {'Tempo SA':>10}")
print(f"{'─' * 46}")
for r in resultados:
    print(
        f"{r['k']:>4}  {r['dsatur']:>8}  {r['sa']:>8}  "
        f"{'Sim' if r['valido'] else 'Não':>8}  {r['t_sa']:>9.1f}s"
    )

# Salvar tabela em arquivo
with open("../results/resultados_dsjc.txt", "w") as f:
    f.write(f"k,dsatur_conflitos,sa_conflitos,valido,tempo_sa_s\n")
    for r in resultados:
        f.write(
            f"{r['k']},{r['dsatur']},{r['sa']},"
            f"{'sim' if r['valido'] else 'nao'},{r['t_sa']:.2f}\n"
        )
print("\nTabela salva em resultados_dsjc.txt")

# ──────────────────────────────────────────────
# Gráficos de convergência
# ──────────────────────────────────────────────
fig, axes = plt.subplots(2, len(resultados), figsize=(5 * len(resultados), 8))
if len(resultados) == 1:
    axes = [[axes[0]], [axes[1]]]

for i, r in enumerate(resultados):
    iters_x = [j * 100 for j in range(len(r["history_cost"]))]

    # Painel superior: conflitos
    ax_cost = axes[0][i]
    ax_cost.plot(iters_x, r["history_cost"], color="#1f77b4", linewidth=1)
    ax_cost.axhline(0, color="red", linestyle="--", linewidth=0.8, label="f=0")
    ax_cost.set_title(f"k = {r['k']}  →  SA: {r['sa']} conflitos")
    ax_cost.set_xlabel("Iterações")
    ax_cost.set_ylabel("Conflitos")
    ax_cost.legend(fontsize=8)
    ax_cost.grid(True, alpha=0.3)

    # Painel inferior: temperatura
    ax_temp = axes[1][i]
    ax_temp.semilogy(iters_x, r["history_temp"], color="#ff7f0e", linewidth=1)
    ax_temp.set_title(f"Temperatura  (α={ALPHA})")
    ax_temp.set_xlabel("Iterações")
    ax_temp.set_ylabel("T (escala log)")
    ax_temp.grid(True, alpha=0.3)

fig.suptitle("SA para DSJC125.5 — Convergência por valor de k", fontsize=13, y=1.01)
fig.tight_layout()
fig.savefig("../results/convergencia_dsjc.png", dpi=150, bbox_inches="tight")
print("Gráfico salvo em ../results/convergencia_dsjc.png")
