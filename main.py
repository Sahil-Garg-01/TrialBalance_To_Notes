import pandas as pd
import os

def clean_value(value):
    try:
        if isinstance(value, str):
            value = value.replace(',', '').strip()
        return float(value) if value else 0.0
    except (ValueError, TypeError):
        return 0.0

def to_lakhs(value):
    return round(value / 100000, 2)

def find_account_col(df):
    for col in df.columns:
        if df[col].astype(str).str.contains('account|particulars|name', case=False, na=False).any():
            return col
    return df.columns[0]

def find_balance_col(df):
    for col in df.columns:
        if df[col].dtype in [float, int] and df[col].notna().any():
            return col
    return df.columns[1] if len(df.columns) > 1 else None

def calculate_note(df, note_name, keywords, exclude=None, other_df=None):
    account_col = find_account_col(df)
    balance_col = find_balance_col(df)
    if not balance_col:
        return {'total': 0}
    df = df.fillna(0)
    total = 0
    for idx, row in df.iterrows():
        account_name = str(row[account_col]).strip().lower()
        if any(kw.lower() in account_name for kw in keywords) and (not exclude or not any(ex.lower() in account_name for ex in exclude)):
            total += row[balance_col]
    if other_df is not None and note_name == '12. Trade Receivables':
        total = other_df['Pending'].sum()
        over_6m = other_df[['360 to 720 days', '720 to 1440 days', '(> 1440 days )']].sum().sum()
        return {'total': total, 'over_6m': over_6m}
    if note_name == '7. Other Current Liabilities' and other_df is None:
        statutory_dues = 7935166.72  # Static value
        total += statutory_dues
    return {'total': total}

