"""
MuleCube USB Monitor
USB device detection and status API

Endpoints:
  GET /health       - Service health check
  GET /api/devices  - List all USB devices
  GET /api/known    - List known MuleCube peripherals (Meshtastic, GPS, RTL-SDR)
  GET /api/storage  - List USB storage devices
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

# Known device patterns (VID:PID)
KNOWN_DEVICES = {
    "meshtastic": {
        "patterns": [
            ("303a", "1001"),  # ESP32-S3 (Heltec, T-Beam S3)
            ("1a86", "7523"),  # CH340 serial (many boards)
            ("1a86", "55d4"),  # CH9102 serial
            ("10c4", "ea60"),  # CP210x (RAK, LilyGo)
            ("0403", "6001"),  # FTDI
        ],
        "name": "Meshtastic Radio",
        "icon": "radio",
    },
    "gps": {
        "patterns": [
            ("1546", "01a7"),  # U-blox 7
            ("1546", "01a8"),  # U-blox 8
            ("067b", "2303"),  # Prolific PL2303 (many GPS)
            ("067b", "23a3"),  # Prolific PL2303GT
        ],
        "name": "GPS Receiver",
        "icon": "navigation",
    },
    "rtlsdr": {
        "patterns": [
            ("0bda", "2838"),  # RTL2838 DVB-T
            ("0bda", "2832"),  # RTL2832U
        ],
        "name": "RTL-SDR Dongle",
        "icon": "antenna",
    },
    "storage": {
        "patterns": [],  # Detected by class
        "name": "USB Storage",
        "icon": "hard-drive",
    },
}

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="MuleCube USB Monitor",
    description="USB device detection and status API",
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

class USBDevice(BaseModel):
    bus: str
    device: str
    vendor_id: str
    product_id: str
    vendor_name: Optional[str]
    product_name: Optional[str]
    serial: Optional[str]
    device_path: Optional[str]  # e.g., /dev/ttyUSB0

class KnownDevice(BaseModel):
    type: str
    name: str
    icon: str
    status: str  # "connected", "not_found"
    device_path: Optional[str]
    vendor_id: Optional[str]
    product_id: Optional[str]

class StorageDevice(BaseModel):
    device_path: str
    mount_point: Optional[str]
    label: Optional[str]
    size_bytes: int
    size_formatted: str
    filesystem: Optional[str]
    mounted: bool

# =============================================================================
# Helper Functions
# =============================================================================

START_TIME = time.time()

def parse_lsusb() -> List[dict]:
    """Parse lsusb output to get USB device list"""
    devices = []
    
    try:
        result = subprocess.run(
            ["lsusb"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        for line in result.stdout.strip().split("\n"):
            # Format: Bus 001 Device 003: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
            match = re.match(
                r"Bus (\d+) Device (\d+): ID ([0-9a-f]{4}):([0-9a-f]{4})\s*(.*)",
                line,
                re.IGNORECASE
            )
            if match:
                bus, device, vid, pid, name = match.groups()
                vendor_name = None
                product_name = name.strip() if name else None
                
                devices.append({
                    "bus": bus,
                    "device": device,
                    "vendor_id": vid.lower(),
                    "product_id": pid.lower(),
                    "vendor_name": vendor_name,
                    "product_name": product_name,
                    "serial": None,
                    "device_path": None,
                })
    except Exception:
        pass
    
    return devices


def find_device_path(vid: str, pid: str) -> Optional[str]:
    """Find /dev/tty* path for a USB serial device"""
    tty_path = Path("/sys/class/tty")
    
    if not tty_path.exists():
        return None
    
    for tty in tty_path.iterdir():
        if not tty.name.startswith("ttyUSB") and not tty.name.startswith("ttyACM"):
            continue
        
        # Check if this tty belongs to our device
        device_link = tty / "device"
        if device_link.exists():
            try:
                # Walk up to find USB device
                usb_path = device_link.resolve()
                while usb_path != Path("/"):
                    id_vendor = usb_path / "idVendor"
                    id_product = usb_path / "idProduct"
                    
                    if id_vendor.exists() and id_product.exists():
                        with open(id_vendor) as f:
                            found_vid = f.read().strip().lower()
                        with open(id_product) as f:
                            found_pid = f.read().strip().lower()
                        
                        if found_vid == vid.lower() and found_pid == pid.lower():
                            return f"/dev/{tty.name}"
                    
                    usb_path = usb_path.parent
            except Exception:
                pass
    
    return None


def get_known_devices() -> List[dict]:
    """Get status of known MuleCube peripherals"""
    usb_devices = parse_lsusb()
    known = []
    
    for device_type, info in KNOWN_DEVICES.items():
        if device_type == "storage":
            continue  # Handle storage separately
        
        found = None
        for usb in usb_devices:
            for vid, pid in info["patterns"]:
                if usb["vendor_id"] == vid.lower() and usb["product_id"] == pid.lower():
                    found = usb
                    break
            if found:
                break
        
        device_path = None
        if found:
            device_path = find_device_path(found["vendor_id"], found["product_id"])
        
        known.append({
            "type": device_type,
            "name": info["name"],
            "icon": info["icon"],
            "status": "connected" if found else "not_found",
            "device_path": device_path,
            "vendor_id": found["vendor_id"] if found else None,
            "product_id": found["product_id"] if found else None,
        })
    
    return known


def get_storage_devices() -> List[dict]:
    """Get USB storage devices with mount info"""
    storage = []
    
    try:
        result = subprocess.run(
            ["lsblk", "-J", "-o", "NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE,LABEL,TRAN,HOTPLUG"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        import json
        data = json.loads(result.stdout)
        
        for device in data.get("blockdevices", []):
            # Only USB devices
            if device.get("tran") != "usb":
                continue
            
            # Get partitions or the device itself
            parts = device.get("children", [device])
            
            for part in parts:
                if part.get("type") not in ["part", "disk"]:
                    continue
                
                name = part.get("name", "")
                size_str = part.get("size", "0")
                
                # Parse size to bytes
                size_bytes = 0
                try:
                    multipliers = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
                    if size_str[-1] in multipliers:
                        size_bytes = int(float(size_str[:-1]) * multipliers[size_str[-1]])
                    else:
                        size_bytes = int(size_str)
                except Exception:
                    pass
                
                storage.append({
                    "device_path": f"/dev/{name}",
                    "mount_point": part.get("mountpoint"),
                    "label": part.get("label"),
                    "size_bytes": size_bytes,
                    "size_formatted": size_str,
                    "filesystem": part.get("fstype"),
                    "mounted": part.get("mountpoint") is not None,
                })
    
    except Exception:
        pass
    
    return storage


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


@app.get("/api/devices", response_model=List[USBDevice])
async def list_devices():
    """List all USB devices"""
    devices = parse_lsusb()
    
    # Add device paths for serial devices
    for dev in devices:
        dev["device_path"] = find_device_path(dev["vendor_id"], dev["product_id"])
    
    return [USBDevice(**d) for d in devices]


@app.get("/api/known", response_model=List[KnownDevice])
async def list_known_devices():
    """List known MuleCube peripherals with status"""
    known = get_known_devices()
    return [KnownDevice(**k) for k in known]


@app.get("/api/storage", response_model=List[StorageDevice])
async def list_storage():
    """List USB storage devices"""
    storage = get_storage_devices()
    return [StorageDevice(**s) for s in storage]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
