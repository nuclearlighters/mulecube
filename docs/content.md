# Adding Content

MuleCube comes pre-loaded with essential content, but you can add your own maps, books, media, and documents. This guide shows you how.

## Content Overview

| Content Type | Service | Location | Formats |
|--------------|---------|----------|---------|
| Wikipedia/Reference | Kiwix | `/srv/kiwix/data/` | .zim |
| Maps | Tileserver | `/srv/maps/data/` | .mbtiles, .pmtiles |
| E-Books | Calibre | `/srv/calibre/library/` | .epub, .mobi, .pdf |
| Media | Jellyfin | `/srv/jellyfin/media/` | .mp4, .mkv, .mp3 |
| Documents | CryptPad/Files | `/srv/Documents/` | Any |
| AI Models | Ollama | `/srv/ollama/models/` | GGUF |

## Prerequisites

For adding content, you'll need:

- **USB drive** (formatted as exFAT or ext4)
- **Or** temporary internet connection
- **Or** access via Syncthing

## Adding Wikipedia & Reference Content (Kiwix)

### Available Content

Download ZIM files from: https://library.kiwix.org

Popular packages:

| Content | Size | Description |
|---------|------|-------------|
| Wikipedia (English) | 95GB | Full English Wikipedia with images |
| Wikipedia (Simple) | 1.5GB | Simplified English, great for kids |
| Wiktionary | 5GB | Dictionary and thesaurus |
| Wikivoyage | 700MB | Travel guides worldwide |
| Stack Overflow | 20GB | Programming Q&A |
| TED Talks | 15GB | Educational videos |
| Khan Academy | 30GB | Math & science courses |
| Medical (WikiMed) | 800MB | Medical encyclopedia |

### Adding ZIM Files via USB

1. **Download ZIM file** on a computer with internet
2. **Copy to USB drive**
3. **Connect USB to MuleCube**
4. **Copy to Kiwix directory:**

```bash
# Find your USB drive
lsblk

# Mount if needed
sudo mount /dev/sda1 /mnt

# Copy ZIM file
sudo cp /mnt/wikipedia_en_all.zim /srv/kiwix/data/

# Restart Kiwix to detect new content
cd /srv/kiwix && docker compose restart
```

5. **Access new content** at http://192.168.42.1:8080

### Adding ZIM Files via Download

If temporarily connected to internet:

```bash
# Download directly (example: Simple English Wikipedia)
cd /srv/kiwix/data/
wget https://download.kiwix.org/zim/wikipedia_en_simple_all.zim

# Restart Kiwix
cd /srv/kiwix && docker compose restart
```

## Adding Offline Maps

### Map Sources

| Source | Description | Format |
|--------|-------------|--------|
| OpenMapTiles | Street maps | .mbtiles |
| Protomaps | Modern vector tiles | .pmtiles |
| OpenTopoMap | Topographic maps | .mbtiles |

Download from:
- https://openmaptiles.org/downloads/
- https://protomaps.com/downloads
- https://www.opentopomap.org/

### Adding Map Tiles

1. **Download map file** for your region
2. **Copy to MuleCube:**

```bash
# Via USB
sudo cp /mnt/netherlands.mbtiles /srv/maps/data/

# Or via SCP from another computer
scp netherlands.mbtiles pi@192.168.42.1:/srv/maps/data/
```

3. **Update map configuration:**

```bash
sudo nano /srv/maps/config.json

# Add your new map source
```

4. **Restart map service:**

```bash
cd /srv/maps && docker compose restart
```

### Recommended Map Packages

| Region | File Size | Coverage |
|--------|-----------|----------|
| World (basic) | 5GB | All countries, low detail |
| Europe | 15GB | Detailed European maps |
| North America | 12GB | US, Canada, Mexico |
| Netherlands | 500MB | Detailed local maps |
| Custom region | Varies | Generate at openmaptiles.org |

## Adding E-Books (Calibre)

### Supported Formats

- **EPUB** (recommended)
- **MOBI** / **AZW3** (Kindle)
- **PDF**
- **TXT**, **RTF**, **HTML**
- **CBZ**, **CBR** (comics)

### Method 1: Web Upload

1. Go to http://192.168.42.1:8083
2. Click **Upload** or drag-and-drop files
3. Books are automatically added to library

### Method 2: USB Transfer

```bash
# Copy from USB
sudo cp -r /mnt/ebooks/* /srv/calibre/library/

# Rescan library
cd /srv/calibre && docker compose exec calibre calibredb add /library/
```

### Method 3: Calibre Desktop Sync

On your computer with Calibre:

1. Install Calibre desktop
2. Connect to MuleCube via network
3. Use "Connect/Share" → "Connect to server"
4. Transfer books directly

### Organizing Books

- **Tags:** Add tags for easy filtering
- **Shelves:** Create custom collections
- **Metadata:** Edit title, author, description
- **Covers:** Upload custom cover images

### Free E-Book Sources

| Source | Content |
|--------|---------|
| Project Gutenberg | 60,000+ classic books |
| Standard Ebooks | Beautifully formatted classics |
| Open Library | Millions of books |
| ManyBooks | Free EPUB downloads |

## Adding Media (Jellyfin)

### Supported Formats

**Video:** MP4, MKV, AVI, MOV, WebM
**Audio:** MP3, FLAC, AAC, OGG, WAV
**Images:** JPG, PNG, GIF

