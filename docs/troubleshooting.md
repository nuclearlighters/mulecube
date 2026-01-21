# Troubleshooting

Common issues and solutions for MuleCube.

## Quick Diagnostics

### Check System Status

```bash
# Via terminal or web terminal (http://192.168.42.1:7681)
/srv/scripts/status.sh
```

### Service Health

1. Open dashboard: http://192.168.42.1
2. Check stats bar for warnings
3. Look for red/yellow service tiles

---

## WiFi & Network Issues

### WiFi Network Not Appearing

**Symptoms:** MuleCube WiFi (SSID) not visible on devices

**Solutions:**

1. **Wait for boot** - Takes 60-90 seconds
2. **Check LED status** - Should be solid green when ready
3. **Restart hostapd:**
```bash
sudo systemctl restart hostapd
```

4. **Unblock WiFi radio:**
```bash
sudo rfkill unblock wlan
```

5. **Check hostapd status:**
```bash
sudo systemctl status hostapd
sudo journalctl -u hostapd -n 50
```

### Can't Connect to WiFi

**Symptoms:** Network visible but connection fails

**Solutions:**

1. **Verify password** - Default: `mulecube`
2. **Forget and reconnect** - Remove saved network, try again
3. **Check client limit** - Max 10 devices, disconnect one
4. **Try different device** - Rule out client-side issues

### Connected but No Internet

**Symptoms:** Connected to MuleCube WiFi but can't reach services

**Solutions:**

1. **Check IP assignment:**
```bash
# On your device, verify you got 192.168.42.x address
```

2. **Restart DHCP:**
```bash
sudo systemctl restart dnsmasq
```

3. **Verify gateway:**
```bash
ping 192.168.42.1
```

4. **DNS check:**
```bash
nslookup mulecube.local 192.168.42.1
```

### Can't Access Dashboard

**Symptoms:** Connected to WiFi but http://192.168.42.1 won't load

**Solutions:**

1. **Try IP directly:** http://192.168.42.1
2. **Check nginx:**
```bash
docker ps | grep nginx
docker logs nginx-proxy
sudo systemctl restart nginx  # If not dockerized
```

3. **Verify port 80 is listening:**
```bash
sudo netstat -tlnp | grep :80
```

---

## Service Issues

### Service Shows Red/Stopped

**Symptoms:** Service tile is red or service not responding

**Solutions:**

1. **Restart the service:**
```bash
cd /srv/service_name
docker compose restart
```

2. **Check logs:**
```bash
docker logs service_name
# Or via Dozzle: http://192.168.42.1:9999
```

3. **Rebuild if corrupted:**
```bash
cd /srv/service_name
docker compose down
docker compose up -d --build
```

4. **Check disk space:**
```bash
df -h /srv
```

### Service Slow or Unresponsive

**Symptoms:** Service loads but is very slow

**Solutions:**

1. **Check system resources:**
```bash
htop
# or
docker stats
```

2. **Reduce load:**
   - Close unused services
   - Limit AI queries
   - Reduce connected clients

3. **Check temperature:**
```bash
vcgencmd measure_temp
```
   - Over 80°C = thermal throttling

4. **Restart heavy services:**
```bash
cd /srv/ollama && docker compose restart
cd /srv/open-webui && docker compose restart
```

### AI (Ollama) Not Responding

**Symptoms:** AI chat returns errors or hangs

**Solutions:**

1. **Check Ollama container:**
```bash
docker logs ollama
```

2. **Restart Ollama:**
```bash
cd /srv/ollama
docker compose restart
```

3. **Memory issue - free up RAM:**
```bash
# Stop other heavy services temporarily
cd /srv/jellyfin && docker compose stop
cd /srv/libretranslate && docker compose stop
```

4. **Use smaller model:**
   - Switch to phi3:mini instead of larger models

### Wikipedia/Kiwix Not Loading Content

**Symptoms:** Kiwix loads but articles show "not found"

**Solutions:**

1. **Check ZIM files exist:**
```bash
ls -la /srv/kiwix/data/*.zim
```

2. **Verify file integrity:**
```bash
# Check file isn't corrupted/partial
ls -lh /srv/kiwix/data/
```

3. **Restart Kiwix:**
```bash
cd /srv/kiwix && docker compose restart
```

4. **Re-download content** if corrupted

---

## Hardware Issues

### High Temperature / Throttling

**Symptoms:** System slow, temperature warnings, fan running constantly

**Solutions:**

1. **Check temperature:**
```bash
vcgencmd measure_temp
# Normal: < 70°C, Warning: 70-80°C, Critical: > 80°C
```

2. **Improve cooling:**
   - Ensure fan is working
   - Clean dust from vents
   - Add heatsinks
   - Improve ventilation around device

3. **Reduce load:**
   - Stop AI services when not needed
   - Limit concurrent users

4. **Check for thermal paste** (if DIY build)

### Battery Not Charging

**Symptoms:** Battery percentage not increasing when plugged in

**Solutions:**

1. **Verify power supply:**
   - Use official 27W adapter
   - Check USB-C connection
   - Try different cable

