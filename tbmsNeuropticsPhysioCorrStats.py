# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 10:04:48 2024

This file:
    1. Reads in a csv file with NeurOptics and physio data (for one eye and one protocol, after 
    running splitNeuropticsDataByProtocol and adding relevant physio data to the file)
    2. Splits data between pregnant and control groups
    3. Computes the correlation between Neuroptics PLR parameters and TMBS physio data.
    4. Computes correlation/correlation matrix between these parameters across preg/control groups
    5. Checks for normality of data and then does t-test or other test for significance across groups
    6. Controls for covariates (physio data+age) using ANOVA and Ordinary Least Squares

@author: kebl6975
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import tkinter as tk
from tkinter import filedialog
import statsmodels.api as sm
from statsmodels.formula.api import ols
import os

# Set pandas display options to prevent truncation of tables
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Ensure full width is used
pd.set_option('display.max_colwidth', None)  # Show full column content

# Create a Tkinter root window (it won't be shown)
root = tk.Tk()
root.withdraw()  # Hide the root window

# Prompt the user to select the file
file_path = filedialog.askopenfilename(
    title="Select the data file",
    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
)

# Check if a file was selected
if not file_path:
    print("No file selected. Exiting...")
    exit()

# Load the dataset
try:
    df = pd.read_csv(file_path)
    print(f"Data loaded successfully from {file_path}")
except Exception as e:
    print(f"Error loading file: {e}")
    exit()

# Output file to save results
output_file = filedialog.asksaveasfilename(
    title="Save results as",
    defaultextension=".txt",
    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
)

if not output_file:
    print("No output file selected. Exiting...")
    exit()

# Create a directory to save CSV files
csv_directory = os.path.dirname(output_file)  # Same location as output file
if not os.path.exists(csv_directory):
    os.makedirs(csv_directory)

