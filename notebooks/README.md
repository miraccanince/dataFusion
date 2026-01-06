# Jupyter Notebooks for Assignment Analysis

## 📚 Available Notebooks

### 1. `DFA_2025_Code 11.ipynb` - Course Educational Material

**Source:** DFA course teaching materials
**Size:** ~100 cells, 1943 lines
**Purpose:** Educational foundation for Bayesian filtering concepts

**Contents:**
- Statistics: Mean, variance, outliers
- Probability distributions: Binomial, Beta, Gaussian, **Von Mises**
- **1D Kalman Filter** implementation
- **Discrete Bayes Filter** (dog in hallway example)
- Convolution for movement prediction

**Key Sections for Your Project:**
- **Cells 28-31:** Von Mises distribution (angular data) ⭐ Already used in bayesian_filter.py
- **Cells 24-27:** 1D Kalman filter ⭐ Already used in web_dashboard_advanced.py
- **Cells 35-94:** Discrete Bayes filter ⭐ Similar to your pedestrian tracking!

**What's Missing:**
- ❌ Particle filter (you need to implement)
- ❌ Your actual pedestrian navigation results
- ❌ Architecture discussion

---

### 2. `03_analyze_data.ipynb` - Placeholder for Your Analysis

**Purpose:** Your assignment analysis (worth ~20% of grade!)

**Required Content:**

#### Section 1: Introduction
- Briefly explain pedestrian inertial navigation
- Reference Koroglu & Yilmaz 2017 paper
- State objectives

#### Section 2: Methodology Review (Use DFA_2025_Code 11.ipynb)
Copy relevant cells:
- Von Mises for heading angles
- 1D Kalman for sensor smoothing
- Discrete Bayes filter concept

#### Section 3: Your Experimental Results ⭐ CRITICAL
- Load trajectory CSV files from walking experiments
- Plot trajectories on floor plan
- Calculate errors vs ground truth
- Compare algorithms:
  - Naive Dead Reckoning
  - Bayesian Filter
  - Particle Filter

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load your data
naive_df = pd.read_csv('../output/naive_trajectory_20260105_143022.csv')
bayesian_df = pd.read_csv('../output/bayesian_trajectory_20260105_143022.csv')

# Plot comparison
plt.figure(figsize=(12, 6))
plt.plot(naive_df['x'], naive_df['y'], 'r-', label='Naive')
plt.plot(bayesian_df['x'], bayesian_df['y'], 'b-', label='Bayesian')
plt.legend()
plt.title('Algorithm Comparison')
plt.show()

# Calculate final position errors
naive_error = np.sqrt((naive_df['x'].iloc[-1] - gt_x)**2 + (naive_df['y'].iloc[-1] - gt_y)**2)
bayesian_error = np.sqrt((bayesian_df['x'].iloc[-1] - gt_x)**2 + (bayesian_df['y'].iloc[-1] - gt_y)**2)

print(f"Naive error: {naive_error:.2f}m")
print(f"Bayesian error: {bayesian_error:.2f}m")
print(f"Improvement: {(1 - bayesian_error/naive_error)*100:.1f}%")
```

#### Section 4: Particle Filter Implementation
- Implement particle filter
- Show algorithm code
- Compare with Bayesian filter

#### Section 5: Architecture Discussion
Classify and discuss 3 data fusion architectures:
1. **Centralized** (all sensors → central processor)
2. **Decentralized** (distributed processing)
3. **Hybrid** (combination)

Where does your system fit?

#### Section 6: Conclusions
- Which algorithm performed best?
- Why does Bayesian beat Naive?
- Floor plan constraint effectiveness
- Limitations and future work

---

## 🚀 How to Use These Notebooks

### For Understanding Concepts:

```bash
jupyter notebook notebooks/DFA_2025_Code\ 11.ipynb
```

Read through cells 35-94 (Discrete Bayes filter) - very similar to your problem!

### For Creating Your Analysis:

1. **Collect data first:**
   ```bash
   # Run launcher
   python3 launcher.py

   # Connect to Pi, start walking
   # Walk your floor plan path
   # Download trajectory CSVs from dashboard
   ```

2. **Open analysis notebook:**
   ```bash
   jupyter notebook notebooks/03_analyze_data.ipynb
   ```

3. **Add your results:**
   - Load CSV files
   - Plot trajectories
   - Calculate errors
   - Compare algorithms

4. **Add particle filter:**
   - Implement in separate cell
   - Test on same data
   - Compare with Bayesian

---

## 📊 Example Analysis Structure

```python
# Cell 1: Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

