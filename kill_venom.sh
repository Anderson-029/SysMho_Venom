#!/bin/bash
# =============================================================================
# kill_venom.sh - Script para forzar detención de SysMho-Venom y limpieza
# =============================================================================

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then
  echo "Por favor ejecuta este script como root (sudo ./kill_venom.sh)"
  exit 1
fi

echo "[*] Buscando procesos de SysMho-Venom..."

# Matar procesos de Python relacionados con Venom
pkill -f venom_route.py
pkill -f sniffer_engine.py
pkill -f anti_sniff_detector.py

echo "[✔] Procesos finalizados."

echo "[*] Restaurando configuración de red (IP Forwarding)..."
echo 0 > /proc/sys/net/ipv4/ip_forward
echo "[✔] IP Forwarding desactivado."

echo "[*] Limpiando reglas iptables residuales..."

# Restaurar la política de FORWARD a DROP (como lo hace el script original)
iptables -P FORWARD DROP

# Extraer y eliminar las reglas MASQUERADE en POSTROUTING
# (Esto elimina las reglas insertadas por el ataque)
while iptables -t nat -S POSTROUTING 2>/dev/null | grep "\-j MASQUERADE" >/dev/null; do
    # Obtenemos la interfaz de la regla para borrarla exactamente
    rule=$(iptables -t nat -S POSTROUTING | grep "\-j MASQUERADE" | head -n 1 | sed 's/-A/-D/')
    iptables -t nat $rule 2>/dev/null
done

echo "[✔] Reglas iptables limpiadas."

echo ""
echo "[✔] SysMho-Venom apagado correctamente y sistema limpio."
