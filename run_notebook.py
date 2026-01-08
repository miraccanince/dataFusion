#!/usr/bin/env python3
"""
Execute Jupyter notebook cells in correct order
"""

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import sys

# Read notebook
notebook_path = 'part2_bayesian_navigation_analysis.ipynb'
print(f"Loading notebook: {notebook_path}")

with open(notebook_path, 'r') as f:
    nb = nbformat.read(f, as_version=4)

print(f"Notebook has {len(nb.cells)} cells")

# Configure executor
ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

# Execute
print("Executing all cells...")
try:
    ep.preprocess(nb, {'metadata': {'path': '.'}})
    print("✓ Execution complete!")

    # Save executed notebook
    output_path = 'part2_bayesian_navigation_analysis.ipynb'
    with open(output_path, 'w') as f:
        nbformat.write(nb, f)
    print(f"✓ Saved executed notebook to: {output_path}")

except Exception as e:
    print(f"✗ Error during execution: {e}", file=sys.stderr)
    sys.exit(1)
