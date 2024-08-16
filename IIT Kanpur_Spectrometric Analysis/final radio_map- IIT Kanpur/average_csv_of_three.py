import os
import csv
import pandas as pd

csv_folder = r'D:\Project-Simulation of the nightsky\TinySA\combined_csv\Combined High and Low\S9'
csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]
if len(csv_files) != 3:
    print("Only 3 CSV files allowed")
    exit()
output_data = []

for i, file in enumerate(csv_files):
    df = pd.read_csv(os.path.join(csv_folder, file), sep=';')
    df = df.replace(';', ',')
    data = df.values.tolist()
    if i == 0:
        output_data = [[float(val) for val in row] for row in data]
    else:
        for j in range(len(data)):
            for k in range(len(data[j])):
                output_data[j][k] += float(data[j][k])
for i in range(len(output_data)):
    for j in range(len(output_data[i])):
        output_data[i][j] /= 3
### OUTPUT
output_folder=r"D:\Project-Simulation of the nightsky\TinySA\combined_csv\Combined High and Low\final_csv"
with open(os.path.join(output_folder, 'S9.csv'), 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(output_data)

print("Output written in the output folder.")

 