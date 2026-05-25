# =============================================================================
# Autor        : (SysMho)
# Módulo       : ui_utils.py
# Descripción  : Componentes visuales para la experiencia del usuario en CLI.
#
# Funcionalidad:
#   - Imprime banners, menús y mensajes con estilo y color.
#   - Proporciona elementos visuales como barras de carga y animaciones.
#   - Incluye herramientas para validación de permisos y respuestas interactivas.
#
# Nota legal     : Esta herramienta está diseñada para pruebas controladas,
#                  fines educativos o auditorías con consentimiento explícito.
# =============================================================================


import time                  # Control de tiempos de espera, retardos y temporización general.
import datetime              # Registro de fechas y horas para logs, archivos y auditorías.
import threading             # Soporte para ejecución en segundo plano y procesos concurrentes.
import os                    # Gestión de archivos, directorios y rutas dentro del sistema.
import sys                   # Acceso a argumentos del sistema, flujo de salida y control de errores.

# Colores de terminal
BOLD_RED   = '\033[1;31m'
BOLD_GREEN = '\033[1;32m'
YELLOW     = '\033[1;33m'
GREY       = '\033[0;90m'
NC         = '\033[0m'


# Verifica que el script se ejecute con privilegios de root.

def check_root():
    if os.geteuid() != 0:
        print(f"{BOLD_RED}[✘] Este script debe ejecutarse como root.{NC}")
        sys.exit(1)


# Muestra una barra de carga animada en terminal.

def loading_bar(mensaje, confirmacion):
    print(f"[*] {mensaje}: ", end='')
    bar = ''
    total = 20
    for i in range(1, total + 1):
        bar += '#'
        percent = int(i * 100 / total)
        print(f"\r[*] {mensaje}: [{bar:<20}] {percent}%", end='')
        time.sleep(0.04)
    print()
    print(f"{BOLD_GREEN}[✓] {confirmacion}.{NC}")
    time.sleep(0.5)


# Prompt interactivo de tipo sí/no.

def preguntar(pregunta):
    while True:
        resp = input(f"{YELLOW}{pregunta} (y/n): {NC}").strip().lower()
        if resp in ['y', 'n']:
            return resp == 'y'


# Anima un spinner que espera ENTER para continuar.

def spinner_presiona_enter():
    stop_event = threading.Event()

    def animacion():
        while not stop_event.is_set():
            for puntos in [".", "..", "...", "....", "    "]:
                if stop_event.is_set():
                    break
                print(f"\r{YELLOW}[→] Presiona ENTER para comenzar el ataque{puntos}{NC}", end='')
                time.sleep(0.3)

    t = threading.Thread(target=animacion)
    t.start()
    try:
        input()
    except KeyboardInterrupt:
        pass
    stop_event.set()
    t.join()
    print()


# Imprime el banner principal con advertencias.

def mostrar_banner():
    print(f"{BOLD_GREEN}")
    print(r"""
██╗   ██╗███████╗███╗   ██╗ ██████╗ ███╗   ███╗      ██████╗  ██████╗ ██╗   ██╗████████╗███████╗
██║   ██║██╔════╝████╗  ██║██╔═══██╗████╗ ████║      ██╔══██╗██╔═══██╗██║   ██║╚══██╔══╝██╔════╝
██║   ██║█████╗  ██╔██╗ ██║██║   ██║██╔████╔██║█████╗██████╔╝██║   ██║██║   ██║   ██║   █████╗  
╚██╗ ██╔╝██╔══╝  ██║╚██╗██║██║   ██║██║╚██╔╝██║╚════╝██╔══██╗██║   ██║██║   ██║   ██║   ██╔══╝  
 ╚████╔╝ ███████╗██║ ╚████║╚██████╔╝██║ ╚═╝ ██║      ██║  ██║╚██████╔╝╚██████╔╝   ██║   ███████╗
  ╚═══╝  ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝      ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝
                                                                                         "Create By SysMho"
    """)
    time.sleep(1)
    print("=========================================================================================")
    print("||                              VENOM-ROUTE v1.0                                       ||")
    print("||        Herramienta ofensiva para auditoría de redes LAN mediante MITM               ||")
    print("||---------------------------------------------------------------------------------    ||")
    print("||    VENOM-ROUTE permite realizar ataques de envenenamiento ARP,                      ||")
    print("||                interceptar tráfico DNS, registrar paquetes en formato .pcap,        ||")
    print("||                detectar sniffers activos y redirigir tráfico mediante iptables.     ||")
    print("||                                                                                     ||")
    print("||  Diseñada para pruebas de seguridad controladas, investigacion y fines educativos.  ||")
    print("||                                                                                     ||")
    print(f"||   Ejecución: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                                                    ||")
    print("=========================================================================================")
    print(f"{NC}")
    print(f"{BOLD_RED}[⚠][⚠] ESTE SCRIPT SOLO DEBE USARSE EN ENTORNOS CONTROLADOS O CON PERMISO EXPLÍCITO.[⚠][⚠]")
    print("[⚠][⚠]       USARLO DE MANERA IRRESPONSABLE PUEDE TRAER CONSECUENCIAS LEGALES.      [⚠][⚠]")
    print(f"{NC}")
    spinner_presiona_enter()
