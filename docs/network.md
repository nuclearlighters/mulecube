# Network Setup

MuleCube creates its own WiFi network for device connectivity. This guide covers WiFi configuration, security settings, and advanced networking options.

## Default Network Configuration

| Setting | Default Value |
|---------|--------------|
| WiFi SSID | MuleCube |
| WiFi Password | mulecube |
| Security | WPA2-PSK |
| IP Address | 192.168.42.1 |
| DHCP Range | 192.168.42.10 - 192.168.42.250 |
| Max Clients | 10 |
| Channel | 7 (auto-selected) |

## Changing WiFi Password

**Important:** Change the default password immediately after setup!

### Method 1: Web Interface (Recommended)

1. Connect to MuleCube WiFi
2. Go to http://192.168.42.1
3. Click **Settings** (gear icon)
4. Select **Network Configuration**
5. Enter new password (minimum 8 characters)
6. Click **Save**
7. Reconnect with new password

### Method 2: Terminal

```bash
# SSH or use web terminal
sudo nano /etc/hostapd/hostapd.conf

# Find and change this line:
wpa_passphrase=mulecube

# Change to your new password:
wpa_passphrase=YourSecurePassword123

# Save and restart
sudo systemctl restart hostapd
```

### Password Requirements

- Minimum 8 characters
- Recommended: 12+ characters
- Mix of letters, numbers, symbols
- Avoid dictionary words

## Changing WiFi Name (SSID)

### Method 1: Web Interface

1. Go to Settings → Network Configuration
2. Edit the **Network Name** field
3. Click **Save**
4. Look for new network name on your devices

### Method 2: Terminal

```bash
sudo nano /etc/hostapd/hostapd.conf

# Find and change:
ssid=MuleCube

# To your preferred name:
ssid=MyExpeditionCube

# Restart
sudo systemctl restart hostapd
```

### SSID Guidelines

- Maximum 32 characters
- Avoid special characters
- Avoid spaces (use underscores)
- Make it recognizable but not personally identifiable

## Advanced WiFi Settings

### Changing WiFi Channel

If experiencing interference:

```bash
sudo nano /etc/hostapd/hostapd.conf

# Find:
channel=7

# Change to another channel (1-11 for 2.4GHz):
channel=1

sudo systemctl restart hostapd
```

**Best channels:** 1, 6, or 11 (non-overlapping)

### Enabling 5GHz WiFi

If your Pi 5 supports it and you need faster speeds:

```bash
sudo nano /etc/hostapd/hostapd.conf

# Change:
hw_mode=g
channel=7

# To:
hw_mode=a
channel=36

sudo systemctl restart hostapd
```

**Note:** 5GHz has shorter range but less interference.

### Hidden Network

To hide your SSID from scanning:

```bash
sudo nano /etc/hostapd/hostapd.conf

# Change:
ignore_broadcast_ssid=0

# To:
ignore_broadcast_ssid=1

sudo systemctl restart hostapd
```

Clients will need to manually enter the network name.

## Connecting to Existing WiFi

MuleCube can connect to another WiFi network (as a client) while also running its own access point.

### Use Case

- Share internet through MuleCube
- Access MuleCube from main network
- Download content updates

### Configuration

```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Add your home/office network:
network={
    ssid="YourHomeWiFi"
    psk="YourHomePassword"
    priority=1
}

# Enable client mode alongside AP
sudo systemctl enable wpa_supplicant
sudo reboot
```

**Note:** This requires compatible hardware that supports simultaneous AP + Client mode.

## Ethernet Connection

MuleCube can use Ethernet for internet access or local network connectivity.

### Internet Sharing (Ethernet → WiFi)

When Ethernet is connected to internet:

1. Connect Ethernet cable to MuleCube
2. NAT is automatically configured
3. WiFi clients can access internet through MuleCube

### Local Network Access

When Ethernet is connected to LAN:

1. Connect Ethernet to your router/switch
2. MuleCube gets DHCP address on that network
3. Access via both WiFi (192.168.42.1) and LAN IP

Check Ethernet IP:

```bash
ip addr show eth0
```

## Static IP Configuration

### Set Static IP for Ethernet

```bash
sudo nano /etc/dhcpcd.conf

# Add at the end:
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1
```

### Set Static IP for WiFi AP

The AP interface already has a static IP (192.168.42.1). To change it:

```bash
sudo nano /etc/dhcpcd.conf

# Find and modify:
interface wlan0
static ip_address=192.168.42.1/24

# Change to your preferred address:
interface wlan0
static ip_address=10.0.0.1/24

# Also update DHCP range:
sudo nano /etc/dnsmasq.d/mulecube.conf
# Change dhcp-range accordingly
```

