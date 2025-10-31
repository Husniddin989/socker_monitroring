#!/bin/bash
# Server Monitoring Auto Start Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  🚀 Server Monitoring Auto Start"
echo "=========================================="
echo ""

# Virtual environment tekshirish
if [ -d "venv" ]; then
    echo "✅ Virtual environment topildi"
    source venv/bin/activate
else
    echo "⚠️  Virtual environment topilmadi, yaratilmoqda..."
    python3 -m venv venv
    source venv/bin/activate
    pip install psutil requests
fi

echo ""
echo "📦 Dependencies tekshirilmoqda..."
python3 -c "import psutil, requests" 2>/dev/null || {
    echo "⚠️  Dependencies o'rnatilmoqda..."
    pip install psutil requests
}

echo ""
echo "📁 Logs papkasi yaratilmoqda..."
mkdir -p logs

echo ""
echo "🔧 Config tekshirilmoqda..."
if [ ! -f "config.json" ]; then
    echo "⚠️  Config topilmadi, yaratilmoqda..."
    python3 -c "from config import ConfigManager; c = ConfigManager(); c.create_default_config()"
    echo ""
    echo "❌ ERROR: config.json faylida Telegram ma'lumotlarini to'ldiring!"
    echo "   - bot_token: @BotFather dan token"
    echo "   - chat_id: Telegram chat ID"
    echo ""
    exit 1
fi

# PID fayllar
SOCKET_SERVER_PID="$SCRIPT_DIR/socket_server.pid"
MONITORING_PID="$SCRIPT_DIR/monitoring.pid"

# Eski processlarni to'xtatish
echo ""
echo "🧹 Eski processlarni tozalash..."
if [ -f "$SOCKET_SERVER_PID" ]; then
    OLD_PID=$(cat "$SOCKET_SERVER_PID")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "   Eski socket server to'xtatilmoqda (PID: $OLD_PID)..."
        kill "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
    rm -f "$SOCKET_SERVER_PID"
fi

if [ -f "$MONITORING_PID" ]; then
    OLD_PID=$(cat "$MONITORING_PID")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "   Eski monitoring to'xtatilmoqda (PID: $OLD_PID)..."
        kill "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
    rm -f "$MONITORING_PID"
fi

# Socket faylni tozalash
if [ -S "/tmp/monitor.sock" ]; then
    echo "   Eski socket fayl o'chirilmoqda..."
    rm -f /tmp/monitor.sock
fi

echo ""
echo "🚀 Socket Server ishga tushirilmoqda..."
nohup python3 socket_server.py > logs/socket_server_console.log 2>&1 &
SOCKET_PID=$!
echo $SOCKET_PID > "$SOCKET_SERVER_PID"
echo "   ✅ Socket Server ishga tushdi (PID: $SOCKET_PID)"

echo ""
echo "⏳ Socket fayl yaratilishi kutilmoqda..."
sleep 3

if [ ! -S "/tmp/monitor.sock" ]; then
    echo "   ❌ ERROR: Socket fayl yaratilmadi!"
    kill $SOCKET_PID 2>/dev/null || true
    exit 1
fi

echo "   ✅ Socket fayl tayyor: /tmp/monitor.sock"

echo ""
echo "🚀 Monitoring + Telegram Alerts ishga tushirilmoqda..."
nohup python3 main_with_socket.py > logs/monitoring_console.log 2>&1 &
MONITOR_PID=$!
echo $MONITOR_PID > "$MONITORING_PID"
echo "   ✅ Monitoring ishga tushdi (PID: $MONITOR_PID)"

echo ""
echo "=========================================="
echo "  ✅ Monitoring muvaffaqiyatli ishga tushdi!"
echo "=========================================="
echo ""
echo "📊 Loglarni ko'rish:"
echo "   tail -f logs/monitoring.log"
echo "   tail -f logs/socket_server.log"
echo ""
echo "🎯 Monitoring to'xtatish:"
echo "   ./stop_monitoring.sh"
echo ""
echo "📺 Dashboard ko'rish:"
echo "   python3 socket_client.py"
echo ""
echo "🔍 Process holatini tekshirish:"
echo "   ps aux | grep -E 'socket_server|main_with_socket'"
echo ""