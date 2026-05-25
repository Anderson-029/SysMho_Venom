DROP TABLE IF EXISTS tab_stats_protocolo;
DROP TABLE IF EXISTS tab_eventos_sesion;
DROP TABLE IF EXISTS tab_scan_hosts;
DROP TABLE IF EXISTS tab_detecciones;
DROP TABLE IF EXISTS tab_artefactos;
DROP TABLE IF EXISTS tab_sesiones;
DROP TABLE IF EXISTS tab_protocolos;
DROP TABLE IF EXISTS tab_tipo_evidencia;
DROP TABLE IF EXISTS tab_runners;
DROP TABLE IF EXISTS tab_alcances;
DROP TABLE IF EXISTS tokens_invitacion;
DROP TABLE IF EXISTS tab_usuarios;


CREATE TABLE tab_Usuarios (

  id_usuario          BIGINT GENERATED ALWAYS AS IDENTITY,            -- ID interno único del usuario
  nombre              VARCHAR(100) NOT NULL,                          -- Nombre para mostrar en la app y reportes
  email_usuario       VARCHAR(100) NOT NULL,                          -- Correo para login/avisos
  dir_usuario         VARCHAR(100) DEFAULT '',                        -- Dirección o notas (texto libre)
  num_telefono        VARCHAR(50) DEFAULT '',                         -- Teléfono en formato texto (+, guiones, ceros)
  passwd_hash         VARCHAR(255) NOT NULL,                          -- Hash de la contraseña (no la clave real)
  rol                 VARCHAR NOT NULL CHECK (rol IN ('admin')), -- Único rol permitido
  activo              BOOLEAN DEFAULT TRUE NOT NULL,                  -- Si la cuenta está habilitada
  fecha_registro      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,          -- Cuándo se creó el usuario
  fecha_actualizacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,          -- Última modificación del registro

 -- Columnas de auditoría
  usr_insert                  VARCHAR(100)  NOT NULL,
  fec_insert                  TIMESTAMP     NOT NULL,
  usr_update                  VARCHAR(100)  NULL,
  fec_update                  TIMESTAMP     NULL,
  usr_delete                  VARCHAR(100)  NULL,
  fec_delete                  TIMESTAMP     NULL,

  PRIMARY KEY (id_usuario),                                           -- Identificador principal
  UNIQUE (email_usuario)                                              -- Evita correos duplicados
);

CREATE TABLE tokens_invitacion (
  id_token           BIGINT GENERATED ALWAYS AS IDENTITY,                     -- Identificador único del token
  token              VARCHAR(100) NOT NULL,                       -- Código único del token de invitación
  rol_destino        VARCHAR NOT NULL CHECK (rol_destino IN ('admin')), -- Único rol permitido
  creado_por         INT NOT NULL,                                       -- ID del usuario (admin) que generó el token
  fecha_creacion     TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,                -- Fecha/hora en que se creó el token
  fecha_expiracion   TIMESTAMPTZ NULL,                                     -- Fecha de expiración del token (opcional)
  usado              BOOLEAN DEFAULT FALSE,                              -- Indica si el token ya fue utilizado
  usado_por          INT NULL,                                           -- ID del usuario que utilizó el token
  fecha_uso          TIMESTAMP NULL,                                     -- Fecha/hora en que el token fue utilizado

  -- Columnas de auditoría
  usr_insert                  VARCHAR(100)  NOT NULL,
  fec_insert                  TIMESTAMP     NOT NULL,
  usr_update                  VARCHAR(100)  NULL,
  fec_update                  TIMESTAMP     NULL,
  usr_delete                  VARCHAR(100)  NULL,
  fec_delete                  TIMESTAMP     NULL,

  PRIMARY KEY (id_token),
  FOREIGN KEY (creado_por) REFERENCES tab_Usuarios(id_usuario), -- Relación con el admin que lo creó
  FOREIGN KEY (usado_por) REFERENCES tab_Usuarios(id_usuario),   -- Relación con el usuario que lo usó
  UNIQUE (token)
);


