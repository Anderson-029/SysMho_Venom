# =============================================================================
# Autor        : (SysMho)
# Módulo       : network_utils.py
# Descripción  : Herramientas prácticas para tareas de red.
#
# Funcionalidad:
#   - Detecta las interfaces de red disponibles en el sistema.
#   - Escanea el entorno local para identificar dispositivos conectados.
#   - Determina IP, máscara de subred y genera identificadores únicos para archivos.
#
# Nota legal     : Esta herramienta está diseñada para pruebas controladas,
#                  fines educativos o auditorías con consentimiento explícito.
# =============================================================================



import subprocess
import sys
import ui_utils
import netifaces
import hashlib
import os
from scapy.all import ARP, Ether, srp
import venom_logger

log = venom_logger.get_logger()

# Variables globales compartidas entre módulos
interface = ""
ip_victima = ""
ip_gateway = ""


# Verifica conectividad con víctima y gateway usando ping.

def validar_conectividad(ip_victima, ip_gateway):
    for etiqueta, ip in [("víctima", ip_victima), ("gateway", ip_gateway)]:
        print(f"{ui_utils.YELLOW}[*] Verificando conectividad con la {etiqueta}:{ui_utils.NC}")
        try:
            resultado = subprocess.run(
                ['ping', '-c', '4', '-W', '0.7', ip],
                stdout=None,
                stderr=None
            )
            if resultado.returncode != 0:
                log.error("Sin respuesta de %s (%s).", ip, etiqueta)
                print(f"{ui_utils.BOLD_RED}[✘] No hay respuesta de {ip}.{ui_utils.NC}")
                sys.exit(1)
            else:
                log.info("Conectividad confirmada con %s (%s).", ip, etiqueta)
                print()
                print(f"{ui_utils.BOLD_GREEN}[✓] {ip} confirmando conectividad.{ui_utils.NC}")
                print()
        except Exception as e:
            log.exception("Error verificando conectividad con %s.", ip)
            print(f"{ui_utils.BOLD_RED}[✘] Error verificando {ip}: {e}{ui_utils.NC}")
            sys.exit(1)


# Realiza escaneo ARP para descubrir dispositivos en la red y permite al usuario seleccionar víctima y gateway.

def escaneo_red(rango_red):
    print()
    print(f"{ui_utils.YELLOW}[*] Escaneando red {rango_red} en la interfaz {interface}...{ui_utils.NC}")
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
            print(f"{ui_utils.BOLD_RED}[✘] No se detectaron dispositivos. Verifica la interfaz y el rango.{ui_utils.NC}")
            sys.exit(1)

        print(f"{ui_utils.YELLOW}[*] Dispositivos encontrados:{ui_utils.NC}")
        for i, (ip, mac, vendor) in enumerate(dispositivos, start=1):
            print(f"[{i}] {ip} → {vendor} → {mac}")

        print()
        idx_victima = int(input(f"{ui_utils.YELLOW}[→] Selecciona el número de la VÍCTIMA: {ui_utils.NC}")) - 1
        idx_gateway = int(input(f"{ui_utils.YELLOW}[→] Selecciona el número del GATEWAY: {ui_utils.NC}")) - 1

        global ip_victima, ip_gateway
        ip_victima = dispositivos[idx_victima][0]
        ip_gateway = dispositivos[idx_gateway][0]

        print()
        print(f"{ui_utils.YELLOW}[*] Interfaz seleccionada: {interface}{ui_utils.NC}")
        print(f"{ui_utils.BOLD_GREEN}[✓] Víctima elegida: {ip_victima}{ui_utils.NC}")
        print(f"{ui_utils.BOLD_GREEN}[✓] Gateway elegido: {ip_gateway}{ui_utils.NC}")
        print()
        log.info(
            "Escaneo de red completado. victima=%s gateway=%s "
            "interfaz=%s", ip_victima, ip_gateway, interface,
        )

    except FileNotFoundError:
        log.error("arp-scan no está instalado en el sistema.")
        print(f"{ui_utils.BOLD_RED}[✘] Error: arp-scan no está instalado. Instálalo con 'sudo apt install arp-scan'.{ui_utils.NC}")
        sys.exit(1)
    except Exception as e:
        log.exception("Error durante el escaneo de red.")
        print(f"{ui_utils.BOLD_RED}[✘] Error durante escaneo: {e}{ui_utils.NC}")
        sys.exit(1)


# Detecta interfaces locales con IP configurada y devuelve lista de (interfaz, red_cidr)

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
                        bits = sum([bin(int(x)).count('1') for x in netmask.split('.')])
                        red = '.'.join(ip.split('.')[:-1]) + '.0'
                        cidr = f"{red}/{bits}"
                        redes_disponibles.append((iface, cidr))
        except Exception:
            pass

    return redes_disponibles


# Genera los hash de loa archivos .pcap y .txt

def generar_hash_sha256(ruta_archivo):
    try:
        sha256 = hashlib.sha256()
        with open(ruta_archivo, 'rb') as f:
            for bloque in iter(lambda: f.read(4096), b""):
                sha256.update(bloque)

        carpeta_hash = "hash"
        os.makedirs(carpeta_hash, exist_ok=True)

        nombre = os.path.basename(ruta_archivo)
        ruta_salida = os.path.join(carpeta_hash, f"{nombre}.sha256")

        with open(ruta_salida, 'w') as out:
            out.write(f"{sha256.hexdigest()}  {nombre}\n")

    except Exception as e:
        log.exception("Error generando hash de %s.", ruta_archivo)
        print(f"[!] Error generando hash de {ruta_archivo}: {e}")