def generate_notes(tb_df, debtors_df=None, creditors_df=None):
    notes = []
    note_mappings = {
        '2. Share Capital': {'keywords': ['Share Capital']},
        '3. Reserves and Surplus': {'keywords': ['Reserves & Surplus']},
        '4. Long Term Borrowings': {'keywords': ['loan'], 'exclude': ['current maturities']},
        '5. Deferred Tax Liability': {'keywords': ['Deferred Tax Liability']},
        '6. Trade Payables': {'keywords': ['Sundry Creditors']},
        '7. Other Current Liabilities': {'keywords': ['Expenses Payable', 'Current Maturities']},
        '8. Short Term Provisions': {'keywords': ['Provision for Taxation']},
        '9. Fixed Assets': {'keywords': ['Equipments', 'Furniture & Fixtures', 'PURCHASE OF COMMERCIAL BULIDING', 'Bar Code Scanner and Printer', 'MERCEDES-BENZ CAR']},
        '10. Long Term Loans and Advances': {'keywords': ['Long Term - Security Deposits']},
        '11. Inventories': {'keywords': ['Opening Stock']},
        '12. Trade Receivables': {'keywords': ['Receivables']},
        '13. Cash and Cash Equivalents': {'keywords': ['Cash-in-Hand', 'Bank Accounts', 'Fixed Deposits']},
        '14. Short Term Loans and Advances': {'keywords': ['Prepaid Expenses', 'TDS Advance Tax', 'Balances with statutory', 'Other Advances']},
        '15. Other Current Assets': {'keywords': ['Interest accrued']},
        '16. Revenue from Operations': {'keywords': ['Servicing of BA/BE PROJECTS']},
        '17. Other Income': {'keywords': ['Interest income', 'Unadjusted Forex Gain/Loss']},
        '18. Cost of Materials Consumed': {'keywords': ['Opening Stock', 'Purchase Accounts']},
        '28. Earnings per Share': {'keywords': ['Profit & Loss A/c']},
        '29. Related Party Disclosures': {'keywords': []},
        '30. Financial Ratios': {'keywords': ['Opening Stock', 'Cash-in-Hand', 'Bank Accounts', 'TDS Receivables', 'Prepaid Expenses', 'Sundry Creditors', 'Expenses Payable']}
    }

    for note_name, mapping in note_mappings.items():
        keywords = mapping['keywords']
        exclude = mapping.get('exclude', [])
        other_df = debtors_df if note_name == '12. Trade Receivables' else creditors_df if note_name == '6. Trade Payables' else None
        result = calculate_note(tb_df, note_name, keywords, exclude, other_df)

        content = ""
        if note_name == '2. Share Capital':
            content = f"""
| Particulars | 2024-03-31 | 2023-03-31 |
|-------------|------------|------------|
| Authorised shares | | |
| 75,70,000 equity shares of ₹ 10/- each | {to_lakhs(75700000)} | {to_lakhs(75700000)} |
| Issued, subscribed and fully paid-up shares | | |
| 54,25,210 equity shares of ₹ 10/- each | {to_lakhs(result['total'])} | {to_lakhs(54252100)} |
| Total issued, subscribed and fully paid-up share capital | {to_lakhs(result['total'])} | {to_lakhs(54252100)} |
"""
        elif note_name == '7. Other Current Liabilities':
            expenses_payable = calculate_note(tb_df, note_name, ['Expenses Payable'])['total']
            current_maturities = calculate_note(tb_df, note_name, ['Current Maturities'])['total']
            statutory_dues = 7935166.72  # Static value
            content = f"""
| Particulars | 2024-03-31 | 2023-03-31 |
|-------------|------------|------------|
| Current Maturities of Long Term Borrowings | {to_lakhs(current_maturities)} | {to_lakhs(13920441)} |
| Outstanding Liabilities for Expenses | {to_lakhs(expenses_payable)} | {to_lakhs(15688272)} |
| Statutory dues | {to_lakhs(statutory_dues)} | {to_lakhs(4803131.66)} |
| Total | {to_lakhs(current_maturities + expenses_payable + statutory_dues)} | {to_lakhs(34411844.66)} |
"""
        elif note_name == '9. Fixed Assets':
            equipments = calculate_note(tb_df, note_name, ['Equipments'])['total']
            furniture = calculate_note(tb_df, note_name, ['Furniture & Fixtures'])['total']
            building = calculate_note(tb_df, note_name, ['PURCHASE OF COMMERCIAL BULIDING'])['total']
            barcode = calculate_note(tb_df, note_name, ['Bar Code Scanner and Printer'])['total']
            vehicle = calculate_note(tb_df, note_name, ['MERCEDES-BENZ CAR'])['total']
            content = f"""
| Particulars | Gross Carrying Value | Accumulated Depreciation | Net Carrying Value |
|-------------|----------------------|--------------------------|--------------------|
| As at 1st April 2023 | Additions | Deletion | As at 31st March 2024 | As at 1st April 2023 | For the year | Deletion | As at 31st March 2024 | As at 31st March 2024 | As at 1st April 2023 |
| **Tangible Assets** | | | | | | | | | |
| Buildings | {to_lakhs(312655)} | {to_lakhs(1419004627.5)} | 0 | {to_lakhs(1422131775)} | {to_lakhs(312654)} | {to_lakhs(1478808)} | 0 | {to_lakhs(1791462)} | {to_lakhs(1404216557.5)} | {to_lakhs(1)} |
| Equipments | {to_lakhs(equipments)} | {to_lakhs(17852001.75)} | 0 | {to_lakhs(equipments + 17852001.75)} | {to_lakhs(0)} | {to_lakhs(0)} | 0 | {to_lakhs(0)} | {to_lakhs(equipments + 17852001.75)} | {to_lakhs(equipments)} |
| Furniture & Fixtures | {to_lakhs(furniture)} | {to_lakhs(0)} | 0 | {to_lakhs(furniture)} | {to_lakhs(0)} | {to_lakhs(0)} | 0 | {to_lakhs(0)} | {to_lakhs(furniture)} | {to_lakhs(furniture)} |
| Motor Vehicle | {to_lakhs(vehicle)} | 0 | 0 | {to_lakhs(vehicle)} | {to_lakhs(0)} | {to_lakhs(752982.45)} | 0 | {to_lakhs(752982.45)} | {to_lakhs(4266900.55)} | {to_lakhs(vehicle)} |
| **Intangible Assets** | | | | | | | | | |
| Software | {to_lakhs(2109198)} | {to_lakhs(1771303)} | 0 | {to_lakhs(3880501)} | {to_lakhs(1502913)} | {to_lakhs(188706)} | 0 | {to_lakhs(1691619)} | {to_lakhs(2188882)} | {to_lakhs(6062850)} |
"""
        elif note_name == '12. Trade Receivables':
            content = f"""
| Particulars | 2024-03-31 | 2023-03-31 |
|-------------|------------|------------|
| Unsecured, considered good | | |
| Outstanding for a period exceeding six months | {to_lakhs(result['over_6m'])} | {to_lakhs(10465395)} |
| Total | {to_lakhs(result['total'])} | {to_lakhs(103758506)} |
"""
        elif note_name == '29. Related Party Disclosures':
            content = """
As per Accounting Standard 18, the disclosures of related parties as defined in the Accounting Standard are given below:
[Related party details require external input.]
"""
        elif note_name == '30. Financial Ratios':
            current_assets = sum(calculate_note(tb_df, note_name, [kw])['total'] for kw in ['Opening Stock', 'Cash-in-Hand', 'Bank Accounts', 'TDS Receivables', 'Prepaid Expenses'])
            current_liabilities = sum(calculate_note(tb_df, note_name, [kw])['total'] for kw in ['Sundry Creditors', 'Expenses Payable'])
            current_ratio = current_assets / current_liabilities if current_liabilities != 0 else 0
            content = f"""
| Particulars | 2024-03-31 | 2023-03-31 |
|-------------|------------|------------|
| Current Ratio | {round(current_ratio, 2)} | 2.52 |
"""
        else:
            content = f"""
| Particulars | 2024-03-31 | 2023-03-31 |
|-------------|------------|------------|
| {note_name} | {to_lakhs(result['total'])} | {to_lakhs(result['total'])} |
"""
        notes.append({'Note': note_name, 'Content': content})
    return notes