CREATE TABLE tab_Alcances (

  id_alcance            BIGINT GENERATED ALWAYS AS IDENTITY,          -- ID del alcance/proyecto
  nombre                VARCHAR(100) NOT NULL,                        -- Título del alcance
  descripcion           TEXT,                                         -- Detalle del objetivo
  rango_red             CIDR,                                         -- Red permitida (ej: 192.168.1.0/24)
  creado_por            BIGINT NOT NULL,                              -- Usuario que lo creó
  fecha_creacion        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- Cuándo se creó
  fecha_actualizacion   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- Última modificación
  activo                BOOLEAN DEFAULT TRUE NOT NULL,                -- Si el alcance está vigente

 -- Columnas de auditoría
  usr_insert                  VARCHAR(100)  NOT NULL,
  fec_insert                  TIMESTAMP     NOT NULL,
  usr_update                  VARCHAR(100)  NULL,
  fec_update                  TIMESTAMP     NULL,
  usr_delete                  VARCHAR(100)  NULL,
  fec_delete                  TIMESTAMP     NULL,

  PRIMARY KEY (id_alcance),                                           -- Identificador del alcance
  FOREIGN KEY (creado_por) REFERENCES tab_Usuarios(id_usuario)        -- Debe existir el usuario creador


);

CREATE TABLE tab_Runners (

  id_runner      BIGINT GENERATED ALWAYS AS IDENTITY,                 -- ID del runner (referencia desde sesiones/jobs)
  nombre         VARCHAR(100) NOT NULL,                               -- Nombre lógico (ej: runner-sede-a-01)
  mgmt_host      VARCHAR(255) NOT NULL,                               -- Hostname/FQDN de gestión
  mgmt_ip        INET,                                                -- IP de gestión (IPv4/IPv6)
  mgmt_interface VARCHAR(50) NOT NULL,                                -- Interfaz de red usada (ej: eth0)
  version_ag     VARCHAR(50) NOT NULL,                                -- Versión del agente
  estado         VARCHAR(50) NOT NULL CHECK (estado IN ('activo','inactivo','mantenimiento')),                                                  -- Estado (activo/inactivo/mantenimiento)
  os_platform    VARCHAR(50) NOT NULL,                                -- SO/plataforma
  capacidades    TEXT[] NOT NULL,                                     -- Lista simple de capacidades declaradas
  ultimo_latido  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,               -- Último “latido” recibido
  created_at     TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,               -- Alta del runner
  updated_at     TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,               -- Última actualización

 -- Columnas de auditoría
  usr_insert                  VARCHAR(100)  NOT NULL,
  fec_insert                  TIMESTAMP     NOT NULL,
  usr_update                  VARCHAR(100)  NULL,
  fec_update                  TIMESTAMP     NULL,
  usr_delete                  VARCHAR(100)  NULL,
  fec_delete                  TIMESTAMP     NULL,

  PRIMARY KEY (id_runner),                                           -- Identificador del runner
  UNIQUE (mgmt_ip)                                                    -- IP de gestión única (corrección de ip_runner)
);