## DNS Configuration

### Local DNS Entries

MuleCube resolves these names locally:

| Hostname | IP Address |
|----------|------------|
| mulecube.local | 192.168.42.1 |
| cube.local | 192.168.42.1 |
| wiki.local | 192.168.42.1 |
| ai.local | 192.168.42.1 |

### Adding Custom DNS Entries

```bash
sudo nano /etc/dnsmasq.d/mulecube.conf

# Add entries like:
address=/myservice.local/192.168.42.1
address=/custom.local/192.168.42.50

sudo systemctl restart dnsmasq
```

### Using Pi-hole for DNS

Pi-hole is pre-installed for ad-blocking:

1. Go to http://192.168.42.1:8053/admin
2. Login (default password: `mulecube`)
3. Configure blocklists and DNS settings

## Meshtastic Integration

If your MuleCube includes Meshtastic hardware:

### Default Configuration

| Setting | Value |
|---------|-------|
| Radio Type | LoRa 915MHz (US) or 868MHz (EU) |
| Mesh Name | MuleCube |
| Encryption | AES-256 enabled |

### Web Interface

Access at: http://192.168.42.1:8084

### Range Expectations

| Environment | Range |
|-------------|-------|
| Urban/indoor | 1-3 km |
| Suburban | 3-10 km |
| Rural/LOS | 10-30 km |
| Mountain/LOS | 50+ km |

### Connecting Radios

1. Power on your Meshtastic radio
2. It will automatically join the MuleCube mesh
3. Messages appear in the web interface
4. Send messages from any connected device

## Firewall Settings

MuleCube has a permissive firewall by default for ease of use.

### View Current Rules

```bash
sudo iptables -L -n
```

### Block External Access to a Service

```bash
# Block external access to SSH (example)
sudo iptables -A INPUT -i wlan0 -p tcp --dport 22 -j DROP
sudo netfilter-persistent save
```

### Allow Access from Specific IP

```bash
# Allow only 192.168.42.50 to access terminal
sudo iptables -A INPUT -i wlan0 -p tcp --dport 7681 -s 192.168.42.50 -j ACCEPT
sudo iptables -A INPUT -i wlan0 -p tcp --dport 7681 -j DROP
sudo netfilter-persistent save
```

## VPN Configuration

### WireGuard (Recommended)

For secure remote access when internet is available:

```bash
# Install WireGuard
sudo apt install wireguard

# Generate keys
wg genkey | tee privatekey | wg pubkey > publickey

# Configure (customize for your setup)
sudo nano /etc/wireguard/wg0.conf
```

### Use Cases

- Remote monitoring of MuleCube
- Secure tunnel to home network
- Access MuleCube from anywhere

## Troubleshooting Network Issues

### WiFi Not Appearing

```bash
# Check hostapd status
sudo systemctl status hostapd

# View logs
sudo journalctl -u hostapd -f

# Restart services
sudo systemctl restart hostapd dnsmasq
```

### Can't Get IP Address

```bash
# Check dnsmasq status
sudo systemctl status dnsmasq

# View DHCP leases
cat /var/lib/misc/dnsmasq.leases

# Restart DHCP
sudo systemctl restart dnsmasq
```

### Slow WiFi Performance

1. Check for interference (try different channel)
2. Reduce distance to MuleCube
3. Limit number of clients
4. Check for heavy service usage

### No Internet Through MuleCube

```bash
# Check Ethernet connection
ip link show eth0

# Verify NAT rules
sudo iptables -t nat -L

# Check IP forwarding
cat /proc/sys/net/ipv4/ip_forward
# Should be 1

# Re-enable if needed
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
```

## Security Best Practices

1. **Change default passwords** immediately
2. **Use strong WiFi password** (12+ characters)
3. **Hide SSID** if not needed for discovery
4. **Limit services** exposed externally
5. **Keep software updated** for security patches
6. **Monitor connections** via Pi-hole dashboard
7. **Use HTTPS** where available
8. **Disable unused services** to reduce attack surface

## Quick Reference

| Task | Command/Location |
|------|-----------------|
| Change WiFi password | Settings → Network or `/etc/hostapd/hostapd.conf` |
| Check connected clients | Pi-hole dashboard or `arp -a` |
| View IP addresses | `ip addr show` |
| Restart networking | `sudo systemctl restart hostapd dnsmasq` |
| Check DNS | `nslookup mulecube.local` |
| View firewall | `sudo iptables -L` |
