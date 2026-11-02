const SVG_NS = "http://www.w3.org/2000/svg";

const COMPLEXITY = {
  dfs: "DFS — O(V + E): com lista de adjacência, cada vértice é empilhado/visitado uma vez e cada aresta é examinada uma vez.",
  bfs: "BFS — O(V + E): mesma razão do DFS, trocando a pilha por uma fila (ordem de visita por 'camadas').",
  dijkstra: "Dijkstra — O((V + E) log V): fila de prioridade (heap binário); cada vértice é extraído uma vez O(log V) e cada aresta pode gerar uma atualização no heap. Exige pesos não-negativos.",
  kruskal: "Kruskal — O(E log E): dominado pela ordenação das arestas; as uniões via Union-Find (path compression + union by rank) custam quase O(1) cada.",
};

let currentGraphData = { directed: false, weighted: true, adjacency: {} };
let pendingEdges = [];
let positions = {};
let nodeEls = {};
let edgeEls = {};
let bestEdge = {};

let currentAlgoType = null;
let currentResult = null;
let currentTrace = [];
let stepIdx = 0;
let playing = false;
let timer = null;

document.addEventListener("DOMContentLoaded", () => {
  bindUI();
  fetchGrafo();
});

function bindUI() {
  document.getElementById("form-edge").addEventListener("submit", onAddEdge);
  document.getElementById("chk-weighted").addEventListener("change", (e) => {
    document.getElementById("input-peso").disabled = !e.target.checked;
  });
  document.getElementById("btn-aplicar-grafo").addEventListener("click", aplicarGrafo);
  document.getElementById("btn-grafo-teste").addEventListener("click", carregarGrafoTeste);
  document.getElementById("btn-limpar-grafo").addEventListener("click", limparGrafo);

  document.querySelectorAll(".btn-algo").forEach((btn) => {
    btn.addEventListener("click", () => runAlgorithm(btn.dataset.algo, btn));
  });

  document.getElementById("btn-play").addEventListener("click", togglePlay);
  document.getElementById("btn-step").addEventListener("click", () => {
    stopTimer();
    stepForward();
  });
  document.getElementById("btn-reset").addEventListener("click", resetPlayback);
  document.getElementById("range-speed").addEventListener("input", () => {
    if (playing) {
      stopTimer();
      timer = setInterval(stepForward, getDelay());
    }
  });

  document.getElementById("btn-finalizar").addEventListener("click", finalizarAplicacao);
}

// ---------- Entrada de dados (formulário de arestas) ----------

function onAddEdge(e) {
  e.preventDefault();
  const origem = document.getElementById("input-origem").value.trim();
  const destino = document.getElementById("input-destino").value.trim();
  const weighted = document.getElementById("chk-weighted").checked;
  const pesoInput = document.getElementById("input-peso").value;
  const peso = weighted ? (parseFloat(pesoInput) || 1) : 1;

  if (!origem || !destino) return;

  pendingEdges.push({ origem, destino, peso });
  renderEdgeTable();

  document.getElementById("input-origem").value = "";
  document.getElementById("input-destino").value = "";
  document.getElementById("input-peso").value = "1";
  document.getElementById("input-origem").focus();
}

