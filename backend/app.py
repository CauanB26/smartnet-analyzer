from flask import Flask, jsonify, render_template, request

from algorithms import bfs, dfs, dijkstra, kruskal
from grafos_classicos import (
    DIJKSTRA_CLASSICO_RESULTADO_ESPERADO,
    MST_CLASSICO_CUSTO_ESPERADO,
    grafo_dijkstra_classico,
    grafo_mst_classico,
)
from graph import Graph, grafo_teste

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
)
# Preserva a ordem de insercao dos vertices (ordem real da lista de
# adjacencia) no JSON devolvido pela API. Sem isso, o Flask ordena as
# chaves alfabeticamente por padrao, e a exibicao/selecao de origem no
# front-end nao reflete a ordem real de armazenamento.
app.json.sort_keys = False

estado = {"grafo": Graph()}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/grafo", methods=["GET"])
def obter_grafo():
    return jsonify(estado["grafo"].to_dict())


@app.route("/api/grafo", methods=["POST"])
def definir_grafo():
    dados = request.get_json(force=True)
    directed = bool(dados.get("directed", False))
    weighted = bool(dados.get("weighted", True))

    grafo = Graph(directed=directed, weighted=weighted)
    for aresta in dados.get("edges", []):
        origem = str(aresta["origem"]).strip()
        destino = str(aresta["destino"]).strip()
        peso = float(aresta.get("peso", 1) or 1)
        if not origem or not destino:
            continue
        grafo.add_edge(origem, destino, peso)

    for vertice in dados.get("vertices", []):
        grafo.add_vertex(str(vertice).strip())

    estado["grafo"] = grafo
    return jsonify(grafo.to_dict())


@app.route("/api/grafo", methods=["DELETE"])
def limpar_grafo():
    estado["grafo"] = Graph()
    return jsonify(estado["grafo"].to_dict())


@app.route("/api/grafo-teste", methods=["POST"])
def carregar_grafo_teste():
    estado["grafo"] = grafo_teste()
    return jsonify(estado["grafo"].to_dict())


_GRAFOS_CLASSICOS = {
    "dijkstra": {
        "construtor": grafo_dijkstra_classico,
        "descricao": "Grafo classico (livro-texto) para Dijkstra: 5 vertices, direcionado.",
        "resultado_esperado": f"Distancias esperadas a partir de s: {DIJKSTRA_CLASSICO_RESULTADO_ESPERADO}",
    },
    "mst": {
        "construtor": grafo_mst_classico,
        "descricao": "Grafo classico (livro-texto) para MST: 9 vertices, nao-direcionado.",
        "resultado_esperado": f"Custo total esperado da MST (Kruskal): {MST_CLASSICO_CUSTO_ESPERADO}",
    },
}


@app.route("/api/grafo-classico/<nome>", methods=["POST"])
def carregar_grafo_classico(nome):
    info = _GRAFOS_CLASSICOS.get(nome)
    if info is None:
        return jsonify({"erro": f"Grafo classico '{nome}' nao existe."}), 404

    estado["grafo"] = info["construtor"]()
    resposta = estado["grafo"].to_dict()
    resposta["descricao"] = info["descricao"]
    resposta["resultado_esperado"] = info["resultado_esperado"]
    return jsonify(resposta)


def _vertice_origem_valido(grafo, dados):
    origem = str(dados.get("origem", "")).strip()
    if origem not in grafo.get_vertices():
        return None, (jsonify({"erro": f"Vertice de origem '{origem}' nao existe no grafo."}), 400)
    return origem, None


@app.route("/api/algoritmo/dfs", methods=["POST"])
def rodar_dfs():
    grafo = estado["grafo"]
    origem, erro = _vertice_origem_valido(grafo, request.get_json(force=True))
    if erro:
        return erro
    return jsonify(dfs(grafo, origem))


@app.route("/api/algoritmo/bfs", methods=["POST"])
def rodar_bfs():
    grafo = estado["grafo"]
    origem, erro = _vertice_origem_valido(grafo, request.get_json(force=True))
    if erro:
        return erro
    return jsonify(bfs(grafo, origem))


@app.route("/api/algoritmo/dijkstra", methods=["POST"])
def rodar_dijkstra():
    grafo = estado["grafo"]
    origem, erro = _vertice_origem_valido(grafo, request.get_json(force=True))
    if erro:
        return erro
    return jsonify(dijkstra(grafo, origem))


@app.route("/api/algoritmo/kruskal", methods=["POST"])
def rodar_kruskal():
    grafo = estado["grafo"]
    if grafo.directed:
        return jsonify({"erro": "Kruskal (MST) exige um grafo nao-direcionado."}), 400
    return jsonify(kruskal(grafo))


if __name__ == "__main__":
    app.run(debug=True)