# Cell 2: Load Data
naive = pd.read_csv('../output/naive_trajectory.csv')
bayesian = pd.read_csv('../output/bayesian_trajectory.csv')

# Cell 3: Visualize Trajectories
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Naive
ax1.plot(naive['x'], naive['y'], 'r-o', markersize=3)
ax1.set_title('Naive Dead Reckoning')
ax1.set_xlabel('X (m)')
ax1.set_ylabel('Y (m)')
ax1.grid(True)

# Bayesian
ax2.plot(bayesian['x'], bayesian['y'], 'b-o', markersize=3)
ax2.set_title('Bayesian Filter (Floor Plan Constrained)')
ax2.set_xlabel('X (m)')
ax2.grid(True)

plt.tight_layout()
plt.show()

# Cell 4: Error Analysis
# Calculate cumulative drift
naive_drift = np.sqrt(naive['x']**2 + naive['y']**2)
bayesian_drift = np.sqrt(bayesian['x']**2 + bayesian['y']**2)

plt.plot(naive_drift, 'r-', label='Naive')
plt.plot(bayesian_drift, 'b-', label='Bayesian')
plt.xlabel('Stride Number')
plt.ylabel('Distance from Origin (m)')
plt.legend()
plt.title('Drift Accumulation')
plt.show()

# Cell 5: Statistical Summary
print("=" * 50)
print("ALGORITHM COMPARISON")
print("=" * 50)
print(f"Naive final error: {naive_drift.iloc[-1]:.2f}m")
print(f"Bayesian final error: {bayesian_drift.iloc[-1]:.2f}m")
print(f"Improvement: {(1 - bayesian_drift.iloc[-1]/naive_drift.iloc[-1])*100:.1f}%")
print("=" * 50)

# Cell 6: Heading Analysis
plt.figure(figsize=(12, 4))
plt.plot(naive['heading'], 'r-', alpha=0.7, label='Naive')
plt.plot(bayesian['heading'], 'b-', alpha=0.7, label='Bayesian')
plt.xlabel('Stride')
plt.ylabel('Heading (degrees)')
plt.legend()
plt.title('Heading Over Time')
plt.grid(True)
plt.show()
```

---

## ⚠️ Assignment Checklist

Use this to ensure your Jupyter notebook meets requirements:

- [ ] **Introduction** - Problem statement and objectives
- [ ] **Methodology** - Explain Bayesian filter (Equation 5)
- [ ] **Experimental Setup** - Floor plan, walking path description
- [ ] **Results** - Trajectory plots for all 3 algorithms
- [ ] **Error Analysis** - Quantitative comparison with ground truth
- [ ] **Discussion** - Why does Bayesian perform better?
- [ ] **Particle Filter** - Implementation and results
- [ ] **Architecture** - Categorize 3 fusion architectures
- [ ] **Conclusions** - Summary and future work
- [ ] **References** - Cite Koroglu & Yilmaz 2017 paper

---

## 💡 Tips

1. **Run experiments multiple times** - Show statistical significance
2. **Include error bars** - Show variance in results
3. **Clear visualizations** - Label axes, add legends, use colors
4. **Explain equations** - Don't just show math, explain what it means
5. **Compare quantitatively** - Not just "Bayesian is better", show "Bayesian reduces error by 73%"

---

## 📞 Need Help?

- Check `DFA_2025_Code 11.ipynb` cells 35-94 for discrete Bayes filter example
- See `AUTO_WALK_GUIDE.md` for collecting walking data
- See `DEMO_SYSTEM.md` for running system demos
