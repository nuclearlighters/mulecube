"""
MuleCube Status Aggregator
Combines all status sources into unified API

Endpoints:
  GET /health         - Service health check
  GET /api/status     - Complete system status
  GET /api/services   - Docker container status
  GET /api/storage    - Storage usage
"""

import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import docker

# =============================================================================
# Configuration
# =============================================================================

HW_MONITOR_URL = os.getenv("HW_MONITOR_URL", "http://mulecube-hw-monitor:8080")
WIFI_STATUS_URL = os.getenv("WIFI_STATUS_URL", "http://host.docker.internal:8086")
USB_MONITOR_URL = os.getenv("USB_MONITOR_URL", "http://mulecube-usb-monitor:8080")

# Service tier groupings for display
TIER1_SERVICES = os.getenv("TIER1_SERVICES", "kiwix,tileserver,nginx,dnsmasq,hostapd").split(",")
TIER2_SERVICES = os.getenv("TIER2_SERVICES", "openwebui,ollama,cryptpad,filebrowser").split(",")
TIER3_SERVICES = os.getenv("TIER3_SERVICES", "retroarch,navidrome").split(",")

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="MuleCube Status Aggregator",
    description="Combined system status API",
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

class BatteryStatus(BaseModel):
    available: bool
    percent: Optional[int]
    time_remaining: Optional[str]
    charging: Optional[bool]
    status: Optional[str]

class TemperatureStatus(BaseModel):
    cpu_temp_c: float
    throttled: bool
    status: str

class WifiStatus(BaseModel):
    ssid: str
    clients_count: int
    status: str

class ServiceStatus(BaseModel):
    name: str
    status: str  # "running", "stopped", "error"
    tier: int
    health: Optional[str]

class StorageStatus(BaseModel):
    total_gb: float
    used_gb: float
    free_gb: float
    percent_used: int

class USBDeviceStatus(BaseModel):
    type: str
    name: str
    status: str
    device_path: Optional[str]

class SystemStatus(BaseModel):
    timestamp: str
    battery: BatteryStatus
    temperature: TemperatureStatus
    wifi: Optional[WifiStatus]
    storage: StorageStatus
    services: Dict[str, Any]
    usb_devices: List[USBDeviceStatus]
    alerts: List[str]

# =============================================================================
# Helper Functions
# =============================================================================

START_TIME = time.time()
http_client = httpx.AsyncClient(timeout=5.0)

async def fetch_json(url: str) -> Optional[dict]:
    """Fetch JSON from URL with error handling"""
    try:
        response = await http_client.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def get_docker_services() -> List[dict]:
    """Get Docker container status"""
    services = []
    
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        
        for container in containers:
            name = container.name.replace("mulecube-", "").replace("-", "_")
            
            # Determine tier
            tier = 0
            name_lower = name.lower()
            if any(s in name_lower for s in TIER1_SERVICES):
                tier = 1
            elif any(s in name_lower for s in TIER2_SERVICES):
                tier = 2
            elif any(s in name_lower for s in TIER3_SERVICES):
                tier = 3
            
            # Get health status
            health = None
            if container.attrs.get("State", {}).get("Health"):
                health = container.attrs["State"]["Health"].get("Status")
            
            status = "running" if container.status == "running" else "stopped"
            if health == "unhealthy":
                status = "error"
            
            services.append({
                "name": container.name,
                "status": status,
                "tier": tier,
                "health": health,
            })
        
        client.close()
    except Exception:
        pass
    
    return services


