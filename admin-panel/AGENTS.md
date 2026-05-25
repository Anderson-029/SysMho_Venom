# AGENTS.md — admin-panel/ (Dashboard Administrador Unificado)

## Responsabilidad

Panel de control central de la plataforma. Proporciona la interfaz visual para gestionar y monitorear las sesiones de red, logs, auditoría y reportes. Consume datos de los endpoints REST expuestos en `/api/`.

---

## Archivos

| Archivo | Función |
|---------|---------|
| `admin.php` | Carga inicial del panel. Incluye control de sesión de backend. |
| `admin.js` | Lógica de la aplicación SPA: navegación entre vistas, llamadas HTTP, renderizado y toggle de mocks (`USE_MOCK`). |
| `admin.css` | Hojas de estilo unificadas con design tokens oscuros. |

---

## Secciones del Panel

1. **Overview** — KPIs principales (conteo de sesiones, hosts escaneados, protocolos y alertas).
2. **Operaciones** — Controles operacionales interactivos para:
   - Escaneo ARP de red.
   - Lanzar/Detener ARP Spoofing (MITM).
   - Lanzar/Detener Sniffer de red.
3. **Sesiones** — Tabla con el histórico de sesiones MITM y sus estados.
4. **Logs & Evidencias** — Tabla de artefactos con hash SHA-256 e interactividad para descarga binaria de pcaps y previsualizaciones.
5. **Auditoría** — Log detallado de eventos de auditoría del sistema extraídos de `tab_Eventos_sesion`.
6. **Reportes** — Formulario para exportar el reporte en markdown de la base de datos real.

---

## Conexión API REST (Toggles y Mocks)

`admin.js` se comunica con el backend mediante peticiones HTTP. La constante `USE_MOCK` permite alternar el comportamiento del panel:
- `const USE_MOCK = true;` (desarrollo): Retorna datos simulados en local.
- `const USE_MOCK = false;` (producción): Realiza llamadas fetch a los endpoints reales en `/api/`.

### Mapeo de Endpoints
```javascript
const ENDPOINTS = {
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
  audit:       '/api/audit',
  report:      '/api/reports/export'
};
```

---

## Guards y Restricciones
* Aunque el backend limita accesos exclusivamente al rol de administrador, el frontend (`admin.js`) conserva de forma preventiva condicionales de control de privilegios (como `currentUser.role === 'AUDITOR'`) para denegar operaciones de red o edición si un usuario no cuenta con privilegios elevados.

---

## Validación

```bash
php -l admin-panel/admin.php
# Cargar el panel en el navegador y verificar la consola de desarrollo para depurar llamadas a la API
```
