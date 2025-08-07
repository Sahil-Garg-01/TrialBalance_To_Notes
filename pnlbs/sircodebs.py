import os
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load the Excel file
file_path = "In Lakhs  BS_FY 23-24 V5 - Final.xlsx"
xls = pd.ExcelFile(file_path)

# Define helper to clean each note
def clean_note(sheet_name, skiprows=3):
    df = xls.parse(sheet_name, skiprows=skiprows)
    df = df.dropna(how='all').dropna(axis=1, how='all').reset_index(drop=True)
    return df

# Clean each sheet
note_2_8_df = clean_note("Note 2 - 8", skiprows=3)
note_9_df = clean_note("Note 9", skiprows=3)
note_10_15_df = clean_note("Note 10-15", skiprows=3)

# Ensure output folder exists
output_folder = "csv_notes_bs"
os.makedirs(output_folder, exist_ok=True)

# Export each as CSV in the folder
note_2_8_df.to_csv(os.path.join(output_folder, "Note_2_to_8_Full.csv"), index=False)
note_9_df.to_csv(os.path.join(output_folder, "Note_9_Full.csv"), index=False)
note_10_15_df.to_csv(os.path.join(output_folder, "Note_10_to_15_Full.csv"), index=False)

# Print confirmation and row counts
print(f"Extracted rows: Note 2–8 = {note_2_8_df.shape[0]} rows")
print(f"Extracted rows: Note 9   = {note_9_df.shape[0]} rows")
print(f"Extracted rows: Note 10–15 = {note_10_15_df.shape[0]} rows")
