// Config
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : '/api';

let tipoCliente = 'regular';

// Tipo de cliente
function setTipo(tipo) {
  tipoCliente = tipo;
  document.getElementById('btn-regular').className = 'toggle-btn' + (tipo === 'regular' ? 'active-regular' : '');
  document.getElementById('btn-vip').className = 'toggle-btn' + (tipo === 'vip' ? 'active-vip' : '');
}

// Slider
function syncSlider(val) {
  document.getElementById('desconto-label').textContent = val + '%';
  const pct = (val / 90) * 100;
  document.getElementById('desconto-slider').style.setProperty('--pct', pct + '%');
}
syncSlider(0);

// Moeda
const fmt = v => 'R$ ' + parseFloat(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// Calcular
async function calcular() {
  const valor = parseFloat(document.getElementById('valor').value);
  const desconto = parseFloat(document.getElementById('desconto-slider').value);
  const errEl = document.getElementById('error-msg');

  errEl.style.display = 'none';

  if (!valor || valor <= 0) {
    errEl.textContent = 'Informe um valor de compra válido.';
    errEl.style.display = 'block';
    return;
  }

  const btn = document.getElementById('btn-calcular');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span>Calculando...';

  try {
    const res = await fetch(API_BASE + '/calcular', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tipo_cliente: tipoCliente, valor_compra: valor, desconto })
    });

    if (!res.ok) throw new Error('Erro na API');
    const d = await res.json();

    // Exibir resultado
    document.getElementById('res-valor').textContent = fmt(d.cashback_final);
    document.getElementById('resultado').style.display = 'block';

    // Badges
    let badges = '';
    if (d.vip) badges += '<span class="cashback-vip-badge">⭐ VIP</span>';
    if (d.dobrado) badges += '<span class="cashback-dobrado-badge">✕2 Compra acima de R$500</span>';
    document.getElementById('badges').innerHTML = badges;

    // Steps
    const steps = [
      ['01', 'Valor bruto da compra', fmt(d.valor_compra), ''],
      ['02', `Desconto de ${d.desconto_percentual}%`, '- ' + fmt(d.desconto_reais), ''],
      ['03', 'Valor final (base de cálculo)', fmt(d.valor_final), ''],
      ['04', 'Cashback base (5%)', fmt(d.cashback_base), ''],
    ];
    if (d.vip) steps.push(['05', 'Bônus VIP (+10% sobre base)', '+ ' + fmt(d.cashback_bonus_vip), 'gold']);
    if (d.dobrado) steps.push([d.vip ? '06' : '05', 'Dobro — compra > R$500 (×2)', fmt(d.cashback_apos_vip) + ' × 2', 'accent']);
    steps.push([String(steps.length + 1).padStart(2, '0'), 'CASHBACK FINAL', fmt(d.cashback_final), 'accent']);

    document.getElementById('steps').innerHTML = steps.map(([n, l, v, c]) => `
      <div class="step">
        <div class="step-num">${n}</div>
        <div class="step-body">
          <div class="step-label">${l}</div>
          <div class="step-val ${c}">${v}</div>
        </div>
      </div>`).join('');

    // Scroll suave
    document.getElementById('resultado').scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Atualizar histórico
    await carregarHistorico();

  } catch (e) {
    errEl.textContent = 'Não foi possível conectar à API. Verifique se o servidor está rodando.';
    errEl.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Calcular Cashback';
  }
}

// Carregar histórico
async function carregarHistorico() {
  try {
    const res = await fetch(API_BASE + '/historico');
    if (!res.ok) return;
    const items = await res.json();

    const sec = document.getElementById('historico-section');
    sec.style.display = 'block';
    document.getElementById('hist-count').textContent = items.length + ' consulta' + (items.length !== 1 ? 's' : '');

    if (!items.length) {
      document.getElementById('hist-list').innerHTML = '<div class="empty-state"><span>📋</span>Nenhuma consulta ainda.</div>';
      return;
    }

    document.getElementById('hist-list').innerHTML = items.map(item => {
      const vip = item.tipo_cliente === 'vip';
      const data = item.criado_em ? new Date(item.criado_em).toLocaleString('pt-BR') : '';
      const desc = item.desconto > 0 ? ` · ${item.desconto}% off` : '';
      return `
        <div class="hist-item">
          <div class="hist-icon ${vip ? 'vip' : 'regular'}">${vip ? '⭐' : '👤'}</div>
          <div class="hist-info">
            <div class="hi-top">${vip ? 'VIP' : 'Regular'} · ${fmt(item.valor_compra)}${desc}</div>
            <div class="hi-bot">${data}</div>
          </div>
          <div class="hist-cashback">
            ${fmt(item.cashback)}
            <small>cashback</small>
          </div>
        </div>`;
    }).join('');

  } catch (_) { }
}

// Carregar histórico ao iniciar
carregarHistorico();

// Enter para calcular
document.getElementById('valor').addEventListener('keydown', e => {
  if (e.key === 'Enter') calcular();
})