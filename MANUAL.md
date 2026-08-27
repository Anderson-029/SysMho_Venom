# MANUAL DE USO — VENOM-ROUTE

> Herramienta CLI de auditoría de redes LAN mediante ataques MITM mediante ARP spoofing.
> Uso exclusivo en redes propias o con autorización explícita por escrito. El autor no se
> hace responsable del uso indebido de esta herramienta.

---

## Índice

1. [¿Qué es Venom-Route?](#1-qué-es-venom-route)
2. [¿Para qué sirve? / ¿Qué se puede lograr?](#2-para-qué-sirve--qué-se-puede-lograr)
3. [Requisitos previos](#3-requisitos-previos)
4. [Instalación](#4-instalación)
5. [Arquitectura y módulos](#5-arquitectura-y-módulos)
6. [Modos de ejecución](#6-modos-de-ejecución)
7. [Modo Interactivo (`-I`)](#7-modo-interactivo--i)
8. [Modo Avanzado (con argumentos)](#8-modo-avanzado-con-argumentos)
9. [Opciones y flags](#9-opciones-y-flags)
10. [Qué pasa durante el ataque](#10-qué-pasa-durante-el-ataque)
11. [Evidencia generada (pcap, txt, hash)](#11-evidencia-generada-pcap-txt-hash)
    - 11.1 [Log de funcionamiento del motor](#111-log-de-funcionamiento-del-motor)
12. [Detección de sniffers (anti-sniff)](#12-detección-de-sniffers-anti-sniff)
13. [Detener el ataque y restauración](#13-detener-el-ataque-y-restauración)
14. [Analizar la evidencia capturada](#14-analizar-la-evidencia-capturada)
15. [Casos de uso típicos](#15-casos-de-uso-típicos)
16. [Solución de problemas](#16-solución-de-problemas)
17. [Buenas prácticas y seguridad operacional](#17-buenas-prácticas-y-seguridad-operacional)
18. [Aviso legal](#18-aviso-legal)

---

## 1. ¿Qué es Venom-Route?

**Venom-Route** es una herramienta CLI escrita en Python puro (con Scapy) para realizar
auditorías de seguridad en redes LAN mediante ataques de **Man-in-the-Middle (MITM)** usando
**ARP spoofing**. Se posiciona lógicamente entre una víctima y su gateway, permitiendo:

- Interceptar y clasificar tráfico de red por protocolo.
- Capturar evidencia forense (`.pcap` / `.txt`) con verificación de integridad (`SHA-256`).
- Detectar de forma pasiva otros hosts en la red que estén "sniffeando" tráfico (modo
  promiscuo).
- Redirigir tráfico de forma controlada mediante reglas de `iptables` (NAT/MASQUERADE).

No depende de base de datos ni de servicios externos: **toda la evidencia se guarda como
archivos locales** en el propio sistema donde se ejecuta.

---

## 2. ¿Para qué sirve? / ¿Qué se puede lograr?

Usado en un entorno de laboratorio o red autorizada, Venom-Route permite:

| Objetivo | Cómo lo logra |
|---|---|
| Auditar si el tráfico de un host viaja sin cifrar | ARP spoofing + sniffer clasificado por protocolo |
| Detectar filtraciones de credenciales en protocolos legacy (FTP, Telnet, SMTP) | Captura y guarda tráfico de esos protocolos en texto plano |
| Verificar si hay DNS spoofing/leak o resolución sospechosa | Captura dedicada de tráfico DNS |
| Comprobar si un pentester/adversario tiene un sniffer activo en la red | Módulo `anti_sniff_detector.py` |
| Generar evidencia forense verificable para un informe | Cada `.pcap`/`.txt` puede acompañarse de su hash `SHA-256` |
| Probar la resiliencia de la red frente a ataques de envenenamiento ARP | El propio ataque, de forma controlada y reversible |

**Lo que NO hace:** no descifra TLS/HTTPS (solo puede observar el SNI si es visible), no
explota vulnerabilidades de servicios, no hace escaneo de puertos ni fuzzing — es una
herramienta de interceptación de capa 2/3, no un framework de explotación completo.

---

## 3. Requisitos previos

### Sistema
- Linux (probado en Debian/Ubuntu/Kali). Requiere `iptables`, `/proc/sys/net/ipv4/ip_forward`.
- **Privilegios de root** (`sudo`) — obligatorio, se valida al inicio (`check_root()`).
- Acceso físico o lógico a la red LAN objetivo (mismo segmento que víctima y gateway).

### Software
```bash
# Python 3.12+
sudo apt install python3 python3-pip

# Herramienta de escaneo ARP (usada en modo interactivo)
sudo apt install arp-scan

# Dependencias Python
pip install scapy netifaces
```

### Autorización
- Debes tener **permiso explícito** para auditar la red/objetivo. Sin autorización, esto es
  ilegal en la mayoría de jurisdicciones.

---

## 4. Instalación

```bash
git clone <repo> SysMho_Venom
cd SysMho_Venom/code
pip install scapy netifaces
sudo apt install arp-scan
```

No requiere `venv` obligatorio, pero se recomienda:
```bash
python3 -m venv venv
source venv/bin/activate
pip install scapy netifaces
```
> Nota: Scapy y operaciones de socket crudo requieren root de todos modos, así que el
> venv solo aísla las dependencias, no reemplaza `sudo`.

---

## 5. Arquitectura y módulos

```
code/
├── venom_route.py           # Entry point CLI — orquesta todos los módulos
├── arp_utils.py              # ARP spoofing bidireccional + restauración
├── iptables_utils.py         # IP forwarding, FORWARD policy, MASQUERADE (NAT)
├── network_utils.py          # Detección de interfaces, escaneo ARP, conectividad
├── sniffer_engine.py         # Captura, clasificación y guardado de tráfico
├── sniffer_utils.py          # Hash SHA-256 y filtro de dominios DNS
├── anti_sniff_detector.py    # Detección pasiva de sniffers en la red
├── ui_utils.py                # Banner, colores, prompts, check_root()
├── venom_logger.py            # Log de funcionamiento interno del motor
├── limpiar_logs.py            # Utilidad de mantenimiento: borra evidencia
├── logs/                      # Evidencia por protocolo (se genera en runtime)
└── archivos_unicos/           # Captura global consolidada + hash (runtime)
```

Cada módulo tiene una única responsabilidad y se coordinan desde `venom_route.py`, que
también captura `SIGINT` (Ctrl+C) para ejecutar limpieza y restauración en orden correcto.

---

## 6. Modos de ejecución

Venom-Route se ejecuta siempre como root, y ofrece dos modos:

| Modo | Cuándo usarlo |
|---|---|
| **Interactivo (`-I`)** | No conoces de antemano la IP de la víctima/gateway; quieres escanear la red primero |
| **Avanzado (argumentos)** | Ya conoces víctima, gateway e interfaz — ideal para scripting o repetir auditorías |

---

## 7. Modo Interactivo (`-I`)

```bash
sudo python3 venom_route.py -I
```

Flujo paso a paso:

1. Se muestra el banner y advertencia legal (pulsa ENTER para continuar).
2. El programa detecta interfaces de red disponibles con IP configurada y muestra un menú:
   ```
   [1] Interfaz: eth0 → Red: 192.168.1.0/24
   [2] Interfaz: wlan0 → Red: 192.168.0.0/24
   ```
3. Seleccionas el número de interfaz a usar.
4. Confirmas o corriges el rango CIDR a escanear.
5. Se ejecuta `arp-scan` sobre ese rango y se listan los dispositivos encontrados:
   ```
   [1] 192.168.1.10 → Apple, Inc. → aa:bb:cc:dd:ee:ff
   [2] 192.168.1.1  → TP-Link     → 11:22:33:44:55:66
   ```
6. Eliges cuál es la **víctima** y cuál el **gateway** (por número).
7. Se te pregunta (sí/no):
   - ¿Activar `iptables FORWARD`?
   - ¿Activar `MASQUERADE` (NAT)?
   - ¿Activar detección de sniffers?
8. Se valida conectividad (ping) con víctima y gateway.
9. Se pregunta confirmación final: **"¿ENVENENAR TABLAS ARP DE LA VÍCTIMA Y LA GATEWAY?"**
10. Si aceptas, comienza el ataque y el sniffer.

---

## 8. Modo Avanzado (con argumentos)

Cuando ya conoces los datos de la red:

```bash
sudo python3 venom_route.py <IP_VICTIMA> <IP_GATEWAY> <INTERFAZ> [-F] [-M] [-A]
```

Ejemplos:

```bash
# Ataque básico, sin forwarding real (solo captura pasiva de lo que llega)
sudo python3 venom_route.py 192.168.1.10 192.168.1.1 eth0

# Con forwarding + NAT activados (la víctima mantiene conectividad a internet)
sudo python3 venom_route.py 192.168.1.10 192.168.1.1 eth0 -F -M

# Con detección de sniffers activa en simultáneo
sudo python3 venom_route.py 192.168.1.10 192.168.1.1 eth0 -F -M -A
```

En este modo:
1. Se valida conectividad con víctima y gateway (ping).
2. Se activa `ip_forward` en el kernel automáticamente (siempre, sea cual sea el modo).
3. Si pasaste `-F`/`-M`, se aplican esas reglas de iptables.
4. Se pregunta confirmación antes de envenenar ARP (siempre, no se puede omitir).
5. Comienza sniffing + (opcional) anti-sniff.

---

## 9. Opciones y flags

| Flag | Efecto | Recomendado cuando... |
|---|---|---|
| `-F` | `iptables -P FORWARD ACCEPT` — permite que el kernel reenvíe paquetes entre interfaces | Quieres que el tráfico interceptado siga fluyendo hacia su destino real |
| `-M` | `iptables -t nat -A POSTROUTING -j MASQUERADE` — NAT de salida | La víctima necesita seguir teniendo acceso a internet mientras la interceptas (evita cortar su conexión y levantar sospechas) |
| `-A` | Activa `anti_sniff_detector` en paralelo | Quieres verificar si hay **otros** sniffers activos en la misma red mientras auditas |
| `-I` | Modo interactivo con descubrimiento de red | No conoces víctima/gateway de antemano |

> Si no usas `-F` ni `-M`, el envenenamiento ARP ocurre igual, pero el tráfico de la
> víctima puede cortarse (no habrá reenvío), lo cual es detectable y puede interrumpir
> su conectividad — útil solo para pruebas puntuales, no para auditorías silenciosas.

---

## 10. Qué pasa durante el ataque

1. **Preparación:** se verifica root, conectividad y se activa `ip_forward` en el kernel.
2. **(Opcional) Reglas iptables:** FORWARD a ACCEPT y/o MASQUERADE si se solicitaron.
3. **Envenenamiento ARP bidireccional:**
   - Un hilo envía paquetes ARP falsos a la víctima diciendo "yo soy el gateway".
   - Otro hilo envía paquetes ARP falsos al gateway diciendo "yo soy la víctima".
   - Ambos hilos repiten esto cada ~2 segundos mientras el ataque esté activo.
4. **Sniffer activo:** captura todo el tráfico visible en la interfaz, en ciclos de 5s,
   clasificándolo por protocolo (`DNS`, `HTTP`, `HTTPS` (SNI), `FTP`, `SMTP`, `TELNET`,
   `IRC`, `SMB`, `ARP`, `ICMP`, `TCP`, `UDP`).
5. **(Opcional) Anti-sniff:** en paralelo, envía ARP falsos a una IP inexistente (`6.6.6.6`)
   y observa si algún host responde sin ser el dueño de esa IP → indicio de modo promiscuo.
6. El programa queda en un bucle mostrando `[*] VENOM-ROUTE activo...` hasta `Ctrl+C`.

---

## 11. Evidencia generada (pcap, txt, hash)

Al detener el ataque (o al finalizar la sesión), se generan:

```
code/
├── logs/
│   ├── dns/DNS_<timestamp>.pcap        + .txt
│   ├── http/HTTP_<timestamp>.pcap      + .txt
│   ├── https_sni/HTTPS_<timestamp>.pcap + .txt
│   ├── ftp/FTP_<timestamp>.pcap        + .txt
│   ├── smtp/ ...
│   ├── telnet/ ...
│   ├── irc/ ...
│   ├── smb/ ...
│   ├── arp/ ...
│   ├── icmp/ ...
│   ├── tcp/ ...
│   ├── udp/ ...
│   └── venom_engine.log                 # Log de funcionamiento del propio motor
├── archivos_unicos/
│   ├── captura_total_<timestamp>.pcap   # Consolidado con TODO el tráfico capturado
│   └── hash_captura_global.txt          # SHA-256 del pcap consolidado
└── sniff_detection/
    └── log.txt                           # Hallazgos del detector anti-sniffer
```

- Cada `.txt` contiene un resumen (`pkt.summary()`) por paquete, legible sin abrir Wireshark.
- El hash `SHA-256` del pcap global sirve como **prueba de integridad** para un informe:
  si alguien modifica el pcap después, el hash ya no coincidirá.
- Solo se generan carpetas/archivos de los protocolos que efectivamente tuvieron tráfico.
- `logs/venom_engine.log` **no es evidencia de red** — es el log de funcionamiento del
  propio programa (arranque, envenenamiento ARP iniciado/detenido, cambios de iptables,
  errores). Útil para diagnosticar una sesión después de que terminó, sin haber tenido que
  ver la terminal en vivo. Ver [sección 11.1](#111-log-de-funcionamiento-del-motor).

### 11.1. Log de funcionamiento del motor

Además de la evidencia de red, VENOM-ROUTE registra su propio ciclo de vida en:

```
code/logs/venom_engine.log
```

Este log incluye, con timestamp y nivel de severidad (`INFO`, `WARNING`, `ERROR`):
- Arranque del programa y parámetros usados (víctima, gateway, interfaz).
- Inicio y fin del envenenamiento ARP.
- Cambios de reglas de `iptables` (FORWARD, MASQUERADE) y su restauración.
- Fallos de conectividad, errores de escaneo ARP, errores generando hashes.
- Detecciones del módulo anti-sniffer.
- Interrupciones (Ctrl+C) y confirmación de limpieza completa.

Ejemplo de contenido:
```
2026-08-27 10:15:02 [INFO] venom_route - VENOM-ROUTE iniciado.
2026-08-27 10:15:10 [INFO] venom_route - Inicializando entorno: victima=192.168.1.10 gateway=192.168.1.1 interfaz=eth0
2026-08-27 10:15:12 [INFO] arp_utils - Envenenamiento ARP iniciado contra la víctima.
2026-08-27 10:20:44 [WARNING] venom_route - Interrupción (SIGINT) recibida. Iniciando limpieza...
2026-08-27 10:20:47 [INFO] venom_route - Ataque detenido y limpieza completada.
```

El archivo rota automáticamente al llegar a 5 MB (se conservan hasta 3 respaldos:
`venom_engine.log.1`, `.2`, `.3`), por lo que no crece indefinidamente en sesiones largas.
Este log **no se imprime en consola** — es independiente de la interfaz visual con colores
que ya ves al ejecutar la herramienta, para no duplicar ni ensuciar esa salida.

```bash
# Ver el log en tiempo real mientras VENOM-ROUTE está corriendo
tail -f code/logs/venom_engine.log

# Ver solo errores de una sesión
grep "ERROR" code/logs/venom_engine.log
```

---

## 12. Detección de sniffers (anti-sniff)

Con `-A` (avanzado) o respondiendo "sí" en modo interactivo, se activa
`anti_sniff_detector.py`, que:

1. Envía un ARP request falso hacia una IP inexistente (`6.6.6.6`) en la red.
2. Escucha (5s) si alguien responde con ARP reply para esa IP.
3. Un host normal **nunca** debería responder por una IP que no es la suya — si lo hace,
   probablemente tiene su interfaz en modo promiscuo (sniffing).
4. Cualquier IP/MAC sospechosa se registra en `sniff_detection/log.txt` con timestamp.
5. El ciclo se repite cada ~10 segundos mientras el módulo esté activo.

Esto es útil para saber si, mientras haces tu propia auditoría, **otra persona en la red
también está capturando tráfico** (competencia, atacante real, o simplemente otro admin).

---

## 13. Detener el ataque y restauración

Presiona `Ctrl+C` en cualquier momento. El `signal_handler` ejecuta, **en este orden**:

1. Señaliza `stop_attack` → detiene los hilos de ARP spoofing y espera (`join`) a que terminen.
2. `restore_arp()` — restaura las tablas ARP reales de víctima y gateway (10 reintentos).
3. `restaurar_forwarding()` — desactiva `ip_forward` en el kernel.
4. Si se activó `-F`: `restaurar_iptables_forward()` → política FORWARD vuelve a `DROP`.
5. Si se activó `-M`: `restaurar_masquerade_rule()` → elimina la regla NAT MASQUERADE.
6. Detiene el sniffer y **guarda toda la evidencia capturada hasta ese momento**.
7. Espera a que el hilo del sniffer finalice antes de salir.

> **Nunca mates el proceso con `kill -9`** — eso salta todo el proceso de limpieza y deja
> las tablas ARP de la red envenenadas y las reglas de iptables mal configuradas. Siempre
> usa `Ctrl+C` y espera a que el programa confirme:
> `[✔] Ataque detenido y limpieza completada.`

---

## 14. Analizar la evidencia capturada

```bash
# Ver resumen de paquetes DNS capturados
cat code/logs/dns/DNS_20260827_141530.txt

# Abrir el pcap consolidado en Wireshark
wireshark code/archivos_unicos/captura_total_20260827_141530.pcap

# Verificar integridad del pcap global
sha256sum code/archivos_unicos/captura_total_20260827_141530.pcap
cat code/archivos_unicos/hash_captura_global.txt
# Deben coincidir

# Revisar si se detectaron sniffers en la red
cat code/sniff_detection/log.txt
```

---

## 15. Casos de uso típicos

### A. Auditoría de credenciales en texto plano
```bash
sudo python3 venom_route.py 192.168.1.15 192.168.1.1 eth0 -F -M
```
Deja correr mientras el objetivo usa servicios legacy (FTP/Telnet/HTTP sin TLS) y revisa
`logs/ftp/`, `logs/telnet/`, `logs/http/` al finalizar.

### B. Verificar filtrado de DNS / resolución sospechosa
```bash
sudo python3 venom_route.py 192.168.1.15 192.168.1.1 eth0 -F -M
```
Analiza `logs/dns/*.txt` para ver a qué dominios resuelve el objetivo.

### C. Detectar si hay un sniffer no autorizado en la red
```bash
sudo python3 venom_route.py -I
# Responder "sí" a la pregunta de detección de sniffers
```

### D. Auditoría exploratoria sin conocer la red
```bash
sudo python3 venom_route.py -I
```
Ideal para la primera visita a una red autorizada: descubre interfaces, dispositivos, y
te deja elegir víctima/gateway de forma guiada.

---

## 16. Solución de problemas

| Problema | Causa probable | Solución |
|---|---|---|
| `[✘] Este script debe ejecutarse como root.` | No usaste `sudo` | Ejecutar con `sudo python3 venom_route.py ...` |
| `[✘] No hay respuesta de <ip>` | Víctima/gateway no responde a ping o está fuera de línea | Verificar IP correcta y que el host esté encendido; algunos hosts bloquean ICMP (revisar firewall del objetivo) |
| `arp-scan no está instalado` | Falta la dependencia del sistema | `sudo apt install arp-scan` |
| No se generan `.pcap`/`.txt` | No hubo tráfico de ese protocolo durante la captura, o se interrumpió antes de tiempo | Esperar más tiempo con el ataque activo antes de detener |
| La víctima pierde internet durante el ataque | No se activó `-F`/`-M` | Reejecutar con `-F -M` para mantener el reenvío y NAT |
| ARP no se restaura bien al salir | Se mató el proceso con `kill -9` en vez de `Ctrl+C` | Restaurar manualmente: repetir `arp -d <ip>` en los hosts afectados, o forzar ARP correcto manualmente |
| `ModuleNotFoundError: scapy` / `netifaces` | Dependencias no instaladas | `pip install scapy netifaces` |

---

## 17. Buenas prácticas y seguridad operacional

- **Nunca** ejecutar contra redes sin autorización explícita y por escrito.
- Usar siempre `-F -M` en auditorías reales para no cortar la conectividad del objetivo
  y evitar levantar sospechas innecesarias.
- Documentar cada sesión: guarda los `.pcap`, `.txt` y hashes junto con fecha/hora y
  alcance autorizado — son tu evidencia para el informe.
- Verificar el hash `SHA-256` del pcap global antes de presentarlo como evidencia.
- Detener siempre con `Ctrl+C` y esperar la confirmación de limpieza completa.
- No modificar la estructura de carpetas (`logs/`, `archivos_unicos/`, `sniff_detection/`)
  manualmente durante una ejecución — otros procesos internos dependen de esas rutas.
- Limitar el acceso al equipo donde corre Venom-Route (requiere root, así que cualquiera
  con acceso a esa cuenta puede repetir el ataque).

---

## 18. Aviso legal

Venom-Route está diseñado **exclusivamente con fines educativos, de investigación y de
auditoría de seguridad en entornos controlados con permiso explícito**.

El uso no autorizado de esta herramienta contra redes o sistemas de terceros es **ilegal**
en la mayoría de jurisdicciones y puede acarrear consecuencias legales civiles y penales.
El autor no asume responsabilidad alguna por el uso indebido de esta herramienta.

**Úsalo solo en tu propia red, en laboratorios controlados, o con autorización explícita
y documentada del propietario de la red objetivo.**
