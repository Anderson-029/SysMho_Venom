#!/usr/bin/env python3

# ============================================================================
# Módulo        : sniffer_engine.py                                   
# Descripción   :   Motor de sniffing avanzado para VENOM-ROUTE.        
#                   Captura tráfico clave en múltiples protocolos y     
#                   lo clasifica para análisis de seguridad.            
#                                                                      
# Funcionalidad :
#   - Sniffing de protocolos clave (DNS, HTTP, FTP, etc)
#   - Filtrado inteligente y almacenamiento ordenado    
#   - Guardado en .pcap y .txt para auditorías          
#                                                                      
# Nota legal     : Esta herramienta está diseñada para pruebas controladas,
#                  fines educativos o auditorías con consentimiento explícito.
# =============================================================================

import os
import datetime
import threading
import hashlib
from scapy.all import sniff, wrpcap

# Configuracion.

INTERFACE = "eth0"
CAPTURE_DIR = "logs"
UNIQUE_DIR = "archivos_unicos"
CAPTURE_LIMIT = 0
PROTOCOL_DIRS = {
    "DNS": "dns",
    "HTTP": "http",
    "HTTPS": "https_sni",
    "FTP": "ftp",
    "SMTP": "smtp",
    "TELNET": "telnet",
    "IRC": "irc",
    "SMB": "smb",
    "ARP": "arp",
    "ICMP": "icmp",
    "TCP": "tcp",
    "UDP": "udp"
}
todos_los_paquetes = []  
paquetes_por_protocolo = {proto: [] for proto in PROTOCOL_DIRS}



# Variables de control para ejecución en hilos ← MODIFICACIÓN
detener_sniffer = threading.Event()
hilo_sniffer = None

# Crear las carpetas necesarias para cada protocolo.

def crear_directorios_logs():
    if not os.path.exists(CAPTURE_DIR):
        os.makedirs(CAPTURE_DIR)

    for carpeta in PROTOCOL_DIRS.values():
        ruta = os.path.join(CAPTURE_DIR, carpeta)
        if not os.path.exists(ruta):
            os.makedirs(ruta)

    # Crear carpeta para el pcap global y hash si no existe
    if not os.path.exists(UNIQUE_DIR):
        os.makedirs(UNIQUE_DIR)

# Filtra los paquetes capturados.

def guardar_paquete(pkt, nombre_proto):
    # Guardar en la lista correspondiente en memoria
    if nombre_proto in paquetes_por_protocolo:
        paquetes_por_protocolo[nombre_proto].append(pkt)

    # También agregamos al total global
    todos_los_paquetes.append(pkt)


# Funcion para detectar la clase de protocolo.

def procesar_paquete(pkt):
    if pkt.haslayer("DNS"):
        guardar_paquete(pkt, "DNS")
    elif pkt.haslayer("HTTP"):
        guardar_paquete(pkt, "HTTP")
    elif pkt.haslayer("TLS") and pkt.haslayer("IP"):
        guardar_paquete(pkt, "HTTPS")  # Captura SNI si es visible
    elif pkt.haslayer("FTP"):
        guardar_paquete(pkt, "FTP")
    elif pkt.haslayer("SMTP"):
        guardar_paquete(pkt, "SMTP")
    elif pkt.haslayer("Telnet"):
        guardar_paquete(pkt, "TELNET")
    elif pkt.haslayer("IRC"):
        guardar_paquete(pkt, "IRC")
    elif pkt.haslayer("NBNS") or pkt.haslayer("SMB"):
        guardar_paquete(pkt, "SMB")
    elif pkt.haslayer("ARP"):
        guardar_paquete(pkt, "ARP")
    elif pkt.haslayer("ICMP"):
        guardar_paquete(pkt, "ICMP")
    elif pkt.haslayer("TCP"):
        guardar_paquete(pkt, "TCP")
    elif pkt.haslayer("UDP"):
        guardar_paquete(pkt, "UDP")

# main para ejecución directa (modo prueba local)

def iniciar_sniffing():
    crear_directorios_logs()
    print("[✓] Sniffer activado. Capturando tráfico...")

    try:
        sniff(
            iface=INTERFACE,
            prn=procesar_paquete,
            store=False,
            count=CAPTURE_LIMIT
        )
    except KeyboardInterrupt:
        print("\n[✘] Sniffer detenido.")
        guardar_resultados_finales()



# Hilo que se ejecuta en segundo plano, verifica cada 5 segundos si debe detenerse

def _sniffer_loop(interfaz):
    while not detener_sniffer.is_set():
        sniff(
            iface=interfaz,
            prn=procesar_paquete,
            store=False,
            timeout=5
        )

# Función que será invocada por venom_route.py para iniciar el sniffer
def iniciar_captura_sniffer(interfaz):
    global hilo_sniffer
    crear_directorios_logs()
    print("[✓] Sniffer activado. Capturando tráfico...")

    hilo_sniffer = threading.Thread(target=_sniffer_loop, args=(interfaz,), daemon=True)
    hilo_sniffer.start()

    return (
        hilo_sniffer,
        os.path.join(CAPTURE_DIR, "captura_total", "captura_total.pcap"),
        os.path.join(CAPTURE_DIR, "dns", "capturas_dns.txt"),
        os.path.join(UNIQUE_DIR, "hash_captura_global.txt"),
        os.path.join(CAPTURE_DIR, "dns", "hash_captura_dns.txt")
    )

# Función para detener el sniffer.

def detener_captura_sniffer():
    detener_sniffer.set()
    guardar_resultados_finales()

    # Esperar que el hilo finalice
    if hilo_sniffer:
        hilo_sniffer.join()

# funcion para guardar al finalizar la ejecución.

def guardar_resultados_finales():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Guardar por protocolo
    for protocolo, lista_paquetes in paquetes_por_protocolo.items():
        if lista_paquetes:
            base_path = os.path.join(CAPTURE_DIR, PROTOCOL_DIRS[protocolo])

            pcap_path = os.path.join(base_path, f"{protocolo}_{timestamp}.pcap")
            wrpcap(pcap_path, lista_paquetes)

            txt_path = os.path.join(base_path, f"{protocolo}_{timestamp}.txt")
            with open(txt_path, "w") as f:
                for pkt in lista_paquetes:
                    f.write(str(pkt.summary()) + "\n")

    # Guardar .pcap global
    global_pcap = None
    if todos_los_paquetes:
        global_pcap = os.path.join(UNIQUE_DIR, f"captura_total_{timestamp}.pcap")
        wrpcap(global_pcap, todos_los_paquetes)

    # Hash del pcap global
    if global_pcap and os.path.isfile(global_pcap):
        sha256_hash = hashlib.sha256()
        with open(global_pcap, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        hash_output_path = os.path.join(UNIQUE_DIR, "hash_captura_global.txt")
        with open(hash_output_path, "w") as f:
            f.write(sha256_hash.hexdigest())

if __name__ == "__main__":
    iniciar_sniffing()