# Open the output file in write mode
with open(output_file, 'w') as file:

    # Write the header
    file.write(f"Results for data from {file_path}\n\n")

    # Step 1: Combine the 'Preg Norm' and 'Preg Hyper' into one group called 'Pregnant'
    df['Group'] = df['Group'].replace({'Preg Norm': 'Pregnant', 'Preg Hyper': 'Pregnant'})

    # List of dependent variables for light flash - uncomment for light flash data
    """dependent_vars = [
        'PLR_Diameter_Init', 'PLR_Diameter_End', 'PLR_Latency',
        'PLR_Constriction_Velocity', 'PLR_Max_Constriction_Velocity',
        'PLR_Dilation_Velocity', 'PLR_T75', 'Amplitude'
    ]"""
    dependent_vars = [ # list for dark flash - uncomment for dark flash data
        'PLR_Diameter_Init', 'PLR_Diameter_End', 'PLR_Latency',
        'PLR_Dilation_Velocity', 'Amplitude'
    ]
    # Covariates
    covariates = ['Age', 'BMI', 'PostpartumMonths', 'BPsys', 'BPdia', 'HR']

    # Group column
    group_col = 'Group'

    # Step 2: Compute the correlation matrix and p-values

    # Create an empty list to store correlation coefficients and p-values
    correlation_matrix = df[dependent_vars + covariates].corr()
    p_values_matrix = pd.DataFrame(np.zeros(correlation_matrix.shape), columns=correlation_matrix.columns, index=correlation_matrix.index)

    # Handle NaN values for Control group - only drop NaNs in the control group for "Postpartum Months"
    df_control = df[df[group_col] == 'Control'].dropna(subset=dependent_vars + covariates)
    df_pregnant = df[df[group_col] == 'Pregnant']

    # Combine the cleaned control group with the pregnant group
    df_cleaned = pd.concat([df_control, df_pregnant])

    # Compute the Pearson correlation and p-values for each pairwise combination
    for i in range(len(correlation_matrix.columns)):
        for j in range(i, len(correlation_matrix.columns)):
            col1 = correlation_matrix.columns[i]
            col2 = correlation_matrix.columns[j]
            
            # Calculate Pearson correlation and p-value on the cleaned data (excluding NaNs in Control group)
            corr, p_val = pearsonr(df_cleaned[col1], df_cleaned[col2])
            correlation_matrix.loc[col1, col2] = corr
            correlation_matrix.loc[col2, col1] = corr  # Symmetric matrix
            
            p_values_matrix.loc[col1, col2] = p_val
            p_values_matrix.loc[col2, col1] = p_val  # Symmetric matrix
            
    # Write the correlation matrix and p-values to the output file
    file.write("\nCorrelation Matrix (with p-values):\n")
    file.write("Correlation Coefficients:\n")
    file.write(str(correlation_matrix) + "\n")
    file.write("\nP-values:\n")
    file.write(str(p_values_matrix) + "\n")
    
    # Save the correlation matrix and p-values as CSV files
    correlation_csv = os.path.join(csv_directory, 'Correlation_Matrix.csv')
    p_values_csv = os.path.join(csv_directory, 'P_Values_Matrix.csv')
    combined_corr_csv = os.path.join(csv_directory, 'Combined_Correlation_Pvalues.csv')

    correlation_matrix.to_csv(correlation_csv)
    p_values_matrix.to_csv(p_values_csv)

    file.write(f"Correlation matrix saved as 'Correlation_Matrix.csv'.\n")
    file.write(f"P-values matrix saved as 'P_Values_Matrix.csv'.\n")
    
    # Combine correlation coefficients and p-values into one table
    combined_matrix = correlation_matrix.copy()

    # Format the combined table by adding p-values in parentheses
    for i in range(len(correlation_matrix.columns)):
        for j in range(i, len(correlation_matrix.columns)):
            # Combine correlation coefficient and p-value into a string
            combined_matrix.iloc[i, j] = f"{correlation_matrix.iloc[i, j]:.2f} (p = {p_values_matrix.iloc[i, j]:.3f})"
            combined_matrix.iloc[j, i] = combined_matrix.iloc[i, j]  # Symmetric matrix

    # Write the combined correlation + p-value matrix to the output file
    file.write("\nCorrelation Matrix with P-values:\n")
    file.write(str(combined_matrix) + "\n")

    # Save the combined table as a CSV file
    combined_matrix.to_csv(combined_corr_csv)


    # Step 3: Visualizations
    # Correlation heatmap with p-values
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Matrix')
    plt.savefig(os.path.join(csv_directory, 'Correlation_Heatmap.png'))  # Save the heatmap plot
    plt.close()
    file.write("Correlation heatmap saved as 'Correlation_Heatmap.png'.\n")

    # Step 4: Statistical comparison between groups
    for dep_var in dependent_vars:
        file.write(f"\nComparing {dep_var} across groups\n")
        
        # Group data by 'Group' and extract the columns
        control_group = df[df[group_col] == 'Control'][dep_var]
        pregnant_group = df[df[group_col] == 'Pregnant'][dep_var]

        # Check normality to decide between ANOVA and Kruskal-Wallis
        from scipy.stats import shapiro
        _, p_normality_control = shapiro(control_group)  # Test for normality (Shapiro-Wilk test)
        _, p_normality_pregnant = shapiro(pregnant_group)

        if p_normality_control > 0.05 and p_normality_pregnant > 0.05:
            # Data is normally distributed: Use ANOVA
            from scipy.stats import f_oneway
            f_stat, p_val = f_oneway(control_group, pregnant_group)
            file.write(f"One-way ANOVA:\n")
        else:
            # Data is not normally distributed: Use Kruskal-Wallis test
            from scipy.stats import kruskal
            h_stat, p_val = kruskal(control_group, pregnant_group)
            file.write(f"Kruskal-Wallis H-test:\n")
        
        # Write the result to file
        if p_val < 0.05:
            file.write(f"{dep_var}: Significant differences found (p = {p_val:.3f})\n")
        else:
            file.write(f"{dep_var}: No significant differences found (p = {p_val:.3f})\n")

    # Step 5: Control for covariates using multiple regression (ANCOVA approach)
    for dep_var in dependent_vars:
        file.write(f"\nControlling for covariates for {dep_var}\n")
        
        # Create formula for regression
        covariate_formula = ' + '.join(covariates)
        formula = f"{dep_var} ~ Group + {covariate_formula}"
        
        # Fit the ANCOVA model
        model = ols(formula, data=df).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        
        # Write the full ANOVA table to file (no truncation)
        file.write(f"\n{dep_var} ANCOVA Table:\n")
        file.write(str(anova_table) + "\n")
        
        # Save the ANCOVA table as CSV
        anova_table_csv = os.path.join(csv_directory, f"{dep_var}_ANCOVA_table.csv")
        anova_table.to_csv(anova_table_csv)

file.write("\nAnalysis complete.\n")
print(f"Results and visualizations saved to {output_file}")
print(f"CSV files saved to {csv_directory}")