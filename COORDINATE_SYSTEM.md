# Coordinate System Reference

## Navigation Convention (CORRECT - As Used by Real IMU)

This project uses **navigation convention** as required by:
- Koroglu & Yilmaz 2017 paper
- Real SenseHat IMU hardware
- Assignment requirements

### Formula

```python
x_displacement = stride_length * sin(heading)
y_displacement = stride_length * cos(heading)
```

### Heading Angles

| Heading | Direction | Movement |
|---------|-----------|----------|
| 0° | North | +Y (up on map) |
| 90° | East | +X (right on map) |
| 180° | South | -Y (down on map) |
| 270° | West | -X (left on map) |

### Map Orientation

```
        North (0°)
            ↑
            |
            +Y
            |
West ←------+------→ East
(270°)      |      (90°)
           -Y
            |
            ↓
        South (180°)
```

### SenseHat Physical Setup

1. **Hold Pi FLAT** (like holding a tray)
2. **Point USB ports NORTH** (0° compass heading)
3. IMU magnetometer returns:
   - 0° when pointing North
   - 90° when pointing East
   - 180° when pointing South
   - 270° when pointing West

### Implementation Files

All files use navigation convention (0°=North):

- ✅ `src/bayesian_filter.py` lines 224, 344
- ✅ `src/particle_filter.py` line 57
- ✅ `src/kalman_filter.py` (uses measurements from above)
- ✅ `src/web_dashboard_advanced.py` lines 239, 269, 479, 740
- ✅ `mqtt/mqtt_location_publisher.py` line 225

### Verification

Run this test to verify:

```bash
python3 -c "
import sys
sys.path.insert(0, 'src')
import numpy as np
from bayesian_filter import BayesianNavigationFilter, FloorPlanPDF

fp = FloorPlanPDF(width_m=3.5, height_m=6.0, resolution=0.1)
bf = BayesianNavigationFilter(fp)
bf.reset(x=1.75, y=3.0)

# Walk North (0°)
result = bf.update(heading=0.0, stride_length=1.0)
print(f'0° (North): ({result[\"x\"]:.2f}, {result[\"y\"]:.2f})')  # Should be (1.75, 4.00)
"
```

Expected output: `0° (North): (1.75, 4.00)` ✓

---

**Last Updated:** 2026-01-07
**Status:** ✅ All filters verified correct
