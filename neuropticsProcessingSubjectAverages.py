import pandas as pd
import tkinter
from tkinter import filedialog

""" This file takes in a csv file from each individual subject, and calculates
the average PLR parameters grouped by "Measurement Type" and "Pupil Measured".
These results are then appended this to a master file, "Averages_by_Measurement_Type_and_Pupil_Measured_tebs.csv".
Once the processing has been done on each individual subject file, splitNeuropticsDataByProtocol
should be run to read in this output csv file and separate them into 4 files
corresponding to left and right eyes and light and dark flash protocols."""

def calculate_averages(csv_file):
    print(f"Processing file: {csv_file}")  # Debugging line
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(csv_file)
        
        # Make sure that the 'Pupil Measured' and 'Measurement Type' columns exist
        if 'Pupil Measured' not in df.columns or 'MeasurementType' not in df.columns:
            print("Error: 'Pupil Measured' or 'Measurement Type' column is missing in the CSV.")
            return
        
        # List of columns to exclude from averaging (non-numeric columns)
        non_numeric_columns = ['Record ID', 'Device ID', 'Time', 'Pupil Measured', 'MeasurementType']
        
        # Select only the numeric columns to average
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        
        # Exclude non-numeric columns from averaging
        numeric_columns = [col for col in numeric_columns if col not in non_numeric_columns]
        
        # Group by "Measurement Type" and "Pupil Measured" and calculate the mean of each group
        averages = df.groupby(['MeasurementType', 'Pupil Measured'])[numeric_columns].mean()
        
        # Return or print the resulting averages
        return averages
    except Exception as e:
        print(f"Error while processing the file: {e}")
        return None

# Function to open a file dialog and select the CSV file
def select_file():
    print("Opening file dialog...")  # Debugging line
    # Set up the Tkinter root window (it won't appear)
    root = tkinter.Tk()
    root.withdraw()  # Hide the root window
    # Open a file dialog to allow the user to select the CSV file
    file_path = filedialog.askopenfilename(
        title="Select a CSV File",
        filetypes=[("CSV Files", "*.csv")]
    )
    
    print(f"Selected file: {file_path}")  # Debugging line
    
    # Return the selected file path
    return file_path

# Main function to load data and calculate averages
# Prompt the user to select a CSV file
csv_file = select_file()
    
if not csv_file:
    print("No file selected. Exiting program.")
else:
    # Get the averages for each "Measurement Type" and "Pupil Measured" group
    averages = calculate_averages(csv_file)
        
    if averages is not None:
        # Print the resulting averages
        print("Averages grouped by 'Measurement Type' and 'Pupil Measured':")
        print(averages)
        filename = "Averages_by_Measurement_Type_and_Pupil_Measured_tebs.csv"
        averages.to_csv(filename, mode='a', header=False) # update header to True as required
        print(f"Results have been written to {filename}")