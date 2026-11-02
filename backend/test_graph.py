from graph import Graph


def test_grafo_nao_direcionado_adiciona_aresta_nos_dois_sentidos():
    g = Graph(directed=False, weighted=True)
    g.add_edge("A", "B", 5)
    assert ("B", 5) in g.get_neighbors("A")
    assert ("A", 5) in g.get_neighbors("B")


def test_grafo_direcionado_adiciona_aresta_em_um_sentido_so():
    g = Graph(directed=True, weighted=True)
    g.add_edge("A", "B", 5)
    assert ("B", 5) in g.get_neighbors("A")
    assert ("A", 5) not in g.get_neighbors("B")


def test_grafo_sem_peso_forca_peso_unitario():
    g = Graph(directed=False, weighted=False)
    g.add_edge("A", "B", 99)
    assert g.get_neighbors("A") == [("B", 1)]


def test_vertice_isolado_aparece_na_lista_de_adjacencia():
    g = Graph()
    g.add_vertex("X")
    assert g.get_vertices() == ["X"]
    assert g.get_neighbors("X") == []


def test_get_edges_nao_duplica_aresta_em_grafo_nao_direcionado():
    g = Graph(directed=False, weighted=True)
    g.add_edge("A", "B", 3)
    assert len(g.get_edges()) == 1


def test_get_edges_mantem_as_duas_direcoes_em_grafo_direcionado():
    g = Graph(directed=True, weighted=True)
    g.add_edge("A", "B", 3)
    g.add_edge("B", "A", 7)
    assert len(g.get_edges()) == 2


def test_clear_esvazia_o_grafo():
    g = Graph()
    g.add_edge("A", "B", 1)
    g.clear()
    assert g.get_vertices() == []
