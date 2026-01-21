"""
MuleCube Reset Service
Factory reset functionality with three tiers

Endpoints:
  GET  /health          - Service health check
  GET  /api/options     - Get available reset options
  POST /api/reset/soft  - Soft reset (restart services)
  POST /api/reset/config - Config reset (reset settings, preserve content)
  POST /api/reset/factory - Factory reset (full wipe)
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import docker

# =============================================================================
# Configuration
# =============================================================================

RESET_SECRET = os.getenv("RESET_SECRET", "")
PRESERVE_PATHS = os.getenv("PRESERVE_PATHS", "").split(",")
SRV_PATH = Path("/srv")

# Paths that contain user data/content (preserved during config reset)
CONTENT_DIRS = [
    "kiwix/data",
    "maps/data", 
    "calibre/data",
    "filebrowser/data",
    "syncthing/data",
]

# Paths that contain configuration (reset during config reset)
CONFIG_PATTERNS = [
    "*/docker-compose.yml",
    "*/.env",
    "*/config/*",
]

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="MuleCube Reset Service",
    description="Factory reset API",
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

class ResetOption(BaseModel):
    type: str
    name: str
    description: str
    requires_auth: bool
    destructive: bool

class ResetResult(BaseModel):
    success: bool
    message: str
    details: List[str]

# =============================================================================
# Helper Functions
# =============================================================================

def verify_auth(authorization: str) -> bool:
    """Verify authorization header contains valid secret"""
    if not RESET_SECRET:
        return False
    
    if not authorization:
        return False
    
    # Expect "Bearer <secret>"
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return False
    
    return parts[1] == RESET_SECRET


def restart_all_services() -> List[str]:
    """Restart all Docker containers"""
    results = []
    
    try:
        client = docker.from_env()
        containers = client.containers.list()
        
        for container in containers:
            try:
                container.restart(timeout=30)
                results.append(f"Restarted: {container.name}")
            except Exception as e:
                results.append(f"Failed to restart {container.name}: {e}")
        
        client.close()
    except Exception as e:
        results.append(f"Docker error: {e}")
    
    return results


def reset_service_configs() -> List[str]:
    """Reset service configurations to defaults"""
    results = []
    
    # Stop all services first
    try:
        client = docker.from_env()
        containers = client.containers.list()
        
        for container in containers:
            try:
                container.stop(timeout=30)
                results.append(f"Stopped: {container.name}")
            except Exception as e:
                results.append(f"Failed to stop {container.name}: {e}")
        
        client.close()
    except Exception as e:
        results.append(f"Docker error: {e}")
    
    # Reset .env files to defaults
    for env_file in SRV_PATH.rglob(".env"):
        example = env_file.parent / ".env.example"
        if example.exists():
            try:
                shutil.copy2(example, env_file)
                results.append(f"Reset: {env_file}")
            except Exception as e:
                results.append(f"Failed to reset {env_file}: {e}")
    
    # Remove volumes (except preserved)
    try:
        client = docker.from_env()
        for volume in client.volumes.list():
            # Skip preserved volumes
            skip = False
            for preserve in PRESERVE_PATHS:
                if preserve.strip() and preserve in volume.name:
                    skip = True
                    break
            
            if not skip and "config" in volume.name.lower():
                try:
                    volume.remove()
                    results.append(f"Removed volume: {volume.name}")
                except Exception as e:
                    results.append(f"Failed to remove volume {volume.name}: {e}")
        
        client.close()
    except Exception as e:
        results.append(f"Volume cleanup error: {e}")
    
    # Restart services
    results.extend(restart_all_services())
    
    return results


def factory_reset() -> List[str]:
    """Full factory reset - removes all user data"""
    results = []
    
    # Stop all services
    try:
        subprocess.run(
            ["docker", "compose", "down", "--volumes", "--remove-orphans"],
            cwd="/srv",
            capture_output=True,
            timeout=300
        )
        results.append("Stopped all services")
    except Exception as e:
        results.append(f"Error stopping services: {e}")
    
    # Remove all Docker volumes
    try:
        client = docker.from_env()
        
        # Remove all volumes except system ones
        for volume in client.volumes.list():
            try:
                volume.remove(force=True)
                results.append(f"Removed volume: {volume.name}")
            except Exception as e:
                results.append(f"Failed to remove {volume.name}: {e}")
        
        # Prune system
        client.containers.prune()
        client.networks.prune()
        client.images.prune(filters={"dangling": True})
        
        client.close()
        results.append("Cleaned up Docker resources")
    except Exception as e:
        results.append(f"Docker cleanup error: {e}")
    
    # Reset all configurations
    for srv_dir in SRV_PATH.iterdir():
        if not srv_dir.is_dir():
            continue
        
        # Reset .env files
        env_file = srv_dir / ".env"
        example = srv_dir / ".env.example"
        if example.exists():
            try:
                shutil.copy2(example, env_file)
                results.append(f"Reset config: {srv_dir.name}")
            except Exception:
                pass
        
        # Remove data directories (except preserved)
        data_dir = srv_dir / "data"
        if data_dir.exists():
            preserve = any(
                p.strip() and str(data_dir).endswith(p.strip())
                for p in PRESERVE_PATHS
            )
            
            if not preserve:
                try:
                    shutil.rmtree(data_dir)
                    data_dir.mkdir()
                    results.append(f"Cleared data: {srv_dir.name}")
                except Exception as e:
                    results.append(f"Failed to clear {srv_dir.name}: {e}")
    
    results.append("Factory reset complete. Reboot recommended.")
    
    return results


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


@app.get("/api/options", response_model=List[ResetOption])
async def get_reset_options():
    """Get available reset options"""
    return [
        ResetOption(
            type="soft",
            name="Soft Reset",
            description="Restart all services without losing any data or settings",
            requires_auth=False,
            destructive=False
        ),
        ResetOption(
            type="config",
            name="Configuration Reset",
            description="Reset all service settings to defaults. Preserves offline content (Wikipedia, maps, ebooks)",
            requires_auth=True,
            destructive=True
        ),
        ResetOption(
            type="factory",
            name="Factory Reset",
            description="Complete reset to factory defaults. Removes all user data except large content files",
            requires_auth=True,
            destructive=True
        ),
    ]


@app.post("/api/reset/soft", response_model=ResetResult)
async def soft_reset():
    """Soft reset - restart all services"""
    results = restart_all_services()
    
    return ResetResult(
        success=True,
        message="Soft reset complete",
        details=results
    )


@app.post("/api/reset/config", response_model=ResetResult)
async def config_reset(authorization: str = Header(None)):
    """Configuration reset - reset settings, preserve content"""
    if not verify_auth(authorization):
        raise HTTPException(
            status_code=401,
            detail="Authorization required. Use 'Bearer <reset_secret>' header"
        )
    
    results = reset_service_configs()
    
    return ResetResult(
        success=True,
        message="Configuration reset complete",
        details=results
    )


@app.post("/api/reset/factory", response_model=ResetResult)
async def full_factory_reset(authorization: str = Header(None)):
    """Factory reset - full wipe"""
    if not verify_auth(authorization):
        raise HTTPException(
            status_code=401,
            detail="Authorization required. Use 'Bearer <reset_secret>' header"
        )
    
    results = factory_reset()
    
    return ResetResult(
        success=True,
        message="Factory reset complete. Please reboot the device.",
        details=results
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
