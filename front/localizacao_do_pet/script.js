(function () {
  const $ = id => document.getElementById(id);

  // Troque MOCK para false quando o back estiver pronto.
  const CONFIG = {
    MOCK: true,
    API: '/api',
    INTERVALO_MS: 5000,        // atualização automática (poucos segundos)
    OFFLINE_APOS_S: 30,        // sem sinal há mais que isso = offline (se o back não mandar ao_vivo)
    URL_HISTORICO: 'historico.html',   // recebe ?pet=<id>
    URL_PETS: 'pets.html',
    URL_ENDERECO: 'endereco.html'
  };

  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const pad = n => String(n).padStart(2, '0');
  const inicial = n => (String(n || '?').trim().charAt(0) || '?').toUpperCase();
  const fmtDataHora = t => { const d = new Date(t); return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} às ${pad(d.getHours())}:${pad(d.getMinutes())}`; };
  function fmtIdade(t){
    const s = Math.max(0, Math.round((Date.now() - t) / 1000));
    return s < 60 ? `há ${s} seg` : s < 3600 ? `há ${Math.floor(s / 60)} min` : null;
  }
  function distancia(a, b){                                  // haversine, em metros
    const R = 6371000, rad = x => x * Math.PI / 180, dLat = rad(b.lat - a.lat), dLng = rad(b.lng - a.lng);
    const h = Math.sin(dLat/2)**2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLng/2)**2;
    return 2 * R * Math.asin(Math.sqrt(h));
  }

  /* ---------- dados ---------- */
  // Contrato esperado do back:
  //   GET /localizacoes -> {
  //     casa: { lat, lng, endereco } | null,        (endereço cadastrado do tutor)
  //     raio_m: 10,
  //     pets: [{ id, nome, lat, lng, precisao_m?, atualizado_em: "2026-11-23T14:32:10Z", ao_vivo?: true|false }] }
  // Se "ao_vivo" não vier, o front considera offline quem não atualiza há mais de OFFLINE_APOS_S segundos.
  const CASA = {lat: -24.0456, lng: -52.3838, endereco: 'Rua Guarapuava, Nº 0000 - Centro, Campo Mourão - PR'};
  const off = (dx, dy) => ({lat: CASA.lat + dy / 111320, lng: CASA.lng + dx / (111320 * Math.cos(CASA.lat * Math.PI / 180))});
  const andarilhos = {1: {x: 6, y: -3, passo: 3.2}, 2: {x: 3, y: 2, passo: 1.2}};
  const t0 = Date.now();

  function mockLocalizacoes(){
    const agora = Date.now();
    Object.values(andarilhos).forEach(w => {
      w.x += (Math.random() - .5) * w.passo; w.y += (Math.random() - .5) * w.passo;
      const d = Math.hypot(w.x, w.y); if(d > 16){ w.x *= 15 / d; w.y *= 15 / d; }
    });
    const vivo = (id, nome, w) => ({id, nome, ...off(w.x, w.y), precisao_m: 3, atualizado_em: new Date(agora - (1 + Math.floor(Math.random() * 4)) * 1000).toISOString()});
    return {casa: CASA, raio_m: 10, pets: [
      vivo(1, 'Scooby Doo', andarilhos[1]),
      vivo(2, 'Luna', andarilhos[2]),
      {id: 3, nome: 'Mel', ...off(-4, 3), precisao_m: 5, atualizado_em: new Date(t0 - (3 * 3600 + 12 * 60) * 1000).toISOString()}   // offline
    ]};
  }

  async function obter(){
    if(CONFIG.MOCK){ await new Promise(r => setTimeout(r, 250)); return mockLocalizacoes(); }
    const r = await fetch(`${CONFIG.API}/localizacoes`); if(!r.ok) throw new Error(r.status); return r.json();
  }

  function tratar(d){
    const raio = d.raio_m || 10, agora = Date.now();
    const pets = (d.pets || []).map(p => {
      const t = new Date(p.atualizado_em).getTime();
      const aoVivo = typeof p.ao_vivo === 'boolean' ? p.ao_vivo : (agora - t) / 1000 <= CONFIG.OFFLINE_APOS_S;
      const dist = d.casa ? Math.round(distancia(d.casa, p)) : null;
      return {id: p.id, nome: p.nome, lat: p.lat, lng: p.lng, precisao: p.precisao_m || 3, t, aoVivo, dist, fora: dist !== null && dist > raio};
    });
    return {casa: d.casa || null, raio, pets};
  }

  /* ---------- estado ---------- */
  let dados = null, selId = null, carregando = true, erroInicial = false, semConexao = false, ocupado = false;
  const petSel = () => dados && dados.pets.find(p => String(p.id) === String(selId));
  const statusDe = p => !p.aoVivo ? {cls: 'off', txt: 'Offline'} : p.fora ? {cls: 'fora', txt: 'Fora do raio'} : {cls: 'vivo', txt: 'Ao vivo'};

  /* ---------- lista de pets ---------- */
  function renderLista(){
    const ul = $('pets');
    if(carregando){ ul.innerHTML = '<li class="msg">Carregando...</li>'; return; }
    if(erroInicial){ ul.innerHTML = '<li class="msg">Não foi possível carregar a localização agora.<br><button type="button" id="tentar">Tentar novamente</button></li>'; return; }
    if(!dados.pets.length){
      ul.innerHTML = `<li class="msg"><strong>Você ainda não cadastrou nenhum pet.</strong><br>Cadastre seu animal de estimação para acompanhar a localização dele em tempo real.<br><a class="btn-sec" href="${esc(CONFIG.URL_PETS)}">Cadastrar pet</a></li>`; return;
    }
    const ae = document.activeElement, foco = ae && ae.dataset ? ae.dataset.id : null;
    ul.innerHTML = dados.pets.map(p => {
      const s = statusDe(p), sel = String(p.id) === String(selId);
      return `<li><button type="button" class="pet-item${sel ? ' sel' : ''}" data-id="${esc(p.id)}" aria-current="${sel}">
        <span class="avatar${p.aoVivo ? '' : ' off'}" aria-hidden="true">${esc(inicial(p.nome))}</span>
        <span class="pet-nome">${esc(p.nome)}</span><span class="badge ${s.cls}">${s.txt}</span></button></li>`;
    }).join('');
    if(foco){ const el = [...ul.querySelectorAll('[data-id]')].find(e => e.dataset.id === foco); if(el) el.focus(); }
  }

  /* ---------- detalhe do pet selecionado ---------- */
  function textoAtualizacao(p){
    if(!p.aoVivo) return `Última localização conhecida: ${fmtDataHora(p.t)}`;
    const i = fmtIdade(p.t); return i ? `Atualizado ${i}` : `Atualizado em ${fmtDataHora(p.t)}`;
  }
  function renderDetalhe(){
    const box = $('detalhe'), p = petSel();
    $('aviso').hidden = !semConexao;
    $('hist').hidden = !p;
    if(!p){ box.innerHTML = ''; return; }
    $('hist').href = `${CONFIG.URL_HISTORICO}?pet=${encodeURIComponent(p.id)}`;
    const s = statusDe(p), c = dados.casa;
    const raioTxt = c ? `${p.aoVivo ? '' : 'Última posição: '}${p.fora ? 'fora' : (p.aoVivo ? 'Dentro' : 'dentro')} do raio de ${dados.raio} m · a ${p.dist} m de casa` : '';
    box.innerHTML = `<h2>${esc(p.nome)}</h2>
      <p class="linha"><span class="badge ${s.cls}">${s.txt}</span><span id="d-atual">${esc(textoAtualizacao(p))}</span></p>
      ${raioTxt ? `<p class="raio-txt${p.fora ? ' fora' : ''}">${esc(raioTxt)}</p>` : ''}
      <div class="sep"></div>
      <p class="rot">Endereço cadastrado</p>
      <p class="end">${c ? esc(c.endereco) : `Nenhum endereço cadastrado. <a href="${esc(CONFIG.URL_ENDERECO)}">Cadastrar endereço</a>`}</p>`;
  }

  /* ---------- mapa simulado: mapa.svg + camada SVG por cima ---------- */
  const VW = 628, VH = 539, KMAX = 4.6, PAD = 50;          // KMAX = px por metro (raio de 10 m ≈ 46 px)
  let mapaChave = '', marc = null;
  const msgMapa = txt => { const m = $('mapa-msg'); m.textContent = txt || ''; m.hidden = !txt; };
  const limparMapa = () => { $('mapa').innerHTML = ''; mapaChave = ''; marc = null; };

  function renderMapa(){
    if(carregando){ limparMapa(); msgMapa('Carregando localização...'); return; }
    if(erroInicial || !dados){ limparMapa(); msgMapa('Não foi possível carregar a localização.'); return; }
    const c = dados.casa;
    if(!c){ limparMapa(); msgMapa('Cadastre seu endereço para ver o raio de ' + dados.raio + ' m e a posição do pet.'); return; }

    const p = petSel(), mLng = 111320 * Math.cos(c.lat * Math.PI / 180);
    const xm = p ? (p.lng - c.lng) * mLng : 0, ym = p ? (p.lat - c.lat) * 111320 : 0;
    const k = Math.round(Math.min(KMAX, (VW/2 - PAD) / Math.max(dados.raio, Math.abs(xm)), (VH/2 - PAD) / Math.max(dados.raio, Math.abs(ym))) * 100) / 100;
    const chave = `${c.lat}|${c.lng}|${dados.raio}|${k}`, cx = VW / 2, cy = VH / 2, r = dados.raio * k;
    let novo = false;
    if(chave !== mapaChave){
      $('mapa').innerHTML = `<svg viewBox="0 0 ${VW} ${VH}" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
        <circle class="raio" cx="${cx}" cy="${cy}" r="${r}"/>
        <text class="raio-rot" x="${cx}" y="${cy + r + 22}" text-anchor="middle">Raio ${esc(dados.raio)} m</text>
        <g class="casa" transform="translate(${cx} ${cy})"><title>${esc(c.endereco || 'Casa')}</title><circle r="11"/><path d="M-5 1L0 -5L5 1V6H-5Z"/></g>
        <g class="marcador"><circle class="halo" r="22"/><circle class="pino" r="17"/><text dy=".36em" text-anchor="middle"></text><title></title></g></svg>`;
      marc = $('mapa').querySelector('.marcador'); mapaChave = chave; novo = true;
    }
    if(!p){ marc.style.display = 'none'; msgMapa('Nenhum pet cadastrado'); return; }
    msgMapa('');
    marc.style.display = '';
    const troca = novo || marc.dataset.pet !== String(p.id);
    marc.dataset.pet = p.id;
    marc.setAttribute('class', 'marcador ' + (!p.aoVivo ? 'off' : p.fora ? 'fora' : 'ok'));
    marc.querySelector('text').textContent = inicial(p.nome);
    marc.querySelector('title').textContent = `${p.nome} · ${p.aoVivo ? 'ao vivo' : 'offline'}`;
    marc.querySelector('.halo').setAttribute('r', Math.max(p.precisao * k, 22));
    const pos = `translate(${cx + xm * k}px, ${cy - ym * k}px)`;
    if(troca){ marc.style.transition = 'none'; marc.style.transform = pos; marc.getBoundingClientRect(); marc.style.transition = ''; }
    else marc.style.transform = pos;                       // desliza suavemente até a nova posição
  }

  const render = () => { renderLista(); renderDetalhe(); renderMapa(); };

  /* ---------- atualização automática ---------- */
  async function atualizar(){
    if(ocupado) return; ocupado = true;
    try{
      dados = tratar(await obter()); semConexao = false; erroInicial = false;
      if(!petSel()) selId = dados.pets.length ? dados.pets[0].id : null;
    }catch(e){ if(dados) semConexao = true; else erroInicial = true; }
    carregando = false; ocupado = false; render();
  }

  $('pets').addEventListener('click', e => {
    if(e.target.closest('#tentar')){ carregando = true; erroInicial = false; render(); atualizar(); return; }
    const b = e.target.closest('.pet-item'); if(b){ selId = b.dataset.id; render(); }
  });
  setInterval(() => { if(!document.hidden) atualizar(); }, CONFIG.INTERVALO_MS);
  document.addEventListener('visibilitychange', () => { if(!document.hidden) atualizar(); });
  setInterval(() => {                                      // "Atualizado há N seg" anda a cada segundo
    const p = petSel(), el = $('d-atual');
    if(p && p.aoVivo && el) el.textContent = textoAtualizacao(p);
  }, 1000);

  render(); atualizar();
})();
