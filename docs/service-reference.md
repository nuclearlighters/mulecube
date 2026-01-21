# Service Reference

Complete reference for all MuleCube services, ports, and configurations.

## Service Overview

MuleCube runs 30+ services organized into categories:

| Category | Services | Purpose |
|----------|----------|---------|
| Knowledge | 4 | Wikipedia, maps, books, medical |
| AI | 3 | Chat, translation, models |
| Productivity | 6 | Documents, notes, passwords |
| Communication | 3 | Mesh, chat, sync |
| Media | 3 | Video, PDF, files |
| Infrastructure | 5 | DNS, proxy, monitoring |
| Control Panel | 8 | System management |

---

## Port Reference

### Public Services (User-Facing)

| Port | Service | URL |
|------|---------|-----|
| 80 | Dashboard / nginx | http://192.168.42.1 |
| 3000 | Open WebUI (AI) | http://192.168.42.1:3000 |
| 3001 | CryptPad | http://192.168.42.1:3001 |
| 3002 | HedgeDoc | http://192.168.42.1:3002 |
| 3003 | Excalidraw | http://192.168.42.1:3003 |
| 5000 | LibreTranslate | http://192.168.42.1:5000 |
| 8000 | Vaultwarden | http://192.168.42.1:8000 |
| 8053 | Pi-hole Admin | http://192.168.42.1:8053/admin |
| 8080 | Kiwix (Wikipedia) | http://192.168.42.1:8080 |
| 8081 | Tileserver (Maps) | http://192.168.42.1:8081 |
| 8082 | Stirling PDF | http://192.168.42.1:8082 |
| 8083 | Calibre Web | http://192.168.42.1:8083 |
| 8084 | Meshtastic Web | http://192.168.42.1:8084 |
| 8085 | File Browser | http://192.168.42.1:8085 |
| 8096 | Jellyfin | http://192.168.42.1:8096 |
| 8384 | Syncthing | http://192.168.42.1:8384 |

### Control Panel Services

| Port | Service | URL |
|------|---------|-----|
| 5001 | Dockge | http://192.168.42.1:5001 |
| 7681 | ttyd (Terminal) | http://192.168.42.1:7681 |
| 9001 | hw-monitor API | http://192.168.42.1:9001 |
| 9002 | wifi-status API | http://192.168.42.1:9002 |
| 9003 | usb-monitor API | http://192.168.42.1:9003 |
| 9004 | status-aggregator | http://192.168.42.1:9004 |
| 9999 | Dozzle (Logs) | http://192.168.42.1:9999 |

### Internal Services (APIs/Backend)

| Port | Service | Purpose |
|------|---------|---------|
| 53 | Pi-hole DNS | DNS resolution |
| 11434 | Ollama API | AI model serving |
| 8448 | Conduit (Matrix) | Federation |
| 22000 | Syncthing | File sync |

---

## Service Details

### Knowledge Services

#### Kiwix (Wikipedia)

| Property | Value |
|----------|-------|
| Port | 8080 |
| Image | `ghcr.io/kiwix/kiwix-serve` |
| Data | `/srv/kiwix/data/` |
| Config | `/srv/kiwix/docker-compose.yml` |

**Content location:** `/srv/kiwix/data/*.zim`

**Add content:**
```bash
cp new_content.zim /srv/kiwix/data/
cd /srv/kiwix && docker compose restart
```

#### Tileserver (Maps)

| Property | Value |
|----------|-------|
| Port | 8081 |
| Image | `maptiler/tileserver-gl` |
| Data | `/srv/maps/data/` |
| Config | `/srv/maps/config.json` |

**Supported formats:** `.mbtiles`, `.pmtiles`

#### Calibre Web

| Property | Value |
|----------|-------|
| Port | 8083 |
| Image | `lscr.io/linuxserver/calibre-web` |
| Library | `/srv/calibre/library/` |
| Config | `/srv/calibre/config/` |

**Default login:** admin / admin123 (change immediately)

---

### AI Services

#### Ollama

| Property | Value |
|----------|-------|
| Port | 11434 |
| Image | `ollama/ollama` |
| Models | `/srv/ollama/models/` |

**Manage models:**
```bash
# List models
docker exec ollama ollama list

# Pull model
docker exec ollama ollama pull phi3:mini

# Remove model
docker exec ollama ollama rm model_name
```

