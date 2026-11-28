(function () {
  const $ = id => document.getElementById(id);

  // Troque MOCK para false quando o back estiver pronto.
  const CONFIG = { MOCK: true, API: '/api', DIAS: 30, URL_AMBIENTE: 'ambiente.html' };
  $('voltar').href = CONFIG.URL_AMBIENTE;
  $('nota').textContent = `Histórico guardado por ${CONFIG.DIAS} dias. Registros mais antigos são removidos.`;

  /* ---------- utilidades ---------- */
  const SEM = ['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'];
  const MES = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'];
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const pad = n => String(n).padStart(2, '0');
  const ymd = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const fmtData = d => `${SEM[d.getDay()]}, ${d.getDate()} de ${MES[d.getMonth()]} de ${d.getFullYear()}`;
  const somar = (d, n) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + n);
  const doYmd = s => { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); };

  const hoje = new Date(), MAX = new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate());
  const MIN = somar(MAX, -(CONFIG.DIAS - 1));           // janela de retenção: últimos 30 dias

  function distancia(a, b){                              // haversine, em metros
    const R = 6371000, rad = x => x * Math.PI / 180;
    const dLat = rad(b.lat - a.lat), dLng = rad(b.lng - a.lng);
    const h = Math.sin(dLat/2)**2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLng/2)**2;
    return 2 * R * Math.asin(Math.sqrt(h));
  }

  /* ---------- dados ---------- */
  // Contrato esperado do back:
  //   GET /pets                                   -> [{ id, nome }]
  //   GET /pets/<id>/historico?data=AAAA-MM-DD    -> {
  //        casa: { lat, lng, endereco },
  //        raio_m: 10,
  //        registros: [{ hora:"07:30", lat, lng, local:"Rua X, 45", titulo?:"Em casa" }] }
  // O front calcula distância, saída/retorno do raio e ordena por horário.
  const CASA = {lat: -24.0456, lng: -52.3838, endereco: 'Rua Guarapuava, Nº 0000'};
  const off = (dx, dy) => ({lat: CASA.lat + dy / 111320, lng: CASA.lng + dx / (111320 * Math.cos(CASA.lat * Math.PI / 180))});
  const reg = (hora, dx, dy, local, titulo) => ({hora, ...off(dx, dy), local, titulo});
  const PETS_MOCK = [{id: 1, nome: 'Scooby Doo'}, {id: 2, nome: 'Mel'}];

  function mockHistorico(petId, d){
    const dia = d.getDate(), casa = 'Rua Guarapuava, Nº 0000';
    let registros = [];
    if(petId == 1 && dia % 5 !== 0){
      registros = dia % 2
        ? [reg('07:30',0,0,casa,'Em casa'), reg('09:45',110,-90,'Rua Exemplo, 45'), reg('10:50',45,25,casa,'Voltou ao raio seguro'), reg('12:00',-55,-40,'Exemplo Praça','Passeio na praça')]
        : [reg('07:30',0,0,casa,'Em casa'), reg('10:00',15,10,'Quintal','Brincando no quintal'), reg('15:30',50,-20,'Exemplo Praça','Passeio na praça'), reg('19:00',0,0,casa,'Em casa')];
    } else if(petId == 2 && dia % 3 === 0){
      registros = [reg('08:00',0,0,casa,'Em casa'), reg('18:00',5,3,casa,'Em casa')];
    }
    return {casa: CASA, raio_m: 100, registros};   // 100 m só para o mapa de teste ficar legível
  }

  async function obterPets(){
    if(CONFIG.MOCK) return PETS_MOCK;
    const r = await fetch(`${CONFIG.API}/pets`); if(!r.ok) throw new Error(r.status); return r.json();
  }
  async function obterHistorico(petId, d){
    if(CONFIG.MOCK){ await new Promise(r => setTimeout(r, 300)); return mockHistorico(petId, d); }
    const r = await fetch(`${CONFIG.API}/pets/${encodeURIComponent(petId)}/historico?data=${ymd(d)}`);
    if(!r.ok) throw new Error(r.status);
    return r.json();
  }

  // Ordena, calcula distância e marca saída/retorno do raio
  function montar(d){
    const raio = d.raio_m || 10;
    let dentroAntes = true, saidas = 0;
    const itens = (d.registros || []).slice().sort((a, b) => a.hora.localeCompare(b.hora)).map(r => {
      const dist = d.casa ? Math.round(distancia(d.casa, r)) : 0, fora = dist > raio;
      const tipo = fora && dentroAntes ? 'saida' : (!fora && !dentroAntes ? 'retorno' : 'normal');
      dentroAntes = !fora; if(tipo === 'saida') saidas++;
      const titulo = r.titulo || (fora ? 'Fora do raio seguro' : tipo === 'retorno' ? 'Voltou ao raio seguro' : 'Dentro do raio seguro');
      const sub = (fora ? `${dist} m de casa` : 'Dentro do raio') + (r.local ? ` | ${r.local}` : '');
      return {hora: r.hora, lat: r.lat, lng: r.lng, dist, fora, tipo, titulo, sub};
    });
    return {casa: d.casa, raio, itens, saidas};
  }

  /* ---------- estado ---------- */
  let pets = [], petId = null, data = MAX, dados = null, carregando = true, erro = false, semPets = false, sel = null, tok = 0;

  /* ---------- mapa simulado: imagem mapa.svg + camada SVG por cima ---------- */
  const VW = 608, VH = 465;        // mesmas proporções do mapa.svg
  let nos = {};                                            // marcador de cada registro
  function mensagemMapa(txt){ const m = $('mapa-msg'); m.textContent = txt || ''; m.hidden = !txt; }
  function limparMapa(){ $('mapa').innerHTML = ''; nos = {}; }

  function desenharMapa(){
    limparMapa();
    if(carregando){ mensagemMapa('Carregando...'); return; }
    if(erro || !dados || !dados.casa){ mensagemMapa(erro ? 'Não foi possível carregar o histórico.' : 'Nenhum registro encontrado'); return; }

    const {casa, raio, itens} = dados;
    const mLng = 111320 * Math.cos(casa.lat * Math.PI / 180);
    const ps = itens.map(it => ({x: (it.lng - casa.lng) * mLng, y: (it.lat - casa.lat) * 111320}));   // metros a partir da casa
    const xs = [-raio, raio, ...ps.map(p => p.x)], ys = [-raio, raio, ...ps.map(p => p.y)];
    const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
    const PAD = 45, k = Math.min((VW - 2*PAD) / (maxX - minX), (VH - 2*PAD) / (maxY - minY), 12);       // px por metro
    const X = m => VW/2 + (m - (minX + maxX) / 2) * k, Y = m => VH/2 - (m - (minY + maxY) / 2) * k;
    const cx = X(0), cy = Y(0);

    let g = `<circle cx="${cx}" cy="${cy}" r="${raio * k}" fill="rgba(15,107,100,.14)" stroke="#0f6b64" stroke-width="4" stroke-dasharray="11 9"/>`;
    for(let i = 1; i < itens.length; i++){                  // trajeto: azul dentro do raio, vermelho fora
      g += `<line x1="${X(ps[i-1].x)}" y1="${Y(ps[i-1].y)}" x2="${X(ps[i].x)}" y2="${Y(ps[i].y)}" stroke="${itens[i].fora ? '#b3201a' : '#1f5fcf'}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>`;
    }
    g += `<g class="casa" transform="translate(${cx} ${cy})"><circle class="anel" r="30"/><circle r="20" fill="#0f6b64" stroke="#fff" stroke-width="5"/><title>${esc(casa.endereco || 'Casa')}</title></g>`;
    itens.forEach((it, i) => {
      if(it.dist < 5 && it.tipo !== 'saida') return;        // já representado pela casa
      const t = `<title>${esc(it.hora)} · ${esc(it.titulo)}</title>`, pos = `translate(${X(ps[i].x)} ${Y(ps[i].y)})`;
      g += it.tipo === 'saida'
        ? `<g class="marcador" data-i="${i}" transform="${pos}"><circle class="anel" r="31"/><circle r="21" fill="#b3201a" stroke="#fff" stroke-width="5"/><text text-anchor="middle" dy=".36em" font-size="28" font-weight="700" fill="#fff">!</text>${t}</g>`
        : `<g class="marcador" data-i="${i}" transform="${pos}"><circle class="anel" r="15"/><circle r="9" fill="${it.fora ? '#b3201a' : '#1f5fcf'}" stroke="#fff" stroke-width="2"/>${t}</g>`;
    });
    $('mapa').innerHTML = `<svg viewBox="0 0 ${VW} ${VH}" preserveAspectRatio="xMidYMid meet" aria-hidden="true">${g}</svg>`;

    const casaNo = $('mapa').querySelector('.casa');
    itens.forEach((it, i) => { nos[i] = $('mapa').querySelector(`.marcador[data-i="${i}"]`) || casaNo; });
    mensagemMapa(itens.length ? '' : 'Nenhum registro encontrado');
  }

  function selecionar(i, doMapa){
    sel = i;
    document.querySelectorAll('.evento').forEach(b => b.setAttribute('aria-current', String(+b.dataset.i === i)));
    document.querySelectorAll('#mapa .sel').forEach(n => n.classList.remove('sel'));
    if(nos[i]) nos[i].classList.add('sel');
    if(doMapa){ const b = document.querySelector(`.evento[data-i="${i}"]`); if(b) b.scrollIntoView({block: 'nearest'}); }
    else if(matchMedia('(max-width:880px)').matches) $('mapa').scrollIntoView({block: 'nearest'});
  }

  /* ---------- telas ---------- */
  function renderPet(){
    const box = $('pet'), p = pets.find(x => String(x.id) === String(petId));
    if(!p){ box.innerHTML = ''; return; }
    const inicial = esc((p.nome || '?').trim().charAt(0).toUpperCase());
    box.innerHTML = `<span class="avatar" aria-hidden="true">${inicial}</span>` + (pets.length > 1
      ? `<label class="sr-only" for="pet-sel">Animal de estimação</label><select id="pet-sel">${pets.map(x => `<option value="${esc(x.id)}"${String(x.id) === String(petId) ? ' selected' : ''}>${esc(x.nome)}</option>`).join('')}</select>`
      : `<span class="pet-nome">${esc(p.nome)}</span>`);
  }

  function renderTimeline(){
    const t = $('timeline');
    if(semPets){ t.innerHTML = '<p class="msg">Cadastre um animal de estimação para ver o histórico.</p>'; return; }
    if(carregando){ t.innerHTML = '<p class="msg">Carregando histórico...</p>'; return; }
    if(erro){ t.innerHTML = '<p class="msg">Não foi possível carregar o histórico.<br><button type="button" id="tentar">Tentar novamente</button></p>'; return; }
    if(!dados.itens.length){ t.innerHTML = '<p class="msg">Nenhum registro encontrado</p>'; return; }
    t.innerHTML = '<ol>' + dados.itens.map((it, i) => `<li><span class="hora">${esc(it.hora.replace(/^0/, ''))}</span>
      <button type="button" class="evento${it.tipo === 'saida' ? ' saida' : ''}" data-i="${i}" aria-current="${i === sel}">
        ${it.tipo === 'saida' ? '<span class="tag">Saída do raio</span>' : ''}<strong>${esc(it.titulo)}</strong><small>${esc(it.sub)}</small></button></li>`).join('') + '</ol>';
  }

  function render(){
    $('data-btn').textContent = fmtData(data);
    $('data-nativa').value = ymd(data);
    $('ant').disabled = data <= MIN;
    $('prox').disabled = data >= MAX;
    renderPet();
    const ok = !carregando && !erro && dados;
    const n = ok ? dados.itens.length : 0, s = ok ? dados.saidas : 0;
    $('n-reg').textContent = n;
    $('n-saida').textContent = s;
    $('l-saida').textContent = s === 1 ? 'Saída do raio' : 'Saídas do raio';
    $('stat-saida').classList.toggle('alerta', s > 0);
    renderTimeline();
    if(!semPets) desenharMapa(); else { limparMapa(); mensagemMapa('Nenhum animal cadastrado'); }
  }

  async function carregar(){
    if(petId == null) return;
    const meu = ++tok; carregando = true; erro = false; sel = null; render();
    try{ const d = await obterHistorico(petId, data); if(meu !== tok) return; dados = montar(d); }
    catch(e){ if(meu !== tok) return; erro = true; dados = null; }
    carregando = false; render();
  }

  function irPara(d){
    if(d < MIN || d > MAX) return;
    data = d; carregar();
  }

  /* ---------- eventos ---------- */
  $('ant').addEventListener('click', () => irPara(somar(data, -1)));
  $('prox').addEventListener('click', () => irPara(somar(data, 1)));
  $('data-nativa').min = ymd(MIN); $('data-nativa').max = ymd(MAX);
  $('data-btn').addEventListener('click', () => { const n = $('data-nativa'); try{ n.showPicker(); }catch(e){ n.focus(); n.click(); } });
  $('data-nativa').addEventListener('change', e => { if(e.target.value) irPara(doYmd(e.target.value)); });
  $('pet').addEventListener('change', e => { if(e.target.id === 'pet-sel'){ petId = e.target.value; carregar(); } });
  $('timeline').addEventListener('click', e => {
    if(e.target.closest('#tentar')){ carregar(); return; }
    const b = e.target.closest('.evento'); if(b) selecionar(+b.dataset.i, false);
  });
  $('mapa').addEventListener('click', e => { const m = e.target.closest('.marcador'); if(m) selecionar(+m.dataset.i, true); });

  (async function iniciar(){
    render();
    try{
      pets = await obterPets();
      if(!pets.length){ semPets = true; carregando = false; render(); return; }
      petId = pets[0].id; carregar();
    }catch(e){ carregando = false; erro = true; render(); }
  })();
})();
