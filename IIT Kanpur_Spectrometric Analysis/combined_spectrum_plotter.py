import pandas as pd
import matplotlib.pyplot as plt
import os

def convert_delimiter(csv_file, comma_csv_file):
    with open(csv_file, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace(';', ',')
    with open(comma_csv_file, 'w') as file:
        file.write(filedata)

def convert_delimiter_2(csv_file, comma_csv_file):
    with open(csv_file, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace(',', ';')
    #with open(csv_file, 'w') as file:
     #  file.write(filedata) 
    with open(comma_csv_file, 'w') as file:
        file.write(filedata)  
    convert_delimiter(csv_file, comma_csv_file)
    return csv_file                

def plot_spectrum(csv_file1, csv_file2, output_file):
    temp_csv_file1 = 'temp_converted_file1.csv'
    temp_csv_file2 = 'temp_converted_file2.csv'
    convert_delimiter_2(csv_file1, temp_csv_file1)
    convert_delimiter(csv_file2, temp_csv_file2)
    
    try:
        data1 = pd.read_csv(temp_csv_file1, header=None)
        data2 = pd.read_csv(temp_csv_file2, header=None)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return
    
    if data1.shape[1] < 2 or data2.shape[1] < 2:
        print(data1.shape[1], data2.shape[1])
        print("Error: The CSV files do not contain the expected columns.")
        return
    
    try:
        frequency1 = data1.iloc[:, 0]
        power1 = data1.iloc[:, 1]
        frequency2 = data2.iloc[:, 0]
        power2 = data2.iloc[:, 1]
    except IndexError as e:
        print(f"Error: {e}")
        return
    
    max_power1 = max(power1)
    max_frequency1 = frequency1[power1.idxmax()]
    max_power2 = max(power2)
    max_frequency2 = frequency2[power2.idxmax()]
    
    plt.figure(figsize=(12, 7))
    plt.plot(frequency1, power1, label='Strength (Log Mag dB) - Low Freq.', color='blue', linestyle='-', linewidth=1.5)
    plt.plot(frequency2, power2, label='Strength (Log Mag dB) - High Freq.', color='red', linestyle='-', linewidth=1.5)
    plt.scatter(max_frequency1, max_power1, color='blue', zorder=5)
    plt.text(max_frequency1, max_power1, f'Max: {max_power1:.2f} dB\n@ {max_frequency1:.2f} Hz', 
             fontsize=10, ha='right', color='blue')
    plt.scatter(max_frequency2, max_power2, color='red', zorder=5)
    plt.text(max_frequency2, max_power2, f'Max: {max_power2:.2f} dB\n@ {max_frequency2:.2f} Hz', 
             fontsize=10, ha='right', color='red')
    plt.title(r'S3_IIT Main Sports Stadium_High_and_Low_3', fontsize=16)
    plt.xlabel('Frequency (Hz)', fontsize=14)
    plt.ylabel('Strength (Log Mag dB)', fontsize=14)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.savefig(output_file, dpi=300)
    plt.show()
    os.remove(temp_csv_file1)
    os.remove(temp_csv_file2)

csv_file1 = r'D:\Project-Simulation of the nightsky\TinySA\Spectrometric Analysis\S3\tinysa_2024-07-06_13-36-30-L-S3-3.csv'
csv_file2 = r'D:\Project-Simulation of the nightsky\TinySA\Spectrometric Analysis\S3\tinysa_2024-07-06_13-39-42-H-S3-3.csv'
output_image = r'D:\Project-Simulation of the nightsky\TinySA\Combined_Spectrum_plots\S3_3'
plot_spectrum(csv_file1, csv_file2, output_image)
