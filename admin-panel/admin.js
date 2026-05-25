/* ===========================
   Config & Endpoints
=========================== */
const USE_MOCK = false;

const ENDPOINTS = {
  stats:       '/api/stats',
  scan:        '/api/network/scan',
  mitmStart:   '/api/arp/start',
  mitmRestore: '/api/arp/restore',
  snifStart:   '/api/sniffer/start',
  snifStop:    '/api/sniffer/stop',
  logsList:    '/api/logs/list',
  logsDL:      '/api/logs/download?path=',
  logsHash:    '/api/logs/hash?path=',
  antisniffer: '/api/antisniffer/findings',
  sessions:    '/api/sessions',
  sessionById: (id) => `/api/sessions/${encodeURIComponent(id)}`,
  users:       '/api/users',
  audit:       '/api/audit',
  report:      '/api/reports/export'
};

// Nombre inyectado por PHP
document.getElementById('userNameMini').textContent =
  window.SESSION?.userName || 'admin@venom';

/* ===========================
   Theming
=========================== */
const themeToggle = document.getElementById('themeToggle');
const preferred = localStorage.getItem('venom_theme') || 'dark';
document.documentElement.setAttribute('data-theme', preferred);
themeToggle.checked = preferred === 'dark';
themeToggle.addEventListener('change', () => {
  const next = themeToggle.checked ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('venom_theme', next);
});

/* ===========================
   Simple SPA Nav
=========================== */
const menuBtns = [...document.querySelectorAll('.menu-item')];
const VIEW_IDS = ['overview','operations','sessions','logs','audit','users','reports'];
const views = {};
VIEW_IDS.forEach(id => { views[id] = document.getElementById(`view-${id}`); });

menuBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    menuBtns.forEach(b => b.classList.remove('is-active'));
    btn.classList.add('is-active');
    const view = btn.dataset.view;
    Object.entries(views).forEach(([name, el]) => {
      if (el) el.classList.toggle('is-visible', name === view);
    });
    if (view === 'audit')    loadAudit();
    if (view === 'sessions') loadSessions();
    if (view === 'users')    loadUsers();
  });
});

/* ===========================
   Tabs (Logs)
=========================== */
const tabs = [...document.querySelectorAll('.tab')];
const tabPanels = {
  captures:    document.getElementById('tab-captures'),
  antisniffer: document.getElementById('tab-antisniffer')
};
tabs.forEach(t => {
  t.addEventListener('click', () => {
    tabs.forEach(x => x.classList.remove('is-active'));
    t.classList.add('is-active');
    const tab = t.dataset.tab;
    Object.entries(tabPanels).forEach(([name, el]) => {
      if (el) el.classList.toggle('is-visible', name === tab);
    });
  });
});

/* ===========================
   Toasts
=========================== */
const toasts = document.getElementById('toasts');
function toast(msg, type = '') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  toasts.appendChild(el);
  setTimeout(() => el.remove(), 4200);
}

/* ===========================
   Fetch helpers
=========================== */
async function apiFetch(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    let errMsg = `HTTP ${res.status}`;
    try { const j = await res.json(); errMsg = j.error || errMsg; } catch {}
    throw new Error(errMsg);
  }
  return res;
}

async function apiJSON(url, options = {}) {
  const res = await apiFetch(url, options);
  const body = await res.json();
  // API wrapper: {ok, data} or raw array
  return body?.data !== undefined ? body.data : body;
}

/* ===========================
   Overview + KPIs
=========================== */
async function loadOverview() {
  try {
    const [stats, sessions] = await Promise.all([
      apiJSON(ENDPOINTS.stats),
      apiJSON(ENDPOINTS.sessions)
    ]);

    document.getElementById('kpiSessions').textContent =
      stats?.sesiones_activas ?? sessions.filter(s => s.estado === 'ejecutandoce').length;
    document.getElementById('kpiDevices').textContent  = stats?.hosts_descubiertos ?? '—';
    document.getElementById('kpiProtocols').textContent = stats?.protocolos ?? '—';

    try {
      const findings = await apiJSON(ENDPOINTS.antisniffer);
      document.getElementById('kpiSniffers').textContent = findings.length ?? 0;
    } catch { document.getElementById('kpiSniffers').textContent = 0; }

    renderSessionsTable(sessions, 'tblSessions');
  } catch (e) {
    toast('No se pudo cargar overview', 'error');
    console.error(e);
  }
}
document.getElementById('refreshOverview')?.addEventListener('click', loadOverview);

