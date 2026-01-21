"""
MuleCube Backup Service
Configuration backup and restore API

Endpoints:
  GET  /health           - Service health check
  GET  /api/backups      - List available backups
  POST /api/backup       - Create new backup
  POST /api/restore      - Restore from backup
  GET  /api/download/:id - Download backup file
  DELETE /api/backup/:id - Delete backup
"""

import os
import shutil
import subprocess
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# =============================================================================
# Configuration
# =============================================================================

BACKUP_DIR = Path(os.getenv("BACKUP_DIR", "/backups"))
BACKUP_PATHS = os.getenv("BACKUP_PATHS", "/srv").split(",")
EXCLUDE_PATHS = os.getenv("EXCLUDE_PATHS", "").split(",")
RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "7"))
USB_MOUNT = Path(os.getenv("USB_MOUNT", "/mnt/usb"))

# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="MuleCube Backup Service",
    description="Configuration backup and restore API",
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

class BackupInfo(BaseModel):
    id: str
    filename: str
    created_at: str
    size_bytes: int
    size_formatted: str

class BackupResult(BaseModel):
    success: bool
    backup_id: Optional[str]
    message: str

class RestoreResult(BaseModel):
    success: bool
    message: str

# =============================================================================
# Helper Functions
# =============================================================================

def format_size(size_bytes: int) -> str:
    """Format bytes to human readable"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def list_backups() -> List[dict]:
    """List all available backups"""
    backups = []
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    for f in BACKUP_DIR.glob("mulecube-backup-*.tar.gz"):
        stat = f.stat()
        
        # Parse timestamp from filename
        # Format: mulecube-backup-20240120-153045.tar.gz
        try:
            ts_str = f.stem.replace("mulecube-backup-", "")
            created = datetime.strptime(ts_str, "%Y%m%d-%H%M%S")
        except ValueError:
            created = datetime.fromtimestamp(stat.st_mtime)
        
        backups.append({
            "id": f.stem,
            "filename": f.name,
            "created_at": created.isoformat(),
            "size_bytes": stat.st_size,
            "size_formatted": format_size(stat.st_size),
        })
    
    # Sort by creation time, newest first
    backups.sort(key=lambda x: x["created_at"], reverse=True)
    
    return backups


def create_backup() -> dict:
    """Create a new backup archive"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_id = f"mulecube-backup-{timestamp}"
    backup_file = BACKUP_DIR / f"{backup_id}.tar.gz"
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Build exclude patterns
    excludes = []
    for path in EXCLUDE_PATHS:
        if path.strip():
            excludes.extend(["--exclude", path.strip()])
    
    # Create tarball
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        cmd = ["tar", "-czf", tmp_path]
        cmd.extend(excludes)
        
        for path in BACKUP_PATHS:
            path = path.strip()
            if path and Path(path).exists():
                cmd.append(path)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            raise Exception(f"tar failed: {result.stderr}")
        
        # Move to backup dir
        shutil.move(tmp_path, backup_file)
        
        stat = backup_file.stat()
        
        return {
            "success": True,
            "backup_id": backup_id,
            "filename": backup_file.name,
            "size_bytes": stat.st_size,
            "size_formatted": format_size(stat.st_size),
        }
    
    except Exception as e:
        # Cleanup temp file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise e


def restore_backup(backup_id: str) -> dict:
    """Restore from a backup archive"""
    backup_file = BACKUP_DIR / f"{backup_id}.tar.gz"
    
    if not backup_file.exists():
        raise FileNotFoundError(f"Backup not found: {backup_id}")
    
    # Extract to root (preserving paths)
    result = subprocess.run(
        ["tar", "-xzf", str(backup_file), "-C", "/"],
        capture_output=True,
        text=True,
        timeout=600
    )
    
    if result.returncode != 0:
        raise Exception(f"Restore failed: {result.stderr}")
    
    return {"success": True, "message": f"Restored from {backup_id}"}


def cleanup_old_backups():
    """Delete backups older than retention period"""
    cutoff = datetime.now().timestamp() - (RETENTION_DAYS * 86400)
    
    for f in BACKUP_DIR.glob("mulecube-backup-*.tar.gz"):
        if f.stat().st_mtime < cutoff:
            f.unlink()


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


@app.get("/api/backups", response_model=List[BackupInfo])
async def get_backups():
    """List available backups"""
    backups = list_backups()
    return [BackupInfo(**b) for b in backups]


@app.post("/api/backup", response_model=BackupResult)
async def create_new_backup(background_tasks: BackgroundTasks):
    """Create a new backup"""
    try:
        result = create_backup()
        
        # Schedule cleanup in background
        background_tasks.add_task(cleanup_old_backups)
        
        return BackupResult(
            success=True,
            backup_id=result["backup_id"],
            message=f"Backup created: {result['filename']} ({result['size_formatted']})"
        )
    except Exception as e:
        return BackupResult(
            success=False,
            backup_id=None,
            message=f"Backup failed: {str(e)}"
        )


@app.post("/api/restore/{backup_id}", response_model=RestoreResult)
async def restore_from_backup(backup_id: str):
    """Restore from a backup"""
    try:
        result = restore_backup(backup_id)
        return RestoreResult(**result)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Backup not found: {backup_id}")
    except Exception as e:
        return RestoreResult(
            success=False,
            message=f"Restore failed: {str(e)}"
        )


@app.get("/api/download/{backup_id}")
async def download_backup(backup_id: str):
    """Download a backup file"""
    backup_file = BACKUP_DIR / f"{backup_id}.tar.gz"
    
    if not backup_file.exists():
        raise HTTPException(status_code=404, detail=f"Backup not found: {backup_id}")
    
    return FileResponse(
        path=str(backup_file),
        filename=backup_file.name,
        media_type="application/gzip"
    )


@app.delete("/api/backup/{backup_id}")
async def delete_backup(backup_id: str):
    """Delete a backup"""
    backup_file = BACKUP_DIR / f"{backup_id}.tar.gz"
    
    if not backup_file.exists():
        raise HTTPException(status_code=404, detail=f"Backup not found: {backup_id}")
    
    backup_file.unlink()
    return {"success": True, "message": f"Deleted {backup_id}"}


@app.post("/api/export/{backup_id}")
async def export_to_usb(backup_id: str):
    """Export backup to USB drive"""
    backup_file = BACKUP_DIR / f"{backup_id}.tar.gz"
    
    if not backup_file.exists():
        raise HTTPException(status_code=404, detail=f"Backup not found: {backup_id}")
    
    # Check if USB is mounted
    if not USB_MOUNT.is_mount():
        raise HTTPException(status_code=400, detail="No USB drive mounted")
    
    dest = USB_MOUNT / backup_file.name
    shutil.copy2(backup_file, dest)
    
    return {"success": True, "message": f"Exported to {dest}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
