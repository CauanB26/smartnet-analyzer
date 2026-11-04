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

Cada funcao abaixo repete essa analise de forma detalhada, logo antes do
"return", explicando quantas vezes cada trecho de codigo roda e por que
isso soma na complexidade final. Essa e a explicacao que o professor
espera ouvir na apresentacao (criterio "dominio da complexidade").
"""

import heapq
from collections import deque


def dfs(graph, origem):
    """Busca em profundidade (DFS), iterativa, usando uma pilha explicita
    em vez de recursao (evita o limite de recursao do Python e deixa o
    "trace" totalmente sob nosso controle)."""

    visitados = set()      # vertices ja processados (nao podem ser reabertos)
    ordem_visita = []       # ordem em que os vertices foram de fato visitados
    arvore = []              # arestas da arvore de busca (quem descobriu quem)
    trace = []                # passo a passo, para a animacao no front-end

    # Cada item da pilha e (vertice, pai-que-o-empilhou). O vertice inicial
    # nao tem pai (None). Usamos uma pilha (lista + pop/append no final) e
    # nao uma fila: pilha = LIFO = "vai fundo num caminho antes de voltar",
    # que e exatamente a definicao de busca em PROFUNDIDADE.
    pilha = [(origem, None)]

    while pilha:
        # pop() sem indice remove do FINAL da lista -> comportamento de pilha.
        vertice, pai = pilha.pop()

        # Um mesmo vertice pode ter sido empilhado mais de uma vez (por
        # vizinhos diferentes, antes de ser processado). Se ja foi
        # visitado, essa entrada da pilha esta "velha" e e descartada.
        if vertice in visitados:
            continue

        # Primeira vez que esse vertice sai da pilha -> ele e "visitado" agora.
        visitados.add(vertice)
        ordem_visita.append(vertice)
        if pai is not None:
            # pai -> vertice e uma aresta da arvore de busca em profundidade
            # (o vertice raiz nao tem aresta de entrada, por isso o "if").
            arvore.append({"origem": pai, "destino": vertice})
        trace.append({"tipo": "visita_vertice", "vertice": vertice, "pai": pai})

        # Empilha os vizinhos ainda nao visitados. O "reversed" aqui e o
        # detalhe mais sutil do algoritmo: como a pilha desempilha do
        # final para o inicio (LIFO), se empilharmos os vizinhos na ordem
        # normal da lista de adjacencia, o ULTIMO vizinho seria visitado
        # primeiro (ordem invertida). Empilhando de tras para frente,
        # o PRIMEIRO vizinho da lista acaba sendo o primeiro a ser
        # desempilhado e visitado, preservando a ordem "natural" da lista
        # de adjacencia na busca.
        for vizinho, peso in reversed(graph.get_neighbors(vertice)):
            if vizinho not in visitados:
                pilha.append((vizinho, vertice))

    # Vertices que nunca foram alcancados por esse DFS = vertices em outro
    # componente conexo (grafo desconexo) ou inalcancaveis (grafo direcionado).
    nao_alcancados = [v for v in graph.get_vertices() if v not in visitados]

    # --- Conta de complexidade: O(V + E) ---
    # O laco "while pilha" processa cada vertice (de fato o "visita") no
    # maximo uma vez -> V iteracoes "uteis". Cada vertice visitado, quando
    # processado, percorre sua lista de vizinhos uma unica vez
    # (graph.get_neighbors(vertice)). A soma dos tamanhos de TODAS as
    # listas de vizinhos, para todos os vertices, e exatamente o numero de
    # arestas (E, se o grafo for direcionado; 2E se for nao-direcionado,
    # pois cada aresta aparece duas vezes na lista de adjacencia) -> isso
    # da o termo E. Empilhar/desempilhar e sempre O(1). Logo, o trabalho
    # total e proporcional a V (vertices processados) + E (arestas
    # examinadas) = O(V + E).
    return {
        "ordem_visita": ordem_visita,
        "arvore_dfs": arvore,
        "nao_alcancados": nao_alcancados,
        "trace": trace,
    }


def bfs(graph, origem):
    """Busca em largura (BFS): usa uma fila (FIFO) em vez de pilha, por
    isso avanca "em camadas" (todos os vizinhos de distancia 1 antes dos
    de distancia 2, e assim por diante)."""

    # Diferenca importante em relacao ao DFS: aqui marcamos um vertice como
    # visitado no momento em que ele ENTRA na fila (e nao quando sai dela).
    # Isso garante que cada vertice entre na fila no maximo uma vez.
    visitados = {origem}
    ordem_visita = []
    distancias = {origem: 0}   # distancia em NUMERO DE ARESTAS (saltos), nao em peso
    arvore = []
    trace = []

    fila = deque([origem])      # deque permite popleft() em O(1); list.pop(0) seria O(n)
    trace.append({"tipo": "enfileira_vertice", "vertice": origem, "pai": None, "distancia": 0})

    while fila:
        # popleft() remove do INICIO da fila -> comportamento FIFO (o
        # primeiro vertice a entrar e o primeiro a sair), o que faz a
        # busca avancar em largura, por camadas.
        vertice = fila.popleft()
        ordem_visita.append(vertice)
        trace.append({"tipo": "processa_vertice", "vertice": vertice})

        # O "peso" de cada aresta e ignorado de proposito: BFS simula a
        # propagacao de um alerta/onda, onde cada conexao custa sempre
        # "1 salto", independentemente da distancia real da via.
        for vizinho, peso in graph.get_neighbors(vertice):
            if vizinho not in visitados:
                # Marca como visitado JA AO DESCOBRIR (nao ao processar),
                # para nunca enfileirar o mesmo vertice duas vezes.
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

    # --- Conta de complexidade: O(V + E) ---
    # Cada vertice entra na fila uma unica vez (garantido pelo "visitados"
    # marcado na descoberta) -> o laco "while fila" roda no maximo V vezes.
    # Para cada vertice retirado da fila, percorremos sua lista de
    # vizinhos uma vez; somando isso para todos os vertices, o total de
    # "passos de vizinho" e E (ou 2E em grafo nao-direcionado), pelo
    # mesmo motivo explicado no DFS. Enfileirar/desenfileirar com deque e
    # O(1). Resultado: O(V) + O(E) = O(V + E), igual ao DFS, so que a
    # ORDEM em que os vertices sao visitados e diferente (por camada, nao
    # por profundidade).
    return {
        "ordem_visita": ordem_visita,
        "distancias_em_saltos": distancias,
        "arvore_bfs": arvore,
        "nao_alcancados": nao_alcancados,
        "trace": trace,
    }


def dijkstra(graph, origem):
    """Caminho minimo (ponderado) a partir de um vertice de origem, usando
    uma fila de prioridade (heap binario). Exige que todos os pesos sejam
    nao-negativos (e a premissa que garante que o algoritmo funciona)."""

    # float("inf") nao e JSON valido (viraria o literal "Infinity" e quebraria
    # JSON.parse no navegador) - por isso sanitizamos para None/null ao expor
    # os valores no resultado e no trace.
    def sanitizar(valor):
        return None if valor == float("inf") else valor

    vertices = graph.get_vertices()
    dist = {v: float("inf") for v in vertices}   # melhor distancia conhecida até agora
    pred = {v: None for v in vertices}             # por onde se chega em cada vertice
    finalizados = set()                              # vertices com distancia DEFINITIVA
    dist[origem] = 0

    # heapq em Python e um min-heap: heap[0] e sempre o menor elemento.
    # Cada item e uma tupla (distancia, vertice); como tuplas sao
    # comparadas posicao a posicao, o heap ordena automaticamente pela
    # distancia (e, em caso de empate, pelo nome do vertice).
    heap = [(0, origem)]
    ordem_finalizacao = []
    trace = []

    while heap:
        # Remove do heap o vertice com MENOR distancia conhecida entre os
        # ainda nao finalizados. Essa e a escolha "greedy" (gulosa) do
        # algoritmo: assumir que esse vertice ja nao pode mais melhorar.
        d_atual, vertice = heapq.heappop(heap)

        # Lazy deletion: como o heapq do Python nao tem "decrease-key"
        # (atualizar a prioridade de um item que ja esta no heap), toda
        # vez que melhoramos a distancia de um vertice nos simplesmente
        # empilhamos uma NOVA entrada para ele (ver "heappush" mais
        # abaixo). Isso significa que o mesmo vertice pode aparecer
        # varias vezes no heap, com distancias diferentes. Quando uma
        # entrada "velha" (de um vertice que ja foi finalizado com uma
        # distancia menor) sai do heap, ela e simplesmente ignorada.
        if vertice in finalizados:
            continue

        # Por que, ao finalizar, a distancia nunca mais muda? Porque
        # todos os pesos sao nao-negativos: se esse e o vertice de menor
        # distancia entre todos os "candidatos" no heap, nenhum caminho
        # que passe por um vertice ainda nao processado (com distancia
        # maior ou igual) poderia chegar a ele com um custo menor. E essa
        # garantia que quebra se existir peso negativo.
        finalizados.add(vertice)
        ordem_finalizacao.append(vertice)
        trace.append({"tipo": "finaliza_vertice", "vertice": vertice, "distancia": d_atual})

        for vizinho, peso in graph.get_neighbors(vertice):
            if vizinho in finalizados:
                # Vertice ja tem distancia definitiva; nao ha nada a melhorar.
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
            # "Relaxamento" (termo classico do livro-texto): se o caminho
            # ATE AQUI (d_atual) MAIS o peso desta aresta for menor do que
            # a melhor distancia conhecida para o vizinho, encontramos um
            # caminho melhor para ele.
            if nova_dist < dist[vizinho]:
                dist[vizinho] = nova_dist
                pred[vizinho] = vertice
                # Empilha uma nova entrada no heap para o vizinho, com a
                # distancia atualizada (ver comentario de "lazy deletion").
                heapq.heappush(heap, (nova_dist, vizinho))
                trace.append({
                    "tipo": "relaxa_aresta",
                    "origem": vertice,
                    "destino": vizinho,
                    "nova_distancia": nova_dist,
                })

    # Vertices que continuam com distancia infinita nunca foram alcancados.
    nao_alcancados = [v for v in vertices if dist[v] == float("inf")]

    # --- Conta de complexidade: O((V + E) log V) ---
    # Cada relaxamento bem-sucedido gera UM heappush (no maximo E vezes,
    # uma por aresta, mais o push inicial do vertice de origem) -> no
    # maximo O(E) elementos passam pelo heap ao longo de toda a execucao.
    # Cada heappush/heappop custa O(log tamanho_do_heap); como o heap
    # nunca tem mais que O(E) elementos, e E <= V*(V-1), log(E) e da mesma
    # ordem que log(V) -> cada operacao de heap custa O(log V). Somando:
    # O(E) operacoes de heap, cada uma O(log V), da O(E log V). Alem
    # disso, cada vertice e "finalizado" (e tem seus vizinhos
    # examinados) no maximo uma vez, e a soma dos tamanhos das listas de
    # vizinhos de todos os vertices e O(E) -> mais O(V + E) de trabalho
    # "fora do heap". Total: O(V + E) + O(E log V) = O((V + E) log V).
    return {
        "origem": origem,
        "distancias": {v: sanitizar(d) for v, d in dist.items()},
        "predecessores": pred,
        "ordem_finalizacao": ordem_finalizacao,
        "nao_alcancados": nao_alcancados,
        "trace": trace,
    }


class UnionFind:
    """Disjoint Set Union (DSU) com path compression + union by rank, do
    zero. Cada "conjunto" representa um componente conexo que ja foi
    interligado pelas arestas aceitas no Kruskal; serve para responder
    rapidamente "esses dois vertices ja estao no mesmo componente?"."""

    def __init__(self, vertices):
        # No inicio, cada vertice e seu proprio representante (cada um e
        # um conjunto isolado, de tamanho 1).
        self.pai = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}   # estimativa da "altura" da arvore de cada conjunto

    def find(self, v):
        """Devolve o representante (raiz) do conjunto de v."""
        if self.pai[v] != v:
            # Path compression: ao subir ate a raiz, faz cada vertice no
            # caminho apontar DIRETO para a raiz. Isso "achata" a arvore,
            # tornando chamadas futuras de find() muito mais rapidas.
            self.pai[v] = self.find(self.pai[v])
        return self.pai[v]

    def union(self, a, b):
        """Junta os conjuntos de a e b. Devolve False se ja estavam no
        mesmo conjunto (ou seja, juntar a e b criaria um ciclo)."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False  # mesmo conjunto -> uniria o que ja esta unido (ciclo)

        # Union by rank: sempre pendura a arvore de MENOR rank embaixo da
        # raiz de MAIOR rank (nunca o contrario). Isso evita que a arvore
        # resultante cresca em altura sem necessidade, mantendo o find()
        # rapido mesmo sem a compressao de caminho.
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.pai[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            # Só quando as duas arvores tinham a MESMA altura estimada a
            # arvore resultante fica efetivamente mais alta.
            self.rank[ra] += 1
        return True

    # --- Conta de complexidade (find/union): praticamente O(1) ---
    # Usando SO path compression, uma sequencia de operacoes já fica
    # O(log V) cada, no pior caso. Usando path compression JUNTO com
    # union by rank (as duas otimizacoes combinadas, como aqui), o custo
    # amortizado de cada find/union cai para O(alfa(V)), onde alfa e a
    # funcao inversa de Ackermann: ela cresce tao devagar que, para
    # qualquer V que caberia na memoria de um computador real, alfa(V) e
    # menor que 5. Por isso se diz, na pratica, que cada operacao e
    # "quase O(1)".


def kruskal(graph):
    """Arvore Geradora Minima (MST): conjunto de arestas de custo total
    minimo que conecta todos os vertices, sem formar ciclos. Estrategia
    gulosa (greedy): considera sempre a aresta mais barata disponivel."""

    # Ordenar as arestas por peso e o que torna o algoritmo "guloso":
    # ao processar da mais barata para a mais cara, e aceitar uma aresta
    # sempre que ela nao fecha ciclo, prova-se (propriedade do corte, vista
    # na teoria) que o resultado final tem custo total minimo.
    arestas_ordenadas = sorted(graph.get_edges(), key=lambda e: e[2])
    uf = UnionFind(graph.get_vertices())

    mst = []              # arestas aceitas (vao compor a arvore geradora minima)
    rejeitadas = []        # arestas descartadas (formariam ciclo)
    custo_total = 0
    trace = []

    for origem, destino, peso in arestas_ordenadas:
        # Se origem e destino ja estao no MESMO componente (mesma raiz no
        # Union-Find), ja existe algum caminho entre eles usando arestas
        # ja aceitas -> adicionar esta aresta formaria um ciclo.
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

    # Observacao: se o grafo nao for conexo, o resultado nao e uma unica
    # arvore, e sim uma FLORESTA geradora minima (uma arvore por
    # componente conexo) - o laco acima nunca exige conectividade total,
    # so rejeita o que formaria ciclo.

    # --- Conta de complexidade: O(E log E) ---
    # 1) Ordenar as E arestas: O(E log E) - este e o termo que domina.
    # 2) O laco percorre as E arestas uma a uma; para cada uma, faz no
    #    maximo 2 chamadas de find() e, se aceitar, 1 chamada de union().
    #    Como visto na classe UnionFind, cada uma dessas chamadas custa
    #    praticamente O(1) (mais precisamente O(alfa(V)), o inverso de
    #    Ackermann). Logo, o laco inteiro custa O(E * alfa(V)), que é
    #    desprezivel frente a O(E log E).
    # Total: O(E log E) + O(E * alfa(V))  =  O(E log E).
    return {
        "arestas_mst": mst,
        "custo_total": custo_total,
        "arestas_rejeitadas": rejeitadas,
        "trace": trace,
    }