CREATE TABLE tab_Sesiones (

  id_sesion             BIGINT GENERATED ALWAYS AS IDENTITY,          -- ID de la sesión
  id_alcance            BIGINT NOT NULL,                              -- A qué alcance pertenece
  id_runner             BIGINT NOT NULL,                              -- En qué runner se ejecuta
  creado_por            BIGINT NOT NULL,                              -- Usuario que creó la sesión
  victima_ip            INET NOT NULL,                                -- IP del equipo observado
  gateway_ip            INET NOT NULL,                                -- IP del gateway
  interfaz              VARCHAR(100) NOT NULL,                        -- Interfaz usada (ej: eth0)
  enable_forward        BOOLEAN DEFAULT TRUE NOT NULL,                -- Si se habilita reenvío de tráfico
  enable_masquerade     BOOLEAN DEFAULT TRUE NOT NULL,                -- Si se aplica NAT/masquerade
  enable_antinsniff     BOOLEAN DEFAULT TRUE NOT NULL,                -- Si se activa anti-sniffer
  estado                VARCHAR(20) NOT NULL CHECK (estado IN ('ejecutandoce','terminada','pendiente','fallida')),                                                        -- pendiente/correindo/en pausa/fallida
  inicio                TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- Cuándo inició
  fin                   TIMESTAMP,                                    -- Cuándo terminó (si terminó)
  notas                 TEXT,                                         -- Comentarios de la sesión

 -- Columnas de auditoría
  usr_insert                  VARCHAR(100)  NOT NULL,
  fec_insert                  TIMESTAMP     NOT NULL,
  usr_update                  VARCHAR(100)  NULL,
  fec_update                  TIMESTAMP     NULL,
  usr_delete                  VARCHAR(100)  NULL,
  fec_delete                  TIMESTAMP     NULL,

  PRIMARY KEY (id_sesion),                                            -- Identificador de la sesión
  FOREIGN KEY (id_alcance) REFERENCES tab_Alcances(id_alcance),       -- Debe existir el alcance
  FOREIGN KEY (id_runner)  REFERENCES tab_Runners(id_runner),         -- Debe existir el runner (si se usa)
  FOREIGN KEY (creado_por) REFERENCES tab_Usuarios(id_usuario)        -- Debe existir el usuario creador
  -- NOTA: se quitaron UNIQUE (id_alcance) / UNIQUE (id_runner) porque
  -- limitarían a una sola sesión por alcance/runner en toda la historia.
);

CREATE TABLE tab_Tipo_evidencia (

  id_evidencia              BIGINT GENERATED ALWAYS AS IDENTITY,      -- ID del tipo (referencia desde artefactos)
  nombre                    VARCHAR(100) NOT NULL,                    -- Nombre amigable para la UI
  codigo                    VARCHAR(100) NOT NULL,                    -- Código corto (ej: pcap, txt, log)
  descripcion               TEXT NOT NULL,                            -- Para qué sirve este tipo
  extension                 VARCHAR(254) NOT NULL,                    -- Extensión típica (ej: .pcap)
  mime_type                 VARCHAR(100) NOT NULL,                    -- Tipo MIME al descargar/mostrar
  formato_estructura        VARCHAR(100) NOT NULL,                    -- Pista: binario / texto / json
  genera_hash_por_defecto   BOOLEAN DEFAULT TRUE,                     -- Si solemos calcular hash para este tipo
  algoritmo_hash            VARCHAR(255) NOT NULL,                    -- Algoritmo sugerido (ej: SHA-256)
  compresible               BOOLEAN DEFAULT TRUE,                     -- Si conviene comprimirlo
  cifrar_en_descanso        BOOLEAN DEFAULT TRUE,                     -- Si debe guardarse cifrado
  retencion_dias_default    INTEGER NOT NULL,                         -- Días sugeridos de conservación
  sensibilidad_nivel        SMALLINT NOT NULL,                        -- Sensibilidad 1..5
  activo                    BOOLEAN DEFAULT TRUE,                     -- Si sigue disponible para usar

 -- Columnas de auditoría
  usr_insert                  VARCHAR(100)  NOT NULL,
  fec_insert                  TIMESTAMP     NOT NULL,
  usr_update                  VARCHAR(100)  NULL,
  fec_update                  TIMESTAMP     NULL,
  usr_delete                  VARCHAR(100)  NULL,
  fec_delete                  TIMESTAMP     NULL,

  PRIMARY KEY (id_evidencia)                                          -- Identificador del catálogo
);