/* ===========================
   Sesiones (vista dedicada)
=========================== */
async function loadSessions() {
  const tbody = document.getElementById('tblSessionsFull');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="7">Cargando…</td></tr>';
  try {
    const sessions = await apiJSON(ENDPOINTS.sessions);
    renderSessionsTable(sessions, 'tblSessionsFull');
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="7" class="danger">Error: ${e.message}</td></tr>`;
  }
}

function renderSessionsTable(sessions, tbodyId) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  tbody.innerHTML = '';
  for (const s of sessions) {
    const flags = [
      s.enable_forward    ? 'FWD' : '',
      s.enable_masquerade ? 'NAT' : '',
      s.enable_antinsniff ? 'AS'  : ''
    ].filter(Boolean).join(' · ') || '—';

    const isRunning = s.estado === 'ejecutandoce';
    const statusTag = isRunning
      ? '<span class="tag success">ACTIVA</span>'
      : `<span class="tag">${s.estado ?? 'DETENIDA'}</span>`;
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${s.inicio ?? s.fec_insert ?? ''}</td>
      <td>${s.victima_ip ?? ''}</td>
      <td>${s.gateway_ip ?? ''}</td>
      <td>${s.interfaz ?? ''}</td>
      <td>${flags}</td>
      <td>${statusTag}</td>
      <td><button class="btn btn-ghost btn-sm" data-action="details" data-id="${s.id_sesion}">Detalles</button></td>
    `;
    tbody.appendChild(tr);
  }
  if (!sessions.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="muted">Sin sesiones registradas</td></tr>';
  }
}

/* ===========================
   Operaciones — Escaneo
=========================== */
document.getElementById('scanForm')?.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const fd = new FormData(ev.currentTarget);
  try {
    const data = await apiJSON(ENDPOINTS.scan, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ interface: fd.get('interface'), cidr: fd.get('cidr') })
    });
    const cont = document.getElementById('scanResults');
    if (!cont) return;
    const devices = data?.devices ?? [];
    cont.innerHTML = `<div class="muted">Red: ${data?.network ?? ''}</div>` +
      (devices.length
        ? devices.map(d => `
          <div class="rowline">
            <span>${d.ip}</span>
            <span class="muted">${d.vendor}</span>
            <code>${d.mac}</code>
          </div>`).join('')
        : '<div class="muted">Sin dispositivos detectados.</div>');
    toast('Escaneo completado');
  } catch (e) {
    toast(`Error en escaneo: ${e.message}`, 'error');
  }
});

/* ===========================
   Operaciones — MITM
=========================== */
document.getElementById('mitmForm')?.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const fd = new FormData(ev.currentTarget);
  const payload = {
    victim:    fd.get('victim'),
    gateway:   fd.get('gateway'),
    forward:   !!fd.get('forward'),
    masquerade: !!fd.get('masquerade'),
    antisniff: !!fd.get('antisniff'),
  };
  try {
    await apiJSON(ENDPOINTS.mitmStart, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    toast('MITM iniciado');
    loadOverview();
  } catch (e) {
    toast(`Error iniciando MITM: ${e.message}`, 'error');
  }
});

document.getElementById('btnRestoreArp')?.addEventListener('click', async () => {
  try {
    await apiJSON(ENDPOINTS.mitmRestore, { method: 'POST' });
    toast('ARP restaurado');
    loadOverview();
  } catch (e) {
    toast(`Error restaurando ARP: ${e.message}`, 'error');
  }
});

/* ===========================
   Operaciones — Sniffer
=========================== */
document.getElementById('snifferForm')?.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const fd = new FormData(ev.currentTarget);
  try {
    await apiJSON(ENDPOINTS.snifStart, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ iface: fd.get('iface') })
    });
    toast('Sniffer activado');
    loadOverview();
  } catch (e) {
    toast(`Error iniciando sniffer: ${e.message}`, 'error');
  }
});

