# graph.py
class Graph:
    """
    Grafo representado por Lista de Adjacência.
    Otimizado para a avaliação incremental O(deg(v)) descrita na Eq. 7 do LaTeX.
    """

    def __init__(self, num_vertices):
        self.num_vertices = num_vertices
        # adj[v] = lista de vizinhos de v
        self.adj = [[] for _ in range(num_vertices)]
        # domains[v] = lista de cores (frequências) permitidas para o vértice v
        self.domains = [[] for _ in range(num_vertices)]

    def add_edge(self, u, v):
        """Adiciona uma aresta não-direcionada entre u e v."""
        if u != v:  # Evita self-loops
            self.adj[u].append(v)
            self.adj[v].append(u)

    def set_domain(self, v, domain):
        """Define o conjunto de cores permitidas para o vértice v."""
        self.domains[v] = domain

    def get_degree(self, v):
        return len(self.adj[v])