### Directory Structure

```
/srv/jellyfin/media/
├── movies/
│   └── Movie Name (2024)/
│       └── Movie Name (2024).mp4
├── tv/
│   └── Show Name/
│       └── Season 01/
│           └── Show Name - S01E01 - Episode Title.mp4
├── music/
│   └── Artist Name/
│       └── Album Name/
│           └── 01 - Track Name.mp3
└── photos/
    └── Event Name/
        └── photo001.jpg
```

### Adding Media

```bash
# Create directories
sudo mkdir -p /srv/jellyfin/media/{movies,tv,music,photos}

# Copy from USB
sudo cp -r /mnt/movies/* /srv/jellyfin/media/movies/

# Set permissions
sudo chown -R 1000:1000 /srv/jellyfin/media/

# Scan library in Jellyfin web UI
# Go to Dashboard → Libraries → Scan All Libraries
```

### Optimizing for MuleCube

For smooth playback on Pi 5:

- **Resolution:** 1080p recommended (4K may stutter)
- **Codec:** H.264 preferred (hardware decoding)
- **Bitrate:** Under 20Mbps for reliable streaming
- **Audio:** AAC or MP3 for compatibility

### Media Preparation

Use HandBrake to optimize videos:

1. Output: MP4 (H.264)
2. Resolution: 1080p or 720p
3. Quality: RF 20-23
4. Audio: AAC 192kbps

## Adding AI Models (Ollama)

### Available Models

| Model | Size | Strengths |
|-------|------|-----------|
| phi3:mini | 2.3GB | Fast, general purpose |
| llama2:7b | 4GB | Good reasoning |
| mistral:7b | 4.1GB | Coding, analysis |
| deepseek-r1:7b | 4.7GB | Complex reasoning |
| qwen2.5:7b | 4.4GB | Multilingual |

### Adding New Models

```bash
# Enter Ollama container
docker exec -it ollama ollama pull mistral:7b

# Or via API
curl http://192.168.42.1:11434/api/pull -d '{"name": "mistral:7b"}'
```

### Removing Models

```bash
docker exec -it ollama ollama rm model_name
```

### Model Recommendations

| Use Case | Recommended Model |
|----------|------------------|
| Quick questions | phi3:mini |
| Writing/creative | qwen2.5:7b |
| Coding | deepseek-coder |
| Analysis | deepseek-r1:7b |
| Multilingual | qwen2.5:7b |

## Adding Custom Documents

### Shared Documents Folder

For general file storage:

```bash
# Location
/srv/Documents/

# Copy files
sudo cp -r /mnt/important-docs/* /srv/Documents/

# Access via File Browser
# http://192.168.42.1:8085
```

### Syncthing Folders

For continuous sync between devices:

1. Go to http://192.168.42.1:8384
2. Add folder to sync
3. Share with your other devices
4. Files stay synchronized

## Content via Syncthing

Syncthing enables continuous synchronization:

### Setup

1. **On MuleCube:** http://192.168.42.1:8384
2. **On your computer:** Install Syncthing
3. **Exchange device IDs**
4. **Create shared folder**
5. **Content syncs automatically**

### Use Cases

- Sync ebook library from main computer
- Continuous backup of expedition notes
- Share maps with team members
- Keep documents updated across devices

## Storage Management

### Check Available Space

```bash
# On dashboard stats bar
# Or via terminal:
df -h /srv
```

### Pre-installed Content Size

| Content | Size |
|---------|------|
| Wikipedia EN | ~95GB |
| Offline maps | ~10GB |
| AI models | ~15GB |
| System & services | ~20GB |
| **Typical used:** | ~140GB |
| **Available (256GB):** | ~100GB |

### Cleanup Tips

```bash
# Remove unused Docker images
docker image prune -a

# Clear old logs
sudo journalctl --vacuum-time=7d

# Remove unused Kiwix content
rm /srv/kiwix/data/old_file.zim
```

## Content Backup

Before making major changes:

```bash
# Backup critical content
sudo tar -czvf /backup/content-$(date +%Y%m%d).tar.gz \
    /srv/calibre/library/ \
    /srv/Documents/ \
    /srv/cryptpad/data/
```

## Troubleshooting

### Content Not Appearing

1. Check file permissions:
```bash
ls -la /srv/service/data/
sudo chown -R 1000:1000 /srv/service/data/
```

2. Restart the service:
```bash
cd /srv/service && docker compose restart
```

3. Check service logs:
```bash
docker logs service_name
```

### USB Drive Not Detected

```bash
# List all drives
lsblk

# Check for drive
sudo fdisk -l

# Mount manually
sudo mount /dev/sda1 /mnt
```

### Out of Storage

```bash
# Find large files
du -sh /srv/* | sort -h

# Consider removing:
# - Unused ZIM files
# - Old media
# - Unused AI models
```

## Quick Reference

| Content Type | Location | Add Method |
|--------------|----------|------------|
| Wikipedia | `/srv/kiwix/data/` | Copy .zim files |
| Maps | `/srv/maps/data/` | Copy .mbtiles |
| Books | `/srv/calibre/library/` | Web upload or copy |
| Media | `/srv/jellyfin/media/` | Copy to subfolders |
| Documents | `/srv/Documents/` | File Browser or copy |
| AI Models | Ollama container | `ollama pull` command |
