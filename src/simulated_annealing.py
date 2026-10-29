# simulated_annealing.py
import math
import random

# A seed global pode ser definida no script de execução para reprodutibilidade.


class SimulatedAnnealing:
    def __init__(self, graph, alpha=0.95, M=500, max_iter=100000, L=100):
        """
        graph: objeto Graph
        alpha: taxa de resfriamento (Eq. 8)
        M: número de amostras para calibrar T0 (Eq. 5)
        max_iter: número máximo de iterações (critério secundário de parada)
        L: número de iterações por nível de temperatura (resfriamento a cada L passos)
        """
        self.graph = graph
        self.alpha = alpha
        self.M = M
        self.max_iter = max_iter
        self.L = L

        # Estado interno
        self.coloring = None
        self.conflict_count = [
            0
        ] * graph.num_vertices  # Contador de conflitos por vértice
        self.total_conflicts = 0
        self.V_conf = set()  # Vértices conflitantes (Eq. 4)

        # Histórico para plotar gráficos (Seção 6.1)
        self.history_cost = []
        self.history_temp = []

    def _init_solution(self, initial_coloring):
        """Inicializa o estado a partir de uma coloração (ex: do DSatur)."""
        self.coloring = initial_coloring[:]
        self.conflict_count = [0] * self.graph.num_vertices
        self.total_conflicts = 0
        self.V_conf = set()

        # Calcular conflitos iniciais percorrendo cada aresta UMA vez (u < v).
        # conflict_count[v] = nº de vizinhos em conflito com v.
        # sum(conflict_count) = 2 * E_conf  →  //2 dá o nº de arestas em conflito.
        for u in range(self.graph.num_vertices):
            for v in self.graph.adj[u]:
                if u < v and self.coloring[u] == self.coloring[v]:
                    self.conflict_count[u] += 1
                    self.conflict_count[v] += 1

        # Popular V_conf
        for v in range(self.graph.num_vertices):
            if self.conflict_count[v] > 0:
                self.V_conf.add(v)

        self.total_conflicts = sum(self.conflict_count) // 2

    def _calculate_delta(self, v, c_new):
        """
        Avaliação incremental (Eq. 7).
        Calcula o Delta sem percorrer todas as arestas.
        """
        c_old = self.coloring[v]
        delta = 0
        for u in self.graph.adj[v]:
            if self.coloring[u] == c_new:
                delta += 1  # Novo conflito introduzido
            if self.coloring[u] == c_old:
                delta -= 1  # Conflito eliminado
        return delta

    def _apply_move(self, v, c_new, delta):
        """Aplica a mudança de cor e atualiza V_conf e conflict_count."""
        c_old = self.coloring[v]

        # Atualizar conflict_count dos vizinhos
        for u in self.graph.adj[v]:
            if self.coloring[u] == c_old:
                self.conflict_count[u] -= 1
                if self.conflict_count[u] == 0:
                    self.V_conf.discard(u)
            if self.coloring[u] == c_new:
                self.conflict_count[u] += 1
                self.V_conf.add(u)

        # Atualizar o próprio vértice
        self.conflict_count[v] += delta
        if self.conflict_count[v] == 0:
            self.V_conf.discard(v)
        else:
            self.V_conf.add(v)

        # Aplicar a cor
        self.coloring[v] = c_new
        self.total_conflicts += delta

    def _calibrate_T0(self):
        """
        Calibração da temperatura inicial (Eq. 5).
        Gera M movimentos de piora e calcula a média.
        """
        deltas = []
        # Fazer cópias para não alterar o estado real
        temp_coloring = self.coloring[:]

        attempts = 0
        while len(deltas) < self.M and attempts < self.M * 10:
            attempts += 1
            if not self.V_conf:
                break  # Se não há conflitos, não há piora possível

            v = random.choice(list(self.V_conf))
            domain = [c for c in self.graph.domains[v] if c != temp_coloring[v]]
            if not domain:
                continue
            c_new = random.choice(domain)

            # Calcular delta teórico
            delta = 0
            c_old = temp_coloring[v]
            for u in self.graph.adj[v]:
                if temp_coloring[u] == c_new:
                    delta += 1
                if temp_coloring[u] == c_old:
                    delta -= 1

            if delta > 0:  # Só acumulamos pioras
                deltas.append(delta)

        if not deltas:
            return 1.0  # Fallback

        avg_delta = sum(deltas) / len(deltas)
        T0 = -avg_delta / math.log(0.8)
        return max(T0, 0.1)  # Garante T0 mínimo

    def run(self, initial_coloring):
        """
        Executa o Simulated Annealing (Algoritmo 2 do LaTeX).
        """
        self._init_solution(initial_coloring)
        T = self._calibrate_T0()

        best_coloring = self.coloring[:]
        best_cost = self.total_conflicts

        iteration = 0

        print(
            f"Início do SA | Conflitos iniciais: {self.total_conflicts} | T0: {T:.2f}"
        )

        while iteration < self.max_iter and self.total_conflicts > 0:
            # 1. Selecionar vértice em V_conf
            if not self.V_conf:
                break  # Solução ótima encontrada!

            v = random.choice(list(self.V_conf))

            # 2. Selecionar nova cor no domínio de v
            domain = [c for c in self.graph.domains[v] if c != self.coloring[v]]
            if not domain:
                iteration += 1
                continue
            c_new = random.choice(domain)

            # 3. Calcular Delta (Eq. 7)
            delta = self._calculate_delta(v, c_new)

            # 4. Critério de Metropolis (Eq. 3)
            accept = False
            if delta <= 0:
                accept = True
            else:
                prob = math.exp(-delta / T)
                if random.random() < prob:
                    accept = True

            # 5. Aplicar movimento se aceito
            if accept:
                self._apply_move(v, c_new, delta)

                if self.total_conflicts < best_cost:
                    best_cost = self.total_conflicts
                    best_coloring = self.coloring[:]

            # 6. Resfriamento (Eq. 8) a cada L iterações
            iteration += 1
            if iteration % self.L == 0:
                T *= self.alpha

            # Registrar histórico (a cada 100 iterações para não pesar na memória)
            if iteration % 100 == 0:
                self.history_cost.append(self.total_conflicts)
                self.history_temp.append(T)

        print(
            f"Fim do SA | Conflitos finais: {self.total_conflicts} | Iterações: {iteration}"
        )

        return best_coloring, best_cost
