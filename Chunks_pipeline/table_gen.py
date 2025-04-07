import matplotlib.pyplot as plt
import numpy as np

# Define the tables
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

# Create x values (indices) for each table
x1 = list(range(len(Table1)))
x2 = list(range(len(Table2)))

# Create the figure and axis
plt.figure(figsize=(12, 8))

# Plot Table1 as dots (circles)
plt.plot(x1, Table1, 'o', color='blue', markersize=8, label='Table 1 (Dots)')

# Plot Table2 as squares
plt.plot(x2, Table2, 's', color='red', markersize=8, label='Table 2 (Squares)')

# Add title and labels
plt.title('Comparison of Two Tables of Values', fontsize=16)
plt.xlabel('Index', fontsize=12)
plt.ylabel('Value', fontsize=12)

# Add a grid for better readability
plt.grid(True, linestyle='--', alpha=0.7)

# Add a legend
plt.legend(fontsize=12)

# Adjust the y-axis limits to show all data clearly
plt.ylim(min(min(Table1), min(Table2)) - 2, max(max(Table1), max(Table2)) + 2)

# Show the plot
plt.tight_layout()
plt.show()