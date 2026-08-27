#!/usr/bin/env python3
# =============================================================================
# Autor        : (SysMho)
# Módulo       : venom_logger.py
# Descripción  : Log de funcionamiento interno de VENOM-ROUTE (no confundir
#                con la evidencia de red capturada en logs/<protocolo>/).
#                Este módulo registra el CICLO DE VIDA del propio programa:
#                arranque, ataques iniciados/detenidos, errores, cambios de
#                iptables, fallos de conectividad, etc. Sirve para poder
#                diagnosticar una sesión después de que terminó, sin haber
#                tenido que estar mirando la terminal en el momento exacto
#                en que ocurrió el problema.
#
# Funcionalidad:
#   - Expone get_logger() para que el resto de módulos obtengan siempre
#     la MISMA instancia de logger, ya configurada (patrón singleton).
#   - Escribe a code/logs/venom_engine.log en texto plano, con rotación
#     de tamaño para no crecer indefinidamente (5 MB x 3 respaldos).
#   - No imprime nada por consola: el logging de funcionamiento es
#     independiente de la interfaz visual (prints con colores) que ya
#     maneja ui_utils.py, para no duplicar ni ensuciar la salida del CLI.
#
# Nota legal   : Esta herramienta está diseñada para pruebas controladas,
#                fines educativos o auditorías con consentimiento explícito.
# =============================================================================

import logging
import os
from logging.handlers import RotatingFileHandler

# Se reutiliza la carpeta logs/ ya existente (ver sniffer_engine.py), pero
# con un archivo propio a nivel raíz para no mezclarse con las subcarpetas
# por protocolo (dns/, http/, etc.) que sniffer_engine.py ya administra.
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "venom_engine.log")

# Nombre único del logger para evitar colisiones con otros loggers que
# pudiera crear alguna librería de terceros (scapy, netifaces, etc.).
NOMBRE_LOGGER = "venom_route"

_logger = None  # Cache interno del logger ya configurado (singleton).


# Crea (una sola vez) y devuelve el logger configurado de VENOM-ROUTE.
# El resto de módulos deben llamar siempre a esta función en vez de
# instanciar logging.getLogger() por su cuenta, para garantizar que todos
# escriban al mismo archivo con el mismo formato.

def get_logger():
    global _logger

    if _logger is not None:
        return _logger

    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(NOMBRE_LOGGER)
    logger.setLevel(logging.DEBUG)

    # Handler con rotación: evita que el archivo crezca sin límite en
    # sesiones largas de captura.
    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    formato = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(module)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formato)

    # Evita agregar el mismo handler dos veces si get_logger() se llama
    # más de una vez dentro del mismo proceso.
    if not logger.handlers:
        logger.addHandler(handler)

    # No propagar al logger raíz: así no aparece nada por consola.
    logger.propagate = False

    _logger = logger
    return _logger