CREATE TABLE tab_Protocolos (

  code                   BIGINT GENERATED ALWAYS AS IDENTITY,         -- Código del protocolo (ej: DNS, HTTP)
  nombre                 VARCHAR(100) NOT NULL,                       -- Nombre completo
  descripcion            TEXT NOT NULL,                               -- Descripción simple
  capa                   VARCHAR(10),                                 -- Capa del modelo (L2/L3/L4/L7)
  transporte             VARCHAR(100) NOT NULL,                       -- Transporte base (TCP/UDP/ICMP/ARP)
  numero_protocolo_iana  INTEGER NOT NULL,                            -- Número IANA si aplica
  puerto_principal       INTEGER NOT NULL,                            -- Puerto típico (53, 80, 443…)
  tls_probable           BOOLEAN DEFAULT TRUE,                        -- Si suele ir cifrado (como HTTPS)
  sni_aplica             BOOLEAN DEFAULT TRUE,                        -- Si se puede leer SNI en TLS
  visibilidad_sniffer    VARCHAR(100) NOT NULL,                       -- Qué suele verse (payload/cabeceras/metadatos)
  riesgo_exfiltracion    SMALLINT NOT NULL,                           -- Riesgo de fuga 1..5
  pii_probable           SMALLINT NOT NULL,                           -- Probabilidad de PII 1..5
  creado_en              TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,       -- Alta del registro
  actualizado_en         TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,       -- Última actualización

 -- Columnas de auditoría
  usr_insert                  VARCHAR(100)  NOT NULL,
  fec_insert                  TIMESTAMP     NOT NULL,
  usr_update                  VARCHAR(100)  NULL,
  fec_update                  TIMESTAMP     NULL,
  usr_delete                  VARCHAR(100)  NULL,
  fec_delete                  TIMESTAMP     NULL,

  PRIMARY KEY (code)                                                  -- Usamos el código como ID principal
);

CREATE TABLE tab_Artefactos (

  id_artefacto          BIGINT GENERATED ALWAYS AS IDENTITY,          -- ID del artefacto
  id_sesion             BIGINT NOT NULL,                              -- A qué sesión pertenece
  id_evidencia          BIGINT NOT NULL,                              -- Tipo de evidencia (pcap/txt/log/hash/report)
  ruta_archivo          TEXT NOT NULL,                                -- Dónde se guardó
  sha256                TEXT,                                         -- Huella de integridad
  tamano_bytes          BIGINT,                                       -- Tamaño en bytes
  creado_en             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- Cuándo se creó

 -- Columnas de auditoría
  usr_insert                  VARCHAR(100)  NOT NULL,
  fec_insert                  TIMESTAMP     NOT NULL,
  usr_update                  VARCHAR(100)  NULL,
  fec_update                  TIMESTAMP     NULL,
  usr_delete                  VARCHAR(100)  NULL,
  fec_delete                  TIMESTAMP     NULL,

  PRIMARY KEY (id_artefacto),                                         -- Identificador del artefacto
  FOREIGN KEY (id_sesion)    REFERENCES tab_Sesiones(id_sesion),      -- Debe existir la sesión
  FOREIGN KEY (id_evidencia) REFERENCES tab_Tipo_evidencia(id_evidencia), -- Debe existir el tipo
  UNIQUE (id_sesion, id_evidencia)                                    -- 1 artefacto por tipo y sesión (como en tu script)
);

CREATE TABLE tab_Detecciones (

  id_deteccion          BIGINT GENERATED ALWAYS AS IDENTITY,          -- ID de la detección
  id_sesion             BIGINT NOT NULL,                              -- En qué sesión ocurrió
  ip_sospechosa         INET,                                         -- IP sospechosa (si aplica)
  mac_sospechosa        MACADDR,                                      -- MAC sospechosa (si aplica)
  severidad             SMALLINT,                                     -- Gravedad 1..5
  detalles              JSONB,                                        -- Pruebas/indicadores en JSON
  detectado_en          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- Cuándo se detectó

 -- Columnas de auditoría
  usr_insert                  VARCHAR(100)  NOT NULL,
  fec_insert                  TIMESTAMP     NOT NULL,
  usr_update                  VARCHAR(100)  NULL,
  fec_update                  TIMESTAMP     NULL,
  usr_delete                  VARCHAR(100)  NULL,
  fec_delete                  TIMESTAMP     NULL,

  PRIMARY KEY (id_deteccion),                                         -- Identificador de la detección
  FOREIGN KEY (id_sesion) REFERENCES tab_Sesiones(id_sesion),         -- Debe existir la sesión
  UNIQUE (id_sesion, ip_sospechosa, mac_sospechosa, detectado_en)     -- Evita duplicados exactos de la misma detección
);

