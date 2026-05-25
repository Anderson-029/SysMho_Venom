<?php
require "../backend/auth.php";

$userName  = $_SESSION["user_name"]  ?? "admin@venom";
$userEmail = $_SESSION["user_email"] ?? "";
?>
<!DOCTYPE html>
<html lang="es" data-theme="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>VENOM-ROUTE · Admin</title>
  <meta name="color-scheme" content="light dark" />
  <link rel="stylesheet" href="admin.css" />
</head>
<body>
  <div class="layout">
    <!-- Sidebar -->
    <aside class="sidebar" aria-label="Navegación del panel">
      <a class="brand" href="#" aria-label="Inicio">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2l3 3-3 3-3-3 3-3zm0 14l3 3-3 3-3-3 3-3zM2 12l3-3 3 3-3 3-3-3zm14 0l3-3 3 3-3 3-3-3z"/>
        </svg>
        <span>VENOM<span class="accent">ROUTE</span></span>
      </a>

      <nav class="menu">
        <button class="menu-item is-active" data-view="overview">📊 Overview</button>
        <button class="menu-item" data-view="operations">⚡ Operaciones</button>
        <button class="menu-item" data-view="sessions">🧭 Sesiones</button>
        <button class="menu-item" data-view="logs">🗂️ Logs & Evidencias</button>
        <button class="menu-item" data-view="audit">📋 Auditoría</button>
        <button class="menu-item" data-view="users">👤 Usuarios</button>
        <button class="menu-item" data-view="reports">📄 Reportes</button>
      </nav>

      <div class="sidebar-footer">
        <div class="role-chip" title="Usuario actual">ADMIN</div>
        <button id="logoutBtn" class="btn btn-ghost btn-sm" type="button">Salir</button>
      </div>
    </aside>

    <!-- Main -->
    <main class="main">
      <!-- Topbar -->
      <header class="topbar">
        <div class="search">
          <input id="globalSearch" type="search" placeholder="Buscar en el panel…" aria-label="Buscar"/>
        </div>
        <div class="actions">
          <label class="theme-switch" title="Cambiar tema">
            <input id="themeToggle" type="checkbox" aria-label="Dark mode"/>
            <span>🌙</span>
          </label>
          <div class="user-mini">
            <span id="userNameMini"><?php echo htmlspecialchars($userName); ?></span>
            <span class="dot"></span>
          </div>
        </div>
      </header>

      <!-- OVERVIEW -->
      <section id="view-overview" class="view is-visible" aria-labelledby="ov-title">
        <h1 id="ov-title">Overview</h1>

        <div class="kpi-grid">
          <article class="card kpi">
            <div class="kpi-value" id="kpiSessions">0</div>
            <div class="kpi-label">Sesiones activas</div>
          </article>
          <article class="card kpi">
            <div class="kpi-value" id="kpiDevices">0</div>
            <div class="kpi-label">Hosts escaneados</div>
          </article>
          <article class="card kpi">
            <div class="kpi-value" id="kpiProtocols">0</div>
            <div class="kpi-label">Protocolos monitoreados</div>
          </article>
          <article class="card kpi">
            <div class="kpi-value danger" id="kpiSniffers">0</div>
            <div class="kpi-label">Sniffers detectados</div>
          </article>
        </div>

        <div class="card table-card">
          <div class="card-head">
            <h2>Sesiones recientes</h2>
            <div class="tools"><button class="btn btn-ghost btn-sm" id="refreshOverview">Actualizar</button></div>
          </div>
          <div class="table-wrap">
            <table class="table" aria-label="Sesiones recientes">
              <thead>
                <tr>
                  <th>Inicio</th><th>Víctima</th><th>Gateway</th><th>Interfaz</th>
                  <th>Flags</th><th>Estado</th><th>Acciones</th>
                </tr>
              </thead>
              <tbody id="tblSessions"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- OPERACIONES -->
      <section id="view-operations" class="view" aria-labelledby="op-title">
        <h1 id="op-title">Operaciones</h1>

        <!-- Escaneo de red -->
        <div class="card">
          <div class="card-head"><h3>Escaneo ARP</h3></div>
          <div class="card-body">
            <form id="scanForm" class="form-grid">
              <label><span>Interfaz</span><input name="interface" placeholder="eth0" required></label>
              <label><span>CIDR</span><input name="cidr" placeholder="192.168.1.0/24" required></label>
              <div class="right"><button class="btn" type="submit">Escanear</button></div>
            </form>
            <div id="scanResults" class="table-wrap" style="margin-top:1rem"></div>
          </div>
        </div>

        <!-- MITM -->
        <div class="card" style="margin-top:1rem">
          <div class="card-head"><h3>MITM / ARP Spoofing</h3></div>
          <div class="card-body">
            <form id="mitmForm" class="form-grid">
              <label><span>IP Víctima</span><input name="victim" placeholder="192.168.1.X" required></label>
              <label><span>IP Gateway</span><input name="gateway" placeholder="192.168.1.1" required></label>
              <label><span>Interfaz</span><input name="iface" placeholder="eth0" required></label>
              <label class="checkbox-label">
                <input name="forward" type="checkbox" checked> IP Forward
              </label>
              <label class="checkbox-label">
                <input name="masquerade" type="checkbox" checked> Masquerade (NAT)
              </label>
              <label class="checkbox-label">
                <input name="antisniff" type="checkbox"> Anti-Sniffer
              </label>
              <div class="right">
                <button class="btn btn-ghost btn-sm" id="btnRestoreArp" type="button">Restaurar ARP</button>
                <button class="btn btn-danger btn-sm" id="btnStopMitm" type="button" disabled>Detener</button>
                <button class="btn" type="submit">Iniciar MITM</button>
              </div>
            </form>
          </div>
        </div>

        <!-- Sniffer -->
        <div class="card" style="margin-top:1rem">
          <div class="card-head"><h3>Sniffer</h3></div>
          <div class="card-body">
            <form id="snifferForm" class="form-grid">
              <label><span>Interfaz</span><input name="iface" placeholder="eth0" required></label>
              <div class="right">
                <button class="btn btn-danger btn-sm" id="btnStopSniffer" type="button" disabled>Detener</button>
                <button class="btn" type="submit">Iniciar Sniffer</button>
              </div>
            </form>
          </div>
        </div>
      </section>

      <!-- SESIONES -->
      <section id="view-sessions" class="view" aria-labelledby="se-title">
        <h1 id="se-title">Sesiones</h1>

        <div class="filters">
          <label><span>Interfaz</span><input id="fIface" placeholder="eth0 / wlan0"></label>
          <label><span>Estado</span>
            <select id="fStatus">
              <option value="">Todos</option>
              <option value="ejecutandoce">Ejecutando</option>
              <option value="pendiente">Pendiente</option>
              <option value="terminada">Terminada</option>
              <option value="fallida">Fallida</option>
            </select>
          </label>
          <label><span>Fecha</span><input id="fDate" type="date"></label>
          <button class="btn btn-ghost btn-sm" id="btnFilterSessions">Filtrar</button>
        </div>

        <div class="card table-card">
          <div class="card-head"><h2>Todas las sesiones</h2></div>
          <div class="table-wrap">
            <table class="table" aria-label="Sesiones MITM">
              <thead>
                <tr>
                  <th>ID</th><th>Inicio</th><th>Víctima</th><th>Gateway</th>
                  <th>Interfaz</th><th>Flags</th><th>Estado</th><th>Acciones</th>
                </tr>
              </thead>
              <tbody id="tblSessionsFull"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- LOGS & EVIDENCIAS -->
      <section id="view-logs" class="view" aria-labelledby="lg-title">
        <h1 id="lg-title">Logs & Evidencias</h1>

        <div class="tabs" role="tablist">
          <button class="tab is-active" data-tab="captures" role="tab" aria-controls="tab-captures">Capturas</button>
          <button class="tab" data-tab="antisniffer" role="tab" aria-controls="tab-antisniffer">Anti-Sniffer</button>
        </div>

        <div id="tab-captures" class="tab-panel is-visible" role="tabpanel">
          <div class="filters">
            <label><span>Protocolo</span>
              <select id="filterProtocol">
                <option value="">Todos</option>
                <option>DNS</option><option>HTTP</option><option>HTTPS</option>
                <option>FTP</option><option>SMTP</option><option>ICMP</option>
                <option>ARP</option><option>GLOBAL</option>
              </select>
            </label>
            <label><span>Fecha</span><input id="filterDate" type="date"></label>
            <button id="btnReloadLogs" class="btn btn-ghost btn-sm">Actualizar</button>
          </div>
          <div class="card table-card">
            <div class="card-head"><h2>Artefactos capturados</h2></div>
            <div class="table-wrap">
              <table class="table" aria-label="Artefactos de captura">
                <thead>
                  <tr><th>Protocolo</th><th>Tipo</th><th>Archivo</th><th>SHA-256</th><th>Fecha</th><th>Acciones</th></tr>
                </thead>
                <tbody id="tblLogs"></tbody>
              </table>
            </div>
          </div>
        </div>

        <div id="tab-antisniffer" class="tab-panel" role="tabpanel">
          <div class="card table-card">
            <div class="card-head"><h2>Detecciones Anti-Sniffer</h2></div>
            <div class="table-wrap">
              <table class="table" aria-label="Detecciones anti-sniffer">
                <thead><tr><th>Fecha/Hora</th><th>IP</th><th>MAC</th></tr></thead>
                <tbody id="tblAntiSniffer"></tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- AUDITORÍA (trail completo de eventos) -->
      <section id="view-audit" class="view" aria-labelledby="au-title">
        <h1 id="au-title">Auditoría</h1>

        <div class="filters">
          <label><span>Fecha desde</span><input id="auditFrom" type="date"></label>
          <label><span>Fecha hasta</span><input id="auditTo" type="date"></label>
          <button class="btn btn-ghost btn-sm" id="btnReloadAudit">Actualizar</button>
        </div>

        <div class="card table-card">
          <div class="card-head"><h2>Trail de eventos</h2></div>
          <div class="table-wrap">
            <table class="table" aria-label="Trail de auditoría">
              <thead>
                <tr><th>Fecha/Hora</th><th>Usuario</th><th>Acción</th><th>Detalle</th></tr>
              </thead>
              <tbody id="tblAudit"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- USUARIOS -->
      <section id="view-users" class="view" aria-labelledby="us-title">
        <h1 id="us-title">Usuarios</h1>

        <div class="card table-card">
          <div class="card-head">
            <h2>Usuarios del sistema</h2>
            <div class="tools"><button class="btn btn-sm" id="btnNewUser">+ Nuevo</button></div>
          </div>
          <div class="table-wrap">
            <table class="table" aria-label="Usuarios">
              <thead>
                <tr><th>Nombre</th><th>Email</th><th>Rol</th><th>Estado</th><th>Acciones</th></tr>
              </thead>
              <tbody id="tblUsers"></tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- REPORTES -->
      <section id="view-reports" class="view" aria-labelledby="rp-title">
        <h1 id="rp-title">Reportes</h1>
        <div class="card">
          <div class="card-head"><h3>Generar reporte</h3></div>
          <div class="card-body">
            <form id="reportForm" class="form-grid">
              <label><span>Rango de fechas</span><input name="dates" placeholder="2025-09-01 a 2025-09-15" required></label>
              <label><span>Formato</span>
                <select name="format">
                  <option>PDF</option><option>CSV</option><option>JSON</option><option>Markdown</option>
                </select>
              </label>
              <div class="right"><button class="btn" type="submit">Exportar</button></div>
            </form>
            <div id="reportInfo" class="muted" aria-live="polite"></div>
          </div>
        </div>
      </section>

      <footer class="legal small">
        ⚠ Uso exclusivo en redes autorizadas. MITM, ARP spoofing y sniffer requieren root y scope definido.
      </footer>
    </main>
  </div>

  <!-- Modal nuevo usuario -->
  <dialog id="userModal" class="modal">
    <h3>Nuevo usuario</h3>
    <form id="userForm" method="dialog">
      <div class="form-grid">
        <label><span>Nombre</span><input name="name" required placeholder="Anderson"></label>
        <label><span>Email</span><input name="email" type="email" required placeholder="admin@venom.local"></label>
        <label><span>Contraseña (opcional — se genera si está vacía)</span><input name="password" type="password" placeholder="••••••••"></label>
        <div class="right">
          <button class="btn btn-ghost btn-sm" value="cancel">Cancelar</button>
          <button class="btn btn-sm" value="ok">Crear</button>
        </div>
      </div>
    </form>
  </dialog>

  <!-- Modal detalle de sesión -->
  <dialog id="sessionModal" class="modal">
    <div class="modal-inner">
      <h3>Detalle de sesión</h3>
      <div id="sessionDetail"></div>
      <div class="right" style="margin-top:1rem">
        <button class="btn btn-ghost" id="closeSessionModal">Cerrar</button>
      </div>
    </div>
  </dialog>

  <div id="toasts" class="toasts" aria-live="polite" aria-atomic="true"></div>

  <script>
    window.SESSION = {
      userName: <?php echo json_encode($userName); ?>,
      userEmail: <?php echo json_encode($userEmail); ?>
    };
  </script>
  <script src="admin.js" defer></script>
</body>
</html>
