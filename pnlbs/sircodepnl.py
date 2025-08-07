import pandas as pd
import os


file_path = "In Lakhs  BS_FY 23-24 V5 - Final.xlsx"
xls = pd.ExcelFile(file_path)


def clean_note(sheet_name, skiprows=3):
    df = xls.parse(sheet_name, skiprows=skiprows)
    df = df.dropna(how='all').dropna(axis=1, how='all').reset_index(drop=True)
    return df

# Clean each sheet
note_16_23_df = clean_note("Note 16-23", skiprows=3)


# Export each as CSV
output_folder = "csv_notes_pnl"
os.makedirs(output_folder, exist_ok=True)

# Export each as CSV in the folder
note_16_23_df.to_csv(os.path.join(output_folder, "Note_16_to_23_Full.csv"), index=False)


# Print confirmation and row counts
print(f"Extracted rows: Note 16-23 = {note_16_23_df.shape[0]} rows")
