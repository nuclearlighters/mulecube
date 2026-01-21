"""
MuleCube Hardware Monitor Service
Provides system temperature, battery status, and throttling information via REST API

Supports:
- Raspberry Pi 5 temperature monitoring via /sys/class/thermal
- MAX17048 fuel gauge (Geekworm UPS HAT) at I2C address 0x36
- Throttling detection via /sys/devices/platform/soc/soc:firmware/get_throttled
"""

import os
import subprocess
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="MuleCube Hardware Monitor",
    description="Hardware monitoring API for MuleCube devices",
    version="1.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment
UPS_I2C_ADDRESS = int(os.getenv("UPS_I2C_ADDRESS", "0x36"), 16)
BATTERY_CAPACITY_MAH = int(os.getenv("BATTERY_CAPACITY_MAH", "3000"))
CRITICAL_BATTERY_PERCENT = int(os.getenv("CRITICAL_BATTERY_PERCENT", "10"))

# Startup time for uptime calculation
START_TIME = datetime.utcnow()


class TemperatureResponse(BaseModel):
    cpu_temp_c: float
    throttled: bool
    throttle_flags: str
    soft_temp_limit: bool
    under_voltage: bool
    status: str


class BatteryResponse(BaseModel):
    available: bool
    voltage: Optional[float] = None
    percent: Optional[int] = None
    charging: Optional[bool] = None
    time_remaining: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None


class SystemResponse(BaseModel):
    temperature: TemperatureResponse
    battery: Optional[BatteryResponse]
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime_seconds: float


def get_temperature() -> dict:
    """Get CPU temperature and throttling status from sysfs"""
    temp = 0.0
    throttle_value = 0
    
    thermal_paths = [
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/class/thermal/thermal_zone1/temp",
    ]
    
    for path in thermal_paths:
        try:
            with open(path, 'r') as f:
                temp = int(f.read().strip()) / 1000.0
                break
        except (FileNotFoundError, IOError, ValueError):
            continue
    
    throttle_paths = [
        "/sys/devices/platform/soc/soc:firmware/get_throttled",
        "/sys/class/hwmon/hwmon0/throttled",
    ]
    
    for path in throttle_paths:
        try:
            with open(path, 'r') as f:
                throttle_value = int(f.read().strip(), 16)
                break
        except (FileNotFoundError, IOError, ValueError):
            try:
                result = subprocess.run(
                    ["vcgencmd", "get_throttled"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    throttle_str = result.stdout.strip().replace("throttled=", "")
                    throttle_value = int(throttle_str, 16)
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
    
    under_voltage = bool(throttle_value & 0x1)
    freq_capped = bool(throttle_value & 0x2)
    throttled = bool(throttle_value & 0x4)
    soft_temp_limit = bool(throttle_value & 0x8)
    
    if throttled:
        status = "throttled"
    elif soft_temp_limit:
        status = "warm"
    elif temp >= 80:
        status = "hot"
    elif temp >= 70:
        status = "warm"
    elif temp > 0:
        status = "normal"
    else:
        status = "unknown"
    
    return {
        "cpu_temp_c": round(temp, 1),
        "throttled": throttled,
        "throttle_flags": hex(throttle_value),
        "soft_temp_limit": soft_temp_limit,
        "under_voltage": under_voltage,
        "status": status
    }


def get_battery_status() -> Optional[dict]:
    """
    Get battery status from MAX17048 fuel gauge via I2C
    
    MAX17048 registers:
    - 0x02: VCELL (voltage)
    - 0x04: SOC (state of charge)
    """
    try:
        import smbus2
        
        bus = smbus2.SMBus(1)
        address = UPS_I2C_ADDRESS
        
        # Read voltage from register 0x02
        v_raw = bus.read_word_data(address, 0x02)
        v_swapped = ((v_raw & 0x00FF) << 8) | ((v_raw >> 8) & 0xFF)
        voltage = v_swapped * 78.125 / 1000000
        
        # Read SOC from register 0x04
        soc_raw = bus.read_word_data(address, 0x04)
        soc_swapped = ((soc_raw & 0x00FF) << 8) | ((soc_raw >> 8) & 0xFF)
        percent = soc_swapped / 256.0
        
        bus.close()
        
        # Clamp percent to 0-100
        percent = max(0, min(100, int(percent)))
        
        # Charging detection heuristic:
        # MAX17048 doesn't report charge current, so we estimate:
        # - At high SOC (>90%) with voltage >4.1V = likely float charging or full
        # - At lower SOC with voltage >4.18V = likely active charging
        # - Otherwise = assume on battery
        if percent >= 90 and voltage >= 4.10:
            charging = True  # Float charge or maintenance
            status = "full" if percent >= 98 else "charging"
            time_remaining = None
        elif voltage >= 4.18:
            charging = True  # Active charging (voltage elevated)
            status = "charging"
            # Estimate time to full
            missing_pct = 100 - percent
            time_remaining = f"~{int(missing_pct * 1.5)}m to full" if missing_pct > 0 else None
        else:
            charging = False
            # Calculate time remaining on battery
            if percent > 0:
                remaining_mah = BATTERY_CAPACITY_MAH * (percent / 100)
                avg_draw_ma = 500
                hours = remaining_mah / avg_draw_ma
                h = int(hours)
                m = int((hours - h) * 60)
                time_remaining = f"{h}h {m}m"
            else:
                time_remaining = None
            
            # Determine status
            if percent <= CRITICAL_BATTERY_PERCENT:
                status = "critical"
            elif percent <= 20:
                status = "low"
            else:
                status = "discharging"
        
        return {
            "available": True,
            "voltage": round(voltage, 2),
            "percent": percent,
            "charging": charging,
            "time_remaining": time_remaining,
            "status": status
        }
        
    except FileNotFoundError:
        return None
    except OSError:
        return None
    except Exception as e:
        print(f"Battery read error: {e}")
        return None


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.utcnow() - START_TIME).total_seconds()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        uptime_seconds=round(uptime, 2)
    )


