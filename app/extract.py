import pandas as pd
import json
import os
import re
import glob
from pathlib import Path
import requests
from dotenv import load_dotenv

def load_mappings(mapping_file='mapping1.json', rules_file='rules1.json'):
    """Loads exact mappings and keyword rules from JSON files."""
    exact_mappings = {}
    keyword_rules = {}
    try:
        if Path(mapping_file).exists():
            with open(mapping_file, 'r') as f:
                exact_mappings = json.load(f)
        if Path(rules_file).exists():
            with open(rules_file, 'r') as f:
                keyword_rules = json.load(f)
    except Exception as e:
        print(f"Error loading mappings: {e}")
    return exact_mappings, keyword_rules

def get_smart_rules():
    """Returns a dictionary of smart rules for account classification."""
    return {
        'Cash and Cash Equivalents': [r'\b(cash|bank|petty|till|vault|fd|fixed\s*deposit)\b'],
        'Trade Receivables': [r'\b(debtor|receivable|customer|outstanding.*debtor)\b'],
        'Trade Payables': [r'\b(creditor|payable|supplier|vendor|outstanding.*creditor)\b'],
        'Inventories': [r'\b(stock|inventory|goods|raw\s*material|wip|work.*progress)\b'],
        'Property, Plant and Equipment': [r'\b(land|building|plant|machinery|equipment|furniture|vehicle|depreciation)\b'],
        'Equity Share Capital': [r'\b(capital|share.*capital|paid.*up|equity)\b'],
        'Revenue from Operations': [r'\b(sales?|revenue|turnover|service.*income)\b'],
        'Employee Benefits Expense': [r'\b(salary|wages?|staff|employee|pf|provident|gratuity)\b'],
        'Finance Costs': [r'\b(interest|finance.*cost|bank.*charge)\b'],
        'Other Current Liabilities': [r'\b(tds|gst|vat|tax.*payable|service.*tax)\b']
    }

def parse_amount(amount_str):
    """Parses an amount string and returns a float."""
    if pd.isna(amount_str) or amount_str == '':
        return 0.0
    amount_str = str(amount_str).strip()
    is_credit = amount_str.lower().endswith('cr')
    amount_str = re.sub(r'[^\d\.\-\+]', '', amount_str)
    if not amount_str or amount_str in ['-', '+']:
        return 0.0
    try:
        amount = float(amount_str)
        if is_credit and amount > 0:
            amount = -amount
        return amount
    except ValueError:
        return 0.0

def classify_account(account_name, exact_mappings, keyword_rules, smart_rules, llm_model="qwen/qwen3-30b-a3b"):
    """Classifies an account name into a category."""
    account_name_clean = account_name.strip().lower()
    if account_name in exact_mappings:
        return exact_mappings[account_name], "mapping.json"
    for mapped_name, group in exact_mappings.items():
        if mapped_name.lower() == account_name_clean:
            return group, "mapping.json"
    for group, keywords in keyword_rules.items():
        for keyword in keywords:
            if keyword.lower() in account_name_clean.split():
                return group, "rules.json"
    for group, patterns in smart_rules.items():
        for pattern in patterns:
            if re.search(pattern, account_name_clean):
                return group, "smart_rules"
            
    # LLM Fallback
    # load_dotenv()
    # api_key = os.getenv("OPENROUTER_API_KEY")
    # if api_key:
    #     try:
    #         response = requests.post(
    #             "https://openrouter.ai/api/v1/chat/completions",
    #             headers={
    #                 "Authorization": f"Bearer {api_key}",
    #                 "Content-Type": "application/json"
    #             },
    #             json={
    #                 "model": "mistralai/mixtral-8x7b-instruct",
    #                 "messages": [
    #                     {
    #                         "role": "system",
    #                         "content": "You are a financial expert. Classify the following account name into one of these categories: Equity, Non-Current Liability, Current Liability, Non-Current Asset, Current Asset, Revenue from Operations, Cost of Materials Consumed, Direct Expenses, Other Income, Other Expenses, Employee Benefits Expense, Finance Cost, Accumulated Depreciation, Deferred Tax Liability, Profit and Loss Account. Respond only with the category name."
    #                     },
    #                     {
    #                         "role": "user",
    #                         "content": account_name
    #                     }
    #                 ]
    #             },
    #             timeout=10  # <-- Add this line!
    #         )
    #         response.raise_for_status()
    #         llm_response = response.json()
    #         llm_suggestion = llm_response['choices'][0]['message']['content'].strip()
    #         return llm_suggestion, "llm_fallback"
    #     except requests.exceptions.RequestException as e:
    #         print(f"LLM fallback failed: {e}")
    #     except Exception as e:
    #         print(f"Unexpected error in LLM fallback: {e}")
    return 'Unmapped', 'Unmapped'

def extract_trial_balance_data(file_path, sheet_name=0, header_row=0):
    """Extracts trial balance data from an Excel file."""
    try:
        df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []
    exact_mappings, keyword_rules = load_mappings()
    smart_rules = get_smart_rules()
    structured_data = []
    source_file = Path(file_path).name
    for idx, row in df_raw.iterrows():
        account_name = row.iloc[0] if len(row) > 0 else None
        if pd.isna(account_name) or str(account_name).strip() == '':
            continue
        account_name = str(account_name).strip()
        if len(account_name) <= 2 or account_name.replace('.', '').replace('-', '').isdigit():
            continue
        amount = 0.0
        if len(row) > 3 and not pd.isna(row.iloc[3]):
            amount = parse_amount(row.iloc[3])
        elif len(row) > 2:
            debit = parse_amount(row.iloc[1]) if len(row) > 1 else 0.0
            credit = parse_amount(row.iloc[2]) if len(row) > 2 else 0.0
            amount = debit - credit
        group, mapped_by = classify_account(account_name, exact_mappings, keyword_rules, smart_rules)
        record = {
            "account_name": account_name,
            "group": group,
            "amount": amount,
            "mapped_by": mapped_by,
            "source_file": source_file
        }
        structured_data.append(record)
    return structured_data

def analyze_and_save_results(structured_data, output_file):
    """Analyzes and saves the extracted data to a JSON file."""
    total_records = len(structured_data)
    mapped_records = [r for r in structured_data if r['mapped_by'] != 'Unmapped']
    unmapped_records = [r for r in structured_data if r['mapped_by'] == 'Unmapped']
    success_rate = (len(mapped_records) / total_records * 100) if total_records > 0 else 0
    total_amount = sum(abs(r['amount']) for r in mapped_records)
    mapping_methods = {}
    for record in mapped_records:
        method = record['mapped_by']
        mapping_methods[method] = mapping_methods.get(method, 0) + 1
    account_groups = {}
    for record in mapped_records:
        group = record['group']
        if group not in account_groups:
            account_groups[group] = {'count': 0, 'total_amount': 0}
        account_groups[group]['count'] += 1
        account_groups[group]['total_amount'] += abs(record['amount'])
    os.makedirs('output1', exist_ok=True)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving results to JSON: {e}")
    return structured_data

def find_file(filename):
    """Finds a file with a given name in the current directory and the input directory."""
    possible_paths = [
        filename,
        f"input/{filename}",
        f"./{filename}",
    ]
    for path in possible_paths:
        if Path(path).exists():
            return path
    filename_lower = filename.lower()
    all_files = glob.glob("*.xlsx") + glob.glob("input/*.xlsx")
    for file_path in all_files:
        file_name_lower = Path(file_path).name.lower()
        if filename_lower in file_name_lower:
            return file_path
    return None