CREATE TABLE tab_Stats_protocolo (
  
  id_stat               BIGINT GENERATED ALWAYS AS IDENTITY,          -- ID de la fila de estadísticas
  id_sesion             BIGINT NOT NULL,                              -- A qué sesión pertenecen estas métricas
  protocolo_code        BIGINT   NOT NULL,                            -- Protocolo medido (ej: DNS, HTTP)
  paquetes              BIGINT NOT NULL,                              -- Cantidad de paquetes vistos
  bytes                 BIGINT,                                       -- Volumen total en bytes (opcional)
  ultima_actualizacion  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- Última vez que se actualizó el conteo
  creado_en             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- Cuándo se creó el registro

 -- Columnas de auditoría
  usr_insert                  VARCHAR(100)  NOT NULL,
  fec_insert                  TIMESTAMP     NOT NULL,
  usr_update                  VARCHAR(100)  NULL,
  fec_update                  TIMESTAMP     NULL,
  usr_delete                  VARCHAR(100)  NULL,
  fec_delete                  TIMESTAMP     NULL,

  PRIMARY KEY (id_stat),                                              -- Identificador principal
  FOREIGN KEY (id_sesion)      REFERENCES tab_Sesiones(id_sesion),    -- Debe existir la sesión
  FOREIGN KEY (protocolo_code) REFERENCES tab_Protocolos(code),       -- Debe existir el protocolo
  UNIQUE (id_sesion, protocolo_code)                                  -- 1 fila por protocolo en cada sesión
);

CREATE TABLE tab_Eventos_sesion (

  id_evento             BIGINT GENERATED ALWAYS AS IDENTITY,          -- ID del evento
  id_sesion             BIGINT NOT NULL,                              -- A qué sesión pertenece
  codigo                TEXT,                                         -- Código corto (ej: ARP_START)
  nivel                 VARCHAR(10),                                  -- debug/info/warn/error
  mensaje               TEXT,                                         -- Texto del evento
  payload               JSONB,                                        -- Datos extras en JSON
  creado_en             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,          -- Cuándo ocurrió

 -- Columnas de auditoría
  usr_insert                  VARCHAR(100)  NOT NULL,
  fec_insert                  TIMESTAMP     NOT NULL,
  usr_update                  VARCHAR(100)  NULL,
  fec_update                  TIMESTAMP     NULL,
  usr_delete                  VARCHAR(100)  NULL,
  fec_delete                  TIMESTAMP     NULL,

  PRIMARY KEY (id_evento),                                            -- Identificador del evento
  FOREIGN KEY (id_sesion) REFERENCES tab_Sesiones(id_sesion),         -- Debe existir la sesión
  UNIQUE (id_sesion, codigo, creado_en)                               -- Permite muchos eventos, evita duplicados exactos
);

CREATE TABLE tab_Scan_hosts (

  id_host         BIGINT GENERATED ALWAYS AS IDENTITY,                -- ID del host detectado
  id_sesion       BIGINT NOT NULL,                                    -- Sesión en la que se detectó
  ip              INET  NOT NULL,                                     -- IP del host encontrado
  mac             MACADDR,                                            -- MAC del host (si se obtuvo)
  vendor          TEXT,                                               -- Fabricante (si se pudo resolver)
  first_seen      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                -- Primera vez que se vio
  last_seen       TIMESTAMP,                                          -- Última vez que se vio

 -- Columnas de auditoría
  usr_insert                  VARCHAR(100)  NOT NULL,
  fec_insert                  TIMESTAMP     NOT NULL,
  usr_update                  VARCHAR(100)  NULL,
  fec_update                  TIMESTAMP     NULL,
  usr_delete                  VARCHAR(100)  NULL,
  fec_delete                  TIMESTAMP     NULL,

  PRIMARY KEY (id_host),                                              -- Identificador del host
  FOREIGN KEY (id_sesion) REFERENCES tab_Sesiones(id_sesion),         -- Debe existir la sesión
  UNIQUE (id_sesion, ip)                                              -- Un host por IP dentro de una sesión
);

