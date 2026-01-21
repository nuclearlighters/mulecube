# Building Your Own MuleCube

This guide walks you through building a MuleCube from scratch. Total build time: 2-4 hours.

## Bill of Materials

### Required Components

| Component | Specification | Est. Cost |
|-----------|--------------|-----------|
| Raspberry Pi 5 | 8GB RAM recommended | €80-95 |
| Power Supply | Official Pi 5 27W USB-C | €15 |
| MicroSD Card | 256GB+ High Endurance (Samsung EVO Select) | €30-40 |
| Case with Cooling | Argon ONE V3 or similar with fan | €25-35 |
| UPS HAT | Geekworm UPS HAT (C) or PiSugar 3 | €35-50 |
| 18650 Batteries | 4× Samsung 30Q or Sony VTC6 | €20-30 |

**Minimum total: ~€205-265**

### Optional Components

| Component | Purpose | Est. Cost |
|-----------|---------|-----------|
| NVMe SSD + HAT | Faster storage (256GB-1TB) | €40-100 |
| External Antenna | Better WiFi range | €10-15 |
| Meshtastic Radio | LoRa mesh communications | €30-50 |
| GPS Module | Location services | €15-25 |
| RTC Module | Real-time clock (offline time) | €5-10 |

### Tools Needed

- Phillips screwdriver
- MicroSD card reader
- Computer with internet (for initial setup)
- USB keyboard (optional, for troubleshooting)
- HDMI monitor (optional, for troubleshooting)

## Hardware Assembly

### Step 1: Prepare the Raspberry Pi

1. **Unbox the Pi 5** and inspect for damage
2. **Attach heatsinks** if not pre-installed (case-dependent)
3. **Do NOT insert the SD card yet**

### Step 2: Install in Case

For Argon ONE V3 or similar:

1. Place Pi 5 on the case base
2. Connect ribbon cables (if applicable)
3. Secure with screws
4. Attach the top cover with fan

For cases with active cooling:
- Ensure fan connector is attached to GPIO or dedicated fan header

### Step 3: Install UPS HAT

**Geekworm UPS HAT (C):**

1. Align the 40-pin header
2. Gently press down until fully seated
3. Secure with standoffs/screws
4. Insert 18650 batteries (observe polarity!)

**Important:** Don't power on yet!

### Step 4: Connect Storage

**MicroSD (Standard):**
1. Skip to software installation
2. Insert SD card after flashing

**NVMe SSD (Optional):**
1. Attach NVMe HAT to Pi
2. Install SSD into HAT
3. You'll configure boot from NVMe later

## Software Installation

### Step 1: Download Raspberry Pi OS

1. Download **Raspberry Pi Imager** from: https://www.raspberrypi.com/software/
2. Install and open the Imager

### Step 2: Flash the SD Card

In Raspberry Pi Imager:

1. **Choose Device:** Raspberry Pi 5
2. **Choose OS:** Raspberry Pi OS Lite (64-bit)
   - Found under: Raspberry Pi OS (other) → Raspberry Pi OS Lite (64-bit)
3. **Choose Storage:** Your SD card
4. **Click the gear icon** for advanced options:

**Configure:**
```
☑ Set hostname: mulecube
☑ Enable SSH: Use password authentication
☑ Set username and password:
   Username: pi
   Password: [choose a strong password]
☑ Configure wireless LAN:
   SSID: [your home WiFi - temporary for setup]
   Password: [your WiFi password]
   Country: [your country code]
☑ Set locale settings:
   Time zone: [your timezone]
   Keyboard layout: [your layout]
```

5. **Click SAVE**
6. **Click WRITE** and confirm

Wait for flashing to complete (5-10 minutes).

### Step 3: First Boot

1. Insert the SD card into the Pi
2. Connect power (via UPS HAT if installed)
3. Wait 2-3 minutes for first boot
4. Find the Pi on your network:

```bash
# On Linux/Mac:
ping mulecube.local

# Or check your router's DHCP leases
# Or use: nmap -sn 192.168.1.0/24
```

### Step 4: Connect via SSH

```bash
ssh pi@mulecube.local
# Enter the password you configured
```

### Step 5: Run the MuleCube Installer

```bash
curl -fsSL https://raw.githubusercontent.com/nuclearlighters/mulecube/main/install.sh | sudo bash
```

The installer will:
- Install Docker and dependencies (~5 min)
- Clone the MuleCube repository (~1 min)
- Configure WiFi Access Point (~2 min)
- Set up networking (~1 min)
- Create helper scripts (~1 min)

**Total install time: ~10-15 minutes**

### Step 6: Reboot

```bash
sudo reboot
```

After reboot:
1. Disconnect from your home WiFi
2. Look for **MuleCube** WiFi network
3. Connect with password: **mulecube**
4. Open http://192.168.42.1

## Post-Installation Setup

### Start Services

```bash
ssh pi@192.168.42.1
cd /srv
sudo ./scripts/start-all.sh
```

First start takes 10-20 minutes as Docker images are pulled.

### Change Default Passwords

**WiFi Password:**
```bash
sudo nano /etc/hostapd/hostapd.conf
# Change: wpa_passphrase=mulecube
sudo systemctl restart hostapd
```

**Pi-hole:**
```bash
docker exec -it pihole pihole -a -p
```

**File Browser:**
- Go to http://192.168.42.1:8085
- Login: admin/admin
- Change in Settings

### Verify Services

1. Open dashboard: http://192.168.42.1
2. Check stats bar shows correct info
3. Click a few service tiles to test
4. Verify WiFi shows in "Connected" state

