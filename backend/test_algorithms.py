"""Testes dos 4 algoritmos sobre o grafo de teste do proprio enunciado
(O, A, B, C, D, E, F, T) - ver enunciado.md, secao 5."""

from algorithms import bfs, dfs, dijkstra, kruskal
from graph import grafo_teste
from test_helpers import assert_dijkstra_valido, assert_mst_valida, prim_mst_peso_total


def test_dfs_alcanca_todos_os_vertices():
    g = grafo_teste()
    r = dfs(g, "O")
    assert set(r["ordem_visita"]) == set(g.get_vertices())
    assert r["nao_alcancados"] == []


def test_dfs_arestas_da_arvore_existem_no_grafo():
    g = grafo_teste()
    r = dfs(g, "O")
    for aresta in r["arvore_dfs"]:
        vizinhos = [v for v, _ in g.get_neighbors(aresta["origem"])]
        assert aresta["destino"] in vizinhos


def test_bfs_processa_em_ordem_de_distancia_nao_decrescente():
    g = grafo_teste()
    r = bfs(g, "O")
    dist = r["distancias_em_saltos"]
    ordem = r["ordem_visita"]
    assert all(dist[ordem[i]] <= dist[ordem[i + 1]] for i in range(len(ordem) - 1))


def test_bfs_distancia_em_saltos_da_origem_e_zero():
    g = grafo_teste()
    r = bfs(g, "O")
    assert r["distancias_em_saltos"]["O"] == 0


def test_dijkstra_distancias_batem_com_calculo_manual():
    g = grafo_teste()
    r = dijkstra(g, "O")
    esperado = {"O": 0, "A": 2, "B": 4, "C": 4, "D": 8, "E": 7, "F": 14, "T": 13}
    assert r["distancias"] == esperado


def test_dijkstra_satisfaz_propriedades_gerais_de_corretude():
    g = grafo_teste()
    r = dijkstra(g, "O")
    assert_dijkstra_valido(g, r, "O")


def test_kruskal_custo_total_da_mst():
    g = grafo_teste()
    r = kruskal(g)
    assert r["custo_total"] == 20


def test_kruskal_produz_arvore_geradora_valida():
    g = grafo_teste()
    r = kruskal(g)
    assert_mst_valida(g, r)


def test_kruskal_bate_com_prim_algoritmo_independente():
    g = grafo_teste()
    r = kruskal(g)
    assert r["custo_total"] == prim_mst_peso_total(g)
