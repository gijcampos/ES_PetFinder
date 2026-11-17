"use strict";

const CLINICAS = [
  { numero: 1, nome: "Clínica Veterinária São Francisco", endereco: "Rua das safiras, 156 - 58462-020",
    metros: 200, aberto: true, favorita: true, x: 29.5, y: 74.2 },
  { numero: 2, nome: "Clínica Veterinária Happy Pet", endereco: "Rua Francisco de Abreu, 1798 - 58752-100",
    metros: 800, aberto: false, favorita: false, x: 20.3, y: 37.3 },
  { numero: 3, nome: "Clínica Veterinária Campo Pets", endereco: "Av Joaquim Avundano, 336 - 54590-068",
    metros: 1500, aberto: true, favorita: false, x: 79.6, y: 72.3 },
  { numero: 4, nome: "Clínica Veterinária Pet 24h", endereco: "Av das Rosas, 4256 - 57596-326",
    metros: 450, aberto: true, favorita: false, x: 33.8, y: 86.4 },
  { numero: 5, nome: "Clínica Veterinária Vida Animal", endereco: "Rua das Acácias, 920 - 57210-340",
    metros: 1100, aberto: true, favorita: false, x: 20.8, y: 13.4 },
];

const $palco = document.getElementById("palco");
const $lista = document.getElementById("lista");
const $form = document.getElementById("busca");
const $texto = document.getElementById("texto-busca");

let selecionada = null;

desenhar("");

$texto.addEventListener("input", () => desenhar($texto.value));
$form.addEventListener("submit", (e) => { e.preventDefault(); desenhar($texto.value); });

function desenhar(texto) {
  const palavras = normalizar(texto.trim()).split(/\s+/).filter(Boolean);
  const visiveis = CLINICAS.filter((c) => {
    const nome = normalizar(c.nome);
    return palavras.every((p) => nome.includes(p));
  });

  $palco.querySelectorAll(".pino").forEach((p) => p.remove());
  if (!visiveis.some((c) => c.numero === selecionada)) selecionada = null;

  if (!visiveis.length) {
    $lista.replaceChildren(el("li", "aviso", "Nenhuma clínica encontrada com esse nome."));
    return;
  }

  $lista.replaceChildren(...visiveis.map(criarItem));
  visiveis.forEach((c) => $palco.append(criarPino(c)));
  marcarSelecao();
}

function criarPino(c) {
  const b = el("button", "pino");
  b.type = "button";
  b.dataset.numero = c.numero;
  b.style.left = c.x + "%";
  b.style.top = c.y + "%";
  b.setAttribute("aria-label", `${c.numero}. ${c.nome}`);
  b.title = c.nome;
  b.innerHTML = svgPino(c.numero);
  b.addEventListener("click", () => selecionar(c.numero, true));
  return b;
}

function criarItem(c) {
  const li = el("li", "clinica");
  li.tabIndex = 0;
  li.dataset.numero = c.numero;

  const topo = el("div", "topo");
  topo.insertAdjacentHTML("beforeend", svgPino(""));
  const nome = el("h2", "nome", c.nome);
  if (c.favorita) {
    const estrela = el("span", "estrela", "★");
    estrela.setAttribute("aria-label", "Clínica favorita");
    nome.append(" ", estrela);
  }
  topo.append(nome);

  const aberta = c.aberto;
  li.append(
    topo,
    el("p", "endereco", c.endereco),
    el("p", "distancia", textoDistancia(c.metros)),
    el("span", "status " + (aberta ? "aberta" : "fechada"), aberta ? "ABERTA" : "FECHADA")
  );

  li.addEventListener("click", () => selecionar(c.numero, false));
  li.addEventListener("keydown", (e) => { if (e.key === "Enter") selecionar(c.numero, false); });
  return li;
}

function selecionar(numero, rolar) {
  selecionada = selecionada === numero && !rolar ? null : numero;
  marcarSelecao();
  if (rolar && selecionada) {
    const li = $lista.querySelector(`.clinica[data-numero="${selecionada}"]`);
    if (li) li.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }
}

function marcarSelecao() {
  document.querySelectorAll(".clinica, .pino").forEach((e) =>
    e.classList.toggle("ativa", Number(e.dataset.numero) === selecionada));
}

function svgPino(numero) {
  const texto = numero === "" ? "" :
    `<text x="20" y="23.5" text-anchor="middle" font-size="12" font-weight="700" font-family="Montserrat, Arial, sans-serif" fill="#033960">${numero}</text>`;
  return `<svg viewBox="0 0 40 52" aria-hidden="true"><path d="M20 2C10 2 3 9.5 3 19c0 12 17 29 17 29s17-17 17-29C37 9.5 30 2 20 2z" fill="#d58386" stroke="#033960" stroke-width="3"/><circle cx="20" cy="19" r="9" fill="#fff"/>${texto}</svg>`;
}

function textoDistancia(m) {
  return `Cerca de ${m.toLocaleString("pt-BR")}m de distância`;
}

function normalizar(t) {
  return t.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
}

function el(tag, classe, texto) {
  const e = document.createElement(tag);
  if (classe) e.className = classe;
  if (texto) e.textContent = texto;
  return e;
}