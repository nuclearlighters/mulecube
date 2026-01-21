"""
MuleCube WiFi Status
WiFi network information API

Endpoints:
  GET /health       - Service health check
  GET /api/wifi     - WiFi AP status (SSID, channel, clients)
  GET /api/clients  - Connected client list
  GET /api/qr       - QR code data for WiFi connection
"""

import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# =============================================================================
# Configuration
# =============================================================================

HOSTAPD_INTERFACE = os.getenv("HOSTAPD_INTERFACE", "wlan0")
API_PORT = int(os.getenv("API_PORT", "8086"))
HOSTAPD_CONF = os.getenv("HOSTAPD_CONF", "/etc/hostapd/hostapd.conf")
DNSMASQ_LEASES = os.getenv("DNSMASQ_LEASES", "/var/lib/misc/dnsmasq.leases")

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="MuleCube WiFi Status",
    description="WiFi network information API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Response Models
# =============================================================================

class HealthResponse(BaseModel):
    status: str
    timestamp: str

class WifiClient(BaseModel):
    mac_address: str
    ip_address: Optional[str]
    hostname: Optional[str]
    connected_since: Optional[str]

class WifiStatus(BaseModel):
    ssid: str
    password: Optional[str]
    channel: int
    frequency: str
    clients_count: int
    interface: str
    status: str  # "up", "down"

class QRCodeData(BaseModel):
    wifi_string: str
    ssid: str
    encryption: str

# =============================================================================
# Helper Functions
# =============================================================================

START_TIME = time.time()

def parse_hostapd_conf() -> dict:
    """Parse hostapd configuration file"""
    config = {
        "ssid": "MuleCube",
        "password": None,
        "channel": 1,
        "wpa": 2,
    }
    
    conf_path = Path(HOSTAPD_CONF)
    if not conf_path.exists():
        return config
    
    try:
        with open(conf_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                if key == "ssid":
                    config["ssid"] = value
                elif key == "wpa_passphrase":
                    config["password"] = value
                elif key == "channel":
                    config["channel"] = int(value)
                elif key == "wpa":
                    config["wpa"] = int(value)
    except Exception:
        pass
    
    return config


def get_wifi_interface_status() -> dict:
    """Get WiFi interface status using iw/iwconfig"""
    status = {
        "up": False,
        "frequency": "2.4GHz",
        "channel": 1,
    }
    
    # Check if interface is up
    try:
        result = subprocess.run(
            ["ip", "link", "show", HOSTAPD_INTERFACE],
            capture_output=True,
            text=True,
            timeout=5
        )
        status["up"] = "state UP" in result.stdout
    except Exception:
        pass
    
    # Get channel/frequency from iw
    try:
        result = subprocess.run(
            ["iw", "dev", HOSTAPD_INTERFACE, "info"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Parse channel
        channel_match = re.search(r"channel (\d+)", result.stdout)
        if channel_match:
            status["channel"] = int(channel_match.group(1))
        
        # Parse frequency
        freq_match = re.search(r"(\d+) MHz", result.stdout)
        if freq_match:
            freq = int(freq_match.group(1))
            status["frequency"] = "5GHz" if freq > 4000 else "2.4GHz"
    except Exception:
        pass
    
    return status


def get_connected_clients() -> List[dict]:
    """Get list of connected WiFi clients"""
    clients = []
    
    # Get MAC addresses from hostapd
    macs = set()
    try:
        result = subprocess.run(
            ["hostapd_cli", "-i", HOSTAPD_INTERFACE, "all_sta"],
            capture_output=True,
            text=True,
            timeout=5
        )
        for line in result.stdout.split("\n"):
            line = line.strip()
            if re.match(r"^[0-9a-f:]{17}$", line, re.IGNORECASE):
                macs.add(line.lower())
    except Exception:
        pass
    
    # Fallback: check iw station dump
    if not macs:
        try:
            result = subprocess.run(
                ["iw", "dev", HOSTAPD_INTERFACE, "station", "dump"],
                capture_output=True,
                text=True,
                timeout=5
            )
            for line in result.stdout.split("\n"):
                match = re.search(r"Station ([0-9a-f:]{17})", line, re.IGNORECASE)
                if match:
                    macs.add(match.group(1).lower())
        except Exception:
            pass
    
    # Get IP/hostname from DHCP leases
    leases = {}
    try:
        with open(DNSMASQ_LEASES, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 4:
                    # Format: timestamp mac ip hostname client_id
                    mac = parts[1].lower()
                    leases[mac] = {
                        "ip": parts[2],
                        "hostname": parts[3] if parts[3] != "*" else None,
                        "timestamp": parts[0],
                    }
    except Exception:
        pass
    
    # Combine data
    for mac in macs:
        client = {
            "mac_address": mac,
            "ip_address": None,
            "hostname": None,
            "connected_since": None,
        }
        
        if mac in leases:
            client["ip_address"] = leases[mac]["ip"]
            client["hostname"] = leases[mac]["hostname"]
            try:
                ts = int(leases[mac]["timestamp"])
                client["connected_since"] = datetime.fromtimestamp(ts).isoformat()
            except Exception:
                pass
        
        clients.append(client)
    
    return clients


def generate_wifi_qr_string(ssid: str, password: str, encryption: str = "WPA") -> str:
    """Generate WiFi QR code string format"""
    # Format: WIFI:T:WPA;S:ssid;P:password;;
    # Escape special characters
    ssid_escaped = ssid.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace('"', '\\"').replace(":", "\\:")
    password_escaped = password.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace('"', '\\"').replace(":", "\\:") if password else ""
    
    if not password:
        return f"WIFI:T:nopass;S:{ssid_escaped};;"
    
    return f"WIFI:T:{encryption};S:{ssid_escaped};P:{password_escaped};;"


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/api/wifi", response_model=WifiStatus)
async def get_wifi_status():
    """Get WiFi AP status"""
    config = parse_hostapd_conf()
    iface_status = get_wifi_interface_status()
    clients = get_connected_clients()
    
    return WifiStatus(
        ssid=config["ssid"],
        password=config["password"],
        channel=iface_status.get("channel", config["channel"]),
        frequency=iface_status["frequency"],
        clients_count=len(clients),
        interface=HOSTAPD_INTERFACE,
        status="up" if iface_status["up"] else "down"
    )


@app.get("/api/clients", response_model=List[WifiClient])
async def get_clients():
    """Get list of connected clients"""
    clients = get_connected_clients()
    return [WifiClient(**c) for c in clients]


@app.get("/api/qr", response_model=QRCodeData)
async def get_qr_data():
    """Get QR code data for WiFi connection"""
    config = parse_hostapd_conf()
    
    encryption = "nopass" if not config["password"] else "WPA"
    qr_string = generate_wifi_qr_string(
        ssid=config["ssid"],
        password=config["password"] or "",
        encryption=encryption
    )
    
    return QRCodeData(
        wifi_string=qr_string,
        ssid=config["ssid"],
        encryption=encryption
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
