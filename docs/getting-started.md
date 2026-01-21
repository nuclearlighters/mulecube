# Getting Started

This guide will help you set up your MuleCube and connect your first device.

## What's in the Box

Your MuleCube package includes:

- **MuleCube unit** — The main device with pre-installed software
- **Power adapter** — 5V/5A USB-C power supply
- **Quick start card** — WiFi credentials and basic instructions
- **Battery pack** — Pre-installed 50Wh UPS (4× 18650 cells)

Optional accessories (depending on your configuration):
- Meshtastic LoRa radio (Cube Sat, Ultimate)
- Hailo AI accelerator (Cube AI, Ultimate)
- Iridium satellite modem (Cube Sat, Ultimate)

## First Power On

### Step 1: Connect Power

1. Plug the USB-C power adapter into the port marked **"PWR"**
2. Connect the adapter to a wall outlet
3. The status LED will turn **solid green** when powered

> **Note:** MuleCube can also run on battery. For first-time setup, we recommend using the power adapter to ensure a stable connection.

### Step 2: Wait for Boot

MuleCube takes approximately **60-90 seconds** to fully boot. During this time:

- The green LED will blink
- The WiFi network will not be visible yet
- This is normal — all 30+ services need to initialize

When boot is complete:
- The LED will turn **solid green**
- The **MuleCube** WiFi network will appear

### Step 3: Connect to WiFi

On your phone, tablet, or laptop:

1. Open WiFi settings
2. Look for network: **MuleCube**
3. Enter password: **mulecube** (default)
4. Wait for connection

> **Security:** Change the default password after setup! See [Network Setup](network.md).

### Step 4: Open the Dashboard

Once connected to MuleCube WiFi:

1. Open any web browser
2. Go to: **http://192.168.42.1**
3. The MuleCube dashboard will load

You can also use:
- http://mulecube.local (if your device supports mDNS)
- http://cube.local

## Dashboard Overview

The dashboard is your control center for MuleCube:

```
┌─────────────────────────────────────────────────────────────┐
│  MuleCube                              [Stats Bar]          │
├─────────────────────────────────────────────────────────────┤
│  CPU 12% | Memory 45% | Disk 62% | 52°C | ⚡ 94% | 2d 5h   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │Wikipedia│ │  Maps   │ │   AI    │ │Translate│           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │CryptPad │ │Passwords│ │ E-Books │ │  Files  │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                          ...                                │
└─────────────────────────────────────────────────────────────┘
```

### Stats Bar

The top bar shows real-time system information:

| Indicator | Meaning |
|-----------|---------|
| CPU | Processor usage percentage |
| Memory | RAM usage percentage |
| Disk | Storage usage percentage |
| 🌡️ Temperature | CPU temperature (green < 70°C, yellow < 80°C, red ≥ 80°C) |
| ⚡ / 🔋 | Battery percentage (⚡ = charging, 🔋 = on battery) |
| Uptime | How long MuleCube has been running |

### Service Tiles

Click any tile to open that service in a new tab. Services are organized by category:

- **Knowledge** — Wikipedia, Maps, E-Books, Medical
- **AI** — Chat with local AI models
- **Productivity** — Documents, Notes, Passwords
- **Communication** — Meshtastic, Matrix chat
- **Media** — Jellyfin, PDF tools
- **Control Panel** — System management

## Connecting Multiple Devices

MuleCube supports up to **10 simultaneous WiFi connections**. Each device can:

- Access all services independently
- Have separate user accounts (where supported)
- Share files through CryptPad or Syncthing

### Recommended Setup

For a family or small team:

1. **Main device** — Laptop for content management
2. **Mobile devices** — Phones/tablets for quick access
3. **Dedicated terminal** — Optional Raspberry Pi for always-on display

## Power Management

### Running on Battery

To run on battery power:

1. Disconnect the USB-C power adapter
2. MuleCube switches automatically to battery
3. The battery icon changes from ⚡ to 🔋
4. Runtime: **10-15 hours** depending on usage

### Charging

When connected to power:

1. The battery charges automatically
2. Charge time: **3-4 hours** from empty
3. You can use MuleCube while charging

### Low Battery Warning

When battery drops below 20%:
- Dashboard shows yellow warning
- Consider connecting power or reducing usage

When battery drops below 10%:
- Dashboard shows red critical warning
- MuleCube will gracefully shut down at 5%

See [Battery Management](battery.md) for detailed information.

## Shutting Down Safely

**Always shut down properly** to prevent data corruption:

### Method 1: Dashboard Button

1. Click the **⏻** (power) button in the stats bar
2. Confirm the shutdown
3. Wait for the LED to turn off (~30 seconds)

### Method 2: Physical Button (if equipped)

1. Press and hold the power button for 3 seconds
2. Release when the LED blinks rapidly
3. Wait for complete shutdown

### Method 3: Terminal

If you have terminal access:

```bash
sudo shutdown -h now
```

**Never unplug power without shutting down** unless the battery can sustain the device.

## Next Steps

Now that your MuleCube is running:

1. **[Using the Services](services.md)** — Learn what each service does
2. **[Network Setup](network.md)** — Change the default WiFi password
3. **[Adding Content](content.md)** — Load your own maps and books

## Quick Reference

| Item | Value |
|------|-------|
| Default WiFi SSID | MuleCube |
| Default WiFi Password | mulecube |
| Dashboard URL | http://192.168.42.1 |
| Alternative URL | http://mulecube.local |
| Boot time | 60-90 seconds |
| Battery runtime | 10-15 hours |
| Max WiFi clients | 10 |
