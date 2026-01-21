#!/bin/bash
# Generate system stats JSON for MuleCube Dashboard
# Enhanced with temperature and battery from control panel APIs

# CPU usage (average over 1 second)
CPU=$(awk '{u=$2+$4; t=$2+$4+$5; if (NR==1){u1=u; t1=t;} else print int(($2+$4-u1) * 100 / (t-t1)); }' <(grep 'cpu ' /proc/stat) <(sleep 1; grep 'cpu ' /proc/stat) 2>/dev/null | head -1 | tr -d '\n')
CPU=${CPU:-0}

# Memory
MEM_TOTAL=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
MEM_AVAILABLE=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)
MEM_PERCENT=$(awk "BEGIN {printf \"%.0f\", (($MEM_TOTAL-$MEM_AVAILABLE)/$MEM_TOTAL)*100}")

# Disk
DISK_PERCENT=$(df / | tail -1 | awk '{print $5}' | tr -d '%')

# Uptime formatted
UPTIME_SECS=$(awk '{print int($1)}' /proc/uptime)
DAYS=$((UPTIME_SECS / 86400))
HOURS=$(((UPTIME_SECS % 86400) / 3600))
MINS=$(((UPTIME_SECS % 3600) / 60))
if [ $DAYS -gt 0 ]; then
    UPTIME_STR="${DAYS}d ${HOURS}h ${MINS}m"
else
    UPTIME_STR="${HOURS}h ${MINS}m"
fi

# Hostname
HOSTNAME=$(hostname)

# WiFi clients
WIFI_RAW=$(iw dev wlan0 station dump 2>/dev/null | grep -c "Station")
WIFI_CLIENTS=$(printf '%d' "${WIFI_RAW:-0}" 2>/dev/null || echo 0)

# Ethernet status
ETH_STATUS="Disconnected"
if [ -f /sys/class/net/eth0/carrier ] && [ "$(cat /sys/class/net/eth0/carrier 2>/dev/null)" = "1" ]; then
    ETH_STATUS="Connected"
fi

# NEW: Temperature from hw-monitor API (fallback to vcgencmd)
TEMP=""
TEMP_STATUS="normal"
if TEMP_JSON=$(curl -sf --max-time 2 http://localhost:9001/api/temperature 2>/dev/null); then
    TEMP=$(echo "$TEMP_JSON" | grep -o '"cpu_temp_c":[0-9.]*' | cut -d: -f2 | cut -d. -f1)
    THROTTLED=$(echo "$TEMP_JSON" | grep -o '"throttled":[a-z]*' | cut -d: -f2)
    if [ "$THROTTLED" = "true" ]; then
        TEMP_STATUS="throttled"
    elif [ "${TEMP:-0}" -ge 80 ]; then
        TEMP_STATUS="critical"
    elif [ "${TEMP:-0}" -ge 70 ]; then
        TEMP_STATUS="warning"
    fi
else
    # Fallback to direct vcgencmd
    TEMP=$(vcgencmd measure_temp 2>/dev/null | grep -o '[0-9]*\.[0-9]' | cut -d. -f1)
fi
TEMP=${TEMP:-0}

# NEW: Battery from hw-monitor API
BATTERY_AVAILABLE="false"
BATTERY_PERCENT=""
BATTERY_CHARGING="false"
BATTERY_TIME=""
if BATT_JSON=$(curl -sf --max-time 2 http://localhost:9001/api/battery 2>/dev/null); then
    BATTERY_AVAILABLE=$(echo "$BATT_JSON" | grep -o '"available":[a-z]*' | cut -d: -f2)
    if [ "$BATTERY_AVAILABLE" = "true" ]; then
        BATTERY_PERCENT=$(echo "$BATT_JSON" | grep -o '"percent":[0-9]*' | cut -d: -f2)
        BATTERY_CHARGING=$(echo "$BATT_JSON" | grep -o '"charging":[a-z]*' | cut -d: -f2)
        BATTERY_TIME=$(echo "$BATT_JSON" | grep -o '"time_remaining":"[^"]*"' | cut -d'"' -f4)
    fi
fi

# NEW: Service counts from status-aggregator
SERVICES_TOTAL=0
SERVICES_RUNNING=0
SERVICES_FAILED=0
if SVC_JSON=$(curl -sf --max-time 2 http://localhost:9004/api/status 2>/dev/null); then
    SERVICES_TOTAL=$(echo "$SVC_JSON" | grep -o '"total":[0-9]*' | head -1 | cut -d: -f2)
    SERVICES_RUNNING=$(echo "$SVC_JSON" | grep -o '"running":[0-9]*' | head -1 | cut -d: -f2)
    SERVICES_FAILED=$(echo "$SVC_JSON" | grep -o '"failed":[0-9]*' | head -1 | cut -d: -f2)
fi
SERVICES_TOTAL=${SERVICES_TOTAL:-0}
SERVICES_RUNNING=${SERVICES_RUNNING:-0}
SERVICES_FAILED=${SERVICES_FAILED:-0}

# Write JSON
cat > /srv/mulecube-dashboard/data/stats.json << ENDJSON
{
  "cpu": ${CPU},
  "memory": ${MEM_PERCENT},
  "disk": ${DISK_PERCENT},
  "uptime": "${UPTIME_STR}",
  "hostname": "${HOSTNAME}",
  "wifi": "${WIFI_CLIENTS} clients",
  "wifi_clients": ${WIFI_CLIENTS},
  "ethernet": "${ETH_STATUS}",
  "temperature": ${TEMP},
  "temp_status": "${TEMP_STATUS}",
  "battery_available": ${BATTERY_AVAILABLE},
  "battery_percent": ${BATTERY_PERCENT:-null},
  "battery_charging": ${BATTERY_CHARGING},
  "battery_time": "${BATTERY_TIME}",
  "services_total": ${SERVICES_TOTAL},
  "services_running": ${SERVICES_RUNNING},
  "services_failed": ${SERVICES_FAILED},
  "timestamp": $(date +%s)
}
ENDJSON
