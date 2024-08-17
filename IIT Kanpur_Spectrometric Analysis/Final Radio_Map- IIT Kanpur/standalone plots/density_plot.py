import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
df = pd.read_csv(r'D:\Project-Simulation of the nightsky\TinySA\combined_csv\Combined High and Low\N1\N1.csv', names=['Frequency (Hz)', 'Magnitude (Log Mag dB)'])

plt.figure(figsize=(6, 4))
sns.kdeplot(df['Magnitude (Log Mag dB)'], 
            shade=True, 
            color='#FFC5C5', 
            alpha=0.5, 
            linewidth=1.5, 
            linestyle='-', 
            label='Magnitude Density')

# CREATING MEAN LINE 
mean_magnitude = df['Magnitude (Log Mag dB)'].mean()
plt.axvline(mean_magnitude, color='gray', linestyle='--', label='Mean Magnitude')

plt.title('N1_SPASE Dept. - Density Plot', fontsize=18)
plt.xlabel('Magnitude (Log Mag dB)')
plt.ylabel('Density')
plt.legend(loc='upper right', fontsize=12)
plt.show()