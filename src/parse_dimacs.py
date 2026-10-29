# parse_dimacs.py
"""
Parser para grafos no formato DIMACS .col (benchmark de coloração).

Formato esperado:
    c  linhas de comentário (ignoradas)
    p edge N M   → N vértices, M declarações de aresta (pode incluir duplicatas)
    e u v        → aresta entre u e v (1-indexado)

Nota: o DSJC125.5.col lista cada aresta duas vezes (e u v e e v u);
o parser deduplica usando um set, produzindo o grafo simples correto.
"""

from graph import Graph


def parse_dimacs(filepath, k):
    """
    Lê um arquivo .col no formato DIMACS e constrói um Grafo.

    Parâmetros
    ----------
    filepath : str
        Caminho para o arquivo .col.
    k : int
        Número de cores disponíveis.  O domínio de todos os vértices
        é definido como {1, 2, ..., k}.

    Retorna
    -------
    Graph
        Objeto grafo pronto para o DSatur e o SA.
    int
        Número de vértices n.
    int
        Número de arestas m (únicas).
    """
    n = 0
    edges_seen = set()

    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            parts = line.split()
            if parts[0] == 'p':
                n = int(parts[2])           # número de vértices
            elif parts[0] == 'e':
                u = int(parts[1]) - 1       # converte para 0-indexado
                v = int(parts[2]) - 1
                if u != v:                  # descarta self-loops (inexistentes aqui)
                    edge = (min(u, v), max(u, v))
                    edges_seen.add(edge)

    if n == 0:
        raise ValueError(f"Arquivo '{filepath}' não contém linha 'p edge ...'")

    g = Graph(n)

    # Domínio uniforme {1, ..., k} para todos os vértices
    domain = list(range(1, k + 1))
    for v in range(n):
        g.set_domain(v, domain)

    for u, v in edges_seen:
        g.add_edge(u, v)

    return g, n, len(edges_seen)
