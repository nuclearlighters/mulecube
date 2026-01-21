# Software Updates

MuleCube can be updated to get new features, security patches, and bug fixes. This guide explains the different update methods.

## Update Types

| Type | Frequency | Requires Internet | Risk Level |
|------|-----------|-------------------|------------|
| Service updates | Monthly | Yes (temporary) | Low |
| System updates | Quarterly | Yes (temporary) | Medium |
| Full image | Yearly | Yes (download) | High |

## Quick Update (Recommended)

When temporarily connected to internet:

```bash
cd /srv
git pull
./scripts/update-all.sh
```

This updates all service configurations and restarts changed services.

## Detailed Update Process

### Step 1: Check Current Version

```bash
# View current version
cat /srv/VERSION

# Check for updates
cd /srv
git fetch origin
git log HEAD..origin/main --oneline
```

### Step 2: Backup Before Update

Always backup before major updates:

```bash
# Quick backup
/srv/scripts/backup.sh

# Or full backup
sudo tar -czvf /backup/pre-update-$(date +%Y%m%d).tar.gz /srv
```

### Step 3: Apply Updates

```bash
cd /srv

# Pull latest configurations
git pull origin main

# Update Docker images
docker compose pull

# Restart services with new images
./scripts/update-all.sh
```

### Step 4: Verify

1. Check dashboard loads correctly
2. Test a few services
3. Check system stats are normal

## Updating Individual Services

### Update a Single Service

```bash
cd /srv/service_name
docker compose pull
docker compose up -d
```

### Rollback a Service

If an update causes problems:

```bash
cd /srv/service_name

# View available versions
docker images | grep service_name

# Use specific version in docker-compose.yml
# Change: image: service:latest
# To:     image: service:v1.2.3

docker compose up -d
```

## System Updates (Raspberry Pi OS)

### Security Updates

```bash
# Update package lists
sudo apt update

# Install security updates only
sudo apt upgrade -y

# Reboot if kernel updated
sudo reboot
```

### Full System Update

```bash
# Update everything
sudo apt update && sudo apt full-upgrade -y

# Clean up
sudo apt autoremove -y

# Reboot
sudo reboot
```

### Firmware Updates

```bash
# Update Raspberry Pi firmware
sudo rpi-update

# Only do this if recommended
# Can cause instability
```

## Updating Without Internet

If you can't connect MuleCube to internet:

### Method 1: USB Transfer

On a computer with internet:

```bash
# Clone/pull the latest repo
git clone https://github.com/nuclearlighters/mulecube.git
# Or: cd mulecube && git pull

# Create update package
tar -czvf mulecube-update.tar.gz mulecube/
```

Copy to USB, then on MuleCube:

```bash
# Mount USB
sudo mount /dev/sda1 /mnt

# Extract update
cd /srv
tar -xzvf /mnt/mulecube-update.tar.gz --strip-components=1

# Apply
./scripts/update-all.sh
```

### Method 2: Docker Image Export

On a computer with internet and Docker:

```bash
# Pull updated images
docker pull ghcr.io/service/image:latest

# Export to file
docker save ghcr.io/service/image:latest > service-image.tar
```

On MuleCube:

```bash
# Load image
docker load < /mnt/service-image.tar

# Restart service
cd /srv/service && docker compose up -d
```

## Automatic Updates (Optional)

### Enable Auto-Updates

For devices with regular internet access:

```bash
# Create update timer
sudo nano /etc/systemd/system/mulecube-update.timer
```

```ini
[Unit]
Description=MuleCube Auto-Update Timer

[Timer]
OnCalendar=weekly
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
sudo nano /etc/systemd/system/mulecube-update.service
```

```ini
[Unit]
Description=MuleCube Auto-Update

[Service]
Type=oneshot
ExecStart=/srv/scripts/update-all.sh
```

```bash
sudo systemctl enable mulecube-update.timer
sudo systemctl start mulecube-update.timer
```

### Disable Auto-Updates

```bash
sudo systemctl disable mulecube-update.timer
sudo systemctl stop mulecube-update.timer
```

## Version History

Track changes at: https://github.com/nuclearlighters/mulecube/releases

### Version Numbering

MuleCube uses semantic versioning: **MAJOR.MINOR.PATCH**

- **MAJOR:** Breaking changes, requires careful upgrade
- **MINOR:** New features, backwards compatible
- **PATCH:** Bug fixes, safe to apply

Example: v1.2.3

### Changelog

View changes before updating:

```bash
# View changelog
cat /srv/CHANGELOG.md

# Or online
https://github.com/nuclearlighters/mulecube/blob/main/CHANGELOG.md
```

## Update Scripts

### update-all.sh

Updates all services:

```bash
#!/bin/bash
cd /srv

echo "Pulling latest configurations..."
git pull origin main

echo "Updating Docker images..."
for dir in */; do
    if [ -f "${dir}docker-compose.yml" ]; then
        echo "Updating ${dir%/}..."
        (cd "$dir" && docker compose pull && docker compose up -d)
    fi
done

echo "Cleaning up old images..."
docker image prune -f

echo "Update complete!"
```

### check-updates.sh

Check for available updates:

```bash
#!/bin/bash
cd /srv

echo "Checking for updates..."
git fetch origin
UPDATES=$(git log HEAD..origin/main --oneline | wc -l)

if [ "$UPDATES" -gt 0 ]; then
    echo "📦 $UPDATES updates available:"
    git log HEAD..origin/main --oneline
else
    echo "✅ System is up to date"
fi
```

## Troubleshooting Updates

### Update Failed Mid-Process

```bash
# Reset to last known good state
cd /srv
git reset --hard HEAD
./scripts/start-all.sh
```

### Service Won't Start After Update

```bash
# Check logs
docker logs service_name

# Try rebuilding
cd /srv/service_name
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Out of Disk Space

```bash
# Clean Docker
docker system prune -a

# Remove old images
docker image prune -a

# Check space
df -h /srv
```

### Merge Conflicts

If you've modified files locally:

```bash
cd /srv

# Stash your changes
git stash

# Pull updates
git pull origin main

# Re-apply your changes
git stash pop

# Resolve any conflicts manually
```

## Keeping Data Safe

### What's Preserved During Updates

- All user data in `data/` directories
- Database contents
- Uploaded files
- Configuration changes in `data/` folders

### What Might Be Overwritten

- Docker compose files (if modified)
- Service configurations (in git)
- Scripts

### Protecting Custom Changes

If you've customized configurations:

```bash
# Create override file (not tracked by git)
cp docker-compose.yml docker-compose.override.yml

# Edit override file with your changes
# Docker Compose automatically merges both files
```

## Update Schedule Recommendations

| Environment | Update Frequency | Notes |
|-------------|-----------------|-------|
| Home use | Monthly | Check for updates regularly |
| Expedition | Before departure | Update fully, then disconnect |
| Critical use | Quarterly | Test updates in staging first |
| Air-gapped | Yearly | Apply curated update packages |

## Getting Help

If updates cause issues:

1. Check GitHub Issues: https://github.com/nuclearlighters/mulecube/issues
2. Review Discussions: https://github.com/nuclearlighters/mulecube/discussions
3. Email: hello@mulecube.com

Include in your report:
- Current version
- Update you attempted
- Error messages
- Steps to reproduce