def main():
    try:
        excel_file = "In Lakhs  BS_FY 23-24 V5 - Final.xlsx"
        if not os.path.exists(excel_file):
            raise FileNotFoundError("Excel file not found")

        # Read sheets
        tb_df = pd.read_excel(excel_file, sheet_name="Trial Balance", engine="openpyxl", header=None)
        tb_df = tb_df.iloc[7:].reset_index(drop=True)  # Skip header rows
        tb_df = tb_df[[7, 8]].dropna(how='all')  # Use column 7 for accounts, 8 for balances
        tb_df.columns = ['Account', 'Balance']
        tb_df['Balance'] = tb_df['Balance'].apply(clean_value)
        print("Processed Trial Balance Columns:", tb_df.columns.tolist())
        print("Trial Balance First 10 Rows:", tb_df.head(10).to_dict())

        debtors_df = pd.read_excel(excel_file, sheet_name="Debtors", engine="openpyxl", skiprows=4)
        creditors_df = pd.read_excel(excel_file, sheet_name="Creditors", engine="openpyxl", skiprows=1)

        # Generate notes
        notes = generate_notes(tb_df, debtors_df, creditors_df)

        # Save to markdown
        os.makedirs("outputs", exist_ok=True)
        output = "# Notes to Financial Statements for the Year Ended March 31, 2024\n\n"
        for note in notes:
            output += f"## {note['Note']}\n{note['Content']}\n"
        with open("outputs/financial_notes_all.md", "w", encoding="utf-8") as f:
            f.write(output)

        # Save to CSV
        output_df = pd.DataFrame([
            [note['Note'], note['Content']] for note in notes
        ], columns=["Note", "Content"])
        with open("outputs/notes_output.csv", "w", encoding="utf-8") as f:
            output_df.to_csv(f, index=False)
        print("Notes generated and saved to 'outputs/financial_notes_all.md' and 'outputs/notes_output.csv'")

    except Exception as e:
        print(f"Error: {str(e)}")
        if 'tb_df' in locals():
            print("Trial Balance First 10 Rows:", tb_df.head(10).to_dict())
        if 'debtors_df' in locals():
            print("Debtors First 10 Rows:", debtors_df.head(10).to_dict())
        if 'creditors_df' in locals():
            print("Creditors First 10 Rows:", creditors_df.head(10).to_dict())

if __name__ == "__main__":
    main()
