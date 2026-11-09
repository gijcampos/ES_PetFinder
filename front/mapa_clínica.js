"use strict";

const RAIO_METROS = 3000;                            
const CENTRO_PADRAO = { lat: -25.4284, lng: -49.2733 }; 
const FAVORITAS = [];                                
const CAMPOS = ["id", "displayName", "formattedAddress", "location",
                "regularOpeningHours", "utcOffsetMinutes", "businessStatus", "googleMapsURI"];

const PIN_SVG = '<svg viewBox="0 0 40 52" aria-hidden="true"><path d="M20 2C10 2 3 9.5 3 19c0 12 17 29 17 29s17-17 17-29C37 9.5 30 2 20 2z" fill="#d58386" stroke="#033960" stroke-width="3"/><circle cx="20" cy="19" r="8" fill="#fff"/></svg>';

const $lista = document.getElementById("lista");
const $form = document.getElementById("busca");
const $texto = document.getElementById("texto-busca");

let mapa, Place, AdvancedMarkerElement, PinElement;
let posicao = CENTRO_PADRAO;
let lugares = [];
let marcadores = [];

window.gm_authFailure = () =>
  aviso("Não foi possível carregar o mapa. Verifique a chave da API e as permissões no Google Cloud.");

window.iniciarMapa = async () => {
  try {
    const { Map: MapaGoogle } = await google.maps.importLibrary("maps");
    ({ Place } = await google.maps.importLibrary("places"));
    ({ AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker"));

    posicao = await obterPosicao();
    mapa = new MapaGoogle(document.getElementById("mapa"), {
      center: posicao,
      zoom: 15,
      mapId: "DEMO_MAP_ID", 
      disableDefaultUI: true,
      zoomControl: true,
    });
    marcarVoce();
    await carregar("");
  } catch (erro) {
    console.error(erro);
    aviso("Não foi possível carregar as clínicas. Tente novamente.");
  }
};

$form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!mapa) return;
  try { await carregar($texto.value.trim()); }
  catch (erro) { console.error(erro); aviso("Não foi possível buscar agora. Tente novamente."); }
});

function obterPosicao() {
  return new Promise((ok) => {
    if (!navigator.geolocation) return ok(CENTRO_PADRAO);
    navigator.geolocation.getCurrentPosition(
      (p) => ok({ lat: p.coords.latitude, lng: p.coords.longitude }),
      () => ok(CENTRO_PADRAO),
      { timeout: 8000 }
    );
  });
}

function marcarVoce() {
  const bolinha = document.createElement("div");
  bolinha.style.cssText = "width:16px;height:16px;border-radius:50%;background:#1a73e8;border:3px solid #fff;box-shadow:0 0 0 2px rgba(26,115,232,.35)";
  new AdvancedMarkerElement({ map: mapa, position: posicao, content: bolinha, title: "Você está aqui" });
}

async function carregar(texto) {
  aviso("Buscando clínicas...");
  const { places } = texto
    ? await Place.searchByText({
        textQuery: `${texto} clínica veterinária`,
        fields: CAMPOS,
        includedType: "veterinary_care",
        locationBias: { center: posicao, radius: 10000 },
        maxResultCount: 10,
      })
    : await Place.searchNearby({
        fields: CAMPOS,
        locationRestriction: { center: posicao, radius: RAIO_METROS },
        includedPrimaryTypes: ["veterinary_care"],
        maxResultCount: 10,
        rankPreference: "DISTANCE",
      });

  lugares = places;
  marcadores.forEach((m) => (m.map = null));
  marcadores = [];

  if (!lugares.length) return aviso("Nenhuma clínica veterinária encontrada.");

  const abertos = await Promise.all(lugares.map((p) => p.isOpen().catch(() => undefined)));
  const limites = new google.maps.LatLngBounds();
  const itens = [];

  lugares.forEach((p, i) => {
    const pin = new PinElement({ glyph: String(i + 1), glyphColor: "#033960", background: "#d58386", borderColor: "#033960" });
    const marcador = new AdvancedMarkerElement({
      map: mapa, position: p.location, content: pin.element ?? pin, title: p.displayName,
    });
    marcador.addEventListener("gmp-click", () => selecionar(i, true));
    marcadores.push(marcador);
    limites.extend(p.location);
    itens.push(criarItem(p, i, abertos[i]));
  });

  $lista.replaceChildren(...itens);
  $lista.scrollTop = 0;

  if (lugares.length === 1) { mapa.setCenter(lugares[0].location); mapa.setZoom(16); }
  else { limites.extend(posicao); mapa.fitBounds(limites, 40); }
}

function criarItem(p, i, aberto) {
  const li = el("li", "clinica");
  li.tabIndex = 0;

  const topo = el("div", "topo");
  topo.insertAdjacentHTML("beforeend", PIN_SVG);
  const nome = el("h2", "nome", p.displayName || "Clínica sem nome");
  if (FAVORITAS.includes(p.id)) {
    const estrela = el("span", "estrela", "★");
    estrela.setAttribute("aria-label", "Clínica favorita");
    nome.append(" ", estrela);
  }
  topo.append(nome);

  const m = distanciaMetros(posicao, { lat: p.location.lat(), lng: p.location.lng() });
  li.append(
    topo,
    el("p", "endereco", p.formattedAddress || "Endereço não informado"),
    el("p", "distancia", textoDistancia(m))
  );

  if (p.googleMapsURI && p.googleMapsURI.startsWith("https://")) {
    const link = el("a", "maps", "Ver no Google Maps");
    link.href = p.googleMapsURI;
    link.target = "_blank";
    link.rel = "noopener";
    link.addEventListener("click", (e) => e.stopPropagation());
    li.append(link);
  }

  const [classe, texto] =
    aberto === true ? ["aberta", "ABERTA"] :
    aberto === false ? ["fechada", "FECHADA"] : ["sem-info", "HORÁRIO NÃO INFORMADO"];
  li.append(el("span", "status " + classe, texto));

  li.addEventListener("click", () => selecionar(i, false));
  li.addEventListener("keydown", (e) => { if (e.key === "Enter") selecionar(i, false); });
  return li;
}

function selecionar(i, rolar) {
  [...$lista.children].forEach((li, j) => li.classList.toggle("ativa", i === j));
  mapa.panTo(lugares[i].location);
  if (rolar) $lista.children[i].scrollIntoView({ block: "nearest", behavior: "smooth" });
}


function distanciaMetros(a, b) {
  const rad = (g) => (g * Math.PI) / 180;
  const h = Math.sin(rad(b.lat - a.lat) / 2) ** 2 +
            Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(rad(b.lng - a.lng) / 2) ** 2;
  return 6371000 * 2 * Math.asin(Math.sqrt(h));
}

function textoDistancia(m) {
  const arredondado = m < 1000 ? Math.max(50, Math.round(m / 50) * 50) : Math.round(m / 100) * 100;
  return `Cerca de ${arredondado.toLocaleString("pt-BR")}m de distância`;
}

function aviso(mensagem) { $lista.replaceChildren(el("li", "aviso", mensagem)); }

function el(tag, classe, texto) {
  const e = document.createElement(tag);
  if (classe) e.className = classe;
  if (texto) e.textContent = texto;
  return e;
}