#### Open WebUI

| Property | Value |
|----------|-------|
| Port | 3000 |
| Image | `ghcr.io/open-webui/open-webui` |
| Data | `/srv/open-webui/data/` |

**Environment variables:**
- `OLLAMA_BASE_URL=http://ollama:11434`
- `WEBUI_AUTH=false` (no login required by default)

#### LibreTranslate

| Property | Value |
|----------|-------|
| Port | 5000 |
| Image | `libretranslate/libretranslate` |
| Data | `/srv/libretranslate/data/` |

**API usage:**
```bash
curl -X POST http://192.168.42.1:5000/translate \
  -H "Content-Type: application/json" \
  -d '{"q":"Hello","source":"en","target":"es"}'
```

---

### Productivity Services

#### CryptPad

| Property | Value |
|----------|-------|
| Port | 3001 |
| Image | `cryptpad/cryptpad` |
| Data | `/srv/cryptpad/data/` |
| Config | `/srv/cryptpad/config/` |

**Document types:** Rich text, Spreadsheet, Presentation, Kanban, Code, Whiteboard

#### HedgeDoc

| Property | Value |
|----------|-------|
| Port | 3002 |
| Image | `quay.io/hedgedoc/hedgedoc` |
| Data | `/srv/hedgedoc/data/` |

**Features:** Markdown, Real-time collaboration, Slide mode

#### Excalidraw

| Property | Value |
|----------|-------|
| Port | 3003 |
| Image | `excalidraw/excalidraw` |

**Note:** Stateless - drawings saved in browser/export

#### Vaultwarden

| Property | Value |
|----------|-------|
| Port | 8000 |
| Image | `vaultwarden/server` |
| Data | `/srv/vaultwarden/data/` |

**Admin panel:** http://192.168.42.1:8000/admin

**Bitwarden apps:** Point to `http://192.168.42.1:8000`

#### Stirling PDF

| Property | Value |
|----------|-------|
| Port | 8082 |
| Image | `frooodle/s-pdf` |

**Capabilities:** Merge, split, compress, convert, OCR, sign

#### IT Tools

| Property | Value |
|----------|-------|
| Port | 8086 |
| Image | `corentinth/it-tools` |

**Tools included:** Encoders, converters, generators, network tools

---

### Communication Services

#### Meshtastic Web

| Property | Value |
|----------|-------|
| Port | 8084 |
| Image | `meshtastic/web` |
| Device | `/dev/ttyUSB0` or `/dev/ttyACM0` |

**Requirements:** Meshtastic-compatible radio hardware

#### Conduit (Matrix)

| Property | Value |
|----------|-------|
| Port | 8448 |
| Image | `matrixconduit/matrix-conduit` |
| Data | `/srv/conduit/data/` |
| Config | `/srv/conduit/conduit.toml` |

**Client:** Element at same installation or any Matrix client

#### Syncthing

| Property | Value |
|----------|-------|
| Port | 8384 (web), 22000 (sync) |
| Image | `syncthing/syncthing` |
| Data | `/srv/syncthing/data/` |

---

### Media Services

#### Jellyfin

| Property | Value |
|----------|-------|
| Port | 8096 |
| Image | `jellyfin/jellyfin` |
| Media | `/srv/jellyfin/media/` |
| Config | `/srv/jellyfin/config/` |

**Directory structure:**
```
media/
├── movies/
├── tv/
├── music/
└── photos/
```

#### File Browser

| Property | Value |
|----------|-------|
| Port | 8085 |
| Image | `filebrowser/filebrowser` |
| Root | `/srv/` |

**Default login:** admin / admin

---

### Infrastructure Services

#### Pi-hole

| Property | Value |
|----------|-------|
| Port | 8053 (web), 53 (DNS) |
| Image | `pihole/pihole` |
| Config | `/srv/pihole/etc-pihole/` |

**Set password:**
```bash
docker exec -it pihole pihole -a -p
```

**Custom DNS:** Edit `/srv/pihole/etc-pihole/custom.list`

#### nginx Proxy

| Property | Value |
|----------|-------|
| Port | 80, 443 |
| Config | `/srv/nginx-proxy/nginx.conf` |

**Reverse proxy** for all services.

#### Beszel (Monitoring)

