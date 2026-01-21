# Battery Management

MuleCube includes a built-in UPS (Uninterruptible Power Supply) that provides 10-15 hours of battery runtime. This guide covers charging, monitoring, and maximizing battery life.

## Battery Specifications

| Specification | Value |
|--------------|-------|
| Type | Lithium-ion (18650 cells) |
| Configuration | 4× Samsung 18650 (hot-swappable) |
| Capacity | 50Wh (approximately 13,600mAh) |
| Voltage | 3.7V nominal, 4.2V fully charged |
| Runtime | 10-15 hours typical usage |
| Charge time | 3-4 hours (0% to 100%) |
| Charge input | USB-C PD, 5V/3A minimum |

## Understanding Battery Status

### Dashboard Indicators

The stats bar shows real-time battery status:

| Icon | Status | Meaning |
|------|--------|---------|
| ⚡ 95% | Charging | Connected to power, battery charging |
| 🔋 85% | On battery | Running from battery power |
| 🔋 20% | Low | Consider connecting power |
| 🔋 10% | Critical | Connect power immediately |

### Battery States

**Charging (⚡)**
- USB-C power connected
- Battery level increasing
- Safe to use indefinitely

**Full (⚡ 100%)**
- Battery fully charged
- Float charging (trickle charge to maintain)
- Optimal for stationary use

**Discharging (🔋)**
- Running on battery
- Battery level decreasing
- Check remaining time estimate

**Low Battery (🔋 < 20%)**
- Yellow warning on dashboard
- Consider connecting power
- Reduce intensive tasks

**Critical (🔋 < 10%)**
- Red warning on dashboard
- Connect power immediately
- Auto-shutdown at 5% to protect data

## Charging Best Practices

### Initial Charge

When you first receive your MuleCube:

1. Connect the included USB-C power adapter
2. Let it charge fully to 100% (3-4 hours)
3. This calibrates the battery gauge

### Daily Use

For best battery longevity:

- **Keep between 20-80%** when possible
- **Avoid deep discharges** (below 10%)
- **Don't leave at 100%** for weeks at a time
- **Charge at room temperature** (15-25°C ideal)

### Optimal Storage

If storing MuleCube for extended periods:

1. Charge to approximately 50-60%
2. Power off completely
3. Store in cool, dry place
4. Recharge every 3 months to prevent over-discharge

## Maximizing Runtime

### Typical Usage Patterns

| Usage Pattern | Expected Runtime |
|--------------|------------------|
| Light (Wikipedia browsing, notes) | 14-16 hours |
| Medium (AI queries, file access) | 10-12 hours |
| Heavy (continuous AI, multiple users) | 6-8 hours |
| Maximum load (AI + media streaming) | 4-6 hours |

### Power Saving Tips

**Reduce AI Usage**
- AI models are the biggest power consumers
- Use Phi-3 (smaller model) for simple tasks
- Batch your AI queries rather than continuous use

**Limit Simultaneous Users**
- Each connected device adds load
- Fewer users = longer runtime

**Stop Unused Services**
- Use Dockge to stop services you're not using
- Jellyfin, LibreTranslate use significant resources

**Reduce Screen Brightness (on connected devices)**
- Your phone/laptop screen affects your battery, not MuleCube
- But fewer requests = less MuleCube processing

### Service Power Consumption

| Service | Power Draw | Notes |
|---------|-----------|-------|
| Idle (no activity) | Low | Dashboard, basic services |
| Wikipedia browsing | Low | Mostly reading from storage |
| Map navigation | Low-Medium | Some processing for rendering |
| AI chat (Phi-3) | Medium | 5-10W during inference |
| AI chat (DeepSeek) | High | 10-15W during inference |
| Jellyfin streaming | Medium | Depends on transcoding |
| Multiple services | Cumulative | Load adds up |

## Hot-Swapping Batteries

MuleCube supports hot-swapping battery cells for unlimited runtime in the field.

### Requirements

- Spare Samsung 18650 cells (or equivalent)
- Cells should be pre-charged
- Swap one cell at a time

### Swap Procedure

> ⚠️ **Warning:** Only swap batteries if your MuleCube model supports hot-swap. Check your specific hardware configuration.