## Optional: Boot from NVMe

For faster performance with NVMe SSD:

### Step 1: Update Bootloader

```bash
sudo rpi-eeprom-config --edit
```

Change `BOOT_ORDER` to:
```
BOOT_ORDER=0xf416
```

This tries NVMe first, then SD card.

### Step 2: Clone SD to NVMe

```bash
# Install rpi-clone
git clone https://github.com/billw2/rpi-clone.git
cd rpi-clone
sudo cp rpi-clone /usr/local/bin/

# Clone to NVMe (usually /dev/nvme0n1)
sudo rpi-clone nvme0n1
```

### Step 3: Reboot

Remove SD card and reboot. Pi will boot from NVMe.

## Optional: Add Meshtastic

If you have a Meshtastic-compatible radio:

### Supported Devices

- Heltec V3
- LILYGO T-Beam
- RAK WisBlock
- Station G1/G2

### Connection

1. Connect radio via USB to Pi
2. Radio appears as `/dev/ttyUSB0` or `/dev/ttyACM0`

### Configuration

```bash
cd /srv/meshtastic
nano docker-compose.yml

# Set the correct device:
# devices:
#   - /dev/ttyUSB0:/dev/ttyUSB0

docker compose up -d
```

Access web interface: http://192.168.42.1:8084

## Optional: Add RTC Module

For accurate time without internet:

### DS3231 RTC

1. Connect to I2C pins (SDA, SCL, 3.3V, GND)
2. Enable I2C:

```bash
sudo raspi-config
# Interface Options → I2C → Enable
```

3. Configure RTC:

```bash
echo "dtoverlay=i2c-rtc,ds3231" | sudo tee -a /boot/firmware/config.txt
sudo reboot

# Set time (while connected to internet)
sudo hwclock -w
```

## Customization

### Adding Services

See the MuleCube repository for additional services you can enable:

```bash
cd /srv

# View available services
ls -la

# Enable a service
cd service_name
docker compose up -d
```

### Creating Custom Dashboard Tiles

Edit the dashboard configuration:

```bash
nano /srv/mulecube-dashboard/config.yml
```

### Adjusting Resource Limits

For low-memory configurations:

```bash
# Edit service docker-compose.yml
nano /srv/service/docker-compose.yml

# Add memory limits:
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

## Troubleshooting Build Issues

### Pi Won't Boot

1. Check power supply is adequate (5V/5A for Pi 5)
2. Try different SD card
3. Re-flash the image
4. Check LED patterns:
   - Solid green: Booting normally
   - Flashing green: Reading SD card
   - No green: SD card issue or power problem

### Can't SSH

1. Wait 2-3 minutes for full boot
2. Verify Pi is on network: `ping mulecube.local`
3. Check router for assigned IP
4. Connect monitor/keyboard to diagnose

### WiFi AP Not Appearing

```bash
# Check hostapd status
sudo systemctl status hostapd

# View errors
sudo journalctl -u hostapd

# Common fix: unblock WiFi
sudo rfkill unblock wlan
```

### Services Won't Start

```bash
# Check Docker is running
sudo systemctl status docker

# View container status
docker ps -a

# Check logs
docker logs container_name
```

### Out of Memory

```bash
# Check memory usage
free -h

# Stop unnecessary services
cd /srv/heavy-service
docker compose down

# Add swap (temporary fix)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## Build Checklist

Use this checklist for your build:

- [ ] Raspberry Pi 5 (8GB)
- [ ] Power supply (27W USB-C)
- [ ] MicroSD card (256GB+)
- [ ] Case with cooling
- [ ] UPS HAT + batteries
- [ ] Raspberry Pi OS Lite flashed
- [ ] SSH enabled
- [ ] First boot successful
- [ ] MuleCube installer run
- [ ] WiFi AP working
- [ ] Services started
- [ ] Dashboard accessible
- [ ] Passwords changed
- [ ] Test complete!

## Cost Summary

### Minimum Build (~€205)

| Item | Cost |
|------|------|
| Raspberry Pi 5 8GB | €80 |
| Official PSU | €15 |
| 256GB SD Card | €30 |
| Basic Case | €20 |
| UPS HAT + Batteries | €60 |

### Recommended Build (~€320)

| Item | Cost |
|------|------|
| Raspberry Pi 5 8GB | €80 |
| Official PSU | €15 |
| 512GB SD Card | €50 |
| Argon ONE V3 Case | €35 |
| Geekworm UPS HAT (C) | €45 |
| 4× Samsung 30Q | €25 |
| External Antenna | €15 |
| RTC Module | €10 |
| Meshtastic Radio | €45 |

### Premium Build (~€450)

All of the above, plus:

| Item | Cost |
|------|------|
| 1TB NVMe SSD | €80 |
| NVMe HAT | €20 |
| GPS Module | €25 |
| Quality aluminum case | €25 |

## Next Steps

After building your MuleCube:

1. **[Getting Started](getting-started.md)** - Basic usage
2. **[Adding Content](content.md)** - Load maps, books, media
3. **[Network Setup](network.md)** - Security configuration
4. **[Services](services.md)** - What each service does

## Community

Share your build!

- GitHub Discussions: https://github.com/nuclearlighters/mulecube/discussions
- Show off your custom case designs
- Share modifications and improvements
- Help others with their builds

## License

The MuleCube project is open source:

- **Code:** MIT License
- **Documentation:** CC BY-SA 4.0
- **Hardware designs:** CERN OHL v2

You're free to build, modify, and even sell your own MuleCubes!
