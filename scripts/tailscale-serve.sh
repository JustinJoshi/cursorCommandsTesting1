#!/usr/bin/env bash
set -euo pipefail

echo "=== Tailscale Serve Setup ==="
echo ""

# Check Tailscale status
if ! tailscale status > /dev/null 2>&1; then
    echo "[ERROR] Tailscale is not running or not connected."
    echo "        Start with: sudo systemctl start tailscaled"
    echo "        Then login:  sudo tailscale up"
    exit 1
fi

HOSTNAME=$(tailscale status --json | python -c "import sys,json; print(json.load(sys.stdin)['Self']['DNSName'].rstrip('.'))" 2>/dev/null || echo "unknown")

echo "[OK] Tailscale connected"
echo ""

# Expose frontend (port 5173) on the default HTTPS port
echo "[SERVE] Exposing frontend (port 5173) via Tailscale..."
tailscale serve --bg 5173

echo ""
echo "=== Tailscale Serve Active ==="
echo ""
echo "  Your app is now accessible at:"
echo "  https://${HOSTNAME}"
echo ""
echo "  Access from your phone:"
echo "  1. Open Tailscale app on your phone"
echo "  2. Make sure you're connected to your tailnet"
echo "  3. Navigate to the URL above"
echo ""
echo "  To stop serving:"
echo "    tailscale serve --remove /"
echo ""
echo "  To check status:"
echo "    tailscale serve status"
