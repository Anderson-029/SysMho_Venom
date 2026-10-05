#!/usr/bin/env python3
# Copyright (C) 2026 SysMho
#
# Este archivo es parte de Venom-Route.
# Venom-Route es software libre: puedes redistribuirlo y/o modificarlo bajo
# los términos de la GNU General Public License v3 (o, a tu elección, una
# versión posterior) publicada por la Free Software Foundation.
# Se distribuye SIN NINGUNA GARANTÍA. Consulta la GNU GPL para más
# detalles: <https://www.gnu.org/licenses/gpl-3.0.html>
# =============================================================================
# -*- coding: utf-8 -*-
# Autor          : (SysMho)
# Módulo         : anti_sniff_detector.py
# Descripción    : Detector de sniffers en modo promiscuo usando ARP.
#                  Parte del proyecto VENOM-ROUTE.
#
# Funcionalidad  :
#   - Detecta hosts escuchando tráfico sin autorización
#   - Envía ARP con IPs no asignadas y detecta respuestas
#   - Guarda resultados en logs de detección
#
# Nota legal     : Esta herramienta está diseñada para pruebas
#                  controladas, fines educativos o auditorías
#                  con consentimiento explícito.
# =============================================================================
import os
import time
import threading
import netifaces
from ui_utils import BOLD_GREEN, BOLD_RED, NC
from scapy.all import ARP, Ether, sendp, sniff, conf
import venom_logger

log = venom_logger.get_logger()

LOG_DIR = "sniff_detection"
LOG_FILE = f"{LOG_DIR}/log.txt"

# Crea la carpeta de logs si no existe
os.makedirs(LOG_DIR, exist_ok=True)

# Señal de parada del hilo (patrón obligatorio de AGENTS.md: todo hilo
# debe poder detenerse con un threading.Event, no solo confiar en
# daemon=True para morir junto con el proceso).
detener_deteccion = threading.Event()

# función para obtener tu IP y MAC

def obtener_mi_mac_ip(interface):
    direcciones = netifaces.ifaddresses(interface)
    ip_local = direcciones[netifaces.AF_INET][0]['addr']
    mac_local = direcciones[netifaces.AF_LINK][0]['addr']
    return ip_local, mac_local

# Crea un paquete ARP a una IP falsa para detectar sniffers.

def _crear_paquete_arp_fake(victim_ip, iface):
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp = ARP(pdst=victim_ip, psrc="1.2.3.4", op=1)
    paquete = ether / arp
    return paquete


# Escucha respuestas ARP por un tiempo específico.

def _capturar_respuestas(timeout=5, iface=None):
    return sniff(filter="arp and arp[6:2] == 2", timeout=timeout, iface=iface)


# Lógica de detección de sniffers.

def detectar_sniffers(interface):
    print(f"{BOLD_GREEN}[✓] Módulo anti-sniffer activo. Escaneando...{NC}")
    mi_ip, mi_mac = obtener_mi_mac_ip(interface)
    ya_mostrado = False
    while not detener_deteccion.is_set():
        fake_ip = "6.6.6.6"
        paquete = _crear_paquete_arp_fake(fake_ip, interface)

        sendp(paquete, iface=interface, verbose=False)
        respuestas = _capturar_respuestas(iface=interface)

        sospechosos = []

        for pkt in respuestas:
            if pkt.haslayer(ARP):
                mac = pkt[ARP].hwsrc
                ip = pkt[ARP].psrc

                if ip != mi_ip and mac.lower() != mi_mac.lower():
                    sospechosos.append((ip, mac))


        if sospechosos:
            log.warning("Sniffer(s) detectado(s): %s", sospechosos)
            print(f"\n{BOLD_GREEN}[!] ¡Sniffer detectado!{NC}")
            _guardar_log(sospechosos)
            ya_mostrado = False
        else:
            if not ya_mostrado:
                msg = "[✓] No se detectaron sniffers en esta pasada."
                print(f"\n{BOLD_RED}{msg}{NC}")
                ya_mostrado = True

        for _ in range(5):
            if detener_deteccion.is_set():
                break
            time.sleep(1)



# Guarda IPs/MACs sospechosas en el log.

def _guardar_log(lista):
    with open(LOG_FILE, "a") as f:
        for ip, mac in lista:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            line = f"[{timestamp}] Sospechoso - IP: {ip} - MAC: {mac}\n"
            f.write(line)

# Inicia el antisniffer con escaneo continuo. Devuelve el hilo para que
# quien lo lanzó pueda esperarlo tras llamar a detener_anti_sniffer().

def iniciar_anti_sniffer(interface):
    def loop_deteccion():
        time.sleep(0.7)
        log.info("Detector anti-sniffer iniciado en interfaz %s.", interface)
        print("[*] Iniciando escaneo antisniffer en segundo plano...")
        detectar_sniffers(interface)
        log.info("Detector anti-sniffer detenido.")

    hilo = threading.Thread(target=loop_deteccion, daemon=True)
    hilo.start()
    return hilo


# Señaliza al hilo del detector que debe detenerse (ver signal_handler
# en venom_route.py).

def detener_anti_sniffer():
    detener_deteccion.set()
