# =============================================================================
# Autor        : (SysMho)
# Módulo       : sniffer_utils.py
# Descripción  : Funciones auxiliares para procesamiento de capturas en VENOM-ROUTE.
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

# Genera el hash SHA256 de un archivo y lo guarda en un archivo .sha256

def generar_hash_sha256(archivo_entrada, archivo_salida_hash):
    try:
        with open(archivo_entrada, "rb") as f:
            contenido = f.read()
            sha256_hash = hashlib.sha256(contenido).hexdigest()

        with open(archivo_salida_hash, "w") as hash_file:
            hash_file.write(f"{sha256_hash}  {os.path.basename(archivo_entrada)}\n")
    except Exception as e:
        print(f"[✘] Error generando hash para {archivo_entrada}: {e}")



# Filtro básico para descartar dominios técnicos o irrelevantes

def es_dominio_valido(dominio):
    filtros_basura = (
        ".in-addr.arpa", ".ip6.arpa", ".local",
        ".lan", ".home", ".arpa", "localdomain"
    )
    return dominio and not dominio.endswith(filtros_basura)
