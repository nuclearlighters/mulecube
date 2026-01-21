# Using the Services

MuleCube includes 30+ pre-installed services, all running locally and accessible without internet. This guide explains what each service does and how to use it.

## Knowledge Services

### Wikipedia (Kiwix)

**URL:** http://192.168.42.1:8080

Full offline Wikipedia with 6+ million articles, images, and the complete article history.

**Features:**
- Search across all articles
- Browse by category
- View images and diagrams
- Available in multiple languages (content packs)

**Tips:**
- Use the search bar for quick lookups
- Bookmark frequently accessed articles
- The "Random" button is great for exploration

**Content included:**
- English Wikipedia (90GB+)
- Wiktionary
- Wikivoyage travel guides
- Medical references (optional)

### Offline Maps (Tileserver)

**URL:** http://192.168.42.1:8081

OpenStreetMap-based offline maps with worldwide coverage.

**Features:**
- Pan and zoom like Google Maps
- Search for locations
- Satellite imagery (where available)
- Topographic layers

**Tips:**
- Download regional map packs before expeditions
- Use the layer switcher for different views
- Maps work offline — no internet needed

**Pre-loaded regions:**
- Your local region (configured during setup)
- Additional regions can be added — see [Adding Content](content.md)

### E-Book Library (Calibre)

**URL:** http://192.168.42.1:8083

Complete e-book management system with reader.

**Features:**
- Browse your library
- Read books in browser
- Download for offline reading
- Search across all books
- Organize with tags and shelves

**Supported formats:**
- EPUB, MOBI, AZW3
- PDF
- TXT, RTF, HTML

**Pre-loaded content:**
- Project Gutenberg classics
- Survival/medical references
- Technical manuals
- Add your own — see [Adding Content](content.md)

---

## AI Services

### AI Chat (Open WebUI + Ollama)

**URL:** http://192.168.42.1:3000

Chat with powerful AI models running entirely on your MuleCube — no internet, no data sharing.

**Available models:**

| Model | Size | Best for |
|-------|------|----------|
| Phi-3 Mini | 2.3GB | General conversation, fast responses |
| DeepSeek-R1 | 4.7GB | Reasoning, analysis, coding |
| Qwen 2.5 | 4.4GB | Multilingual, creative writing |

**Features:**
- Natural conversation
- Code assistance
- Translation
- Writing help
- Document analysis (upload files)

**Tips:**
- Be specific in your prompts for better results
- Phi-3 is fastest; use DeepSeek for complex reasoning
- Create custom "personas" for specialized tasks

**Limitations:**
- Response time: 5-30 seconds depending on model and query
- Knowledge cutoff: Models have training date limitations
- No internet: Cannot access real-time information

### LibreTranslate

**URL:** http://192.168.42.1:5000

Offline translation between 49 languages.

**Supported languages include:**
- English, Spanish, French, German, Italian
- Chinese, Japanese, Korean
- Arabic, Russian, Portuguese
- And 40+ more

**Features:**
- Text translation
- Language auto-detection
- API for programmatic access
- No character limits

**Tips:**
- For best results, use simple sentence structures
- Technical terms may need context
- Check translations with native speakers when possible

---

## Productivity Services

### CryptPad

**URL:** http://192.168.42.1:3001

Collaborative documents, spreadsheets, and presentations with real-time sync.

**Document types:**
- **Rich Text** — Word processor
- **Sheets** — Spreadsheets
- **Slides** — Presentations
- **Code** — Syntax-highlighted code editor
- **Kanban** — Task boards
- **Whiteboard** — Freeform drawing
- **Form** — Surveys and forms

**Features:**
- Real-time collaboration
- End-to-end encryption
- Version history
- Share via links
- No account required (optional registration)

**Tips:**
- Create an account to save your documents
- Share links with other MuleCube users
- Export to standard formats (docx, xlsx, pdf)

### HedgeDoc

**URL:** http://192.168.42.1:3002

Collaborative Markdown editor for notes and documentation.

**Features:**
- Live Markdown preview
- Real-time collaboration
- Slide mode for presentations
- Code syntax highlighting
- Diagram support (Mermaid, PlantUML)

**Best for:**
- Meeting notes
- Technical documentation
- Quick collaborative editing

### Excalidraw

**URL:** http://192.168.42.1:3003

Virtual whiteboard for diagrams and sketching.

**Features:**
- Hand-drawn style graphics
- Shapes, arrows, text
- Real-time collaboration
- Export to PNG, SVG
- Libraries of pre-made elements

**Tips:**
- Great for architecture diagrams
- Use keyboard shortcuts for speed
- Import existing Excalidraw files

### Vaultwarden

**URL:** http://192.168.42.1:8000

Self-hosted password manager (Bitwarden-compatible).

**Features:**
- Secure password storage
- Password generator
- Two-factor authentication
- Secure notes
- Browser extension support

