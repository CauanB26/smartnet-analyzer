# SmartNet Analyzer

Ferramenta de mapeamento e análise de infraestrutura de cidades inteligentes, desenvolvida como Avaliação Contínua (AC) da disciplina de Análise e Complexidade de Algoritmos.

## Integrantes

| Nome | Matrícula |
|---|---|
| Cauan Magalhães Baptista | 202501700632 |
| Bernardo Cicchelli | 202407095852 |
| Luahn Kayê | 202507377256 |

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

### Como o front-end se comunica com o back-end

Não existe lógica de grafo nem de algoritmo em JavaScript. O front-end só desenha e anima; quem calcula é sempre o Python. A comunicação é via `fetch()` fazendo requisições HTTP para uma API REST servida pelo próprio Flask (mesma origem, sem CORS):

| Método | Rota | O que faz | Corpo da requisição | Resposta |
|---|---|---|---|---|
| GET | `/api/grafo` | Devolve o grafo atualmente em memória | — | `{ directed, weighted, adjacency }` |
| POST | `/api/grafo` | Substitui o grafo atual pelo enviado | `{ directed, weighted, edges: [...] }` | grafo atualizado |
| DELETE | `/api/grafo` | Apaga o grafo atual | — | grafo vazio |
| POST | `/api/grafo-teste` | Carrega o grafo de teste do enunciado | — | grafo carregado |
| POST | `/api/algoritmo/dfs` | Executa DFS a partir de um vértice | `{ origem }` | resultado + `trace` |
| POST | `/api/algoritmo/bfs` | Executa BFS a partir de um vértice | `{ origem }` | resultado + `trace` |
| POST | `/api/algoritmo/dijkstra` | Executa Dijkstra a partir de um vértice | `{ origem }` | resultado + `trace` |
| POST | `/api/algoritmo/kruskal` | Executa Kruskal (MST) | `{}` | resultado + `trace` |

Fluxo típico: o usuário clica em "Aplicar grafo" → `script.js` monta um JSON com as arestas digitadas → `POST /api/grafo` → `app.py` reconstrói o objeto `Graph` (lista de adjacência) do zero e devolve a estrutura em JSON → o front redesenha o SVG. Ao clicar em um algoritmo, o mesmo padrão se repete: `POST /api/algoritmo/<nome>` → `algorithms.py` roda o algoritmo sobre o `Graph` atual e devolve o resultado final **e** o `trace` (lista de passos) → o JavaScript reproduz o `trace` no SVG, um passo por vez, de forma animada.

## Como executar

Pré-requisitos: **Python 3.10+** instalado.

**Resumo rápido (copiar e colar):**
```bash
git clone https://github.com/CauanB26/smartnet-analyzer.git
cd smartnet-analyzer/backend
python -m venv venv && venv\Scripts\activate   # Windows (use source venv/bin/activate no Linux/Mac)
pip install -r requirements.txt
python app.py
```
Depois abra **http://127.0.0.1:5000** no navegador.

**Passo a passo:**

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

### Entrando com um grafo novo (ex.: o grafo do professor na apresentação)

Há duas formas de inserir arestas, nas abas do passo 1:

- **"Uma por vez":** digite origem/destino/peso e clique em "+ Aresta" (repita para cada aresta). Também dá pra adicionar um vértice isolado (sem arestas) pelo campo abaixo.
- **"Colar em lote":** cole várias linhas de uma vez, uma aresta por linha, no formato `origem destino peso` (peso é opcional se o grafo não for ponderado). Essa opção **substitui** a lista de arestas pendente — útil para digitar rapidamente um grafo grande ditado na hora.

Em ambos os casos, marque "Direcionado" e/ou "Ponderado" conforme o grafo pedido, e só depois clique em **"Aplicar grafo"** para efetivamente construir a estrutura e habilitar os algoritmos.

## Testes automatizados

Além dos quatro algoritmos funcionarem na interface, o projeto tem uma suíte de testes automatizados (`pytest`) que verifica a corretude de forma mais rigorosa do que apenas rodar e olhar o resultado manualmente:

