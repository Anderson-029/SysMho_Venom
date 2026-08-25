#!/usr/bin/env python3
# =============================================================================
# -*- coding: utf-8 -*-
# Autor          : (SysMho)
# Módulo         : anti_sniff_detector.py
# Descripción    : Detector simple de sniffers en modo promiscuo usando método ARP clásico.
#                  Este módulo forma parte del proyecto VENOM-ROUTE.
#
# Funcionalidad  :
#                - Detecta si hay hosts en la red escuchando tráfico que no les corresponde.
#                - Utiliza paquetes ARP con IPs no asignadas y revisa respuestas sospechosas.
#                - Guarda los resultados en logs en caso de detección.
#
# Nota legal     : Esta herramienta está diseñada para pruebas controladas,
#                  fines educativos o auditorías con consentimiento explícito.
# =============================================================================
import os
import time
import logging
import threading
import netifaces
from ui_utils import BOLD_GREEN, BOLD_RED, NC
from scapy.all import ARP, Ether, sendp, sniff, conf

LOG_DIR = "sniff_detection"
LOG_FILE = f"{LOG_DIR}/log.txt"

# Crea la carpeta de logs si no existe
os.makedirs(LOG_DIR, exist_ok=True)

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
    while True:
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
            print(f"\n{BOLD_GREEN}[!] ¡Sniffer detectado!{NC}")
            _guardar_log(sospechosos)
        else:
            if not ya_mostrado:
                print(f"\n{BOLD_RED}[✓] No se detectaron sniffers en esta pasada.{NC}")

        for _ in range(5):
            time.sleep(1)



# Guarda IPs/MACs sospechosas en el log.

def _guardar_log(lista):
    with open(LOG_FILE, "a") as f:
        for ip, mac in lista:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sospechoso - IP: {ip} - MAC: {mac}\n")

# Inicia el antisniffer

# Inicia el antisniffer con escaneo continuo

def iniciar_anti_sniffer(interface):
    def loop_deteccion():
        time.sleep(0.7)
        print("[*] Iniciando escaneo antisniffer en segundo plano...")
        while True:
            detectar_sniffers(interface)
            time.sleep(10)
    hilo = threading.Thread(target=loop_deteccion)
    hilo.daemon = True
    hilo.start()
