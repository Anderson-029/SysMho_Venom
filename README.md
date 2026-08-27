# VENOM-ROUTE

> Herramienta CLI de auditoría de redes LAN mediante ataques MITM (Man-in-the-Middle) usando ARP spoofing.
> 
> Motor Python puro: captura de tráfico clasificada por protocolo, detección pasiva de sniffers, logging de funcionamiento y gestión automática de iptables.

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![License](https://img.shields.io/badge/License-Educational%20Use%20Only-red)

---

## ¿Qué es Venom-Route?

**Venom-Route** es una herramienta de auditoría diseñada para redes LAN autorizadas. Se posiciona lógicamente entre una víctima y su gateway mediante ARP spoofing, permitiendo:

- ✅ Interceptar y clasificar tráfico de red por protocolo (DNS, HTTP, FTP, SMTP, etc.)
- ✅ Capturar evidencia forense (.pcap, .txt) con verificación de integridad (SHA-256)
- ✅ Detectar de forma pasiva hosts en modo promiscuo (sniffers activos en la red)
- ✅ Redirigir tráfico de forma controlada mediante reglas de iptables (NAT/MASQUERADE)
- ✅ Registrar el ciclo de vida completo del motor (arranque, ataque, limpieza)
- ✅ Generar evidencia auditable para informes de seguridad

**Toda la evidencia se guarda como archivos locales** — sin base de datos ni dependencias externas de persistencia.

---

## Requisitos Previos

### Sistema
- **Linux** (Debian/Ubuntu/Kali probado)
- **Privilegios root** (`sudo`) — obligatorio
- Acceso físico o lógico a la red LAN objetivo (mismo segmento que víctima y gateway)

### Software
```bash
# Python 3.12+
sudo apt install python3 python3-pip

# Herramienta de escaneo ARP (para modo interactivo)
sudo apt install arp-scan

# Dependencias Python
pip install scapy netifaces
```

### Autorización
**Requiere permiso explícito por escrito.** El uso no autorizado contra redes de terceros es ilegal en la mayoría de jurisdicciones.

---

## Instalación

```bash
git clone <repo> SysMho_Venom
cd SysMho_Venom
pip install scapy netifaces
sudo apt install arp-scan
```

---

## Uso Rápido

### Modo Interactivo (Recomendado para principiantes)
```bash
sudo python3 code/venom_route.py -I
```
El programa detectará interfaces, escaneará la red y te permitirá elegir víctima/gateway de forma guiada.

### Modo Avanzado (Scripts/Automatización)
```bash
# Ataque básico
sudo python3 code/venom_route.py 192.168.1.10 192.168.1.1 eth0

# Con reenvío IP + NAT (mantiene conectividad de la víctima)
sudo python3 code/venom_route.py 192.168.1.10 192.168.1.1 eth0 -F -M

# Con detección de sniffers
sudo python3 code/venom_route.py 192.168.1.10 192.168.1.1 eth0 -F -M -A
```

### Limpiar Evidencia Capturada
```bash
sudo python3 code/limpiar_logs.py
```
Borra todo el contenido de `logs/`, `archivos_unicos/` y `sniff_detection/` (sin tocar la estructura de carpetas).

---

## Evidencia Generada

Después de cada sesión, se generan:

```
code/
├── logs/
│   ├── dns/DNS_<timestamp>.pcap + .txt
│   ├── http/HTTP_<timestamp>.pcap + .txt
│   ├── arp/ARP_<timestamp>.pcap + .txt
│   ├── tcp/, udp/, icmp/, ... (otros protocolos capturados)
│   └── venom_engine.log          ← Log de funcionamiento del motor
├── archivos_unicos/
│   ├── captura_total_<timestamp>.pcap   ← Consolidado (fuente de verdad)
│   └── hash_captura_global.txt          ← SHA-256 del pcap
└── sniff_detection/
    └── log.txt                          ← Sniffers detectados
```

- **venom_engine.log**: registro completo del ciclo de vida (arranque, envenenamiento ARP, cambios de iptables, errores, limpieza)
- **captura_total_*.pcap**: todos los paquetes sin filtrar (evidencia íntegra)
- **hash_captura_global.txt**: SHA-256 verificable para auditorías

---

## Documentación

- **[MANUAL.md](MANUAL.md)** — Guía completa (18 secciones): cómo funciona, modos de ejecución, análisis de evidencia, troubleshooting
- **[CLAUDE.md](CLAUDE.md)** — Instrucciones de desarrollo: 4 pilares obligatorios (coherencia, congruencia, estabilidad, funcionalidad), regla de oro
- **[code/AGENTS.md](code/AGENTS.md)** — Responsabilidades de cada módulo
- **[.claude/rules/venom_python.md](.claude/rules/venom_python.md)** — Estándares PEP8 y patrones del proyecto

---

## Arquitectura

| Módulo | Responsabilidad |
|--------|-----------------|
| `venom_route.py` | Orquestación CLI, manejo de SIGINT, flujo principal |
| `arp_utils.py` | ARP spoofing bidireccional + restauración |
| `iptables_utils.py` | IP forwarding, FORWARD policy, MASQUERADE (NAT) |
| `network_utils.py` | Detección de interfaces, escaneo ARP, validación de conectividad |
| `sniffer_engine.py` | Captura, clasificación y guardado de tráfico por protocolo |
| `anti_sniff_detector.py` | Detección pasiva de sniffers en modo promiscuo |
| `sniffer_utils.py` | Hash SHA-256, filtro de dominios DNS |
| `ui_utils.py` | Banner, colores, prompts interactivos, validación de root |
| `venom_logger.py` | Log centralizado de funcionamiento (singleton pattern) |
| `limpiar_logs.py` | Utilidad de mantenimiento |

---

## Casos de Uso Típicos

### 1. Auditar credenciales en texto plano
```bash
sudo python3 code/venom_route.py 192.168.1.15 192.168.1.1 eth0 -F -M
```
Deja capturando mientras el objetivo usa FTP/Telnet/HTTP sin TLS. Revisa `logs/ftp/`, `logs/telnet/`, `logs/http/` después.

### 2. Verificar resolución de DNS sospechosa
```bash
sudo python3 code/venom_route.py -I
```
Analiza `logs/dns/*.txt` para ver a qué dominios resuelve el objetivo.

### 3. Detectar sniffers no autorizados en la red
```bash
sudo python3 code/venom_route.py -I
# Responder "sí" a la pregunta de detección de sniffers
```

### 4. Generar evidencia auditable para un informe
Todos los .pcap se acompañan de hash SHA-256 verificable (`hash_captura_global.txt`).

---

## Análisis de Evidencia

```bash
# Ver resumen de paquetes capturados
cat code/logs/dns/DNS_20260827_091326.txt

# Abrir pcap en Wireshark
wireshark code/archivos_unicos/captura_total_20260827_091326.pcap

# Verificar integridad del pcap global
sha256sum code/archivos_unicos/captura_total_20260827_091326.pcap
cat code/archivos_unicos/hash_captura_global.txt
# Los hashes deben coincidir

# Ver sniffers detectados durante la sesión
cat code/sniff_detection/log.txt

# Ver log de funcionamiento del motor en tiempo real
tail -f code/logs/venom_engine.log
```

---

## Flujo de Ejecución

1. **Arranque**: validación de root, detección de interfaces, validación de conectividad
2. **Preparación**: activación de ip_forward, configuración de iptables (opcional)
3. **Envenenamiento ARP**: hilos bidireccionales víctima ↔ gateway
4. **Sniffing**: captura y clasificación de tráfico por protocolo (5s ciclos)
5. **Anti-sniffer (opcional)**: detección pasiva cada 10s
6. **Monitoreo**: bucle de espera hasta Ctrl+C
7. **Limpieza**: restauración de ARP, ip_forward, iptables; guardado de evidencia
8. **Finalización**: salida limpia

---

## Validación y Calidad

✅ **PEP8**: Línea máximo 79 caracteres  
✅ **Coherencia**: Código nuevo sigue patrones existentes  
✅ **Congruencia**: Documentación + código + comportamiento alineados  
✅ **Estabilidad**: Ejecución end-to-end sin fallos, cleanup perfecto  
✅ **Funcionalidad**: Captura real, logs precisos, evidencia auditable  

---

## Buenas Prácticas

- **Siempre** ejecutar con `-F -M` en auditorías reales (mantiene conectividad de la víctima)
- **Detener siempre con Ctrl+C**, nunca `kill -9` (salta la limpieza de ARP e iptables)
- **Documentar cada sesión**: guarda .pcap, .txt y hashes junto con fecha/hora y alcance
- **Verificar integridad**: compara hash SHA-256 antes de presentar evidencia
- **No modificar estructura de carpetas**: otros scripts internos dependen de `logs/`, `archivos_unicos/`, `sniff_detection/`

---

## Aviso Legal

**VENOM-ROUTE está diseñado exclusivamente con fines educativos, de investigación y de auditoría de seguridad en entornos controlados con permiso explícito.**

El uso no autorizado de esta herramienta contra redes o sistemas de terceros es **ilegal** y puede acarrear consecuencias legales civiles y penales.

**El autor no asume responsabilidad alguna por el uso indebido de esta herramienta.**

Úsalo solo en tu propia red, laboratorios, o con autorización explícita y documentada del propietario de la red objetivo.

---

## Estado del Proyecto

- ✅ Motor CLI funcional (ARP spoofing, sniffing, logging)
- ✅ Detección de sniffers operativa
- ✅ Logging centralizado con rotación
- ✅ Documentación completa (MANUAL.md, CLAUDE.md)
- ✅ Validación end-to-end en red real
- ✅ Todas las consignas de calidad confirmadas

---

## Autor

**SysMho** — Proyecto de auditoría de redes para laboratorio educativo.

Contacto: [anderson@...] (usar solo para redes autorizadas / educational purposes)

---

**Última actualización**: 27 Agosto 2026  
**Versión**: 1.0 — Production Ready