1. **Check current status**
   - Ensure at least 3 cells remain above 20%
   - Don't swap if only one cell is healthy

2. **Remove depleted cell**
   - Open the battery compartment
   - Identify the depleted cell (if marked)
   - Gently remove it

3. **Insert fresh cell**
   - Observe correct polarity (+/-)
   - Slide in the fresh cell
   - Close compartment

4. **Verify**
   - Check dashboard shows charging
   - Battery percentage should increase

### Cell Rotation

For field expeditions:

1. Carry spare charged cells
2. Rotate depleted cells for charging
3. Use solar charger for cell recharging
4. Label cells to track charge cycles

## Battery Health

### Monitoring Health

Check battery health in the Control Panel:

1. Open Diagnostics (from dashboard)
2. View "Battery Health" section
3. Check:
   - Cycle count
   - Capacity vs. design
   - Cell voltages

### Signs of Battery Degradation

| Symptom | Possible Cause | Action |
|---------|---------------|--------|
| Runtime decreased significantly | Normal aging | Consider cell replacement |
| Won't charge past 80% | Cell imbalance | Perform calibration cycle |
| Charges very slowly | Degraded cell | Test individual cells |
| Swelling/heat | Damaged cell | **Stop use immediately**, replace cells |

### Calibration Cycle

If the battery gauge seems inaccurate:

1. Charge to 100%
2. Use until auto-shutdown (5%)
3. Charge to 100% without interruption
4. This recalibrates the fuel gauge

Perform calibration every 3-6 months or when gauge seems off.

## Charging Options

### Standard Charging (Included Adapter)

- **Adapter:** 5V/5A USB-C (25W)
- **Charge time:** 3-4 hours
- **Recommended for:** Home/office use

### Fast Charging (USB-C PD)

MuleCube supports USB-C Power Delivery:

- **Up to 45W** charging supported
- **Charge time:** 1.5-2 hours
- **Requirements:** USB-C PD charger with 9V/3A or higher

### Solar Charging

For off-grid use:

- **Requirements:** 
  - 50W+ solar panel (100W recommended)
  - USB-C output or solar charge controller
  - Direct sunlight for best results

- **Expected charge rate:**
  - Full sun: 3-5 hours to full charge
  - Cloudy: May only maintain charge, not increase

- **Tips:**
  - Use MPPT charge controller for efficiency
  - Angle panel toward sun
  - Clean panel surface regularly

### Vehicle Charging

- **12V DC adapter:** Use USB-C car charger (15W minimum)
- **Charge time:** 4-6 hours from vehicle power
- **Note:** Don't drain your vehicle battery!

## Safety Information

### Do's

✅ Use the included charger or quality USB-C PD chargers
✅ Charge in ventilated area
✅ Store at room temperature
✅ Use genuine Samsung 18650 cells for replacements

### Don'ts

❌ Don't expose to extreme heat (>45°C / 113°F)
❌ Don't leave in direct sunlight for extended periods
❌ Don't use damaged or swollen batteries
❌ Don't charge unattended if cells are damaged
❌ Don't short-circuit battery terminals
❌ Don't dispose of batteries in regular trash

### Emergency Procedures

**If battery is swelling or very hot:**

1. Disconnect power immediately
2. Move to ventilated area
3. Do not attempt to use
4. Let cool naturally (don't use water)
5. Contact support for replacement

**If battery won't charge:**

1. Try different USB-C cable
2. Try different power adapter
3. Check for debris in USB-C port
4. Perform calibration cycle
5. Contact support if issue persists

## Specifications by Model

| Model | Battery Config | Capacity | Runtime |
|-------|---------------|----------|---------|
| Cube 8 | 4× 18650 | 50Wh | 10-15h |
| Cube 16 | 4× 18650 | 50Wh | 8-12h* |
| Cube AI | 6× 18650 | 75Wh | 8-12h |
| Cube Sat | 6× 18650 | 75Wh | 10-14h |
| Ultimate | 6× 18650 | 75Wh | 8-12h |

*Cube 16 may have slightly lower runtime due to higher RAM power consumption.
