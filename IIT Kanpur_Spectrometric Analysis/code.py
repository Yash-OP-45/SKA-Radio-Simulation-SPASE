import pandas as pd
import matplotlib.pyplot as plt
import os

def convert_delimiter(csv_file, comma_csv_file):
    with open(csv_file, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace(';', ',')
    with open(comma_csv_file, 'w') as file:
        file.write(filedata)

def plot_spectrum(csv_file, output_file):
    temp_csv_file = 'temp_converted_file.csv'
    convert_delimiter(csv_file, temp_csv_file)
    
    try:
        data = pd.read_csv(temp_csv_file, header=None)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return
    
    if data.shape[1] < 2:
        print("Error: The CSV file does not contain the expected columns.")
        return
    
    try:
        frequency = data.iloc[:, 0]
        power = data.iloc[:, 1]
    except IndexError as e:
        print(f"Error: {e}")
        return
    
    max_power = max(power)
    max_frequency = frequency[power.idxmax()]    #max_power_point
    plt.figure(figsize=(12, 7))
    plt.plot(frequency, power, label='Strength (Log Mag dB)', color='blue', linestyle='-', linewidth=1.5)
    plt.scatter(max_frequency, max_power, color='red', zorder=5)
    plt.text(max_frequency, max_power, f'Max: {max_power:.2f} dB\n@ {max_frequency:.2f} Hz', 
             fontsize=10, ha='right', color='red')
    plt.title('N1- SPASE Dept. Low_3', fontsize=16)
    plt.xlabel('Frequency (Hz)', fontsize=14)
    plt.ylabel('Strength (Log Mag dB)', fontsize=14)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.savefig(output_image, dpi=300)
    plt.show()
    os.remove(temp_csv_file)


csv_file = r'D:\Project-Simulation of the nightsky\TinySA\Spectrometric Analysis\N1\tinysa_2024-07-06_16-05-12-L-N1-3.csv'
output_image = r'D:\Project-Simulation of the nightsky\TinySA\Spectrum Plots_Processed\N1_L_3.png'
plot_spectrum(csv_file, output_image)
