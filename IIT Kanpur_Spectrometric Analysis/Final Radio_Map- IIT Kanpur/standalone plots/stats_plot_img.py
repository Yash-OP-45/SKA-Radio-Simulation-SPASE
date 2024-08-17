import matplotlib.pyplot as plt
import pandas as pd
df = pd.read_csv(r'D:\Project-Simulation of the nightsky\TinySA\combined_csv\Combined High and Low\N1\N1.csv', names=['Frequency (Hz)', 'Magnitude (Log Mag dB)'])

stats = df['Magnitude (Log Mag dB)'].describe()
fig, ax = plt.subplots(figsize=(6, 4)) 
ax.axis('off')  
ax.text(0.5, 0.5, f"Count: {stats['count']:.2f}\n"
                    f"Mean: {stats['mean']:.2f}\n"
                    f"Standard Deviation: {stats['std']:.2f}\n"
                    f"Minimum: {stats['min']:.2f}\n"
                    f"25%: {stats['25%']:.2f}\n"
                    f"50%: {stats['50%']:.2f}\n"
                    f"75%: {stats['75%']:.2f}\n"
                    f"Maximum: {stats['max']:.2f}\n",
         transform=ax.transAxes, fontsize=14, ha='center')
plt.savefig('statistics_box.png', bbox_inches='tight')
plt.show()