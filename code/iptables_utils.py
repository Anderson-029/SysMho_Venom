# =============================================================================
# Autor        : (SysMho)
# Módulo       : iptables_utils.py
# Descripción  : Manejo de reglas iptables para enrutar tráfico durante el ataque.
#
# Funcionalidad:
#   - Habilita o desactiva el reenvío de paquetes (IP forwarding).
#   - Configura NAT mediante MASQUERADE para que el tráfico fluya sin interrupciones.
#   - Restaura las políticas de iptables y la red al finalizar la operación.
#
# Nota legal     : Esta herramienta está diseñada para pruebas controladas,
#                  fines educativos o auditorías con consentimiento explícito.
# =============================================================================




# iptables_utils.py

import subprocess
import time
import ui_utils
import network_utils
import venom_logger

log = venom_logger.get_logger()

def activar_forwarding():
    log.info("Activando ip_forward en el kernel.")
    print("[*] ADAPTANDO MAQUINA PARA INTERCEPTACION.")
    time.sleep(0.7)
    ui_utils.loading_bar("Configurando entorno", "Entorno adaptado para ataque")
    with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
        f.write('1')

def restaurar_forwarding():
    log.info("Restaurando ip_forward en el kernel (deshabilitado).")
    print("\n[*] RESTAURAR CONFIGURACION DE RED.")
    time.sleep(1)
    ui_utils.loading_bar("Restaurando red", "Red revertida a su estado normal")
    with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
        f.write('0')
    print(ui_utils.BOLD_GREEN + "[✔] Redireccionamiento desactivado correctamente." + ui_utils.NC)

def activar_iptables_forward():
    log.info("Aplicando iptables FORWARD ACCEPT.")
    print("[*] Configurando iptables para permitir el reenvío de paquetes.")
    subprocess.run(['iptables', '-P', 'FORWARD', 'ACCEPT'])
    ui_utils.loading_bar("Ajustando reglas iptables", "Redireccionamiento IP listo y activo")

def restaurar_iptables_forward():
    log.info("Restaurando iptables FORWARD a DROP.")
    print("[*] Restaurando iptables a configuración segura (DROP).")
    subprocess.run(['iptables', '-P', 'FORWARD', 'DROP'])
    ui_utils.loading_bar("Restaurando reglas iptables", "iptables FORWARD policy ahora en DROP")

def activar_masquerade_rule(interface):
    log.info("Aplicando regla MASQUERADE en interfaz %s.", interface)
    print("[*] Configurando iptables MASQUERADE para redirección NAT.")
    subprocess.run(['iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', network_utils.interface, '-j', 'MASQUERADE'])
    ui_utils.loading_bar("Aplicando regla MASQUERADE", "MASQUERADE NAT activo")

def restaurar_masquerade_rule(interface):
    log.info("Eliminando regla MASQUERADE en interfaz %s.", interface)
    print("[*] Restaurando reglas NAT (MASQUERADE).")
    subprocess.run(['iptables', '-t', 'nat', '-D', 'POSTROUTING', '-o', network_utils.interface, '-j', 'MASQUERADE'])
    ui_utils.loading_bar("Eliminando regla MASQUERADE", "MASQUERADE NAT eliminado")
