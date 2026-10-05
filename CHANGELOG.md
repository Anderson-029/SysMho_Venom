# Changelog

Todos los cambios notables de Venom-Route se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto sigue [Versionado Semántico](https://semver.org/lang/es/).

## [Unreleased]

### Added
- `requirements.txt` declarando las dependencias de runtime (`scapy`, `netifaces`).
- Licencia **GPL-3.0** (archivo `LICENSE`), sección de licencia en el README y
  cabecera de licencia GPL-3.0 al inicio de los 10 módulos `.py`.
- `SECURITY.md` con la política de uso responsable y el reporte de vulnerabilidades.
- Tabla de contenidos en el README.
- Demo animado del banner (`img/venom-demo.gif`) en el README.

### Changed
- Documentación de integridad: aclarado que el hash SHA-256 corresponde
  únicamente al pcap consolidado global (`hash_captura_global.txt`); los pcap
  por protocolo no llevan `.sha256` individual.

### Fixed
- Limpieza y restauración de red ante **cualquier excepción** durante el ataque,
  no solo ante Ctrl+C (ARP, ip_forward, iptables); hilos de ARP como `daemon`.
- Sniffer: se espera al hilo de captura **antes** de guardar la evidencia, para
  no perder el último tramo de tráfico.
- Detector anti-sniffer: señal de parada (`threading.Event`) para una detención
  limpia, coherente con el resto de hilos del motor.

## [1.0.0] - 2026-08-27

Primera versión estable (production ready), validada en red real.

### Added
- Motor CLI de auditoría MITM mediante ARP spoofing, con **modo interactivo**
  (`-I`) y **modo avanzado** por argumentos posicionales (`IP_VIC IP_GW IFACE`).
- Sniffer con clasificación de tráfico por protocolo (DNS, HTTP, HTTPS/SNI, FTP,
  SMTP, Telnet, IRC, SMB, ARP, ICMP, TCP, UDP), guardando `.pcap` y `.txt` por
  protocolo.
- Captura consolidada global (`captura_total_<ts>.pcap`) con hash **SHA-256**
  (`hash_captura_global.txt`) como prueba de integridad.
- Detección pasiva de sniffers en modo promiscuo (`-A`).
- Gestión de `iptables`: IP forwarding, política FORWARD y MASQUERADE/NAT
  (`-F`, `-M`) para mantener la conectividad de la víctima.
- Logging centralizado del ciclo de vida del motor (`logs/venom_engine.log`,
  singleton con rotación de 5 MB × 3 respaldos).
- Restauración de red ante Ctrl+C (ARP, ip_forward, iptables).
- Utilidad de mantenimiento `limpiar_logs.py` para borrar la evidencia.
- Documentación de usuario: `README.md` y `MANUAL.md`.
