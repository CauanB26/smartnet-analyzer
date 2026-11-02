"""
Verificacoes de propriedade (property-based), reutilizaveis em qualquer
grafo - nao dependem de decorar o resultado esperado de um grafo
especifico. Usadas pelos testes para validar Dijkstra e Kruskal de forma
mais rigorosa do que apenas comparar com um valor fixo.
"""

import heapq


def assert_dijkstra_valido(grafo, resultado, origem):
    """Toda solucao correta de Dijkstra satisfaz:
      1) distancia da origem para si mesma e 0;
      2) nenhuma aresta viola a desigualdade triangular:
         dist[v] <= dist[u] + peso(u, v);
      3) a distancia de cada vertice alcancado bate com
         dist[predecessor] + peso da aresta usada para chegar nele.
    """
    dist = resultado["distancias"]
    pred = resultado["predecessores"]
    assert dist[origem] == 0

    for u in grafo.get_vertices():
        if dist[u] is None:
            continue
        for v, peso in grafo.get_neighbors(u):
            if dist[v] is not None:
                assert dist[v] <= dist[u] + peso, f"desigualdade triangular violada em {u}->{v}"

    for v in grafo.get_vertices():
        if v == origem or dist[v] is None:
            continue
        p = pred[v]
        assert p is not None, f"vertice alcancado {v} sem predecessor"
        peso_aresta = next(peso for destino, peso in grafo.get_neighbors(p) if destino == v)
        assert dist[v] == dist[p] + peso_aresta


def assert_mst_valida(grafo, resultado):
    """Verifica que o resultado do Kruskal eh uma arvore geradora valida:
    exatamente V-1 arestas, sem ciclos, conectando todos os vertices."""
    vertices = grafo.get_vertices()
    arestas = resultado["arestas_mst"]
    assert len(arestas) == len(vertices) - 1

    pai = {v: v for v in vertices}

    def find(v):
        while pai[v] != v:
            v = pai[v]
        return v

    for a in arestas:
        ra, rb = find(a["origem"]), find(a["destino"])
        assert ra != rb, "MST com ciclo"
        pai[ra] = rb

    raizes = {find(v) for v in vertices}
    assert len(raizes) == 1, "MST nao conecta todos os vertices"


def prim_mst_peso_total(grafo):
    """Implementacao de referencia (Prim), usada SO nos testes, para
    validar por um caminho algoritmico independente o peso total que o
    Kruskal (algorithms.py) calcula. Se dois algoritmos diferentes,
    implementados de forma independente, concordam no peso total, isso e
    evidencia forte de que a implementacao esta correta."""
    vertices = grafo.get_vertices()
    if not vertices:
        return 0

    visitado = set()
    inicio = vertices[0]
    visitado.add(inicio)
    heap = [(peso, v) for v, peso in grafo.get_neighbors(inicio)]
    heapq.heapify(heap)

    custo_total = 0
    while heap and len(visitado) < len(vertices):
        peso, v = heapq.heappop(heap)
        if v in visitado:
            continue
        visitado.add(v)
        custo_total += peso
        for prox, p2 in grafo.get_neighbors(v):
            if prox not in visitado:
                heapq.heappush(heap, (p2, prox))

    return custo_total
