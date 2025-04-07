import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

# Define the original tables
Table1 = [-75, -64.96, -50.92, -48.88, -46.84, -43.8, -42.76, -41.72, -40.68, -39.64,
        -38.6, -37.56, -36.52, -36, -35.5, -35, -34.5, -34, -33.5, -33,
        -32.5, -32, -31.5, -31, -30.5, -30, -29.72, -29.44, -29.16, -28.88,
        -28.6, -28.32, -28.04, -27.76, -27.48, -27.2, -26.92, -26.64, -26.36, -26.08,
        -25.8, -25.52, -25.24, -24.96, -24.68, -24.4, -24.12, -23.84, -23.56, -23.28,
        -23, -22.86, -22.72, -22.58, -22.44, -22.3, -22.16, -22.02, -21.88, -21.74,
        -21.6, -21.46, -21.32, -21.18, -21.04, -20.9, -20.76, -20.62, -20.48, -20.34,
        -20.2, -20.06, -19.92, -19.78, -19.64, -19.5, -19.36, -19.22, -19.08, -18.94,
        -18.8, -18.66, -18.52, -18.38, -18.24, -18.1, -17.96, -17.82, -17.68, -17.54,
        -17.4, -17.26, -17.12, -16.98, -16.84, -16.7, -16.56, -16.42, -16.28, -16.14,
        -16.0]

Table2 = [-75, -50, -45, -40, -37.75, -35, -33.5, -32, -30, -28.5,
        -27.5, -26.5, -25.75, -24.75, -24, -23.5, -23, -22.5, -21.9, -21.5,
        -20.8, -20.3, -19.8, -19.3, -19, -18.5, -18.2, -17.8, -17.4, -17.2,
        -16.8, -16.56, -16.32, -16.08, -15.84, -15.6, -15.36, -15.12, -14.88, -14.64,
        -14.4, -14.16, -13.92, -13.68, -13.44, -13.2, -12.96, -12.75, -12.6, -12.4,
        -12.25, -12, -11.85, -11.7, -11.6, -11.5, -11.4, -11.3, -11.2, -11.1,
        -11, -10.9, -10.8, -10.7, -10.6, -10.5, -10.4, -10.3, -10.2, -10.1,
        -10, -9.9, -9.8, -9.7, -9.6, -9.5, -9.4, -9.3, -9.2, -9.1,
        -9, -8.9, -8.8, -8.7, -8.6, -8.5, -8.4, -8.3, -8.2, -8.1,
        -8, -7.9, -7.8, -7.7, -7.6, -7.5, -7.4, -7.3, -7.2, -7.1,
        -7.0]

# Create x values for each table (normalized to [0,1])
x1 = np.linspace(0, 1, len(Table1))
x2 = np.linspace(0, 1, len(Table2))

# Choose a length for Table3 (I'll use the average of Table1 and Table2 lengths)
n3 = (len(Table1) + len(Table2)) // 2

# Create new x-values for Table3
x3 = np.linspace(0, 1, n3)

# Create interpolation functions for both tables
f1 = interpolate.interp1d(x1, Table1, kind='cubic')
f2 = interpolate.interp1d(x2, Table2, kind='cubic')

# Calculate interpolated values for both original tables at the new x-points
v1 = f1(x3)
v2 = f2(x3)

# Create Table3 as a weighted average of the two interpolations
# Weight changes gradually from favoring Table1 at start to favoring Table2 at end
weights = np.linspace(0.5, 0.5, n3)  # Equal weight to start
Table3 = weights * v1 + (1 - weights) * v2

# Force first and last values to match requirements
Table3[0] = -75.0  # First value: -75 dB

# Find the closest index to where -11 dB should be
target_idx = np.argmin(np.abs(Table3 - (-11.0)))
cutoff_idx = min(target_idx, len(Table3) - 1)

# Truncate Table3 at this index and ensure the last value is exactly -11 dB
Table3 = Table3[:cutoff_idx+1]
Table3[-1] = -11.0

# Round to 2 decimal places for readability
Table3 = np.round(Table3, 2)

# Plot the results
plt.figure(figsize=(14, 8))
plt.plot(x1, Table1, 'o', color='blue', markersize=6, label='Table1 (Dots)')
plt.plot(x2, Table2, 's', color='red', markersize=6, label='Table2 (Squares)')
plt.plot(np.linspace(0, 1, len(Table3)), Table3, '^', color='green', markersize=6, label='Table3 (Interpolated)')

# Add title and labels
plt.title('Comparison of Tables with Interpolated Table3', fontsize=16)
plt.xlabel('Normalized Index', fontsize=12)
plt.ylabel('Value (dB)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=12)
plt.tight_layout()
plt.show()

# Print Table3 for reference
print("Table3 = [", end="")
for i, val in enumerate(Table3):
    if i % 10 == 0 and i > 0:
        print("\n        ", end="")
    print(f"{val}", end=", " if i < len(Table3)-1 else "")
print("]")