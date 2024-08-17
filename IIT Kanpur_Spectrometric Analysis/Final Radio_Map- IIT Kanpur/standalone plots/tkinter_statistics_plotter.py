import tkinter as tk
from tkinter import ttk
import pandas as pd
df = pd.read_csv(r'D:\Project-Simulation of the nightsky\TinySA\combined_csv\Combined High and Low\N1\N1.csv', names=['Frequency (Hz)', 'Magnitude (Log Mag dB)'])
stats = df['Magnitude (Log Mag dB)'].describe()
root = tk.Tk() #gui
root.title("Statistics")

stats_frame = ttk.Frame(root, padding="10 10 10 10")
stats_frame.pack(fill="both", expand=True)
ttk.Label(stats_frame, text="Count:").grid(row=0, column=0, sticky="W")
ttk.Label(stats_frame, text=str(stats['count'])).grid(row=0, column=1, sticky="W")

ttk.Label(stats_frame, text="Mean:").grid(row=1, column=0, sticky="W")
ttk.Label(stats_frame, text=str(stats['mean'])).grid(row=1, column=1, sticky="W")

ttk.Label(stats_frame, text="Standard Deviation:").grid(row=2, column=0, sticky="W")
ttk.Label(stats_frame, text=str(stats['std'])).grid(row=2, column=1, sticky="W")

ttk.Label(stats_frame, text="Minimum:").grid(row=3, column=0, sticky="W")
ttk.Label(stats_frame, text=str(stats['min'])).grid(row=3, column=1, sticky="W")

ttk.Label(stats_frame, text="25%:").grid(row=4, column=0, sticky="W")
ttk.Label(stats_frame, text=str(stats['25%'])).grid(row=4, column=1, sticky="W")

ttk.Label(stats_frame, text="50%:").grid(row=5, column=0, sticky="W")
ttk.Label(stats_frame, text=str(stats['50%'])).grid(row=5, column=1, sticky="W")

ttk.Label(stats_frame, text="75%:").grid(row=6, column=0, sticky="W")
ttk.Label(stats_frame, text=str(stats['75%'])).grid(row=6, column=1, sticky="W")

ttk.Label(stats_frame, text="Maximum:").grid(row=7, column=0, sticky="W")
ttk.Label(stats_frame, text=str(stats['max'])).grid(row=7, column=1, sticky="W")


root.mainloop()