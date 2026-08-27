#!/usr/bin/env python3
# =============================================================================
# Autor        : (SysMho)
# Módulo       : limpiar_logs.py
# Descripción  : Utilidad de mantenimiento para VENOM-ROUTE. Borra todo el
#                contenido de las carpetas de evidencia (logs/,
#                archivos_unicos/ y sniff_detection/) dejándolas vacías,
#                sin eliminar la estructura de subcarpetas que el resto
#                de módulos espera encontrar (ver AGENTS.md: "no cambiar
#                la estructura de directorios de salida sin avisar al
#                usuario").
#
# Funcionalidad:
#   - Recorre cada carpeta de evidencia y borra únicamente los archivos
#     que contiene (pcap, txt, sha256, log.txt), preservando las carpetas.
#   - Pide confirmación explícita antes de borrar nada (irreversible).
#   - Reporta cuántos archivos fueron eliminados por carpeta.
#
# Nota legal   : Esta herramienta está diseñada para pruebas controladas,
#                fines educativos o auditorías con consentimiento explícito.
# =============================================================================

import os
import sys
import ui_utils

# Carpetas de evidencia generadas por el motor (ver sniffer_engine.py y
# anti_sniff_detector.py). Se listan aquí de forma centralizada para no
# duplicar rutas mágicas repartidas en varios módulos.
CARPETAS_EVIDENCIA = [
    "logs",
    "archivos_unicos",
    "sniff_detection",
]


# Recorre una carpeta y borra solo los archivos que contiene, conservando
# la carpeta y todas sus subcarpetas intactas (para que sniffer_engine.py
# y anti_sniff_detector.py sigan encontrando la estructura esperada).

def limpiar_carpeta(ruta_carpeta):
    archivos_borrados = 0

    if not os.path.isdir(ruta_carpeta):
        return archivos_borrados

    for raiz, _subcarpetas, archivos in os.walk(ruta_carpeta):
        for nombre_archivo in archivos:
            ruta_archivo = os.path.join(raiz, nombre_archivo)
            try:
                os.remove(ruta_archivo)
                archivos_borrados += 1
            except OSError as e:
                print(
                    f"{ui_utils.BOLD_RED}[✘] No se pudo borrar "
                    f"{ruta_archivo}: {e}{ui_utils.NC}"
                )

    return archivos_borrados


# Punto de entrada: pide confirmación y limpia cada carpeta de evidencia.

def main():
    print(
        f"{ui_utils.YELLOW}[*] Limpieza de evidencia de "
        f"VENOM-ROUTE{ui_utils.NC}"
    )
    print(
        f"{ui_utils.BOLD_RED}[⚠] Esta acción borrará TODOS los archivos "
        f"guardados en:{ui_utils.NC}"
    )
    for carpeta in CARPETAS_EVIDENCIA:
        print(f"    - {carpeta}/")
    print()

    pregunta = "¿ESTÁS SEGURO DE QUE DESEAS BORRAR TODA LA EVIDENCIA?"
    if not ui_utils.preguntar(pregunta):
        print(f"{ui_utils.BOLD_RED}[-] Limpieza cancelada.{ui_utils.NC}")
        sys.exit(0)

    print()
    total_borrados = 0

    for carpeta in CARPETAS_EVIDENCIA:
        if not os.path.isdir(carpeta):
            print(
                f"{ui_utils.GREY}[→] {carpeta}/ no existe, se omite."
                f"{ui_utils.NC}"
            )
            continue

        borrados = limpiar_carpeta(carpeta)
        total_borrados += borrados
        print(
            f"{ui_utils.BOLD_GREEN}[✓] {carpeta}/ limpiada "
            f"({borrados} archivo(s) borrado(s)).{ui_utils.NC}"
        )

    print()
    print(
        f"{ui_utils.BOLD_GREEN}[✔] Limpieza completada. "
        f"Total de archivos borrados: {total_borrados}.{ui_utils.NC}"
    )


if __name__ == "__main__":
    main()
