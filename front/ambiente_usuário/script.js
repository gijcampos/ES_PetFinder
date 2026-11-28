(function(){
  const $ = id => document.getElementById(id);
  const DAYS = ['Domingo','Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado'];
  const KEY = 'petfinder.clinica';
  // Troque MOCK para false e ajuste API quando o back estiver pronto.
  const CONFIG = { MOCK:true, API:'/api' };

  /* ---------- estado padrão ---------- */
  const defaults = () => ({
    site:'', nome:'', end:'', tel:'', tz:'America/Sao_Paulo', h24:false,
    // índice 0-6 = dom-sáb, 7 = feriados
    sched:[
      {c:true,o:'08:00',f:'12:00'},
      ...Array(5).fill(0).map(()=>({c:false,o:'08:00',f:'18:00'})),
      {c:false,o:'08:00',f:'12:00'},
      {c:true,o:'08:00',f:'12:00'}
    ]
  });
  let saved = null;
  try{ saved = JSON.parse(localStorage.getItem(KEY)); }catch(e){}
  let data = saved || defaults();

  /* ---------- tabela de horários do formulário ---------- */
  const order = [1,2,3,4,5,6,0,7]; // seg → dom, feriados
  const label = i => i===7 ? 'Feriados' : DAYS[i];
  $('sched').innerHTML = '<tbody>' + order.map(i =>
    `<tr data-i="${i}"><th scope="row">${label(i)}</th>
      <td><input type="time" aria-label="Abre ${label(i)}" data-k="o"></td>
      <td>às</td>
      <td><input type="time" aria-label="Fecha ${label(i)}" data-k="f"></td>
      <td class="cl"><label style="margin:0;font-size:.85rem"><input type="checkbox" data-k="c"> Fechado</label></td></tr>`
  ).join('') + '</tbody>';

  function fillForm(){
    $('site').value = data.site || ''; $('nome').value = data.nome; $('end').value = data.end; $('tel').value = data.tel;
    $('tz').value = data.tz; $('h24').checked = data.h24;
    document.querySelectorAll('#sched tr').forEach(tr=>{
      const s = data.sched[tr.dataset.i];
      tr.querySelector('[data-k=o]').value = s.o;
      tr.querySelector('[data-k=f]').value = s.f;
      tr.querySelector('[data-k=c]').checked = s.c;
    });
    syncSched();
  }
  function syncSched(){
    const all = $('h24').checked;
    document.querySelectorAll('#sched tr').forEach(tr=>{
      const c = tr.querySelector('[data-k=c]').checked;
      tr.classList.toggle('off', c || all);
      tr.querySelectorAll('input[type=time]').forEach(t=>t.disabled = c || all);
      tr.querySelector('[data-k=c]').disabled = all;
    });
  }
  function readForm(){
    const d = {site:$('site').value.trim(), nome:$('nome').value.trim(), end:$('end').value.trim(), tel:$('tel').value, tz:$('tz').value, h24:$('h24').checked, sched:[]};
    document.querySelectorAll('#sched tr').forEach(tr=>{
      d.sched[tr.dataset.i] = {
        o:tr.querySelector('[data-k=o]').value, f:tr.querySelector('[data-k=f]').value, c:tr.querySelector('[data-k=c]').checked
      };
    });
    return d;
  }

  /* ---------- feriados nacionais (fixos + móveis) ---------- */
  const hcache = {};
  function easter(y){ // algoritmo de Meeus/Jones/Butcher
    const a=y%19,b=Math.floor(y/100),c=y%100,d=Math.floor(b/4),e=b%4,f=Math.floor((b+8)/25),
      g=Math.floor((b-f+1)/3),h=(19*a+b-d-g+15)%30,i=Math.floor(c/4),k=c%4,
      l=(32+2*e+2*i-h-k)%7,m=Math.floor((a+11*h+22*l)/451),
      mo=Math.floor((h+l-7*m+114)/31),da=((h+l-7*m+114)%31)+1;
    return Date.UTC(y,mo-1,da);
  }
  const mmdd = t => { const d=new Date(t); return String(d.getUTCMonth()+1).padStart(2,'0')+'-'+String(d.getUTCDate()).padStart(2,'0'); };
  function holidays(y){
    if(hcache[y]) return hcache[y];
    const p = easter(y), day = 864e5;
    const h = {'01-01':'Confraternização Universal','04-21':'Tiradentes','05-01':'Dia do Trabalho','09-07':'Independência do Brasil',
      '10-12':'Nossa Senhora Aparecida','11-02':'Finados','11-15':'Proclamação da República','11-20':'Consciência Negra','12-25':'Natal'};
    h[mmdd(p-2*day)] = 'Sexta-feira Santa';
    h[mmdd(p+60*day)] = 'Corpus Christi';
    return hcache[y] = h;
  }

  /* ---------- data/hora no fuso da CLÍNICA (não do navegador) ---------- */
  function nowIn(tz){
    const parts = new Intl.DateTimeFormat('en-CA',{timeZone:tz,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(new Date());
    const g = t => +parts.find(p=>p.type===t).value;
    return {utc:Date.UTC(g('year'),g('month')-1,g('day')), min:g('hour')*60+g('minute'), hh:g('hour'), mm:g('minute')};
  }
  const toMin = s => { const [h,m]=s.split(':').map(Number); return h*60+m; };
  const fmt = s => s.replace(':','h').replace(/h00$/,'h');

  // Expediente de uma data (utc meia-noite): devolve {h24, closed, o, f, holiday}
  function dayInfo(d, utc){
    const dt = new Date(utc), hol = holidays(dt.getUTCFullYear())[mmdd(utc)] || null;
    if(d.h24) return {h24:true, holiday:hol};
    const s = (hol ? d.sched[7] : d.sched[dt.getUTCDay()]);
    return {closed:s.c || !s.o || !s.f, o:s.o, f:s.f, holiday:hol};
  }
  const rangeTxt = i => i.h24 ? '24 horas' : i.closed ? 'Fechado' : `${fmt(i.o)} às ${fmt(i.f)}`;

  function status(d){
    const n = nowIn(d.tz), t = n.min, today = dayInfo(d, n.utc), prev = dayInfo(d, n.utc-864e5);
    const res = {today, n};
    if(today.h24){ res.open = true; res.msg = 'Atendimento 24 horas'; return res; }
    // turno de ontem que vira a madrugada
    if(!prev.closed && toMin(prev.f) <= toMin(prev.o) && t < toMin(prev.f)){ res.open = true; res.msg = `Fecha às ${fmt(prev.f)}`; return res; }
    if(!today.closed){
      const o = toMin(today.o), f = toMin(today.f), noturno = f <= o;
      if(noturno ? t >= o : (t >= o && t < f)){ res.open = true; res.msg = `Fecha ${noturno?'às':'hoje às'} ${fmt(today.f)}${noturno?' (madrugada)':''}`; return res; }
      if(t < o){ res.open = false; res.msg = `Abre hoje às ${fmt(today.o)}`; return res; }
    }
    for(let k=1;k<=8;k++){ // próxima abertura
      const u = n.utc + k*864e5, i = dayInfo(d,u);
      if(i.h24 || !i.closed){
        const nome = k===1 ? 'amanhã' : DAYS[new Date(u).getUTCDay()].toLowerCase();
        res.open = false; res.msg = `Abre ${nome} às ${i.h24 ? '00h' : fmt(i.o)}`; return res;
      }
    }
    res.open = false; res.msg = 'Sem horário de abertura cadastrado'; return res;
  }

  /* ---------- painel automático ---------- */
  function renderPanel(){
    const d = readForm(), el = $('p-status');
    $('p-nome').textContent = d.nome || 'Sua clínica';
    $('p-meta').textContent = (d.end || d.tel) ? [d.end, d.tel].filter(Boolean).join(' · ') : 'Preencha os dados ao lado para ver a prévia.';

    const s = status(d);
    el.className = 'status ' + (s.open ? 'open' : 'closed');
    el.innerHTML = `<span class="dot"></span><div><strong>${s.open ? 'Aberta agora' : 'Fechada agora'}</strong><span>${s.msg}</span></div>`;

    $('p-holiday').innerHTML = s.today.holiday
      ? `<div class="holiday">Hoje é feriado: ${s.today.holiday}. ${s.today.h24 ? 'A clínica atende 24 horas.' : s.today.closed ? 'A clínica não atende em feriados.' : 'Vale o horário de feriados.'}</div>` : '';

    const tzName = $('tz').selectedOptions[0].textContent;
    $('p-clock').textContent = `Hora na clínica: ${String(s.n.hh).padStart(2,'0')}:${String(s.n.mm).padStart(2,'0')} (${tzName})`;

    const dow = new Date(s.n.utc).getUTCDay();
    $('p-week').innerHTML = '<tbody>' + order.map(i => {
      const info = d.h24 ? {h24:true} : {closed:d.sched[i].c || !d.sched[i].o || !d.sched[i].f, o:d.sched[i].o, f:d.sched[i].f};
      const hoje = (i===dow && !s.today.holiday) || (i===7 && s.today.holiday);
      return `<tr class="${hoje?'today':''}"><td>${label(i)}${hoje?' (hoje)':''}</td><td>${rangeTxt(info)}</td></tr>`;
    }).join('') + '</tbody>';
  }

  /* ---------- máscara e validação ---------- */
  function maskTel(v){
    v = v.replace(/\D/g,'').slice(0,11);
    if(v.length > 10) return v.replace(/(\d{2})(\d{5})(\d{0,4})/,'($1) $2-$3');
    if(v.length > 6)  return v.replace(/(\d{2})(\d{4})(\d{0,4})/,'($1) $2-$3');
    if(v.length > 2)  return v.replace(/(\d{2})(\d*)/,'($1) $2');
    return v;
  }
  function setErr(id, field, msg){
    const e = $(id); e.textContent = msg || ''; e.classList.toggle('on', !!msg);
    if(field) field.setAttribute('aria-invalid', msg ? 'true' : 'false');
    return !msg;
  }
  function vNome(){ const v=$('nome').value.trim(); return setErr('e-nome',$('nome'), !v ? 'Informe o nome da clínica.' : v.length<3 ? 'O nome precisa ter ao menos 3 caracteres.' : ''); }
  function vEnd(){ const v=$('end').value.trim(); return setErr('e-end',$('end'), !v ? 'Informe o endereço da clínica.' : v.length<8 ? 'Endereço muito curto. Use o formato: Rua, Nº - Bairro, Cidade.' : ''); }
  function vTel(){
    const n = $('tel').value.replace(/\D/g,''); let m='';
    if(!n) m='Informe o telefone da clínica.';
    else if(n.length<10) m='Telefone incompleto. Digite o DDD e o número.';
    else if(+n.slice(0,2)<11 || /^(\d)\1+$/.test(n.slice(2))) m='Telefone inválido. Confira o DDD e o número.';
    else if(n.length===11 && n[2]!=='9') m='Celular com 11 dígitos deve começar com 9 após o DDD.';
    return setErr('e-tel',$('tel'),m);
  }
  function vSched(){
    let m='';
    if(!$('h24').checked){
      const d = readForm();
      const bad = order.find(i => !d.sched[i].c && (!d.sched[i].o || !d.sched[i].f || d.sched[i].o===d.sched[i].f));
      if(bad!==undefined) m = `Revise o horário de ${label(bad).toLowerCase()}: informe abertura e fechamento diferentes ou marque "Fechado".`;
      else if(d.sched.slice(0,7).every(s=>s.c)) m = 'A clínica precisa abrir em pelo menos um dia da semana (ou marque 24 horas).';
    }
    return setErr('e-sched',null,m);
  }

  /* ---------- eventos ---------- */
  $('tel').addEventListener('input', e => { e.target.value = maskTel(e.target.value); });
  $('nome').addEventListener('blur', vNome); $('end').addEventListener('blur', vEnd); $('tel').addEventListener('blur', vTel);
  ['nome','end'].forEach(id => $(id).addEventListener('input', () => $(id).getAttribute('aria-invalid')==='true' && (id==='nome'?vNome():vEnd())));
  $('tel').addEventListener('input', () => $('tel').getAttribute('aria-invalid')==='true' && vTel());
  $('form').addEventListener('input', () => { syncSched(); renderPanel(); });
  $('form').addEventListener('change', () => { syncSched(); renderPanel(); });

  function toast(msg, bad){
    const t = $('toast'); t.textContent = msg; t.style.background = bad ? 'var(--bad)' : 'var(--ok)';
    t.classList.add('on'); clearTimeout(toast.id); toast.id = setTimeout(()=>t.classList.remove('on'), 3200);
  }

  async function api(path, body){
    const r = await fetch(CONFIG.API + path, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
    if(!r.ok) throw new Error(r.status);
    return r.json();
  }

  $('form').addEventListener('submit', async e => {
    e.preventDefault();
    const oks = [vNome(), vEnd(), vTel(), vSched()];
    if(oks.includes(false)){
      toast('Corrija os campos destacados para salvar.', true);
      const first = document.querySelector('[aria-invalid=true]'); if(first) first.focus();
      return;
    }
    const novo = readForm();
    try{
      if(CONFIG.MOCK){ localStorage.setItem(KEY, JSON.stringify(novo)); }
      else { await api('/clinicas', novo); }   // ajuste o formato aqui se o back usar outros nomes
      data = novo;
      toast('Clínica preferida salva com sucesso!');
    }catch(err){
      toast('Não foi possível salvar agora. Tente novamente.', true);
    }
  });

  $('cancel').addEventListener('click', () => {
    if(!confirm('Descartar as alterações e voltar ao último cadastro salvo?')) return;
    data = saved = (()=>{ try{ return JSON.parse(localStorage.getItem(KEY)); }catch(e){ return null; } })() || defaults();
    fillForm(); ['e-nome','e-end','e-tel','e-sched'].forEach(i=>setErr(i,null,''));
    document.querySelectorAll('[aria-invalid]').forEach(f=>f.removeAttribute('aria-invalid'));
    renderPanel(); toast('Alterações descartadas.', true);
  });

  /* ---------- importar dados pelo site ---------- */
  // Contrato esperado do back: POST /clinicas/importar  { url }
  // Resposta (todos os campos opcionais):
  // { nome, endereco, telefone, fuso, h24,
  //   horarios:[{dia:0-6 (0=dom), fechado, abre:"08:00", fecha:"18:00"}],
  //   feriados:{fechado, abre, fecha} }
  const mockImportar = url => new Promise(res => setTimeout(() => res({
    nome:'Clínica Vet Exemplo', endereco:'Rua das Flores, 120 - Centro, Campo Mourão',
    telefone:'44999991234', fuso:'America/Sao_Paulo', h24:false,
    horarios:[1,2,3,4,5].map(d=>({dia:d,fechado:false,abre:'08:00',fecha:'19:00'})).concat([{dia:6,fechado:false,abre:'08:00',fecha:'13:00'},{dia:0,fechado:true}]),
    feriados:{fechado:true}
  }), 900));

  const siteOk = v => { try{ const u = new URL(/^https?:\/\//i.test(v) ? v : 'https://'+v); return u.hostname.includes('.') ? u.href : null; }catch(e){ return null; } };

  function aplicar(r){
    let n = 0;
    const set = (el, v) => { if(v===undefined || v===null || v==='') return; el.value = v; el.classList.add('auto'); n++; };
    set($('nome'), r.nome); set($('end'), r.endereco);
    if(r.telefone) set($('tel'), maskTel(r.telefone));
    if(r.fuso && [...$('tz').options].some(o=>o.value===r.fuso)) set($('tz'), r.fuso);
    if(typeof r.h24 === 'boolean'){ $('h24').checked = r.h24; n++; }
    const linha = (i, h) => {
      const tr = document.querySelector(`#sched tr[data-i="${i}"]`); if(!tr || !h) return;
      tr.querySelector('[data-k=c]').checked = !!h.fechado;
      if(h.abre) tr.querySelector('[data-k=o]').value = h.abre;
      if(h.fecha) tr.querySelector('[data-k=f]').value = h.fecha;
      n++;
    };
    (r.horarios || []).forEach(h => linha(h.dia, h));
    linha(7, r.feriados);
    if(!n) throw new Error('vazio');
    syncSched(); renderPanel();
    setErr('e-nome',$('nome'),''); setErr('e-end',$('end'),''); setErr('e-tel',$('tel'),''); setErr('e-sched',null,'');
    toast('Dados preenchidos. Confira tudo antes de salvar.');
  }

  async function importar(){
    const v = $('site').value.trim(), url = v && siteOk(v);
    if(!url){ setErr('e-site',$('site'), v ? 'Site inválido. Exemplo: www.suaclinica.com.br' : 'Cole o link do site da clínica.'); $('site').focus(); return; }
    setErr('e-site',$('site'),'');
    const b = $('fetch'); b.disabled = true; b.textContent = 'Buscando...';
    try{ aplicar(await (CONFIG.MOCK ? mockImportar(url) : api('/clinicas/importar', {url}))); }
    catch(err){ toast('Não encontramos os dados nesse site. Preencha manualmente.', true); }
    finally{ b.disabled = false; b.textContent = 'Buscar dados'; }
  }
  $('fetch').addEventListener('click', importar);
  $('site').addEventListener('keydown', e => { if(e.key==='Enter'){ e.preventDefault(); importar(); } });
  $('form').addEventListener('input', e => e.target.classList.remove('auto'));
  $('form').addEventListener('change', e => e.target.classList.remove('auto'));

  fillForm(); renderPanel();
  setInterval(renderPanel, 30000); // mantém "aberta/fechada" atualizado sozinho
})();
