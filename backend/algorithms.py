"""
Algoritmos de grafo implementados do zero sobre a lista de adjacencia (graph.py).

Cada funcao devolve:
  - o resultado final (estrutura pronta para exibir em texto/tabela)
  - um "trace": lista de passos, em ordem cronologica, usada para animar
    a execucao do algoritmo no front-end.

Complexidade (V = numero de vertices, E = numero de arestas):
  - DFS:      O(V + E)       -> cada vertice e cada aresta sao visitados uma vez.
  - BFS:      O(V + E)       -> mesma razao do DFS, mas com fila em vez de pilha.
  - Dijkstra: O((V + E) log V) -> fila de prioridade (heap binario); cada
              vertice e extraido uma vez O(log V), cada aresta pode gerar
              uma insercao no heap O(log V). Exige pesos nao-negativos.
  - Kruskal:  O(E log E)     -> dominado pela ordenacao das arestas; as
              operacoes de Union-Find (com path compression + union by
              rank) sao quase O(1) (inverso de Ackermann) cada.
"""

import heapq
from collections import deque


def dfs(graph, origem):
    visitados = set()
    ordem_visita = []
    arvore = []
    trace = []

    pilha = [(origem, None)]
    while pilha:
        vertice, pai = pilha.pop()
        if vertice in visitados:
            continue

        visitados.add(vertice)
        ordem_visita.append(vertice)
        if pai is not None:
            arvore.append({"origem": pai, "destino": vertice})
        trace.append({"tipo": "visita_vertice", "vertice": vertice, "pai": pai})

        for vizinho, peso in reversed(graph.get_neighbors(vertice)):
            if vizinho not in visitados:
                pilha.append((vizinho, vertice))

    nao_alcancados = [v for v in graph.get_vertices() if v not in visitados]

    return {
        "ordem_visita": ordem_visita,
        "arvore_dfs": arvore,
        "nao_alcancados": nao_alcancados,
        "trace": trace,
    }


def bfs(graph, origem):
    visitados = {origem}
    ordem_visita = []
    distancias = {origem: 0}
    arvore = []
    trace = []

    fila = deque([origem])
    trace.append({"tipo": "enfileira_vertice", "vertice": origem, "pai": None, "distancia": 0})

    while fila:
        vertice = fila.popleft()
        ordem_visita.append(vertice)
        trace.append({"tipo": "processa_vertice", "vertice": vertice})

        for vizinho, peso in graph.get_neighbors(vertice):
            if vizinho not in visitados:
                visitados.add(vizinho)
                distancias[vizinho] = distancias[vertice] + 1
                arvore.append({"origem": vertice, "destino": vizinho})
                fila.append(vizinho)
                trace.append({
                    "tipo": "enfileira_vertice",
                    "vertice": vizinho,
                    "pai": vertice,
                    "distancia": distancias[vizinho],
                })

    nao_alcancados = [v for v in graph.get_vertices() if v not in visitados]

    return {
        "ordem_visita": ordem_visita,
        "distancias_em_saltos": distancias,
        "arvore_bfs": arvore,
        "nao_alcancados": nao_alcancados,
        "trace": trace,
    }


def dijkstra(graph, origem):
    # float("inf") nao e JSON valido (viraria o literal "Infinity" e quebraria
    # JSON.parse no navegador) - por isso sanitizamos para None/null ao expor
    # os valores no resultado e no trace.
    def sanitizar(valor):
        return None if valor == float("inf") else valor

    vertices = graph.get_vertices()
    dist = {v: float("inf") for v in vertices}
    pred = {v: None for v in vertices}
    finalizados = set()
    dist[origem] = 0

    heap = [(0, origem)]
    ordem_finalizacao = []
    trace = []

    while heap:
        d_atual, vertice = heapq.heappop(heap)
        if vertice in finalizados:
            continue

        finalizados.add(vertice)
        ordem_finalizacao.append(vertice)
        trace.append({"tipo": "finaliza_vertice", "vertice": vertice, "distancia": d_atual})

        for vizinho, peso in graph.get_neighbors(vertice):
            if vizinho in finalizados:
                continue
            nova_dist = d_atual + peso
            trace.append({
                "tipo": "explora_aresta",
                "origem": vertice,
                "destino": vizinho,
                "peso": peso,
                "distancia_atual": sanitizar(dist[vizinho]),
                "nova_distancia": nova_dist,
            })
            if nova_dist < dist[vizinho]:
                dist[vizinho] = nova_dist
                pred[vizinho] = vertice
                heapq.heappush(heap, (nova_dist, vizinho))
                trace.append({
                    "tipo": "relaxa_aresta",
                    "origem": vertice,
                    "destino": vizinho,
                    "nova_distancia": nova_dist,
                })

    nao_alcancados = [v for v in vertices if dist[v] == float("inf")]

    return {
        "origem": origem,
        "distancias": {v: sanitizar(d) for v, d in dist.items()},
        "predecessores": pred,
        "ordem_finalizacao": ordem_finalizacao,
        "nao_alcancados": nao_alcancados,
        "trace": trace,
    }


class UnionFind:
    """Disjoint Set Union com path compression + union by rank, do zero."""

    def __init__(self, vertices):
        self.pai = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}

    def find(self, v):
        if self.pai[v] != v:
            self.pai[v] = self.find(self.pai[v])
        return self.pai[v]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.pai[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def kruskal(graph):
    arestas_ordenadas = sorted(graph.get_edges(), key=lambda e: e[2])
    uf = UnionFind(graph.get_vertices())

    mst = []
    rejeitadas = []
    custo_total = 0
    trace = []

    for origem, destino, peso in arestas_ordenadas:
        if uf.find(origem) != uf.find(destino):
            uf.union(origem, destino)
            mst.append({"origem": origem, "destino": destino, "peso": peso})
            custo_total += peso
            trace.append({
                "tipo": "aceita_aresta",
                "origem": origem, "destino": destino, "peso": peso,
                "custo_acumulado": custo_total,
            })
        else:
            rejeitadas.append({"origem": origem, "destino": destino, "peso": peso})
            trace.append({
                "tipo": "rejeita_aresta",
                "origem": origem, "destino": destino, "peso": peso,
                "motivo": "formaria_ciclo",
            })

    return {
        "arestas_mst": mst,
        "custo_total": custo_total,
        "arestas_rejeitadas": rejeitadas,
        "trace": trace,
    }
