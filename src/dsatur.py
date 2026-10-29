# dsatur.py
import random


def run_dsatur(graph):
    """
    Implementação do algoritmo DSatur (Brélaz, 1979).
    Retorna um vetor 'coloring' onde coloring[v] é a cor atribuída a v.
    """
    n = graph.num_vertices
    coloring = [-1] * n  # -1 significa não colorido

    # Rastreio de saturação e grau não-colorido
    saturation = [0] * n
    uncolored_degree = [graph.get_degree(v) for v in range(n)]

    # Conjunto de vértices não coloridos
    uncolored = set(range(n))

    # Rastreio de cores vizinhas para cálculo rápido de saturação
    neighbor_colors = [set() for _ in range(n)]

    while uncolored:
        # Selecionar o vértice com maior saturação (desempate por grau)
        # O(max(|uncolored|)) - para grafos do CELAR (~900 vértices) é muito rápido
        v = max(uncolored, key=lambda x: (saturation[x], uncolored_degree[x]))

        # Encontrar a menor cor disponível no domínio de v
        available_colors = [c for c in graph.domains[v] if c not in neighbor_colors[v]]

        if not available_colors:
            # Fallback: se todas as cores do domínio estão nos vizinhos,
            # escolhe uma aleatória do domínio (vai gerar conflito, mas o SA resolve).
            # A reprodutibilidade depende da seed definida no script de execução.
            color = random.choice(graph.domains[v])
        else:
            color = available_colors[0]  # Menor cor disponível

        coloring[v] = color
        uncolored.remove(v)

        # Atualizar vizinhos
        for u in graph.adj[v]:
            if u in uncolored:
                if color not in neighbor_colors[u]:
                    neighbor_colors[u].add(color)
                    saturation[u] += 1
                uncolored_degree[u] -= 1

    return coloring


def count_conflicts(graph, coloring):
    """
    Calcula o custo f(s) da Eq. 6 do LaTeX.
    Retorna o número total de arestas em conflito.
    """
    conflicts = 0
    for u in range(graph.num_vertices):
        for v in graph.adj[u]:
            if u < v and coloring[u] == coloring[v]:
                conflicts += 1
    return conflicts
