from app.utils import clean_value, to_lakhs

def calculate_note(df, note_name, keywords, exclude=None, other_df=None):
    if 'account_name' in df.columns:
        account_col = 'account_name'
        balance_col = 'amount'
    else:
        account_col = df.columns[0]
        balance_col = df.columns[1] if len(df.columns) > 1 else None

    if not balance_col:
        return {'total': 0}

    df = df.fillna(0)
    total = 0
    matched_accounts = []

    for idx, row in df.iterrows():
        account_name = str(row[account_col]).strip().lower()
        if any(kw.lower() in account_name for kw in keywords) and (not exclude or not any(ex.lower() in account_name for ex in exclude)):
            amount = clean_value(row[balance_col])
            total += amount
            matched_accounts.append({
                'account': str(row[account_col]),
                'amount': amount,
                'group': row.get('group', 'Unknown') if 'group' in df.columns else 'Unknown'
            })

    # Special case for Trade Receivables
    if other_df is not None and note_name == '12. Trade Receivables':
        if 'Pending' in other_df.columns:
            total = other_df['Pending'].sum()
            over_6m = other_df[['360 to 720 days', '720 to 1440 days', '(> 1440 days )']].sum().sum()
        else:
            over_6m = 0
        return {'total': total, 'over_6m': over_6m, 'matched_accounts': matched_accounts}

    if note_name == '7. Other Current Liabilities' and other_df is None:
        statutory_dues = 7935166.72  # Static value
        total += statutory_dues

    return {'total': total, 'matched_accounts': matched_accounts}

