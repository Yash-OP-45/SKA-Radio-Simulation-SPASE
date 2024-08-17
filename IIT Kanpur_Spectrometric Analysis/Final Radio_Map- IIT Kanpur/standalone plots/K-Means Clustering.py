import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
df = pd.read_csv(r'D:\Project-Simulation of the nightsky\TinySA\combined_csv\Combined High and Low\N1\N1.csv', names=['Frequency (Hz)', 'Magnitude (Log Mag dB)'])

scaler = StandardScaler()
df_scaled = scaler.fit_transform(df)
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(df_scaled)
labels = kmeans.labels_

plt.scatter(df_scaled[:, 0], df_scaled[:, 1], c=labels, cmap='viridis')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude (Log Mag dB)')
plt.title('K-Means Clustering with 3 Clusters')
plt.show()