-- ============================================================
-- Datos iniciales de catálogos
-- ============================================================

INSERT INTO tab_Protocolos
  (nombre, descripcion, capa, transporte, numero_protocolo_iana, puerto_principal,
   tls_probable, sni_aplica, visibilidad_sniffer, riesgo_exfiltracion, pii_probable,
   usr_insert, fec_insert)
VALUES
  ('DNS',   'Domain Name System — resolución de nombres',        'L7', 'UDP',  17,   53,  false, false, 'queries/respuestas de nombres', 3, 2, 'system', NOW()),
  ('HTTP',  'Hypertext Transfer Protocol — tráfico web claro',   'L7', 'TCP',   6,   80,  false, false, 'headers + body completo',       5, 5, 'system', NOW()),
  ('HTTPS', 'HTTP seguro — solo metadatos (SNI, IP, tamaño)',    'L7', 'TCP',   6,  443,  true,  true,  'SNI + metadatos TLS',           2, 1, 'system', NOW()),
  ('FTP',   'File Transfer Protocol — transferencia de archivos','L7', 'TCP',   6,   21,  false, false, 'comandos + datos en claro',     5, 4, 'system', NOW()),
  ('SMTP',  'Simple Mail Transfer Protocol — correo saliente',   'L7', 'TCP',   6,   25,  false, false, 'headers de mail + body',        5, 5, 'system', NOW()),
  ('ARP',   'Address Resolution Protocol — mapeo IP/MAC',        'L2', 'ARP',  -1,   -1,  false, false, 'peticiones y respuestas ARP',   2, 1, 'system', NOW()),
  ('ICMP',  'Internet Control Message Protocol — ping/traceroute','L3','ICMP',   1,   -1,  false, false, 'tipo, código, payload básico',  1, 1, 'system', NOW()),
  ('GLOBAL','Captura total — todos los protocolos',              'L2', 'ANY',  -1,   -1,  false, false, 'tráfico completo sin filtro',   5, 5, 'system', NOW());

INSERT INTO tab_Tipo_evidencia
  (nombre, codigo, descripcion, extension, mime_type, formato_estructura,
   genera_hash_por_defecto, algoritmo_hash, compresible, cifrar_en_descanso,
   retencion_dias_default, sensibilidad_nivel,
   usr_insert, fec_insert)
VALUES
  ('Captura PCAP',   'pcap',   'Captura binaria de paquetes (Wireshark/Scapy)',    '.pcap',   'application/vnd.tcpdump.pcap', 'binario', true,  'SHA-256', true,  true,  90, 5, 'system', NOW()),
  ('Texto plano',    'txt',    'Resumen legible de paquetes capturados',            '.txt',    'text/plain',                   'texto',   true,  'SHA-256', true,  false, 90, 4, 'system', NOW()),
  ('Hash SHA-256',   'sha256', 'Archivo de integridad SHA-256 de un artefacto',    '.sha256', 'text/plain',                   'texto',   false, 'SHA-256', false, false, 90, 3, 'system', NOW()),
  ('Log detección',  'log',    'Log de texto del detector de sniffers',             '.txt',    'text/plain',                   'texto',   true,  'SHA-256', true,  false, 30, 3, 'system', NOW()),
  ('Reporte',        'report', 'Reporte de sesión generado por el sistema',         '.md',     'text/markdown',                'texto',   false, 'SHA-256', false, false, 365,2, 'system', NOW());
