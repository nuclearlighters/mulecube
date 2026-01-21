"""
MuleCube Watchdog
Self-healing daemon for service monitoring

Features:
  - Auto-restart failed/unhealthy containers
  - Thermal shedding (stop heavy services when hot)
  - Battery shedding (stop non-essential services when low)
  - Restart cooldown to prevent loops
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Set
import docker
import requests

# =============================================================================
# Configuration
# =============================================================================

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", "30"))
MAX_RESTART_ATTEMPTS = int(os.getenv("MAX_RESTART_ATTEMPTS", "3"))
RESTART_COOLDOWN = int(os.getenv("RESTART_COOLDOWN_SECONDS", "300"))

CRITICAL_SERVICES = os.getenv("CRITICAL_SERVICES", "kiwix,tileserver,nginx,dnsmasq").split(",")
THERMAL_SHED_SERVICES = os.getenv("THERMAL_SHED_SERVICES", "ollama,retroarch,navidrome").split(",")
THERMAL_SHED_TEMP = int(os.getenv("THERMAL_SHED_TEMP_C", "80"))
BATTERY_SHED_SERVICES = os.getenv("BATTERY_SHED_SERVICES", "ollama,retroarch,navidrome,openwebui").split(",")
BATTERY_SHED_PERCENT = int(os.getenv("BATTERY_SHED_PERCENT", "15"))

HW_MONITOR_URL = os.getenv("HW_MONITOR_URL", "http://mulecube-hw-monitor:8080")

# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("watchdog")

# =============================================================================
# State Tracking
# =============================================================================

# Track restart attempts per container
restart_attempts: Dict[str, int] = {}

# Track last restart time per container
last_restart: Dict[str, datetime] = {}

# Track services we've intentionally stopped (thermal/battery shedding)
shed_services: Set[str] = set()

# =============================================================================
# Helper Functions
# =============================================================================

def get_hw_status() -> dict:
    """Fetch hardware status from hw-monitor"""
    try:
        response = requests.get(f"{HW_MONITOR_URL}/api/system", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.warning(f"Failed to fetch hw-monitor status: {e}")
    return {}


def should_restart(container_name: str) -> bool:
    """Check if container should be restarted (cooldown, max attempts)"""
    now = datetime.now()
    
    # Check cooldown
    if container_name in last_restart:
        cooldown_end = last_restart[container_name] + timedelta(seconds=RESTART_COOLDOWN)
        if now < cooldown_end:
            return False
    
    # Check max attempts
    if restart_attempts.get(container_name, 0) >= MAX_RESTART_ATTEMPTS:
        logger.warning(f"Container {container_name} exceeded max restart attempts")
        return False
    
    return True


def restart_container(client: docker.DockerClient, container_name: str) -> bool:
    """Restart a container with tracking"""
    if not should_restart(container_name):
        return False
    
    try:
        container = client.containers.get(container_name)
        logger.info(f"Restarting container: {container_name}")
        container.restart(timeout=30)
        
        # Update tracking
        restart_attempts[container_name] = restart_attempts.get(container_name, 0) + 1
        last_restart[container_name] = datetime.now()
        
        return True
    except Exception as e:
        logger.error(f"Failed to restart {container_name}: {e}")
        return False


def stop_container(client: docker.DockerClient, container_name: str, reason: str) -> bool:
    """Stop a container for shedding"""
    try:
        container = client.containers.get(container_name)
        if container.status == "running":
            logger.info(f"Stopping container for {reason}: {container_name}")
            container.stop(timeout=30)
            shed_services.add(container_name)
            return True
    except docker.errors.NotFound:
        pass
    except Exception as e:
        logger.error(f"Failed to stop {container_name}: {e}")
    return False


def start_container(client: docker.DockerClient, container_name: str) -> bool:
    """Start a previously shed container"""
    try:
        container = client.containers.get(container_name)
        if container.status != "running":
            logger.info(f"Restarting shed container: {container_name}")
            container.start()
            shed_services.discard(container_name)
            return True
    except docker.errors.NotFound:
        pass
    except Exception as e:
        logger.error(f"Failed to start {container_name}: {e}")
    return False


def container_matches(container_name: str, patterns: list) -> bool:
    """Check if container name matches any pattern"""
    name_lower = container_name.lower()
    return any(p.lower() in name_lower for p in patterns)


# =============================================================================
# Main Monitoring Functions
# =============================================================================

def check_container_health(client: docker.DockerClient):
    """Check and restart unhealthy containers"""
    try:
        containers = client.containers.list(all=True)
        
        for container in containers:
            name = container.name
            
            # Skip containers we intentionally shed
            if name in shed_services:
                continue
            
            # Check if container should be running
            restart_policy = container.attrs.get("HostConfig", {}).get("RestartPolicy", {})
            if restart_policy.get("Name") == "no":
                continue
            
            # Check health status
            health = container.attrs.get("State", {}).get("Health", {})
            health_status = health.get("Status") if health else None
            
            if health_status == "unhealthy":
                logger.warning(f"Container unhealthy: {name}")
                restart_container(client, name)
            
            # Check if critical service is stopped
            if container.status != "running" and container_matches(name, CRITICAL_SERVICES):
                logger.warning(f"Critical service stopped: {name}")
                restart_container(client, name)
    
    except Exception as e:
        logger.error(f"Error checking container health: {e}")


def check_thermal_shedding(client: docker.DockerClient, hw_status: dict):
    """Stop heavy services if temperature is critical"""
    temp = hw_status.get("temperature", {})
    cpu_temp = temp.get("cpu_temp_c", 0)
    
    if cpu_temp >= THERMAL_SHED_TEMP:
        logger.warning(f"CPU temperature critical ({cpu_temp}°C), shedding services")
        
        containers = client.containers.list()
        for container in containers:
            if container_matches(container.name, THERMAL_SHED_SERVICES):
                stop_container(client, container.name, "thermal shedding")
    
    elif cpu_temp < THERMAL_SHED_TEMP - 5:  # 5 degree hysteresis
        # Temperature recovered, restart shed services
        for service_name in list(shed_services):
            if container_matches(service_name, THERMAL_SHED_SERVICES):
                if not container_matches(service_name, BATTERY_SHED_SERVICES):
                    start_container(client, service_name)


def check_battery_shedding(client: docker.DockerClient, hw_status: dict):
    """Stop non-essential services if battery is low"""
    battery = hw_status.get("battery")
    
    if not battery or not battery.get("percent"):
        return  # No battery info available
    
    percent = battery["percent"]
    charging = battery.get("charging", False)
    
    if percent <= BATTERY_SHED_PERCENT and not charging:
        logger.warning(f"Battery low ({percent}%), shedding services")
        
        containers = client.containers.list()
        for container in containers:
            if container_matches(container.name, BATTERY_SHED_SERVICES):
                stop_container(client, container.name, "battery shedding")
    
    elif percent > BATTERY_SHED_PERCENT + 5 or charging:  # 5% hysteresis
        # Battery recovered, restart shed services
        for service_name in list(shed_services):
            if container_matches(service_name, BATTERY_SHED_SERVICES):
                start_container(client, service_name)


def reset_restart_counts():
    """Reset restart counts periodically (every hour)"""
    global restart_attempts
    restart_attempts = {}
    logger.info("Reset restart attempt counts")


# =============================================================================
# Main Loop
# =============================================================================

def main():
    logger.info("MuleCube Watchdog starting")
    logger.info(f"Check interval: {CHECK_INTERVAL}s")
    logger.info(f"Critical services: {CRITICAL_SERVICES}")
    logger.info(f"Thermal shed temp: {THERMAL_SHED_TEMP}°C")
    logger.info(f"Battery shed percent: {BATTERY_SHED_PERCENT}%")
    
    client = docker.from_env()
    last_reset = datetime.now()
    
    while True:
        try:
            # Get hardware status
            hw_status = get_hw_status()
            
            # Run checks
            check_container_health(client)
            check_thermal_shedding(client, hw_status)
            check_battery_shedding(client, hw_status)
            
            # Reset restart counts hourly
            if datetime.now() - last_reset > timedelta(hours=1):
                reset_restart_counts()
                last_reset = datetime.now()
        
        except Exception as e:
            logger.error(f"Watchdog error: {e}")
        
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