function renderEdgeTable() {
  const weighted = document.getElementById("chk-weighted").checked;
  const tbody = document.getElementById("edge-list");
  tbody.innerHTML = "";
  pendingEdges.forEach((aresta, idx) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeHtml(aresta.origem)}</td>
      <td>${escapeHtml(aresta.destino)}</td>
      <td>${weighted ? aresta.peso : "-"}</td>
      <td><button type="button" data-idx="${idx}" title="Remover">✕</button></td>
    `;
    tbody.appendChild(tr);
  });
  tbody.querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", () => {
      pendingEdges.splice(Number(btn.dataset.idx), 1);
      renderEdgeTable();
    });
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------- Chamadas à API ----------

async function fetchGrafo() {
  const resp = await fetch("/api/grafo");
  const data = await resp.json();
  renderAll(data);
}

async function aplicarGrafo() {
  const body = {
    directed: document.getElementById("chk-directed").checked,
    weighted: document.getElementById("chk-weighted").checked,
    edges: pendingEdges,
  };
  const resp = await fetch("/api/grafo", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await resp.json();
  renderAll(data);
}

async function carregarGrafoTeste() {
  const resp = await fetch("/api/grafo-teste", { method: "POST" });
  const data = await resp.json();

  document.getElementById("chk-directed").checked = data.directed;
  document.getElementById("chk-weighted").checked = data.weighted;
  document.getElementById("input-peso").disabled = !data.weighted;
  pendingEdges = edgesFromAdjacency(data);
  renderEdgeTable();

  renderAll(data);
}

async function limparGrafo() {
  const resp = await fetch("/api/grafo", { method: "DELETE" });
  const data = await resp.json();
  pendingEdges = [];
  renderEdgeTable();
  renderAll(data);
}

async function runAlgorithm(tipo, btnEl) {
  const vertices = Object.keys(currentGraphData.adjacency || {});
  if (vertices.length === 0) {
    alert("Carregue um grafo primeiro.");
    return;
  }

  let body = {};
  if (tipo !== "kruskal") {
    const origem = document.getElementById("select-origem").value;
    if (!origem) {
      alert("Selecione um vértice de origem.");
      return;
    }
    body = { origem };
  }

  const resp = await fetch(`/api/algoritmo/${tipo}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await resp.json();
  if (!resp.ok) {
    alert(data.erro || "Erro ao executar o algoritmo.");
    return;
  }

  document.querySelectorAll(".btn-algo").forEach((b) => b.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");

  startPlayback(tipo, data);
}

// ---------- Renderização geral ----------

function renderAll(data) {
  currentGraphData = data;
  renderAdjacencyView(data);
  renderGraphSvg(data);
  populateOriginSelect(data);
  stopTimer();
  currentTrace = [];
  currentResult = null;
  document.getElementById("playback-controls").hidden = true;
  document.getElementById("complexity-box").hidden = true;
  document.getElementById("step-log").innerHTML = "";
  document.getElementById("final-result").hidden = true;
  document.getElementById("final-result").innerHTML = "";
  document.querySelectorAll(".btn-algo").forEach((b) => b.classList.remove("active"));
}

function renderAdjacencyView(data) {
  const el = document.getElementById("adjacency-view");
  const vertices = Object.keys(data.adjacency);
  if (vertices.length === 0) {
    el.textContent = "(grafo vazio)";
    return;
  }
  const linhas = vertices.map((v) => {
    const vizinhos = data.adjacency[v]
      .map((x) => (data.weighted ? `${x.vizinho}(${x.peso})` : x.vizinho))
      .join(", ");
    return `${v}: ${vizinhos}`;
  });
  el.textContent = linhas.join("\n");
}

function populateOriginSelect(data) {
  const select = document.getElementById("select-origem");
  select.innerHTML = "";
  Object.keys(data.adjacency).forEach((v) => {
    const opt = document.createElement("option");
    opt.value = v;
    opt.textContent = v;
    select.appendChild(opt);
  });
}

function edgesFromAdjacency(data) {
  const edges = [];
  const seen = new Set();
  Object.entries(data.adjacency).forEach(([origem, vizinhos]) => {
    vizinhos.forEach(({ vizinho, peso }) => {
      if (data.directed) {
        edges.push({ origem, destino: vizinho, peso });
      } else {
        const key = [origem, vizinho].sort().join("|") + "|" + peso;
        if (!seen.has(key)) {
          seen.add(key);
          edges.push({ origem, destino: vizinho, peso });
        }
      }
    });
  });
  return edges;
}

function edgeKey(origem, destino, directed) {
  return directed ? `${origem}=>${destino}` : [origem, destino].sort().join("--");
}

// ---------- Visualização SVG ----------

function computeLayout(vertices) {
  const n = vertices.length;
  const cx = 300, cy = 300;
  const r = n <= 1 ? 0 : Math.min(240, 90 + n * 12);
  const pos = {};
  vertices.forEach((v, i) => {
    const angle = (2 * Math.PI * i) / n - Math.PI / 2;
    pos[v] = { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  });
  return pos;
}

function renderGraphSvg(data) {
  const svg = document.getElementById("graph-svg");
  svg.innerHTML = "";
  nodeEls = {};
  edgeEls = {};

  const vertices = Object.keys(data.adjacency);
  if (vertices.length === 0) return;

  positions = computeLayout(vertices);

  if (data.directed) {
    const defs = document.createElementNS(SVG_NS, "defs");
    defs.innerHTML = `<marker id="arrow" viewBox="0 0 10 10" refX="28" refY="5"
        markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M0,0 L10,5 L0,10 z" fill="#64748b"></path></marker>`;
    svg.appendChild(defs);
  }

  const edgesLayer = document.createElementNS(SVG_NS, "g");
  svg.appendChild(edgesLayer);

  const edges = edgesFromAdjacency(data);
  edges.forEach(({ origem, destino, peso }) => {
    const p1 = positions[origem], p2 = positions[destino];
    if (!p1 || !p2) return;
    const key = edgeKey(origem, destino, data.directed);

    const line = document.createElementNS(SVG_NS, "line");
    line.setAttribute("x1", p1.x);
    line.setAttribute("y1", p1.y);
    line.setAttribute("x2", p2.x);
    line.setAttribute("y2", p2.y);
    line.setAttribute("class", "edge");
    if (data.directed) line.setAttribute("marker-end", "url(#arrow)");
    edgesLayer.appendChild(line);
    edgeEls[key] = line;

    if (data.weighted) {
      const mx = (p1.x + p2.x) / 2, my = (p1.y + p2.y) / 2;
      const label = document.createElementNS(SVG_NS, "text");
      label.setAttribute("x", mx);
      label.setAttribute("y", my);
      label.setAttribute("class", "edge-label");
      label.textContent = peso;
      edgesLayer.appendChild(label);
    }
  });

  const nodesLayer = document.createElementNS(SVG_NS, "g");
  svg.appendChild(nodesLayer);

  vertices.forEach((v) => {
    const p = positions[v];
    const g = document.createElementNS(SVG_NS, "g");
    g.setAttribute("class", "node");
    g.setAttribute("transform", `translate(${p.x},${p.y})`);

    const circle = document.createElementNS(SVG_NS, "circle");
    circle.setAttribute("r", 22);
    g.appendChild(circle);

    const text = document.createElementNS(SVG_NS, "text");
    text.textContent = v;
    g.appendChild(text);

    nodesLayer.appendChild(g);
    nodeEls[v] = g;
  });
}

// ---------- Animação / playback do trace ----------

function getDelay() {
  const v = Number(document.getElementById("range-speed").value);
  return 1050 - v * 95;
}

function clearHighlights() {
  Object.values(nodeEls).forEach((n) => n.classList.remove("current", "visited", "queued"));
  Object.values(edgeEls).forEach((e) => e.classList.remove("tree", "exploring", "reject"));
  bestEdge = {};
}

function setCurrent(v) {
  Object.values(nodeEls).forEach((n) => n.classList.remove("current"));
  nodeEls[v]?.classList.add("current");
}
function markVisited(v) {
  nodeEls[v]?.classList.remove("queued");
  nodeEls[v]?.classList.add("visited");
}
function markQueued(v) {
  if (!nodeEls[v]?.classList.contains("visited")) nodeEls[v]?.classList.add("queued");
}
function markEdge(origem, destino, cls) {
  const key = edgeKey(origem, destino, currentGraphData.directed);
  edgeEls[key]?.classList.add(cls);
}

function addLog(text) {
  const ol = document.getElementById("step-log");
  const li = document.createElement("li");
  li.textContent = text;
  ol.appendChild(li);
  ol.scrollTop = ol.scrollHeight;
}

function fmtDist(d) {
  return d === null || d === undefined ? "∞" : d;
}

function applyStep(tipo, step) {
  if (tipo === "dfs") {
    if (step.tipo === "visita_vertice") {
      setCurrent(step.vertice);
      markVisited(step.vertice);
      if (step.pai) markEdge(step.pai, step.vertice, "tree");
      addLog(`Visita ${step.vertice}` + (step.pai ? ` (chegando de ${step.pai})` : " (início)"));
    }
  } else if (tipo === "bfs") {
    if (step.tipo === "enfileira_vertice") {
      markQueued(step.vertice);
      if (step.pai) markEdge(step.pai, step.vertice, "tree");
      addLog(
        step.pai
          ? `Enfileira ${step.vertice} (distância em saltos: ${step.distancia}, via ${step.pai})`
          : `Enfileira ${step.vertice} (início, distância 0)`
      );
    } else if (step.tipo === "processa_vertice") {
      setCurrent(step.vertice);
      markVisited(step.vertice);
      addLog(`Remove ${step.vertice} da fila e processa seus vizinhos`);
    }
  } else if (tipo === "dijkstra") {
    if (step.tipo === "finaliza_vertice") {
      setCurrent(step.vertice);
      markVisited(step.vertice);
      addLog(`Finaliza ${step.vertice} com distância ${step.distancia}`);
    } else if (step.tipo === "explora_aresta") {
      markEdge(step.origem, step.destino, "exploring");
      addLog(
        `Explora ${step.origem}→${step.destino} (peso ${step.peso}): ${fmtDist(step.distancia_atual)} vs candidata ${step.nova_distancia}`
      );
    } else if (step.tipo === "relaxa_aresta") {
      const key = edgeKey(step.origem, step.destino, currentGraphData.directed);
      if (bestEdge[step.destino] && bestEdge[step.destino] !== key) {
        edgeEls[bestEdge[step.destino]]?.classList.remove("tree");
      }
      edgeEls[key]?.classList.remove("exploring");
      edgeEls[key]?.classList.add("tree");
      bestEdge[step.destino] = key;
      addLog(`Relaxa: menor distância para ${step.destino} agora é ${step.nova_distancia} (via ${step.origem})`);
    }
  } else if (tipo === "kruskal") {
    if (step.tipo === "aceita_aresta") {
      markEdge(step.origem, step.destino, "tree");
      markVisited(step.origem);
      markVisited(step.destino);
      addLog(`Aceita ${step.origem}-${step.destino} (peso ${step.peso}) — custo acumulado: ${step.custo_acumulado}`);
    } else if (step.tipo === "rejeita_aresta") {
      markEdge(step.origem, step.destino, "reject");
      addLog(`Rejeita ${step.origem}-${step.destino} (formaria ciclo)`);
    }
  }
}

function startPlayback(tipo, result) {
  stopTimer();
  clearHighlights();
  currentAlgoType = tipo;
  currentResult = result;
  currentTrace = result.trace || [];
  stepIdx = 0;

  document.getElementById("step-log").innerHTML = "";
  document.getElementById("final-result").hidden = true;
  document.getElementById("final-result").innerHTML = "";
  document.getElementById("playback-controls").hidden = false;
  document.getElementById("complexity-box").hidden = false;
  document.getElementById("complexity-box").textContent = COMPLEXITY[tipo];
  updateStepCounter();

  playing = true;
  document.getElementById("btn-play").textContent = "⏸ Pausar";
  timer = setInterval(stepForward, getDelay());
}

function stepForward() {
  if (stepIdx >= currentTrace.length) {
    finishPlayback();
    return;
  }
  applyStep(currentAlgoType, currentTrace[stepIdx]);
  stepIdx++;
  updateStepCounter();
  if (stepIdx >= currentTrace.length) finishPlayback();
}

function finishPlayback() {
  stopTimer();
  playing = false;
  document.getElementById("btn-play").textContent = "▶ Play";
  renderFinalResult(currentAlgoType, currentResult);
}

function togglePlay() {
  if (stepIdx >= currentTrace.length) return;
  playing = !playing;
  if (playing) {
    document.getElementById("btn-play").textContent = "⏸ Pausar";
    timer = setInterval(stepForward, getDelay());
  } else {
    document.getElementById("btn-play").textContent = "▶ Play";
    stopTimer();
  }
}

function stopTimer() {
  if (timer) clearInterval(timer);
  timer = null;
}

function resetPlayback() {
  stopTimer();
  playing = false;
  stepIdx = 0;
  clearHighlights();
  document.getElementById("step-log").innerHTML = "";
  document.getElementById("final-result").hidden = true;
  document.getElementById("btn-play").textContent = "▶ Play";
  updateStepCounter();
}

function updateStepCounter() {
  document.getElementById("step-counter").textContent = `${Math.min(stepIdx, currentTrace.length)} / ${currentTrace.length}`;
}

// ---------- Resultado final estruturado ----------

function reconstructPath(pred, origem, destino) {
  if (pred[destino] === undefined) return null;
  const caminho = [];
  let atual = destino;
  while (atual !== null && atual !== undefined) {
    caminho.unshift(atual);
    if (atual === origem) break;
    atual = pred[atual];
  }
  if (caminho[0] !== origem) return null;
  return caminho;
}

function renderFinalResult(tipo, result) {
  const el = document.getElementById("final-result");
  el.hidden = false;

  if (tipo === "dfs") {
    const arvore = result.arvore_dfs.map((a) => `${a.origem} → ${a.destino}`).join("<br>") || "(sem arestas de árvore)";
    el.innerHTML = `
      <strong>Ordem de visita (DFS):</strong> ${result.ordem_visita.join(" → ")}<br><br>
      <strong>Árvore de busca:</strong><br>${arvore}
      ${result.nao_alcancados.length ? `<p class="unreachable">Não alcançados: ${result.nao_alcancados.join(", ")} (grafo desconexo)</p>` : ""}
    `;
  } else if (tipo === "bfs") {
    el.innerHTML = `
      <strong>Fila de execução (ordem de processamento):</strong> ${result.ordem_visita.join(" → ")}<br><br>
      <table>
        <thead><tr><th>Vértice</th><th>Distância (saltos)</th></tr></thead>
        <tbody>
          ${result.ordem_visita.map((v) => `<tr><td>${v}</td><td>${result.distancias_em_saltos[v]}</td></tr>`).join("")}
        </tbody>
      </table>
      ${result.nao_alcancados.length ? `<p class="unreachable">Não alcançados: ${result.nao_alcancados.join(", ")}</p>` : ""}
    `;
  } else if (tipo === "dijkstra") {
    const vertices = Object.keys(result.distancias);
    el.innerHTML = `
      <table>
        <thead><tr><th>Vértice</th><th>Distância</th><th>Caminho</th></tr></thead>
        <tbody>
          ${vertices
            .map((v) => {
              const d = result.distancias[v];
              if (d === null) return `<tr><td>${v}</td><td class="unreachable">∞</td><td class="unreachable">inalcançável</td></tr>`;
              const caminho = reconstructPath(result.predecessores, result.origem, v);
              return `<tr><td>${v}</td><td>${d}</td><td>${caminho ? caminho.join(" → ") : "-"}</td></tr>`;
            })
            .join("")}
        </tbody>
      </table>
    `;
  } else if (tipo === "kruskal") {
    el.innerHTML = `
      <table>
        <thead><tr><th>Origem</th><th>Destino</th><th>Peso</th></tr></thead>
        <tbody>
          ${result.arestas_mst.map((a) => `<tr><td>${a.origem}</td><td>${a.destino}</td><td>${a.peso}</td></tr>`).join("")}
          <tr class="total-row"><td colspan="2">Custo total</td><td>${result.custo_total}</td></tr>
        </tbody>
      </table>
    `;
  }
}

// ---------- Finalizar aplicação ----------

function finalizarAplicacao() {
  if (!confirm("Finalizar a aplicação? Isso encerra o loop interativo.")) return;
  stopTimer();
  document.getElementById("overlay-fim").hidden = false;
}
