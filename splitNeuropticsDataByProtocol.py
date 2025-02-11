# -*- coding: utf-8 -*-
"""
Created on Tue Nov 19 12:06:16 2024

This file reads in a csv file from the NeurOptics PLR-3000 output, and creates 
different files for each combination of pupil measured (left or right) and 
type of protocol (positive or negative flash protocol, corresponding to 1 or 2
respectively). This is to enable further analysis with other files.

@author: kebl6975
"""

import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os
# TODO: determine which eye's data to use

# Function to read and split the CSV file based on "MeasurementType" and "Pupil Measured"
def split_csv_file(csv_file):
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file)
        
        # Ensure the necessary columns exist
        required_columns = [
            'MeasurementType', 'Pupil Measured', 'Patient ID', 
            'PLR Diameter Init', 'PLR Diameter End', 'PLR Latency', 
            'PLR Constriction Velocity', 'PLR Max Constriction Velocity', 
            'PLR Dilation Velocity', 'PLR T75', 'Amplitude'
        ]
        
        # Check if all required columns exist
        if not all(col in df.columns for col in required_columns):
            print("Error: Some required columns are missing in the CSV file.")
            return
        
        # Select only the required columns
        df = df[required_columns]

        # Group the DataFrame by both "MeasurementType" and "Pupil Measured"
        grouped = df.groupby(['MeasurementType', 'Pupil Measured'])

        # Create a directory to store the output files if it doesn't exist
        output_dir = "tebs_neuroptics_output_files"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Iterate through each group and save it as a new CSV file
        for (measurement_type, pupil_measured), group in grouped:
            # Generate a clean filename based on the group
            filename = f"{measurement_type}_{pupil_measured}_tebs.csv"
            file_path = os.path.join(output_dir, filename)
            
            # Save each group to a separate CSV file
            group.to_csv(file_path, index=False)
            print(f"Saved {file_path}")
            
    except Exception as e:
        print(f"Error while processing the file: {e}")

# Function to open a file dialog and select the CSV file
def select_file():
    print("Opening file dialog...")  # Debugging line
    # Set up the Tkinter root window (it won't appear)
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    # Open a file dialog to allow the user to select the CSV file
    file_path = filedialog.askopenfilename(
        title="Select a CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )
    
    print(f"Selected file: {file_path}")  # Debugging line
    
    # Return the selected file path
    return file_path

# Main function
if __name__ == "__main__":
    # Prompt the user to select a CSV file
    csv_file = select_file()

    if not csv_file:
        print("No file selected. Exiting program.")
    else:
        # Split the CSV file based on "MeasurementType" and "Pupil Measured"
        split_csv_file(csv_file)