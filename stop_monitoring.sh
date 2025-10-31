#!/bin/bash
# Server Monitoring Stop Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  ⛔ Server Monitoring To'xtatilmoqda"
echo "=========================================="
echo ""

SOCKET_SERVER_PID="$SCRIPT_DIR/socket_server.pid"
MONITORING_PID="$SCRIPT_DIR/monitoring.pid"

# Monitoring to'xtatish
if [ -f "$MONITORING_PID" ]; then
    PID=$(cat "$MONITORING_PID")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⏳ Monitoring to'xtatilmoqda (PID: $PID)..."
        kill "$PID" 2>/dev/null || true
        sleep 2
        
        # Agar hali ham ishlayotgan bo'lsa
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️  Force kill..."
            kill -9 "$PID" 2>/dev/null || true
        fi
        echo "✅ Monitoring to'xtatildi"
    else
        echo "⚠️  Monitoring process topilmadi"
    fi
    rm -f "$MONITORING_PID"
else
    echo "⚠️  Monitoring PID fayl topilmadi"
fi

# Socket Server to'xtatish
if [ -f "$SOCKET_SERVER_PID" ]; then
    PID=$(cat "$SOCKET_SERVER_PID")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⏳ Socket Server to'xtatilmoqda (PID: $PID)..."
        kill "$PID" 2>/dev/null || true
        sleep 2
        
        # Agar hali ham ishlayotgan bo'lsa
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️  Force kill..."
            kill -9 "$PID" 2>/dev/null || true
        fi
        echo "✅ Socket Server to'xtatildi"
    else
        echo "⚠️  Socket Server process topilmadi"
    fi
    rm -f "$SOCKET_SERVER_PID"
else
    echo "⚠️  Socket Server PID fayl topilmadi"
fi

# Socket faylni o'chirish
if [ -S "/tmp/monitor.sock" ]; then
    echo "🧹 Socket fayl o'chirilmoqda..."
    rm -f /tmp/monitor.sock
fi

echo ""
echo "=========================================="
echo "  ✅ Barcha processlar to'xtatildi"
echo "=========================================="
echo ""