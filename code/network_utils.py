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
# Módulo       : network_utils.py
# Descripción  : Herramientas prácticas para tareas de red.
#
# Funcionalidad:
#   - Detecta las interfaces de red disponibles en el sistema.
#   - Escanea el entorno local para identificar dispositivos conectados.
#   - Determina IP, máscara de subred
#
# Nota legal     : Esta herramienta está diseñada para pruebas
#                  controladas, fines educativos o auditorías
#                  con consentimiento explícito.
# =============================================================================



import subprocess
import sys
import ui_utils
import netifaces
import venom_logger

log = venom_logger.get_logger()

# Variables globales compartidas entre módulos
interface = ""
ip_victima = ""
ip_gateway = ""


# Verifica conectividad con víctima y gateway usando ping.

def validar_conectividad(ip_victima, ip_gateway):
    for etiqueta, ip in [("víctima", ip_victima), ("gateway", ip_gateway)]:
        msg = f"[*] Verificando conectividad con la {etiqueta}:"
        print(f"{ui_utils.YELLOW}{msg}{ui_utils.NC}")
        try:
            resultado = subprocess.run(
                ['ping', '-c', '4', '-W', '0.7', ip],
                stdout=None,
                stderr=None
            )
            if resultado.returncode != 0:
                log.error("Sin respuesta de %s (%s).", ip, etiqueta)
                msg = f"[✘] No hay respuesta de {ip}."
                print(f"{ui_utils.BOLD_RED}{msg}{ui_utils.NC}")
                sys.exit(1)
            else:
                log.info("Conectividad confirmada con %s (%s).", ip, etiqueta)
                print()
                msg = f"[✓] {ip} confirmando conectividad."
                print(f"{ui_utils.BOLD_GREEN}{msg}{ui_utils.NC}")
                print()
        except Exception as e:
            log.exception("Error verificando conectividad con %s.", ip)
            msg = f"[✘] Error verificando {ip}: {e}"
            print(f"{ui_utils.BOLD_RED}{msg}{ui_utils.NC}")
            sys.exit(1)


# Escaneo ARP para descubrir dispositivos en la red

def escaneo_red(rango_red):
    print()
    msg = f"[*] Escaneando red {rango_red} en interfaz {interface}..."
    print(f"{ui_utils.YELLOW}{msg}{ui_utils.NC}")
    print()

    try:
        resultado = subprocess.run(
            ['arp-scan', '--interface', interface, rango_red],
            capture_output=True,
            text=True
        )
        lineas = resultado.stdout.strip().split("\n")
        dispositivos = []
        contador = 1

        for linea in lineas:
            partes = linea.split()
            if len(partes) >= 3 and ":" in partes[1]:
                ip = partes[0]
                mac = partes[1]
                vendor = " ".join(partes[2:])
                dispositivos.append((ip, mac, vendor))

        if not dispositivos:
            log.warning(
                "Escaneo ARP sin resultados en %s (%s).",
                rango_red, interface,
            )
            msg = "[✘] No se detectaron dispositivos. Verifica"
            msg += " la interfaz y el rango."
            print(f"{ui_utils.BOLD_RED}{msg}{ui_utils.NC}")
            sys.exit(1)

        print(f"{ui_utils.YELLOW}[*] Dispositivos encontrados:{ui_utils.NC}")
        for i, (ip, mac, vendor) in enumerate(dispositivos, start=1):
            print(f"[{i}] {ip} → {vendor} → {mac}")

        print()
        prompt = f"{ui_utils.YELLOW}[→] Selecciona VÍCTIMA: "
        prompt += f"{ui_utils.NC}"
        idx_victima = int(input(prompt)) - 1
        prompt = f"{ui_utils.YELLOW}[→] Selecciona GATEWAY: "
        prompt += f"{ui_utils.NC}"
        idx_gateway = int(input(prompt)) - 1

        global ip_victima, ip_gateway
        ip_victima = dispositivos[idx_victima][0]
        ip_gateway = dispositivos[idx_gateway][0]

        print()
        msg = f"[*] Interfaz: {interface}"
        print(f"{ui_utils.YELLOW}{msg}{ui_utils.NC}")
        msg = f"[✓] Víctima: {ip_victima}"
        print(f"{ui_utils.BOLD_GREEN}{msg}{ui_utils.NC}")
        msg = f"[✓] Gateway: {ip_gateway}"
        print(f"{ui_utils.BOLD_GREEN}{msg}{ui_utils.NC}")
        print()
        log.info(
            "Escaneo de red completado. victima=%s gateway=%s "
            "interfaz=%s", ip_victima, ip_gateway, interface,
        )

    except FileNotFoundError:
        log.error("arp-scan no está instalado en el sistema.")
        msg = "[✘] Error: arp-scan no está instalado."
        msg += " Instálalo con 'sudo apt install arp-scan'."
        print(f"{ui_utils.BOLD_RED}{msg}{ui_utils.NC}")
        sys.exit(1)
    except Exception as e:
        log.exception("Error durante el escaneo de red.")
        msg = f"[✘] Error durante escaneo: {e}"
        print(f"{ui_utils.BOLD_RED}{msg}{ui_utils.NC}")
        sys.exit(1)


# Detecta interfaces locales con IP configurada

def detectar_redes_disponibles():
    redes_disponibles = []

    for iface in netifaces.interfaces():
        try:
            datos = netifaces.ifaddresses(iface)
            ipv4 = datos.get(netifaces.AF_INET)
            if ipv4:
                for conf in ipv4:
                    ip = conf.get('addr')
                    netmask = conf.get('netmask')
                    if ip and netmask:
                        octetos = netmask.split('.')
                        bits = sum([bin(int(x)).count('1')
                                   for x in octetos])
                        red = '.'.join(ip.split('.')[:-1]) + '.0'
                        cidr = f"{red}/{bits}"
                        redes_disponibles.append((iface, cidr))
        except Exception:
            pass

    return redes_disponibles