def generate_notes(tb_df, debtors_df=None, creditors_df=None):
    notes = []
    note_mappings = {
        '2. Share Capital': {'keywords': ['Share Capital', 'share capital', 'equity share', 'paid up']},
        '3. Reserves and Surplus': {'keywords': ['Reserves', 'Surplus', 'reserves', 'surplus', 'retained earnings']},
        '4. Long Term Borrowings': {'keywords': ['loan', 'borrowing', 'term loan'], 'exclude': ['current maturities', 'short term']},
        '5. Deferred Tax Liability': {'keywords': ['Deferred Tax', 'deferred tax']},
        '6. Trade Payables': {'keywords': ['Creditors', 'creditors', 'trade payable', 'suppliers']},
        '7. Other Current Liabilities': {'keywords': ['Expenses Payable', 'Current Maturities', 'payable', 'accrued']},
        '8. Short Term Provisions': {'keywords': ['Provision', 'provision', 'taxation']},
        '9. Fixed Assets': {'keywords': ['Equipment', 'Furniture', 'Building', 'Vehicle', 'Motor', 'Asset', 'plant', 'machinery']},
        '10. Long Term Loans and Advances': {'keywords': ['Long Term', 'Security Deposits', 'advances', 'deposits']},
        '11. Inventories': {'keywords': ['Stock', 'Inventory', 'stock', 'inventory', 'goods']},
        '12. Trade Receivables': {'keywords': ['Receivables', 'receivables', 'debtors', 'trade receivable']},
        '13. Cash and Bank Balances': {'keywords': ['Cash-in-hand', 'Bank accounts','Deposits']},
        '14. Short Term Loans and Advances': {'keywords': ['Prepaid Expenses', 'TDS Receivables', 'Loans & Advances', 'TCS RECEIVABLES', 'TDS Advance Tax Paid', 'Advance to Perennail']},
        '15. Other Current Assets': {'keywords': ['Interest accrued', 'accrued', 'current asset']},
        '16. Revenue from Operations': {'keywords': ['Revenue', 'Sales', 'Service', 'income', 'operations']},
        '17. Other Income': {'keywords': ['Interest on FD', 'Interest on Income Tax Refund', 'Unadjusted Forex Gain/Loss', 'Forex Gain / Loss']},
        '18. Cost of Materials Consumed': {'keywords': ['opening stock', 'Bio Lab Consumables', 'Non GST', 'Purchase GST','closing stock']},
        '28. Earnings per Share': {'keywords': ['Profit', 'Loss', 'profit', 'loss']},
        '29. Related Party Disclosures': {'keywords': []},
        '30. Financial Ratios': {'keywords': ['Stock', 'Cash', 'Bank', 'Receivables', 'Creditors', 'Payable']}
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
        elif note_name == '3. Reserves and Surplus':
            content = f"""
                                                 | March,31 2024  | March,31 2023    
| {note_name.split('.', 1)[1].strip() if '.' in note_name else note_name}                           | {to_lakhs(result['total'])}  
"""
        elif note_name == '4. Long Term Borrowings':
            content = f"""
                                                 | March,31 2024  | March,31 2023    
| {note_name.split('.', 1)[1].strip() if '.' in note_name else note_name}                           | {to_lakhs(result['total'])}  
"""
        elif note_name == '5. Deferred Tax Liability':
            content = f"""
                                                 | March,31 2024  | March,31 2023    
| {note_name.split('.', 1)[1].strip() if '.' in note_name else note_name}                         | {to_lakhs(result['total'])}  
"""
        elif note_name == '6. Trade Payables':
            content = f"""
                                                 | March,31 2024  | March,31 2023    
| {note_name.split('.', 1)[1].strip() if '.' in note_name else note_name}                                 | {to_lakhs(result['total'])}  
"""
        elif note_name == '7. Other Current Liabilities':
            expenses_payable = calculate_note(tb_df, note_name, ['Expenses Payable', 'payable', 'accrued'])['total']
            current_maturities = calculate_note(tb_df, note_name, ['Current Maturities', 'current portion'])['total']
            statutory_dues = 7935166.72  # Static value
            content = f"""
                                             | March,31 2024  | March,31 2023         

| Current Maturities of Long Term Borrowings | {to_lakhs(current_maturities)}          | {to_lakhs(13920441)} 
| Outstanding Liabilities for Expenses       | {to_lakhs(expenses_payable)}         | {to_lakhs(15688272)} 
| Statutory dues                             | {to_lakhs(statutory_dues)}          | {to_lakhs(4803131.66)} 
                                             | {to_lakhs(current_maturities + expenses_payable + statutory_dues)}         | {to_lakhs(34411844.66)} 
"""
        elif note_name == '8. Short Term Provisions':
            content = f"""
                                                 | March,31 2024  | March,31 2023    
| {note_name.split('.', 1)[1].strip() if '.' in note_name else note_name}                          | {to_lakhs(result['total'])}  
"""
        elif note_name == '9. Fixed Assets':
            equipments = calculate_note(tb_df, note_name, ['Equipment', 'equipment'])['total']
            furniture = calculate_note(tb_df, note_name, ['Furniture', 'furniture', 'fixture'])['total']
            building = calculate_note(tb_df, note_name, ['Building', 'building'])['total']
            vehicle = calculate_note(tb_df, note_name, ['Vehicle', 'vehicle', 'car'])['total']
            content = f"""
| Particulars | Gross Carrying Value | Accumulated Depreciation | Net Carrying Value |
|-------------|----------------------|--------------------------|--------------------|
| As at 1st April 2023 | Additions | Deletion | As at 31st March 2024 | As at 1st April 2023 | For the year | Deletion | As at 31st March 2024 | As at 31st March 2024 | As at 1st April 2023 |
| Tangible Assets | | | | | | | | | |
| Buildings | {to_lakhs(312655)} | {to_lakhs(building)} | 0 | {to_lakhs(312655 + building)} | {to_lakhs(312654)} | {to_lakhs(1478808)} | 0 | {to_lakhs(1791462)} | {to_lakhs(building)} | {to_lakhs(1)} |
| Equipments | {to_lakhs(equipments)} | {to_lakhs(0)} | 0 | {to_lakhs(equipments)} | {to_lakhs(0)} | {to_lakhs(0)} | 0 | {to_lakhs(0)} | {to_lakhs(equipments)} | {to_lakhs(equipments)} |
| Furniture & Fixtures | {to_lakhs(furniture)} | {to_lakhs(0)} | 0 | {to_lakhs(furniture)} | {to_lakhs(0)} | {to_lakhs(0)} | 0 | {to_lakhs(0)} | {to_lakhs(furniture)} | {to_lakhs(furniture)} |
| Motor Vehicle | {to_lakhs(vehicle)} | 0 | 0 | {to_lakhs(vehicle)} | {to_lakhs(0)} | {to_lakhs(752982.45)} | 0 | {to_lakhs(752982.45)} | {to_lakhs(vehicle - 752982.45)} | {to_lakhs(vehicle)} |
"""
        elif note_name == '11. Inventories':
            content = f"""
                                                 | March,31 2024  | March,31 2023    
| Consumables                                    | {to_lakhs(result['total'])}  
"""
        elif note_name == '12. Trade Receivables':
            over_6m = result.get('over_6m', 0)
            content = f"""
| Particulars | 2024-03-31 | 2023-03-31 |
|-------------|------------|------------|
| Unsecured, considered good | | |
| Outstanding for a period exceeding six months | {to_lakhs(over_6m)} | {to_lakhs(10465395)} |
| Total | {to_lakhs(result['total'])} | {to_lakhs(103758506)} |
"""
        elif note_name == '13. Cash and Bank Balances':
            cash_in_hand = calculate_note(tb_df, note_name, ['Cash-in-hand'])['total']
            bank_accounts = calculate_note(tb_df, note_name, ['Bank accounts'])['total']
            fixed_deposit = calculate_note(tb_df, note_name, ['Deposits'])['total']
            total = cash_in_hand + bank_accounts + fixed_deposit
            content = f"""
| Particulars      | March 31, 2024 | March 31, 2023 |
|------------------|----------------|----------------|
| Cash in hand     | {to_lakhs(cash_in_hand)}        | -              |
| Bank accounts    | {to_lakhs(bank_accounts)}       | -              |
| Fixed Deposit    | {to_lakhs(fixed_deposit)}       | -              |
| **Total**        | **{to_lakhs(total)}**           | -              |
"""
            result['total'] = total
        elif note_name == '14. Short Term Loans and Advances':
            otherAdvances = calculate_note(tb_df, note_name, ['Loans & Advances'])['total']
            PrepaidExpenses = calculate_note(tb_df, note_name, ['Prepaid Expenses'])['total']
            advancetaxes = calculate_note(tb_df, note_name, ['TDS Advance Tax Paid'])['total']
            balances = calculate_note(tb_df, note_name, ['TDS Receivables'])['total']
            total = otherAdvances + PrepaidExpenses + advancetaxes + balances
            content = f"""
| Particulars      | March 31, 2024 | March 31, 2023 |
|------------------|----------------|----------------|
| Prepaid Expenses | {to_lakhs(PrepaidExpenses)}     | -              |
| Other Advances   | {to_lakhs(otherAdvances)}       | -              |
| Advance tax      | {to_lakhs(advancetaxes)}        | -              |
| Balances with statutory/government authorities | {to_lakhs(balances)} | - |
| **Total**        | **{to_lakhs(total)}**           | -              |
"""
            result['total'] = total
        elif note_name == '16. Revenue from Operations':
            ServicingBABEExport = calculate_note(tb_df, note_name, ['Servicing of BA/BE PROJECTS EXPORT'])['total']
            WorkingStandardsExport = calculate_note(tb_df, note_name, ['Working Standards - Export'])['total']
            exports = ServicingBABEExport + WorkingStandardsExport

            ServicingBABEInterState = calculate_note(tb_df, note_name, ['Servicing of BA/BE PROJECTS-Inter State'])['total']
            ServicingBABEIntraState = calculate_note(tb_df, note_name, ['Servicing of BA/BE PROJECTS-Intra State'])['total']
            ServicingBAIntraState = calculate_note(tb_df, note_name, ['SERVICING OF BA PROJECTS-Intra State'])['total']
            ServicingClinicalIntraState = calculate_note(tb_df, note_name, ['SERVICING OF ONLY CLINICAL INTRA STATE'])['total']
            domestic = ServicingBABEInterState + ServicingBABEIntraState + ServicingBAIntraState + ServicingClinicalIntraState

            total = exports + domestic

            content = f"""
|                    | March 31, 2024          | March 31, 2023 |
|--------------------|------------------------|----------------|
| Sale of Services   |                        |                |
| Domestic           | {to_lakhs(domestic)}   | -              |
| Exports            | {to_lakhs(exports)}    | -              |
| **Total**          | {to_lakhs(total)}      | -              |
"""
            result['total'] = total
        elif note_name == '17. Other Income':
            InterestnFD = calculate_note(tb_df, note_name, ['Interest on FD'])['total']
            InterestonIncomeTaxRefund = calculate_note(tb_df, note_name, ['Interest on Income Tax Refund'])['total']
            UnadjustedForexGainLoss = calculate_note(tb_df, note_name, ['Unadjusted Forex Gain/Loss'])['total']
            ForexGainLoss = calculate_note(tb_df, note_name, ['Forex Gain/Loss'])['total']
            Interestincome = InterestnFD + InterestonIncomeTaxRefund
            ForeignexchangeainNet = UnadjustedForexGainLoss + ForexGainLoss
            total = Interestincome + ForeignexchangeainNet

            content = f"""
| Particulars                | March 31, 2024 | March 31, 2023 |
|----------------------------|----------------|----------------|
| Interest income            | {to_lakhs(Interestincome)} | - |
| Foreign exchange gain (Net)| {to_lakhs(ForeignexchangeainNet)} | - |
| **Total**                  | {to_lakhs(total)} | - |
"""
            result['total'] = total
        elif note_name == '18. Cost of Materials Consumed':
            openingstock = calculate_note(tb_df, note_name, ['opening stock'])['total']
            BioLabConsumables = calculate_note(tb_df, note_name, ['Bio Lab Consumables'])['total']
            NonGST = calculate_note(tb_df, note_name, ['Non GST'])['total']
            PurchaseGST = calculate_note(tb_df, note_name, ['Purchase GST'])['total']
            closingstock = calculate_note(tb_df, note_name, ['closing stock'])['total']

            purchases = BioLabConsumables + NonGST + PurchaseGST
            mid = openingstock + purchases
            total = openingstock + purchases - closingstock

            content = f"""
| Particulars         | March 31, 2024 | March 31, 2023 |
|---------------------|----------------|----------------|
| Opening Stock       | {to_lakhs(openingstock)} | - |
| Purchases           | {to_lakhs(purchases)} | - |
|                     | {to_lakhs(mid)} | - |
| Closing Stock       | {to_lakhs(closingstock)} | - |
| Cost of materials consumed | {to_lakhs(total)} | - |
"""
            result['total'] = total
        elif note_name == '30. Financial Ratios':
            current_assets = sum(calculate_note(tb_df, note_name, [kw])['total'] for kw in ['Stock', 'Cash', 'Bank', 'Receivables', 'Prepaid'])
            current_liabilities = sum(calculate_note(tb_df, note_name, [kw])['total'] for kw in ['Creditors', 'Payable'])
            current_ratio = current_assets / abs(current_liabilities) if current_liabilities != 0 else 0
            content = f"""
| Particulars     | 2024-03-31 | 2023-03-31 |
|-----------------|------------|------------|
| Current Ratio   | {round(current_ratio, 2)} | 2.52 |
| Current Assets  | {to_lakhs(current_assets)} | - |
| Current Liabilities | {to_lakhs(abs(current_liabilities))} | - |
"""
        else:
            content = f"""
                                                 | March,31 2024  | March,31 2023    
| {note_name.split('.', 1)[1].strip() if '.' in note_name else note_name}                      | {to_lakhs(result['total'])}  
"""
        notes.append({'Note': note_name, 'Content': content, 'Total': result['total'], 'Matched_Accounts': len(result.get('matched_accounts', []))})
    return notes