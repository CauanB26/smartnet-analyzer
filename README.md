# SmartNet Analyzer

Ferramenta de mapeamento e análise de infraestrutura de cidades inteligentes, desenvolvida como Avaliação Contínua (AC) da disciplina de Análise e Complexidade de Algoritmos.

## Integrantes

| Nome | Matrícula |
|---|---|
| Cauan Magalhães Baptista | 202501700632 |
| Bernardo Cicchelli | 202407095852 |

## Dados acadêmicos

| Campo | Valor |
|---|---|
| **Curso** | Engenharia de Software |
| **Disciplina** | Análise e Complexidade de Algoritmos (IBM3121) |
| **Professor** | Cassius Figueiredo |
| **Semestre** | 2026.2 |
| **Avaliação** | AC — SmartNet Analyzer |

## Sobre a aplicação

O SmartNet Analyzer é uma aplicação web que modela a infraestrutura de uma cidade inteligente como um grafo (bairros/pontos de interesse como vértices, vias/conexões como arestas) e executa quatro algoritmos clássicos de grafos sobre esse modelo:

- **DFS (Busca em Profundidade):** auditoria de rotas e verificação de conectividade.
- **BFS (Busca em Largura):** simulação de propagação de alertas/ondas de rádio a partir de um ponto de origem.
- **Dijkstra:** rota mais curta entre um ponto de origem e os demais bairros (ex.: rota de veículos de emergência).
- **Kruskal (Árvore Geradora Mínima):** rede de menor custo capaz de interligar todos os bairros, sem redundâncias.

A aplicação aceita grafos **direcionados ou não-direcionados**, **com ou sem peso**, inseridos manualmente pelo usuário através de um formulário, ou carregados a partir do grafo de teste do enunciado.

### Estrutura de dados: lista de adjacência

O grafo é armazenado internamente em uma **lista de adjacência**, implementada do zero (sem bibliotecas de grafo prontas). A escolha foi feita porque:

- Grafos de infraestrutura urbana tendem a ser **esparsos** (cada bairro se conecta a poucos outros, não a todos) — a lista de adjacência ocupa O(V + E) de memória, contra O(V²) de uma matriz de adjacência, que desperdiçaria espaço com posições vazias.
- Dijkstra e Kruskal consomem diretamente essa estrutura: Dijkstra percorre os vizinhos de um vértice (exatamente o que a lista devolve), e Kruskal precisa apenas de uma lista de arestas ordenadas por peso, trivial de gerar a partir da lista de adjacência.

### Complexidade dos algoritmos (V = vértices, E = arestas)

| Algoritmo | Complexidade | Observação |
|---|---|---|
| DFS | O(V + E) | cada vértice e cada aresta são visitados uma única vez |
| BFS | O(V + E) | mesma razão do DFS, com fila em vez de pilha |
| Dijkstra | O((V + E) log V) | fila de prioridade (heap binário); exige pesos não-negativos |
| Kruskal | O(E log E) | dominado pela ordenação das arestas; Union-Find é quase O(1) por operação |

### Arquitetura

```
Navegador (HTML/CSS/JS)  <-- fetch/JSON -->  Servidor Flask (Python)
  - formulário de entrada do grafo              - Graph: lista de adjacência (do zero)
  - visualização SVG com animação                - DFS, BFS, Dijkstra, Kruskal (do zero)
  - botões dos algoritmos                        - rotas da API (/api/...)
  - tabelas de resultado
```

Cada algoritmo (em Python) devolve, além do resultado final, um "trace": uma sequência de passos da execução. O front-end reproduz esse trace no desenho do grafo, destacando vértices e arestas (atual, visitado, em análise, aceito, rejeitado) com animação, controles de play/pausa/passo-a-passo e velocidade ajustável.

## Como executar

Pré-requisitos: **Python 3.10+** instalado.

1. Clone o repositório e entre na pasta do backend:
   ```bash
   git clone <URL-DO-REPOSITORIO>
   cd <pasta-do-repositorio>/backend
   ```

2. (Recomendado) crie um ambiente virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Linux/Mac
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Rode o servidor:
   ```bash
   python app.py
   ```

5. Abra o navegador em **http://127.0.0.1:5000**

A aplicação abre com o grafo vazio. Use o botão **"Carregar grafo de teste"** para carregar o grafo de exemplo do enunciado (vértices O, A, B, C, D, E, F, T), ou monte um grafo próprio pelo formulário (origem, destino, peso — marcando "Direcionado" e/ou "Ponderado" conforme o caso) e clique em **"Aplicar grafo"**.

Depois de carregar um grafo, escolha o vértice de origem (para DFS/BFS/Dijkstra) e clique em um dos botões de algoritmo para ver a animação e o resultado. O botão **"Finalizar aplicação"** encerra o loop interativo.

## Estrutura do repositório

```
backend/
  app.py              # servidor Flask + rotas da API
  graph.py             # estrutura de dados (lista de adjacência)
  algorithms.py         # DFS, BFS, Dijkstra, Kruskal
  test_algorithms.py    # validação dos algoritmos com o grafo de teste
  requirements.txt
frontend/
  templates/index.html
  static/style.css
  static/script.js
enunciado.md            # enunciado original da atividade
```