def get_storage_status() -> dict:
    """Get storage usage from filesystem"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        
        return {
            "total_gb": round(total / (1024**3), 1),
            "used_gb": round(used / (1024**3), 1),
            "free_gb": round(free / (1024**3), 1),
            "percent_used": int((used / total) * 100),
        }
    except Exception:
        return {
            "total_gb": 0,
            "used_gb": 0,
            "free_gb": 0,
            "percent_used": 0,
        }


def generate_alerts(battery: dict, temp: dict, storage: dict, services: list) -> List[str]:
    """Generate system alerts based on status"""
    alerts = []
    
    # Battery alerts
    if battery.get("available") and battery.get("percent"):
        if battery["percent"] <= 10:
            alerts.append("CRITICAL: Battery below 10% - shutdown imminent")
        elif battery["percent"] <= 20:
            alerts.append("WARNING: Battery below 20%")
    
    # Temperature alerts
    if temp.get("cpu_temp_c", 0) >= 80:
        alerts.append("CRITICAL: CPU temperature above 80°C - throttling active")
    elif temp.get("cpu_temp_c", 0) >= 75:
        alerts.append("WARNING: CPU temperature above 75°C")
    
    if temp.get("throttled"):
        alerts.append("WARNING: CPU is being throttled")
    
    # Storage alerts
    if storage.get("percent_used", 0) >= 95:
        alerts.append("CRITICAL: Storage nearly full (>95%)")
    elif storage.get("percent_used", 0) >= 90:
        alerts.append("WARNING: Storage above 90%")
    
    # Service alerts
    failed = [s for s in services if s.get("status") == "error"]
    if failed:
        names = ", ".join(s["name"] for s in failed[:3])
        alerts.append(f"WARNING: Services unhealthy: {names}")
    
    return alerts


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


@app.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """Get complete system status"""
    
    # Fetch from hw-monitor
    hw_data = await fetch_json(f"{HW_MONITOR_URL}/api/system")
    
    # Parse battery status
    battery = {"available": False, "percent": None, "time_remaining": None, "charging": None, "status": None}
    if hw_data and hw_data.get("battery"):
        b = hw_data["battery"]
        battery = {
            "available": True,
            "percent": b.get("percent"),
            "time_remaining": b.get("time_remaining_formatted"),
            "charging": b.get("charging"),
            "status": b.get("status"),
        }
    
    # Parse temperature
    temp = {"cpu_temp_c": -1, "throttled": False, "status": "unknown"}
    if hw_data and hw_data.get("temperature"):
        t = hw_data["temperature"]
        temp = {
            "cpu_temp_c": t.get("cpu_temp_c", -1),
            "throttled": t.get("throttled", False),
            "status": t.get("status", "unknown"),
        }
    
    # Fetch WiFi status
    wifi = None
    wifi_data = await fetch_json(f"{WIFI_STATUS_URL}/api/wifi")
    if wifi_data:
        wifi = {
            "ssid": wifi_data.get("ssid", "Unknown"),
            "clients_count": wifi_data.get("clients_count", 0),
            "status": wifi_data.get("status", "unknown"),
        }
    
    # Get storage
    storage = get_storage_status()
    
    # Get services
    services = get_docker_services()
    running = len([s for s in services if s["status"] == "running"])
    stopped = len([s for s in services if s["status"] == "stopped"])
    failed = len([s for s in services if s["status"] == "error"])
    
    services_summary = {
        "total": len(services),
        "running": running,
        "stopped": stopped,
        "failed": failed,
        "list": services,
    }
    
    # Fetch USB devices
    usb_devices = []
    usb_data = await fetch_json(f"{USB_MONITOR_URL}/api/known")
    if usb_data:
        usb_devices = [
            {
                "type": d.get("type"),
                "name": d.get("name"),
                "status": d.get("status"),
                "device_path": d.get("device_path"),
            }
            for d in usb_data
        ]
    
    # Generate alerts
    alerts = generate_alerts(battery, temp, storage, services)
    
    return SystemStatus(
        timestamp=datetime.utcnow().isoformat(),
        battery=BatteryStatus(**battery),
        temperature=TemperatureStatus(**temp),
        wifi=WifiStatus(**wifi) if wifi else None,
        storage=StorageStatus(**storage),
        services=services_summary,
        usb_devices=[USBDeviceStatus(**d) for d in usb_devices],
        alerts=alerts,
    )


@app.get("/api/services")
async def get_services():
    """Get Docker container status"""
    services = get_docker_services()
    return {
        "total": len(services),
        "running": len([s for s in services if s["status"] == "running"]),
        "stopped": len([s for s in services if s["status"] == "stopped"]),
        "failed": len([s for s in services if s["status"] == "error"]),
        "services": services,
    }


@app.get("/api/storage", response_model=StorageStatus)
async def get_storage():
    """Get storage status"""
    storage = get_storage_status()
    return StorageStatus(**storage)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
