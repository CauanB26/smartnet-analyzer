"""
Estrutura de dados de grafo (lista de adjacencia), implementada do zero.

Justificativa da escolha (lista x matriz):
O grafo da cidade inteligente tende a ser esparso (poucas vias/conexoes
em relacao ao total de pares possiveis de bairros). A lista de adjacencia
ocupa O(V + E) de memoria, contra O(V^2) da matriz, e e a estrutura que
os algoritmos de Dijkstra e Kruskal mais naturalmente consomem (percorrer
vizinhos de um vertice / gerar lista de arestas ordenadas por peso).
"""


class Graph:
    def __init__(self, directed=False, weighted=True):
        self.directed = directed
        self.weighted = weighted
        # lista de adjacencia: { vertice: [(vizinho, peso), ...] }
        self.adjacency = {}

    def add_vertex(self, vertex):
        if vertex not in self.adjacency:
            self.adjacency[vertex] = []

    def add_edge(self, origem, destino, peso=1):
        if not self.weighted:
            peso = 1

        self.add_vertex(origem)
        self.add_vertex(destino)

        self.adjacency[origem].append((destino, peso))
        if not self.directed:
            self.adjacency[destino].append((origem, peso))

    def get_vertices(self):
        return list(self.adjacency.keys())

    def get_neighbors(self, vertex):
        return self.adjacency.get(vertex, [])

    def get_edges(self):
        """Retorna a lista de arestas unicas (origem, destino, peso)."""
        edges = []
        seen = set()
        for origem, vizinhos in self.adjacency.items():
            for destino, peso in vizinhos:
                if self.directed:
                    edges.append((origem, destino, peso))
                else:
                    chave = tuple(sorted((origem, destino))) + (peso,)
                    if chave not in seen:
                        seen.add(chave)
                        edges.append((origem, destino, peso))
        return edges

    def clear(self):
        self.adjacency = {}

    def to_dict(self):
        """Formato serializavel (JSON) para exibir a estrutura no front-end."""
        return {
            "directed": self.directed,
            "weighted": self.weighted,
            "adjacency": {
                v: [{"vizinho": n, "peso": p} for n, p in vizinhos]
                for v, vizinhos in self.adjacency.items()
            },
        }

    def __str__(self):
        linhas = []
        for v, vizinhos in self.adjacency.items():
            vizinhos_str = ", ".join(f"{n}({p})" for n, p in vizinhos)
            linhas.append(f"{v}: {vizinhos_str}")
        return "\n".join(linhas)


def grafo_teste():
    """Grafo de teste do enunciado (nao-direcionado, ponderado)."""
    g = Graph(directed=False, weighted=True)
    arestas = [
        ("O", "A", 2), ("O", "B", 5), ("O", "C", 4),
        ("A", "B", 2), ("A", "D", 7), ("A", "F", 12),
        ("B", "C", 1), ("B", "D", 4), ("B", "E", 3),
        ("C", "E", 4),
        ("D", "E", 4), ("D", "T", 5),
        ("E", "T", 7),
        ("F", "T", 3),
    ]
    for origem, destino, peso in arestas:
        g.add_edge(origem, destino, peso)
    return g


if __name__ == "__main__":
    g = grafo_teste()
    print(g)
