"""
MuleCube Diagnostics Service
System health checks and troubleshooting

Endpoints:
  GET /health         - Service health check
  GET /api/full       - Run full diagnostic suite
  GET /api/network    - Network diagnostics
  GET /api/storage    - Storage diagnostics
  GET /api/services   - Service health diagnostics
  GET /api/hardware   - Hardware diagnostics
"""

import os
import shutil
import subprocess
from datetime import datetime
from typing import Any, Dict, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import docker
import psutil

# =============================================================================
# Configuration
# =============================================================================

HW_MONITOR_URL = os.getenv("HW_MONITOR_URL", "http://mulecube-hw-monitor:8080")

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="MuleCube Diagnostics",
    description="System health checks and troubleshooting",
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

class DiagnosticCheck(BaseModel):
    name: str
    status: str  # "pass", "warn", "fail"
    message: str
    details: Dict[str, Any] = {}

class DiagnosticReport(BaseModel):
    timestamp: str
    overall_status: str
    checks: List[DiagnosticCheck]
    summary: Dict[str, int]

# =============================================================================
# Diagnostic Functions
# =============================================================================

def check_cpu() -> DiagnosticCheck:
    """Check CPU usage and load"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        load_avg = os.getloadavg()
        cpu_count = psutil.cpu_count()
        
        # High load if > 80% or load avg > cpu count
        if cpu_percent > 90 or load_avg[0] > cpu_count * 1.5:
            status = "fail"
            message = f"High CPU usage: {cpu_percent}%"
        elif cpu_percent > 70 or load_avg[0] > cpu_count:
            status = "warn"
            message = f"Elevated CPU usage: {cpu_percent}%"
        else:
            status = "pass"
            message = f"CPU usage normal: {cpu_percent}%"
        
        return DiagnosticCheck(
            name="CPU",
            status=status,
            message=message,
            details={
                "usage_percent": cpu_percent,
                "load_average": load_avg,
                "cpu_count": cpu_count,
            }
        )
    except Exception as e:
        return DiagnosticCheck(
            name="CPU",
            status="fail",
            message=f"Error checking CPU: {e}",
            details={}
        )


def check_memory() -> DiagnosticCheck:
    """Check memory usage"""
    try:
        mem = psutil.virtual_memory()
        
        if mem.percent > 95:
            status = "fail"
            message = f"Critical memory usage: {mem.percent}%"
        elif mem.percent > 85:
            status = "warn"
            message = f"High memory usage: {mem.percent}%"
        else:
            status = "pass"
            message = f"Memory usage normal: {mem.percent}%"
        
        return DiagnosticCheck(
            name="Memory",
            status=status,
            message=message,
            details={
                "total_gb": round(mem.total / (1024**3), 1),
                "available_gb": round(mem.available / (1024**3), 1),
                "used_percent": mem.percent,
            }
        )
    except Exception as e:
        return DiagnosticCheck(
            name="Memory",
            status="fail",
            message=f"Error checking memory: {e}",
            details={}
        )


def check_storage() -> DiagnosticCheck:
    """Check storage usage"""
    try:
        disk = shutil.disk_usage("/")
        percent_used = (disk.used / disk.total) * 100
        
        if percent_used > 95:
            status = "fail"
            message = f"Critical storage usage: {percent_used:.1f}%"
        elif percent_used > 90:
            status = "warn"
            message = f"High storage usage: {percent_used:.1f}%"
        else:
            status = "pass"
            message = f"Storage usage normal: {percent_used:.1f}%"
        
        return DiagnosticCheck(
            name="Storage",
            status=status,
            message=message,
            details={
                "total_gb": round(disk.total / (1024**3), 1),
                "free_gb": round(disk.free / (1024**3), 1),
                "used_percent": round(percent_used, 1),
            }
        )
    except Exception as e:
        return DiagnosticCheck(
            name="Storage",
            status="fail",
            message=f"Error checking storage: {e}",
            details={}
        )


def check_temperature() -> DiagnosticCheck:
    """Check CPU temperature"""
    try:
        response = httpx.get(f"{HW_MONITOR_URL}/api/temperature", timeout=5.0)
        
        if response.status_code != 200:
            return DiagnosticCheck(
                name="Temperature",
                status="warn",
                message="Unable to read temperature from hw-monitor",
                details={}
            )
        
        data = response.json()
        temp = data.get("cpu_temp_c", 0)
        throttled = data.get("throttled", False)
        
        if temp > 85 or throttled:
            status = "fail"
            message = f"CPU overheating: {temp}°C (throttled: {throttled})"
        elif temp > 75:
            status = "warn"
            message = f"CPU temperature elevated: {temp}°C"
        else:
            status = "pass"
            message = f"CPU temperature normal: {temp}°C"
        
        return DiagnosticCheck(
            name="Temperature",
            status=status,
            message=message,
            details=data
        )
    except Exception as e:
        return DiagnosticCheck(
            name="Temperature",
            status="warn",
            message=f"Error checking temperature: {e}",
            details={}
        )


def check_docker_services() -> DiagnosticCheck:
    """Check Docker container health"""
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        client.close()
        
        running = 0
        stopped = 0
        unhealthy = []
        
        for c in containers:
            if c.status == "running":
                running += 1
                health = c.attrs.get("State", {}).get("Health", {})
                if health and health.get("Status") == "unhealthy":
                    unhealthy.append(c.name)
            else:
                stopped += 1
        
        if unhealthy:
            status = "fail"
            message = f"Unhealthy services: {', '.join(unhealthy[:3])}"
        elif stopped > 5:
            status = "warn"
            message = f"{stopped} services stopped"
        else:
            status = "pass"
            message = f"{running} services running"
        
        return DiagnosticCheck(
            name="Docker Services",
            status=status,
            message=message,
            details={
                "running": running,
                "stopped": stopped,
                "unhealthy": unhealthy,
            }
        )
    except Exception as e:
        return DiagnosticCheck(
            name="Docker Services",
            status="fail",
            message=f"Error checking Docker: {e}",
            details={}
        )


def check_network_interfaces() -> DiagnosticCheck:
    """Check network interfaces"""
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        interfaces = {}
        wifi_up = False
        eth_up = False
        
        for iface, nic_stats in stats.items():
            if iface in ["lo", "docker0"] or iface.startswith("veth"):
                continue
            
            interfaces[iface] = {
                "up": nic_stats.isup,
                "speed": nic_stats.speed,
            }
            
            if iface.startswith("wlan") and nic_stats.isup:
                wifi_up = True
            if iface.startswith("eth") and nic_stats.isup:
                eth_up = True
        
        if wifi_up:
            status = "pass"
            message = "WiFi interface is up"
        elif eth_up:
            status = "pass"
            message = "Ethernet interface is up"
        else:
            status = "warn"
            message = "No active network interfaces"
        
        return DiagnosticCheck(
            name="Network Interfaces",
            status=status,
            message=message,
            details={"interfaces": interfaces}
        )
    except Exception as e:
        return DiagnosticCheck(
            name="Network Interfaces",
            status="fail",
            message=f"Error checking network: {e}",
            details={}
        )


def check_dns() -> DiagnosticCheck:
    """Check DNS resolution (internal only for offline device)"""
    try:
        # Just check if dnsmasq is responding
        result = subprocess.run(
            ["nslookup", "mulecube.local", "127.0.0.1"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            status = "pass"
            message = "DNS resolution working"
        else:
            status = "warn"
            message = "DNS resolution may have issues"
        
        return DiagnosticCheck(
            name="DNS",
            status=status,
            message=message,
            details={"output": result.stdout[:200] if result.stdout else ""}
        )
    except subprocess.TimeoutExpired:
        return DiagnosticCheck(
            name="DNS",
            status="fail",
            message="DNS lookup timed out",
            details={}
        )
    except Exception as e:
        return DiagnosticCheck(
            name="DNS",
            status="warn",
            message=f"Could not check DNS: {e}",
            details={}
        )


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


@app.get("/api/full", response_model=DiagnosticReport)
async def run_full_diagnostics():
    """Run complete diagnostic suite"""
    checks = [
        check_cpu(),
        check_memory(),
        check_storage(),
        check_temperature(),
        check_docker_services(),
        check_network_interfaces(),
        check_dns(),
    ]
    
    # Calculate summary
    summary = {"pass": 0, "warn": 0, "fail": 0}
    for check in checks:
        summary[check.status] = summary.get(check.status, 0) + 1
    
    # Determine overall status
    if summary["fail"] > 0:
        overall = "fail"
    elif summary["warn"] > 0:
        overall = "warn"
    else:
        overall = "pass"
    
    return DiagnosticReport(
        timestamp=datetime.utcnow().isoformat(),
        overall_status=overall,
        checks=checks,
        summary=summary
    )


@app.get("/api/network")
async def run_network_diagnostics():
    """Run network-specific diagnostics"""
    checks = [
        check_network_interfaces(),
        check_dns(),
    ]
    return {"checks": checks}


@app.get("/api/storage")
async def run_storage_diagnostics():
    """Run storage-specific diagnostics"""
    return check_storage()


@app.get("/api/services")
async def run_service_diagnostics():
    """Run service-specific diagnostics"""
    return check_docker_services()


@app.get("/api/hardware")
async def run_hardware_diagnostics():
    """Run hardware-specific diagnostics"""
    checks = [
        check_cpu(),
        check_memory(),
        check_temperature(),
    ]
    return {"checks": checks}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