document.getElementById('btnStopSniffer')?.addEventListener('click', async () => {
  try {
    await apiJSON(ENDPOINTS.snifStop, { method: 'POST' });
    toast('Sniffer detenido y guardado');
    loadOverview();
  } catch (e) {
    toast(`No se pudo detener sniffer: ${e.message}`, 'error');
  }
});

/* ===========================
   Logs & Evidencias
=========================== */
async function loadLogs() {
  const tbody = document.getElementById('tblLogs');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="6">Cargando…</td></tr>';
  try {
    const proto = document.getElementById('filterProtocol')?.value || '';
    const date  = document.getElementById('filterDate')?.value  || '';
    const url = `${ENDPOINTS.logsList}?protocol=${encodeURIComponent(proto)}&date=${encodeURIComponent(date)}`;
    const rows = await apiJSON(url);
    tbody.innerHTML = '';
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="muted">Sin artefactos</td></tr>';
      return;
    }
    for (const r of rows) {
      const sha = r.sha256 ?? r.sha ?? '';
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.protocolo ?? r.protocol ?? ''}</td>
        <td>${r.tipo ?? r.type ?? ''}</td>
        <td><code title="${r.ruta_archivo ?? r.path ?? ''}">${r.nombre ?? r.file ?? ''}</code></td>
        <td><code title="${sha}">${sha.slice(0, 12)}${sha ? '…' : ''}</code></td>
        <td>${r.fec_insert ?? r.date ?? ''}</td>
        <td><a class="btn btn-ghost btn-sm" href="${ENDPOINTS.logsDL}${encodeURIComponent(r.ruta_archivo ?? r.path ?? '')}">Descargar</a></td>
      `;
      tbody.appendChild(tr);
    }
  } catch (e) {
    toast(`No se pudieron cargar logs: ${e.message}`, 'error');
    tbody.innerHTML = `<tr><td colspan="6" class="danger">${e.message}</td></tr>`;
  }
}
document.getElementById('btnReloadLogs')?.addEventListener('click', loadLogs);
document.getElementById('filterProtocol')?.addEventListener('change', loadLogs);
document.getElementById('filterDate')?.addEventListener('change', loadLogs);

/* ===========================
   Anti-Sniffer
=========================== */
async function loadAntiSniffer() {
  const tbody = document.getElementById('tblAntiSniffer');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="3">Cargando…</td></tr>';
  try {
    const rows = await apiJSON(ENDPOINTS.antisniffer);
    tbody.innerHTML = '';
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="3" class="muted">Sin detecciones</td></tr>';
      return;
    }
    for (const r of rows) {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${r.detectado_en ?? r.ts ?? ''}</td><td>${r.ip_sospechosa ?? r.ip ?? ''}</td><td><code>${r.mac_sospechosa ?? r.mac ?? ''}</code></td>`;
      tbody.appendChild(tr);
    }
  } catch (e) {
    toast(`No se pudo cargar Anti-Sniffer: ${e.message}`, 'error');
  }
}

/* ===========================
   Usuarios
=========================== */
const userModal = document.getElementById('userModal');
document.getElementById('btnNewUser')?.addEventListener('click', () => {
  userModal?.showModal();
});
userModal?.addEventListener('close', async () => {
  if (userModal.returnValue !== 'ok') return;
  const fd = new FormData(document.getElementById('userForm'));
  try {
    await apiJSON(ENDPOINTS.users, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: fd.get('name'), email: fd.get('email'), role: 'admin' })
    });
    toast('Usuario creado');
    loadUsers();
  } catch (e) { toast(`Error creando usuario: ${e.message}`, 'error'); }
});