@app.get("/api/temperature", response_model=TemperatureResponse)
async def get_temp():
    """Get CPU temperature and throttling status"""
    temp_data = get_temperature()
    return TemperatureResponse(**temp_data)


@app.get("/api/battery", response_model=BatteryResponse)
async def get_battery():
    """Get battery status (returns null if no UPS detected)"""
    status = get_battery_status()
    if status is None:
        return BatteryResponse(available=False, message="No UPS/battery detected")
    return BatteryResponse(**status)


@app.get("/api/system", response_model=SystemResponse)
async def get_system():
    """Get combined system status"""
    temp = get_temperature()
    battery = get_battery_status()
    
    return SystemResponse(
        temperature=TemperatureResponse(**temp),
        battery=BatteryResponse(**battery) if battery else BatteryResponse(available=False),
        timestamp=datetime.utcnow().isoformat()
    )




@app.post("/api/reboot")
async def reboot_system():
    """Trigger system reboot"""
    try:
        subprocess.Popen(["shutdown", "-r", "+1", "MuleCube reboot requested via API"])
        return {"status": "reboot_scheduled", "message": "System will reboot in 1 minute"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate reboot: {str(e)}")


@app.post("/api/reboot/cancel")
async def cancel_reboot():
    """Cancel a pending reboot"""
    try:
        subprocess.run(["shutdown", "-c"], check=True)
        return {"status": "reboot_cancelled"}
    except subprocess.CalledProcessError:
        return {"status": "no_reboot_pending"}

@app.post("/api/shutdown")
async def shutdown_system():
    """Trigger graceful system shutdown"""
    try:
        subprocess.Popen(["shutdown", "-h", "+1", "MuleCube shutdown requested via API"])
        return {"status": "shutdown_scheduled", "message": "System will shut down in 1 minute"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate shutdown: {str(e)}")


@app.post("/api/shutdown/cancel")
async def cancel_shutdown():
    """Cancel a pending shutdown"""
    try:
        subprocess.run(["shutdown", "-c"], check=True)
        return {"status": "shutdown_cancelled"}
    except subprocess.CalledProcessError:
        return {"status": "no_shutdown_pending"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
