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
# Módulo       : sniffer_utils.py
# Descripción  : Funciones auxiliares para capturas en VENOM-ROUTE.
#
# Funcionalidad:
#   - Generación de hash SHA256 para archivos capturados (.pcap / .txt).
#   - Filtro de dominios basura en consultas DNS.
#
# Nota legal   : Esta herramienta está diseñada para pruebas controladas,
#                fines educativos o auditorías con consentimiento explícito.
# =============================================================================

import os
import hashlib
import venom_logger

log = venom_logger.get_logger()

# Genera el hash SHA256 de un archivo y lo guarda en un archivo .sha256

def generar_hash_sha256(archivo_entrada, archivo_salida_hash):
    try:
        with open(archivo_entrada, "rb") as f:
            contenido = f.read()
            sha256_hash = hashlib.sha256(contenido).hexdigest()

        with open(archivo_salida_hash, "w") as hash_file:
            basename = os.path.basename(archivo_entrada)
            hash_file.write(f"{sha256_hash}  {basename}\n")
    except Exception as e:
        log.exception("Error generando hash para %s.", archivo_entrada)
        print(f"[✘] Error generando hash para {archivo_entrada}: {e}")



# Filtro básico para descartar dominios técnicos o irrelevantes

def es_dominio_valido(dominio):
    filtros_basura = (
        ".in-addr.arpa", ".ip6.arpa", ".local",
        ".lan", ".home", ".arpa", "localdomain"
    )
    return dominio and not dominio.endswith(filtros_basura)
