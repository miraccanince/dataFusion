# Simple Workflow to Complete Assignment

## What You Need to Do (3 Simple Steps)

### Step 1: Collect Data on Raspberry Pi (30 minutes)

#### Setup
```bash
# Transfer updated code to Pi (with new download buttons!)
./scripts/transfer_to_pi.sh

# SSH to Pi
ssh jdmc@10.192.168.71

# Start dashboard
cd ~/dataFusion
./start_dashboard_pi.sh
```

#### Open Dashboard on Your Laptop
Open browser: `http://10.192.168.71:5001`

You'll now see **NEW BLUE DOWNLOAD BUTTONS** below the START/STOP buttons!

#### Experiment 1: Walk Straight (3 strides is enough!)

1. Click "START WALKING"
2. Walk 3 strides in ANY direction (North, East, whatever)
3. Press middle button on joystick after each stride
4. Click "STOP WALKING"
5. **Click "📥 DOWNLOAD ALL DATA (CSV)"** ← Downloads 4 CSV files!
6. Files save to your laptop's Downloads folder

That's ONE experiment done! The CSV files have names like:
- `naive_trajectory_20260108_153045.csv`
- `bayesian_trajectory_20260108_153045.csv`
- `kalman_trajectory_20260108_153045.csv`
- `particle_trajectory_20260108_153045.csv`

#### Experiment 2: Walk a Square (optional, but good to have)

1. Click "Reset Tracking" (clears previous data)
2. Click "START WALKING"
3. Walk 3 strides North → turn → 3 strides East → turn → 3 strides South → turn → 3 strides West
4. Click "STOP WALKING"
5. **Click "📥 DOWNLOAD ALL DATA (CSV)"** again
6. Get another set of 4 CSV files

---

### Step 2: Move CSV Files to Project (2 minutes)

On your laptop, move the CSV files from Downloads to your project:

```bash
cd /Users/mirac/Desktop/master_sse_25_26-main/dataFusion

# Create a data folder
mkdir -p data/experiments

# Move CSV files from Downloads
mv ~/Downloads/*_trajectory_*.csv data/experiments/

# Check files are there
ls data/experiments/
```

You should see something like:
```
naive_trajectory_20260108_153045.csv
bayesian_trajectory_20260108_153045.csv
kalman_trajectory_20260108_153045.csv
particle_trajectory_20260108_153045.csv
naive_trajectory_20260108_154012.csv      (second experiment)
bayesian_trajectory_20260108_154012.csv    (second experiment)
...
```

---

### Step 3: Run Jupyter Notebook (30 minutes)

#### Open the Notebook

```bash
cd /Users/mirac/Desktop/master_sse_25_26-main/dataFusion
jupyter notebook part2_bayesian_navigation_analysis.ipynb
```

#### What the Notebook Does

The notebook will:

1. **Load your CSV files**
   ```python
   # Something like this (already in the notebook):
   import pandas as pd
   naive_df = pd.read_csv('data/experiments/naive_trajectory_20260108_153045.csv')
   bayesian_df = pd.read_csv('data/experiments/bayesian_trajectory_20260108_153045.csv')
   ```

2. **Generate trajectory plots**
   - Shows paths of all 4 algorithms on the floor plan
   - You'll see how Naive walks through walls, but Bayesian avoids them

3. **Calculate errors**
   - Compares final positions
   - Shows which algorithm is most accurate

4. **Create analysis**
   - Mathematical equations (Equation 5)
   - Parameter tables
   - Error plots

#### Run the Notebook

Just click: **Cell → Run All**

Or press `Shift + Enter` on each cell one by one.

The notebook will:
- Load your data ✅
- Generate plots ✅
- Calculate statistics ✅
- Show results ✅

#### Export to PDF

When done:
1. Click: **File → Download as → PDF via LaTeX**
2. Or: **File → Print Preview → Save as PDF**

---

## That's It! You're Done! 🎉

### Summary of Workflow

```
Pi Dashboard → Walk 3 strides → Click DOWNLOAD → Get CSV files
                                       ↓
                               Move to data/experiments/
                                       ↓
                         Jupyter Notebook → Run All → PDF
                                       ↓
                                    DONE! ✅
```

### What Gets Generated

From the notebook, you'll get:
- **Trajectory plots** - Visual comparison of algorithms
- **Error analysis** - Numbers showing Bayesian is better
- **Parameter tables** - All filter settings documented
- **Mathematical explanations** - Equation 5 explained
- **PDF report** - Ready to submit

---

## FAQ

### Q: How many strides do I need to walk?
**A:** 3-4 strides per direction is enough! You don't need 10 strides or 10 meters. Your room is only 3.5m × 6.0m, so 3 strides (2.1 meters) is perfect.

### Q: How many experiments do I need?
**A:** Minimum 2-3 experiments:
- Experiment 1: Straight line (any direction)
- Experiment 2: Square or L-shape (shows wall avoidance)
- (Optional) Experiment 3: Test heading errors

### Q: Will the Jupyter notebook work automatically?
**A:** The notebook structure is already there. You just need to:
1. Update the CSV file paths to match your downloaded files
2. Run all cells
3. Plots and analysis generate automatically

### Q: What if I don't know how to use Jupyter?
**A:** It's very simple:
1. Open the notebook (it's like a document with code)
2. Click "Run All" button
3. Wait for plots to appear
4. Save as PDF
Done!

### Q: Do I need to write code in the notebook?
**A:** No! The code is already written. You just need to:
- Update file paths to your CSV files
- Run the cells
- Maybe add a few text explanations

---

## Time Estimate

- **Collect data on Pi:** 30 minutes
- **Move files:** 2 minutes
- **Run notebook:** 30 minutes
- **Export PDF:** 5 minutes

**Total: ~1 hour to complete everything!**

---

## Next Action

1. Transfer code to Pi: `./scripts/transfer_to_pi.sh`
2. Start dashboard: `./start_dashboard_pi.sh`
3. Open browser: `http://10.192.168.71:5001`
4. **Look for the new BLUE "📥 DOWNLOAD ALL DATA (CSV)" button!**
5. Walk 3 strides, click download, done!

---

**Last Updated:** 2026-01-08
