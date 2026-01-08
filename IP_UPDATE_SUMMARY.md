# IP Address Update Summary
**Date:** 2026-01-08
**Old IP Addresses:** 10.111.224.71, 10.49.216.71
**New IP Address:** 10.192.168.71

---

## ✅ All Files Updated Successfully

Total of **35 occurrences** updated across **15 files**:

### Shell Scripts (4 files)
1. ✅ `scripts/transfer_to_pi.sh` - Transfer dashboard to Pi
2. ✅ `scripts/transfer_mqtt_to_pi.sh` - Transfer MQTT system
3. ✅ `scripts/get_data_from_pi.sh` - Retrieve CSV data
4. ✅ `scripts/start_dashboard.sh` - Start dashboard remotely
5. ✅ `start_dashboard_pi.sh` - Dashboard launcher on Pi

### Python Files (1 file)
6. ✅ `src/web_dashboard_advanced.py` - Access URL in comments and logs

### Documentation Files (10 files)
7. ✅ `README.md` - Main project documentation
8. ✅ `SIMPLE_WORKFLOW.md` - Simple workflow guide
9. ✅ `docs/BAYESIAN_FILTER_README.md` - Bayesian filter docs
10. ✅ `docs/QUICK_START_BAYESIAN.md` - Quick start guide
11. ✅ `mqtt/README.md` - MQTT system documentation
12. ✅ `mqtt/GETTING_STARTED.md` - MQTT getting started
13. ✅ `mqtt/DASHBOARD_INTEGRATION.md` - Dashboard integration

---

## Verification

**Old IPs remaining:** 0 ✅
**New IP occurrences:** 35 ✅

All references to old IP addresses have been successfully replaced!

---

## Quick Test Commands

### 1. Transfer Code to Pi
```bash
./scripts/transfer_to_pi.sh
```

Should connect to: `jdmc@10.192.168.71`

### 2. SSH to Pi
```bash
ssh jdmc@10.192.168.71
```

### 3. Access Dashboard
```
http://10.192.168.71:5001
```

---

## What to Do Now

1. **Test connection:**
   ```bash
   ping 10.192.168.71
   ```

2. **Transfer updated code:**
   ```bash
   cd /Users/mirac/Desktop/master_sse_25_26-main/dataFusion
   ./scripts/transfer_to_pi.sh
   ```

3. **Start dashboard on Pi:**
   - SSH: `ssh jdmc@10.192.168.71`
   - Run: `cd ~/dataFusion && ./start_dashboard_pi.sh`

4. **Access from browser:**
   - Open: `http://10.192.168.71:5001`

5. **Collect data:**
   - Click "START WALKING"
   - Walk and press middle button for each stride
   - Click "📥 DOWNLOAD ALL DATA (CSV)"

---

**Status:** ✅ All IP addresses updated and ready to use!

---

**Last Updated:** 2026-01-08