async function loadUsers() {
  const tbody = document.getElementById('tblUsers');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="5">Cargando…</td></tr>';
  try {
    const users = await apiJSON(ENDPOINTS.users);
    tbody.innerHTML = '';
    if (!users.length) {
      tbody.innerHTML = '<tr><td colspan="5" class="muted">Sin usuarios</td></tr>';
      return;
    }
    for (const u of users) {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${u.nombre ?? u.name ?? ''}</td>
        <td>${u.email_usuario ?? u.email ?? ''}</td>
        <td><span class="tag">${u.rol ?? u.role ?? ''}</span></td>
        <td>${u.activo ?? u.active
          ? '<span class="tag success">Activo</span>'
          : '<span class="tag">Inactivo</span>'}</td>
        <td>
          <button class="btn btn-ghost btn-sm" data-edit="${u.id_usuario ?? u.id}">Editar</button>
          <button class="btn btn-ghost btn-sm" data-del="${u.id_usuario ?? u.id}">Eliminar</button>
        </td>
      `;
      tbody.appendChild(tr);
    }
    tbody.onclick = async (ev) => {
      const delId = ev.target.dataset.del;
      if (delId) {
        try {
          await apiJSON(`${ENDPOINTS.users}/${delId}`, { method: 'DELETE' });
          toast('Usuario eliminado');
          loadUsers();
        } catch (e) { toast(`No se pudo eliminar: ${e.message}`, 'error'); }
      }
      const editId = ev.target.dataset.edit;
      if (editId) {
        try {
          await apiJSON(`${ENDPOINTS.users}/${editId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ activeToggle: true })
          });
          toast('Usuario actualizado');
          loadUsers();
        } catch (e) { toast(`No se pudo actualizar: ${e.message}`, 'error'); }
      }
    };
  } catch (e) {
    toast(`No se pudieron cargar usuarios: ${e.message}`, 'error');
  }
}

/* ===========================
   Auditoría
=========================== */
async function loadAudit() {
  const tbody = document.getElementById('tblAudit');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="4">Cargando…</td></tr>';
  try {
    const from = document.getElementById('auditFrom')?.value || '';
    const to   = document.getElementById('auditTo')?.value   || '';
    const params = new URLSearchParams();
    if (from) params.set('from', from);
    if (to)   params.set('to', to);
    const events = await apiJSON(`${ENDPOINTS.audit}?${params}`);
    if (!events.length) {
      tbody.innerHTML = '<tr><td colspan="4" class="muted">Sin eventos</td></tr>';
      return;
    }
    tbody.innerHTML = events.map(e => `
      <tr>
        <td>${e.fec_insert ?? e.ts ?? ''}</td>
        <td>${e.usr_insert ?? e.user ?? 'venom_cli'}</td>
        <td>${e.codigo ?? e.action ?? ''}</td>
        <td class="muted small">${e.mensaje ?? e.detail ?? ''}</td>
      </tr>`).join('');
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4" class="danger">Error: ${e.message}</td></tr>`;
  }
}
document.getElementById('btnReloadAudit')?.addEventListener('click', loadAudit);
document.querySelector('[data-view="audit"]')?.addEventListener('click', loadAudit);

/* ===========================
   Reportes
=========================== */
document.getElementById('reportForm')?.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const fd = new FormData(ev.currentTarget);
  try {
    const data = await apiJSON(ENDPOINTS.report, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dates: fd.get('dates'), format: fd.get('format') })
    });
    const info = document.getElementById('reportInfo');
    if (info) info.textContent = data?.file ? `Reporte listo: ${data.file}` : 'Reporte generado.';
    toast('Reporte generado');
  } catch (e) { toast(`Error generando reporte: ${e.message}`, 'error'); }
});

/* ===========================
   Búsqueda global
=========================== */
document.getElementById('globalSearch')?.addEventListener('input', (ev) => {
  const q = ev.target.value.toLowerCase().trim();
  for (const tbody of document.querySelectorAll('table tbody')) {
    for (const tr of tbody.querySelectorAll('tr')) {
      tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
    }
  }
});

/* ===========================
   Modal detalle sesión
=========================== */
document.getElementById('closeSessionModal')?.addEventListener('click', () => {
  document.getElementById('sessionModal')?.close();
});

/* ===========================
   Logout
=========================== */
document.getElementById('logoutBtn')?.addEventListener('click', () => {
  window.location.href = '../backend/logout.php';
});

/* ===========================
   SSE — Real-time
=========================== */
let _sseSource   = null;
let _sseRetries  = 0;
const SSE_MAX_RETRY = 8;

