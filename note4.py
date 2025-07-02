import pandas as pd
import os

def calculate_note_4(df):
   
    particulars_row = df[df.iloc[:, 0].str.contains('Particulars', case=False, na=False)].index
    if particulars_row.empty:
        raise ValueError("No 'Particulars' row found")
    df = df.iloc[particulars_row[0]+1:].reset_index(drop=True)
    
   
    account_col = df.columns[0]
    
    
    balance_col = None
    for col in df.columns[1:]:
        if df[col].dtype in [float, int] and df[col].notna().any():
            balance_col = col
            break
    if not balance_col:
        raise ValueError("No numeric balance column found")
    
    
    loans_value = 0
    maturities_value = 0
    df = df.fillna(0)
    for idx, row in df.iterrows():
        account_name = str(row[account_col]).strip().lower()
        if 'loan' in account_name and 'maturities' not in account_name:
            loans_value += row[balance_col] / 100000  
        if 'current maturities' in account_name:
            maturities_value = row[balance_col] / 100000
    
    if loans_value == 0:
        print("Accounts:", df[account_col].dropna().unique()[:10])
        raise ValueError("No loan accounts found")
    
    return loans_value - maturities_value

def main():
    try:
        excel_file = "In Lakhs  BS_FY 23-24 V5 - Final.xlsx"
        if not os.path.exists(excel_file):
            data_folder = "data"
            excel_files = [f for f in os.listdir(data_folder) if f.endswith(('.xlsx', '.xls'))] if os.path.exists(data_folder) else []
            if not excel_files:
                raise FileNotFoundError(f"No Excel files in '{data_folder}'")
            print("Excel files found:")
            for i, f in enumerate(excel_files, 1):
                print(f"{i}. {f}")
            excel_file = os.path.join(data_folder, excel_files[0])
        
        df = pd.read_excel(excel_file, sheet_name="Trial Balance", engine="openpyxl", header=None)
        result = calculate_note_4(df)
        
        output_df = pd.DataFrame([["Long-term Borrowings", result]], columns=["Item", "Value"])
        os.makedirs("outputs", exist_ok=True)
        output_df.to_csv("outputs/note_4_output.csv", index=False)
        print(f"Long-term Borrowings: {result} Lakhs")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()