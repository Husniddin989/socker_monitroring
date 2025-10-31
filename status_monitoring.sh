#!/bin/bash
# Server Monitoring Status Check

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "  📊 Server Monitoring Status"
echo "=========================================="
echo ""

# Socket Server status
SOCKET_PID_FILE="$SCRIPT_DIR/socket_server.pid"
if [ -f "$SOCKET_PID_FILE" ]; then
    SOCKET_PID=$(cat "$SOCKET_PID_FILE")
    if ps -p "$SOCKET_PID" > /dev/null 2>&1; then
        echo "✅ Socket Server: RUNNING (PID: $SOCKET_PID)"
    else
        echo "❌ Socket Server: STOPPED (stale PID file)"
    fi
else
    echo "❌ Socket Server: NOT RUNNING"
fi

# Monitoring status
MONITOR_PID_FILE="$SCRIPT_DIR/monitoring.pid"
if [ -f "$MONITOR_PID_FILE" ]; then
    MONITOR_PID=$(cat "$MONITOR_PID_FILE")
    if ps -p "$MONITOR_PID" > /dev/null 2>&1; then
        echo "✅ Monitoring: RUNNING (PID: $MONITOR_PID)"
    else
        echo "❌ Monitoring: STOPPED (stale PID file)"
    fi
else
    echo "❌ Monitoring: NOT RUNNING"
fi

# Socket file status
if [ -S "/tmp/monitor.sock" ]; then
    echo "✅ Socket File: EXISTS (/tmp/monitor.sock)"
else
    echo "❌ Socket File: NOT FOUND"
fi

echo ""
echo "📁 Log Files:"
echo "----------------------------------------"

if [ -f "logs/monitoring.log" ]; then
    LOG_SIZE=$(du -h logs/monitoring.log | cut -f1)
    LOG_LINES=$(wc -l < logs/monitoring.log)
    echo "   📄 monitoring.log: $LOG_SIZE ($LOG_LINES lines)"
else
    echo "   📄 monitoring.log: NOT FOUND"
fi

if [ -f "logs/socket_server.log" ]; then
    LOG_SIZE=$(du -h logs/socket_server.log | cut -f1)
    LOG_LINES=$(wc -l < logs/socket_server.log)
    echo "   📄 socket_server.log: $LOG_SIZE ($LOG_LINES lines)"
else
    echo "   📄 socket_server.log: NOT FOUND"
fi

echo ""
echo "💾 Disk Usage (logs directory):"
echo "----------------------------------------"
if [ -d "logs" ]; then
    du -sh logs/
    echo ""
    echo "Log fayllar:"
    ls -lh logs/ 2>/dev/null | grep -v "^total" || echo "   Bo'sh"
fi

echo ""
echo "🔄 Recent Activity (last 5 log entries):"
echo "----------------------------------------"
if [ -f "logs/monitoring.log" ]; then
    tail -n 5 logs/monitoring.log
fi

echo ""
echo "=========================================="