function sseConnect() {
  if (_sseSource) { _sseSource.close(); _sseSource = null; }

  const es = new EventSource('/api/stream');
  _sseSource = es;

  // ── Evento: nuevo evento de sesión ────────────────────────
  es.addEventListener('session_event', (e) => {
    const d = JSON.parse(e.data);
    // Si es inicio/fin de sesión, refrescar overview
    if (d.code === 'SESION_INICIO' || d.code === 'SESION_FIN') {
      loadOverview();
    }
    // Agregar fila al trail de auditoría si la vista está activa
    const tbody = document.getElementById('tblAudit');
    if (tbody && document.getElementById('view-audit')?.classList.contains('is-visible')) {
      const tr = document.createElement('tr');
      tr.classList.add('sse-new');
      tr.innerHTML = `
        <td>${d.ts ?? ''}</td>
        <td>venom_cli</td>
        <td>${d.code ?? ''}</td>
        <td class="muted small">${d.msg ?? ''}</td>`;
      tbody.prepend(tr);
      setTimeout(() => tr.classList.remove('sse-new'), 2000);
    }
  });

  // ── Evento: detección anti-sniffer ────────────────────────
  es.addEventListener('detection', (e) => {
    const d = JSON.parse(e.data);

    // Actualizar KPI sniffers
    const kpi = document.getElementById('kpiSniffers');
    if (kpi) kpi.textContent = (parseInt(kpi.textContent) || 0) + 1;

    // Agregar fila a la tabla si la vista está activa
    const tbody = document.getElementById('tblAntiSniffer');
    if (tbody) {
      const tr = document.createElement('tr');
      tr.classList.add('sse-new');
      tr.innerHTML = `<td>${d.ts ?? ''}</td><td>${d.ip}</td><td><code>${d.mac}</code></td>`;
      tbody.prepend(tr);
      setTimeout(() => tr.classList.remove('sse-new'), 2000);
    }

    // Toast de alerta
    toast(`⚠ Sniffer detectado: ${d.ip} (${d.mac})`, 'error');

    // Notificación del navegador para severidad alta
    if (d.severity >= 4) sseNotify(`Sniffer detectado: ${d.ip}`, d.mac);
  });

  // ── Evento: estado de sesiones activas ────────────────────
  es.addEventListener('session_status', (e) => {
    const d = JSON.parse(e.data);
    sseSetSessionIndicator(d.active_count > 0);
    const kpi = document.getElementById('kpiSessions');
    if (kpi) kpi.textContent = d.active_count;
  });

  es.onerror = () => {
    _sseRetries++;
    sseSetStatus('offline');
    es.close();
    _sseSource = null;
    if (_sseRetries <= SSE_MAX_RETRY) {
      const delay = Math.min(3000 * _sseRetries, 30000);
      setTimeout(sseConnect, delay);
    }
  };

  es.onopen = () => {
    _sseRetries = 0;
    sseSetStatus('online');
  };
}

function sseSetStatus(state) {
  const dot = document.querySelector('.user-mini .dot');
  if (!dot) return;
  dot.style.background   = state === 'online' ? 'var(--primary)' : 'var(--muted)';
  dot.style.boxShadow    = state === 'online'
    ? '0 0 6px rgba(var(--primary-rgb),.8)'
    : 'none';
  dot.title = state === 'online' ? 'Conectado (SSE)' : 'Sin conexión en tiempo real';
}

function sseSetSessionIndicator(active) {
  const btn = document.querySelector('.menu-item[data-view="operations"]');
  if (!btn) return;
  let dot = btn.querySelector('.session-dot');
  if (active) {
    if (!dot) {
      dot = document.createElement('span');
      dot.className = 'session-dot';
      btn.appendChild(dot);
    }
  } else {
    dot?.remove();
  }
}

function sseNotify(title, body) {
  if (!('Notification' in window)) return;
  if (Notification.permission === 'granted') {
    new Notification(`VENOM · ${title}`, { body, icon: '' });
  } else if (Notification.permission !== 'denied') {
    Notification.requestPermission().then(p => {
      if (p === 'granted') new Notification(`VENOM · ${title}`, { body });
    });
  }
}

/* ===========================
   Inicio
=========================== */
async function init() {
  await Promise.allSettled([
    loadOverview(),
    loadLogs(),
    loadAntiSniffer(),
    loadUsers()
  ]);
  sseConnect();
}
init();
