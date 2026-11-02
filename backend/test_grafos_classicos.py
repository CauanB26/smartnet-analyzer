"""
Testes com grafos classicos de livros-texto de algoritmos (ex.: CLRS -
Cormen, Leiserson, Rivest, Stein - "Introduction to Algorithms"), cujos
resultados sao amplamente conhecidos e usados em cursos de algoritmos
para ilustrar Dijkstra e MST. Isso complementa os testes com o grafo do
enunciado, mostrando que a implementacao tambem funciona corretamente em
grafos nunca vistos durante o desenvolvimento - o mesmo cenario da
apresentacao, em que o professor propoe um grafo inedito.
"""

from algorithms import bfs, dfs, dijkstra, kruskal
from graph import Graph, grafo_teste
from test_helpers import assert_dijkstra_valido, assert_mst_valida, prim_mst_peso_total


def grafo_dijkstra_classico():
    """Grafo direcionado e ponderado classico (5 vertices: s, t, x, y, z),
    usado em livros-texto de algoritmos para ilustrar o Dijkstra."""
    g = Graph(directed=True, weighted=True)
    arestas = [
        ("s", "t", 10), ("s", "y", 5),
        ("t", "x", 1), ("t", "y", 2),
        ("x", "z", 4),
        ("y", "t", 3), ("y", "x", 9), ("y", "z", 2),
        ("z", "s", 7), ("z", "x", 6),
    ]
    for origem, destino, peso in arestas:
        g.add_edge(origem, destino, peso)
    return g


def grafo_mst_classico():
    """Grafo nao-direcionado e ponderado classico (9 vertices, a..i),
    usado em livros-texto de algoritmos para ilustrar MST (Kruskal/Prim)."""
    g = Graph(directed=False, weighted=True)
    arestas = [
        ("a", "b", 4), ("a", "h", 8),
        ("b", "c", 8), ("b", "h", 11),
        ("c", "d", 7), ("c", "f", 4), ("c", "i", 2),
        ("d", "e", 9), ("d", "f", 14),
        ("e", "f", 10),
        ("f", "g", 2),
        ("g", "h", 1), ("g", "i", 6),
        ("h", "i", 7),
    ]
    for origem, destino, peso in arestas:
        g.add_edge(origem, destino, peso)
    return g


def test_dijkstra_grafo_classico_distancias_conhecidas():
    g = grafo_dijkstra_classico()
    r = dijkstra(g, "s")
    esperado = {"s": 0, "t": 8, "x": 9, "y": 5, "z": 7}
    assert r["distancias"] == esperado


def test_dijkstra_grafo_classico_satisfaz_propriedades_gerais():
    g = grafo_dijkstra_classico()
    r = dijkstra(g, "s")
    assert_dijkstra_valido(g, r, "s")


def test_kruskal_grafo_classico_peso_total_conhecido():
    g = grafo_mst_classico()
    r = kruskal(g)
    assert r["custo_total"] == 37


def test_kruskal_grafo_classico_produz_arvore_geradora_valida():
    g = grafo_mst_classico()
    r = kruskal(g)
    assert_mst_valida(g, r)


def test_kruskal_bate_com_prim_no_grafo_classico():
    """Kruskal e Prim sao algoritmos diferentes; se os dois, implementados
    de forma independente, concordam no peso total, isso e evidencia forte
    de que a implementacao do Kruskal esta correta - nao so 'decorou' o
    resultado de um grafo especifico."""
    g = grafo_mst_classico()
    r = kruskal(g)
    assert r["custo_total"] == prim_mst_peso_total(g)


def test_kruskal_bate_com_prim_no_grafo_do_enunciado():
    g = grafo_teste()
    r = kruskal(g)
    assert r["custo_total"] == prim_mst_peso_total(g)


def test_dfs_e_bfs_alcancam_o_mesmo_conjunto_de_vertices():
    """DFS e BFS podem visitar em ordens diferentes, mas devem sempre
    alcancar exatamente o mesmo conjunto de vertices (o componente
    conexo da origem) - essa e a propriedade que de fato importa, e nao
    uma ordem de visita especifica."""
    g = grafo_mst_classico()
    r_dfs = dfs(g, "a")
    r_bfs = bfs(g, "a")
    assert set(r_dfs["ordem_visita"]) == set(g.get_vertices())
    assert set(r_bfs["ordem_visita"]) == set(g.get_vertices())
    assert set(r_dfs["ordem_visita"]) == set(r_bfs["ordem_visita"])


def test_dfs_no_grafo_direcionado_classico_respeita_direcao_das_arestas():
    """No grafo direcionado classico, z aponta para s e para x, mas s e x
    nao apontam de volta para z por aresta direta - entao, partindo de s,
    DFS/BFS devem alcancar z (via y) mas nao podem usar arestas que nao
    existem no sentido percorrido."""
    g = grafo_dijkstra_classico()
    r = dfs(g, "s")
    for aresta in r["arvore_dfs"]:
        vizinhos = [v for v, _ in g.get_neighbors(aresta["origem"])]
        assert aresta["destino"] in vizinhos