**Setup:**
1. Create an account on first visit
2. Install Bitwarden browser extension
3. Point extension to: `http://192.168.42.1:8000`
4. Log in with your credentials

**Security:**
- All data encrypted locally
- Master password never leaves your device
- Works offline once synced

### Stirling PDF

**URL:** http://192.168.42.1:8082

Complete PDF toolkit.

**Features:**
- Merge PDFs
- Split PDFs
- Compress files
- Convert to/from PDF
- Add watermarks
- Sign documents
- OCR text extraction
- Rotate, rearrange pages

---

## Communication Services

### Meshtastic Web

**URL:** http://192.168.42.1:8084

Interface for Meshtastic LoRa mesh networking (requires hardware).

**Features:**
- Send/receive encrypted messages
- View network topology
- Configure radio settings
- GPS location sharing

**Requirements:**
- Meshtastic-compatible radio
- Included with Cube Sat and Ultimate

**Range:**
- Urban: 1-3 km
- Rural/Line of sight: 10-30 km
- With repeaters: Unlimited

### Matrix Chat (Conduit + Element)

**URL:** http://192.168.42.1:8085

Secure, decentralized chat for your local network.

**Features:**
- Private chat rooms
- File sharing
- End-to-end encryption
- Works without internet

**Setup:**
1. Create account on first visit
2. Create or join rooms
3. Invite other MuleCube users

---

## Media Services

### Jellyfin

**URL:** http://192.168.42.1:8096

Media server for movies, music, and photos.

**Features:**
- Stream to any device
- Automatic metadata
- Multiple user profiles
- Resume playback
- Transcoding for compatibility

**Adding media:**
See [Adding Content](content.md) for instructions on loading your media library.

### File Browser

**URL:** http://192.168.42.1:8085

Web-based file manager.

**Features:**
- Browse all MuleCube files
- Upload/download
- Create folders
- Edit text files
- Share links

**Default credentials:**
- Username: `admin`
- Password: `admin`
- **Change these immediately!**

---

## Infrastructure Services

### Pi-hole

**URL:** http://192.168.42.1:8053/admin

Network-wide ad blocking and DNS management.

**Features:**
- Blocks ads on all connected devices
- Query logging
- Custom DNS entries
- Blocklist management

**Default password:** `mulecube` (change in settings)

### Syncthing

**URL:** http://192.168.42.1:8384

Continuous file synchronization between devices.

**Features:**
- Sync folders between devices
- No cloud required
- Encrypted transfers
- Versioning

**Setup:**
1. Install Syncthing on your other devices
2. Add MuleCube as a remote device
3. Share folders between devices

---

## Control Panel Services

### System Dashboard

**URL:** http://192.168.42.1

The main MuleCube dashboard showing all services and system status.

### Container Management (Dockge)

**URL:** http://192.168.42.1:5001

Manage Docker containers (advanced users).

**Features:**
- Start/stop services
- View logs
- Edit configurations
- Monitor resources

### Log Viewer (Dozzle)

**URL:** http://192.168.42.1:9999

Real-time container logs.

**Features:**
- View all service logs
- Search and filter
- Download logs

### Web Terminal (ttyd)

**URL:** http://192.168.42.1:7681

Browser-based terminal access.

**Features:**
- Full shell access
- No SSH client needed
- Command history

**Default credentials:**
- Username: `pi`
- Password: Set during installation

---

## Service Status

The dashboard shows the status of all services:

| Status | Meaning |
|--------|---------|
| 🟢 Green | Running normally |
| 🟡 Yellow | Starting or warning |
| 🔴 Red | Stopped or error |

If a service shows red:
1. Click the service tile to check for errors
2. Use Dockge to view logs
3. Try restarting the service
4. See [Troubleshooting](troubleshooting.md)

---

## Service URLs Quick Reference

| Service | URL | Port |
|---------|-----|------|
| Dashboard | http://192.168.42.1 | 80 |
| Wikipedia | http://192.168.42.1:8080 | 8080 |
| Maps | http://192.168.42.1:8081 | 8081 |
| Calibre | http://192.168.42.1:8083 | 8083 |
| AI Chat | http://192.168.42.1:3000 | 3000 |
| Translate | http://192.168.42.1:5000 | 5000 |
| CryptPad | http://192.168.42.1:3001 | 3001 |
| HedgeDoc | http://192.168.42.1:3002 | 3002 |
| Excalidraw | http://192.168.42.1:3003 | 3003 |
| Vaultwarden | http://192.168.42.1:8000 | 8000 |
| PDF Tools | http://192.168.42.1:8082 | 8082 |
| Jellyfin | http://192.168.42.1:8096 | 8096 |
| Pi-hole | http://192.168.42.1:8053/admin | 8053 |
| Syncthing | http://192.168.42.1:8384 | 8384 |
| Dockge | http://192.168.42.1:5001 | 5001 |
| Dozzle | http://192.168.42.1:9999 | 9999 |
| Terminal | http://192.168.42.1:7681 | 7681 |
