from graph import grafo_teste
from algorithms import dfs, bfs, dijkstra, kruskal

g = grafo_teste()

print("=== DFS a partir de O ===")
r = dfs(g, "O")
print("Ordem de visita:", r["ordem_visita"])
print("Nao alcancados:", r["nao_alcancados"])
print("Passos no trace:", len(r["trace"]))

print("\n=== BFS a partir de O ===")
r = bfs(g, "O")
print("Ordem de visita (fila):", r["ordem_visita"])
print("Distancias em saltos:", r["distancias_em_saltos"])

print("\n=== Dijkstra a partir de O ===")
r = dijkstra(g, "O")
print("Distancias:", r["distancias"])
print("Predecessores:", r["predecessores"])
esperado = {"O": 0, "A": 2, "B": 4, "C": 4, "D": 8, "E": 7, "F": 14, "T": 13}
print("Esperado:      ", esperado)
assert r["distancias"] == esperado, "DIVERGIU do esperado!"
print("OK: bate com o calculo manual.")

print("\n=== Kruskal (MST) ===")
r = kruskal(g)
for a in r["arestas_mst"]:
    print(f"  {a['origem']} - {a['destino']} (peso {a['peso']})")
print("Custo total:", r["custo_total"])
assert r["custo_total"] == 20, "Custo da MST diferente do esperado (20)!"
print("OK: custo total bate com o calculo manual.")