2. **Check battery status:**
```bash
curl -s http://localhost:9001/api/battery | jq .
```

3. **Check UPS HAT:**
   - LEDs should indicate charging
   - Verify battery connections
   - Check cell polarity

4. **Battery calibration:**
   - Full discharge → Full charge cycle

### Battery Draining Too Fast

**Symptoms:** Battery life much shorter than expected

**Solutions:**

1. **Check power consumption:**
```bash
docker stats --no-stream
```

2. **Stop heavy services:**
```bash
cd /srv/ollama && docker compose stop
cd /srv/jellyfin && docker compose stop
```

3. **Reduce WiFi clients**

4. **Check battery health** - May need cell replacement after 500+ cycles

### SD Card Errors

**Symptoms:** Read-only filesystem, I/O errors, corruption

**Solutions:**

1. **Check filesystem:**
```bash
dmesg | grep -i error
```

2. **If read-only, remount:**
```bash
sudo mount -o remount,rw /
```

3. **Backup immediately** if errors appear

4. **Replace SD card** - Use high-endurance cards

5. **Consider NVMe** for better reliability

---

## Boot Issues

### Won't Boot / No LED Activity

**Solutions:**

1. **Check power supply** - Pi 5 needs 5V/5A minimum
2. **Try without UPS HAT** - Direct power to Pi
3. **Re-flash SD card**
4. **Check SD card seating**
5. **Test with different SD card**

### Boot Loops / Crashes

**Symptoms:** Boots partially then restarts

**Solutions:**

1. **Check power supply** - Insufficient power causes reboots
2. **Remove peripherals** - Boot with only power connected
3. **Check for overheating** - Feel the case temperature
4. **View boot log:**
```bash
# Connect HDMI monitor to see boot messages
```

### Services Don't Start After Boot

**Symptoms:** MuleCube boots but services remain stopped

**Solutions:**

1. **Manual start:**
```bash
cd /srv
./scripts/start-all.sh
```

2. **Check Docker:**
```bash
sudo systemctl status docker
sudo systemctl start docker
```

3. **Enable auto-start:**
```bash
sudo systemctl enable docker
```

4. **Check disk space:**
```bash
df -h
```

---

## Data Issues

### Lost Documents/Files

**Solutions:**

1. **Check CryptPad history:**
   - Open document → History → Restore

2. **Check Syncthing versioning:**
   - `~/.config/syncthing/` for versions

3. **Restore from backup:**
```bash
# If you have backups
tar -xzvf /backup/latest.tar.gz -C /srv
```

### Database Corruption

**Symptoms:** Service won't start, database errors in logs

**Solutions:**

1. **Try service restart:**
```bash
cd /srv/service && docker compose restart
```

2. **Rebuild database** (loses data):
```bash
cd /srv/service
docker compose down
rm -rf data/
docker compose up -d
```

3. **Restore from backup** if available

---

## Password Issues

### Forgot WiFi Password

**Solutions:**

1. **Connect via Ethernet** instead
2. **Connect monitor/keyboard** and login locally
3. **Reset hostapd config:**
```bash
sudo nano /etc/hostapd/hostapd.conf
# Change wpa_passphrase=YourNewPassword
sudo systemctl restart hostapd
```

### Forgot Service Password

**Pi-hole:**
```bash
docker exec -it pihole pihole -a -p
```

**File Browser:**
- Delete config and restart (resets to admin/admin)
```bash
rm /srv/filebrowser/database/filebrowser.db
cd /srv/filebrowser && docker compose restart
```

**Vaultwarden:**
- If you have access to email, use forgot password
- Otherwise, admin panel can reset

### SSH Access Lost

1. **Connect monitor + keyboard**
2. **Login locally as pi user**
3. **Reset password:**
```bash
sudo passwd pi
```
4. **Or re-enable SSH:**
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

---

## Update Issues

### Update Failed

**Solutions:**

1. **Reset to previous state:**
```bash
cd /srv
git reset --hard HEAD~1
./scripts/start-all.sh
```

2. **Clean and retry:**
```bash
docker system prune -a
git pull
./scripts/start-all.sh
```

### Merge Conflicts

**Solutions:**

1. **Keep upstream changes:**
```bash
cd /srv
git checkout --theirs .
git add .
git commit -m "Accept upstream changes"
```

2. **Keep local changes:**
```bash
git checkout --ours .
git add .
git commit -m "Keep local changes"
```

---

## Getting More Help

### Diagnostic Information

When reporting issues, include:

```bash
# System info
cat /etc/os-release
uname -a
vcgencmd measure_temp

# Docker status
docker ps -a
docker system df

# Resource usage
free -h
df -h

# Recent logs
sudo journalctl -n 100 --no-pager
```

### Support Channels

1. **GitHub Issues:** https://github.com/nuclearlighters/mulecube/issues
2. **Discussions:** https://github.com/nuclearlighters/mulecube/discussions
3. **Email:** hello@mulecube.com

### Before Reporting

1. Check this troubleshooting guide
2. Search existing GitHub issues
3. Try restarting the service/device
4. Collect diagnostic information
5. Describe steps to reproduce