- **`test_graph.py`** — testa a estrutura de dados (lista de adjacência): grafos direcionados/não-direcionados, com/sem peso, vértices isolados.
- **`test_algorithms.py`** — testa os 4 algoritmos no grafo de teste do próprio enunciado.
- **`test_grafos_classicos.py`** — testa os algoritmos em **grafos clássicos de livros-texto de algoritmos** (o grafo de 5 vértices usado para ilustrar Dijkstra e o grafo de 9 vértices usado para ilustrar MST, ambos com resultados numéricos amplamente conhecidos), simulando o cenário de "grafo nunca visto antes" — o mesmo da apresentação.
- **`test_helpers.py`** — verificações de propriedade reutilizáveis, que não dependem de decorar um resultado específico:
  - Dijkstra: checa a desigualdade triangular (`dist[v] <= dist[u] + peso(u,v)`) para toda aresta, e que cada distância bate com `dist[predecessor] + peso`.
  - Kruskal: checa que o resultado é uma árvore geradora válida (V-1 arestas, sem ciclos, conecta todos os vértices), e cruza o custo total com uma implementação independente de **Prim** (dois algoritmos diferentes concordando no resultado é uma evidência forte de corretude).

Para rodar os testes:
```bash
cd backend
pip install -r requirements-dev.txt
pytest -v
```

### Validar pela própria interface (sem rodar pytest)

Na seção "Grafos clássicos (testes)" da interface, há dois botões que carregam os mesmos grafos usados em `test_grafos_classicos.py` diretamente na aplicação:

- **"Clássico: Dijkstra"** — carrega o grafo de 5 vértices abaixo e mostra o resultado esperado na tela; basta rodar o algoritmo Dijkstra a partir de `s` e comparar.
- **"Clássico: MST"** — carrega o grafo de 9 vértices abaixo; basta rodar o Kruskal e comparar o custo total.

Isso permite ao professor (ou a qualquer pessoa) verificar a corretude da implementação visualmente, sem precisar instalar `pytest` ou ler código.

#### Grafo clássico de Dijkstra (direcionado, ponderado, 5 vértices)

| Origem | Destino | Peso |
|:---:|:---:|:---:|
| s | t | 10 |
| s | y | 5 |
| t | x | 1 |
| t | y | 2 |
| x | z | 4 |
| y | t | 3 |
| y | x | 9 |
| y | z | 2 |
| z | s | 7 |
| z | x | 6 |

**Resultado esperado (Dijkstra a partir de `s`):** `s=0, t=8, x=9, y=5, z=7`

#### Grafo clássico de MST (não-direcionado, ponderado, 9 vértices)

| Origem | Destino | Peso |
|:---:|:---:|:---:|
| a | b | 4 |
| a | h | 8 |
| b | c | 8 |
| b | h | 11 |
| c | d | 7 |
| c | f | 4 |
| c | i | 2 |
| d | e | 9 |
| d | f | 14 |
| e | f | 10 |
| f | g | 2 |
| g | h | 1 |
| g | i | 6 |
| h | i | 7 |

**Resultado esperado (Kruskal):** custo total **37** (um conjunto possível de arestas da MST: `g-h(1), c-i(2), f-g(2), a-b(4), c-f(4), c-d(7), a-h(8), d-e(9)` — pode variar em caso de empate de peso, mas o custo total mínimo é sempre 37).

Ambos os grafos são definidos uma única vez em `backend/grafos_classicos.py`, e tanto os testes automatizados quanto os botões da interface importam dessa mesma fonte — não há risco de a documentação, os testes e o que roda na tela divergirem entre si.

## Estrutura do repositório

```
backend/
  app.py                    # servidor Flask + rotas da API
  graph.py                   # estrutura de dados (lista de adjacência)
  algorithms.py               # DFS, BFS, Dijkstra, Kruskal
  grafos_classicos.py          # grafos clássicos (usados nos testes E nos botões da interface)
  test_graph.py                # testes da estrutura de dados
  test_algorithms.py           # testes dos algoritmos no grafo do enunciado
  test_grafos_classicos.py     # testes em grafos clássicos (CLRS)
  test_helpers.py               # verificações de propriedade reutilizáveis
  requirements.txt
  requirements-dev.txt         # + pytest, para rodar os testes
frontend/
  templates/index.html
  static/style.css
  static/script.js
enunciado.md            # enunciado original da atividade
```
