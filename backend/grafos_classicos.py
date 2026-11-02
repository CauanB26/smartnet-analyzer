"""
Grafos classicos de livros-texto de algoritmos (ex.: CLRS - Cormen,
Leiserson, Rivest, Stein, "Introduction to Algorithms"), usados tanto
pelos testes automatizados (test_grafos_classicos.py) quanto pela propria
aplicacao (botoes "Grafo classico" na interface) - para demonstrar que a
implementacao funciona corretamente em grafos conhecidos e nunca vistos
durante o desenvolvimento, o mesmo cenario de quando o professor propoe
um grafo inedito na apresentacao.

Cada funcao documenta tambem o resultado esperado, para que a corretude
possa ser conferida "a olho" (sem rodar os testes) tanto pelo grupo
quanto pelo professor.
"""

from graph import Graph

DIJKSTRA_CLASSICO_RESULTADO_ESPERADO = {"s": 0, "t": 8, "x": 9, "y": 5, "z": 7}
MST_CLASSICO_CUSTO_ESPERADO = 37


def grafo_dijkstra_classico():
    """Grafo direcionado e ponderado classico (5 vertices: s, t, x, y, z),
    usado em livros-texto de algoritmos para ilustrar o Dijkstra.

    Distancias minimas esperadas a partir de s:
        s=0, t=8, x=9, y=5, z=7
    """
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
    usado em livros-texto de algoritmos para ilustrar MST (Kruskal/Prim).

    Custo total esperado da arvore geradora minima: 37
    (um conjunto possivel de arestas: g-h(1), c-i(2), f-g(2), a-b(4),
    c-f(4), c-d(7), a-h(8), d-e(9) - pode variar em caso de empate de
    peso, mas o custo total minimo e sempre 37).
    """
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
