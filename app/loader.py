import os
import json
import pandas as pd
from app.utils import clean_value

def load_trial_balance():
    json_file = "output1/parsed_trial_balance.json"
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"{json_file} not found! Please run the data extraction step first.")
    with open(json_file, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)
    if isinstance(parsed_data, list):
        tb_df = pd.DataFrame(parsed_data)
    else:
        tb_df = pd.DataFrame(parsed_data.get("trial_balance", parsed_data))
    tb_df['amount'] = tb_df['amount'].apply(clean_value)
    return tb_df