| Property | Value |
|----------|-------|
| Port | 8090 |
| Image | `henrygd/beszel` |
| Data | `/srv/beszel/data/` |

**Metrics:** CPU, memory, disk, network, containers

#### Uptime Kuma

| Property | Value |
|----------|-------|
| Port | 3001 |
| Image | `louislam/uptime-kuma` |
| Data | `/srv/uptime-kuma/data/` |

**Monitors:** Service health, response times, notifications

---

### Control Panel Services

#### hw-monitor

| Property | Value |
|----------|-------|
| Port | 9001 |
| Source | `/srv/mulecube-controlpanel-user/hw-monitor/` |

**Endpoints:**
- `GET /api/temperature` - CPU temp, throttling
- `GET /api/battery` - UPS status
- `GET /api/system` - Combined status
- `POST /api/reboot` - Trigger reboot
- `POST /api/shutdown` - Trigger shutdown

#### wifi-status

| Property | Value |
|----------|-------|
| Port | 9002 |
| Source | `/srv/mulecube-controlpanel-user/wifi-status/` |

**Endpoints:**
- `GET /api/clients` - Connected WiFi clients
- `GET /api/status` - AP status

#### Dockge

| Property | Value |
|----------|-------|
| Port | 5001 |
| Image | `louislam/dockge` |
| Stacks | `/srv/` |

**Capabilities:** Start, stop, restart, logs, compose editing

#### ttyd (Web Terminal)

| Property | Value |
|----------|-------|
| Port | 7681 |
| Image | `tsl0922/ttyd` |

**Full shell access** via browser.

#### Dozzle (Logs)

| Property | Value |
|----------|-------|
| Port | 9999 |
| Image | `amir20/dozzle` |

**Real-time logs** for all containers.

---

## Resource Requirements

### RAM Usage by Service

| Service | Idle | Active |
|---------|------|--------|
| Ollama (phi3) | 500MB | 2-4GB |
| Open WebUI | 200MB | 300MB |
| Kiwix | 100MB | 200MB |
| Jellyfin | 150MB | 500MB+ |
| CryptPad | 300MB | 500MB |
| Pi-hole | 50MB | 100MB |
| LibreTranslate | 500MB | 1GB |
| Other services | 50-100MB each | - |

**Total typical usage:** 4-6GB RAM

### Storage Usage

| Content | Size |
|---------|------|
| System + Docker | ~15GB |
| Wikipedia EN | ~95GB |
| AI Models | ~15GB |
| Maps (region) | ~10GB |
| Services data | ~5GB |
| **Typical total** | ~140GB |

---

## Environment Variables

Common environment variables across services:

| Variable | Default | Purpose |
|----------|---------|---------|
| `TZ` | `Europe/Amsterdam` | Timezone |
| `PUID` | `1000` | User ID for permissions |
| `PGID` | `1000` | Group ID for permissions |

---

## Docker Networks

| Network | Purpose | Services |
|---------|---------|----------|
| `mulecube` | Main network | All services |
| `bridge` | Default Docker | Legacy |

All services communicate via the `mulecube` network.

---

## Volumes & Persistence

**Data directories** (persistent, excluded from git):
- `/srv/*/data/`
- `/srv/*/config/`
- `/srv/*/library/`

**Configuration files** (in git):
- `/srv/*/docker-compose.yml`
- `/srv/*/*.toml`, `*.conf`

---

## Starting/Stopping Services

### Individual Service

```bash
cd /srv/service_name
docker compose up -d      # Start
docker compose stop       # Stop
docker compose restart    # Restart
docker compose down       # Stop and remove
docker compose logs -f    # View logs
```

### All Services

```bash
/srv/scripts/start-all.sh
/srv/scripts/stop-all.sh
/srv/scripts/status.sh
```

---

## Health Checks

Most services have built-in health checks:

```bash
# View health status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Check specific service
docker inspect --format='{{.State.Health.Status}}' service_name
```

---

## Backup Locations

Critical data to backup:

| Service | Backup Path |
|---------|-------------|
| Vaultwarden | `/srv/vaultwarden/data/` |
| CryptPad | `/srv/cryptpad/data/` |
| Calibre | `/srv/calibre/library/` |
| Syncthing | `/srv/syncthing/data/` |
| Documents | `/srv/Documents/` |
