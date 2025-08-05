import pandas as pd
import json
import jsonlines
import os
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, pipeline
from peft import LoraConfig, get_peft_model, PeftModel
from transformers import BitsAndBytesConfig
from huggingface_hub import login
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Function to clean and convert numeric values
def clean_numeric(value):
    if isinstance(value, str):
        # Remove commas and convert to float
        value = value.replace(',', '')
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    return float(value) if pd.notnull(value) else 0.0

# Step 1: Read and process the Excel file
def process_trial_balance_excel(file_path, source_file_name):
    # Try different skiprows to find the correct header
    for skip in range(0, 10):
        df = pd.read_excel(file_path, skiprows=skip)
        print(f"Trying skiprows={skip} -> Columns: {df.columns.tolist()}")
        # Try to find the correct columns for account name and amount
        possible_account_cols = ["Account Name", "Unnamed: 0", "A/c Name", "A/c Code", "Advance Tax"]
        possible_amount_cols = ["Net Credit", "Amount", "Net Amount", "Net Debit", "Closing Balance", "95,56,617.16", 9487093, 69524.16, 0]
        account_col = None
        amount_col = None
        for col in possible_account_cols:
            if col in df.columns:
                account_col = col
                break
        for col in possible_amount_cols:
            if col in df.columns:
                amount_col = col
                break
        if account_col and amount_col:
            print(f"Using skiprows={skip}, account_col={account_col}, amount_col={amount_col}")
            break
    else:
        raise KeyError(f"Could not find account or amount columns. Columns found: {df.columns.tolist()}")

    # Rename columns for consistency
    df = df.rename(columns={account_col: "Account Name", amount_col: "Amount"})

    # Select relevant columns and drop rows with missing Account Name
    df = df[["Account Name", "Amount"]].dropna(subset=["Account Name"])

    # Clean account names and amounts
    df["Account Name"] = df["Account Name"].astype(str).str.strip()
    df["Amount"] = df["Amount"].apply(clean_numeric)

    # Create JSON structure
    json_data = [
        {
            "account_name": row["Account Name"],
            "group": "Unmapped" if row["Amount"] != 0 else "Unmapped",  # Placeholder for group
            "amount": row["Amount"],
            "mapped_by": "Unmapped",
            "source_file": source_file_name
        }
        for _, row in df.iterrows() if row["Account Name"] not in ["Assets", "Liabilities", "Equities", "Income", "Expense", "Total for Trial Balance"]
    ]

    return json_data

# Step 2: Generate train.jsonl for LLM fine-tuning
def create_train_jsonl(json_data, output_file="train.jsonl"):
    jsonl_data = [
        {
            "instruction": f"Classify the account name '{entry['account_name']}' under Schedule III group.",
            "output": entry["group"]
        }
        for entry in json_data
    ]

    with jsonlines.open(output_file, "w") as writer:
        writer.write_all(jsonl_data)

    print(f"✅ Saved {len(jsonl_data)} samples to {output_file}")
    return jsonl_data

# Step 3: Main processing
excel_file = "input\Book2 (2).xlsx"
source_file_name = "Book2 (2).xlsx"
json_data = process_trial_balance_excel(excel_file, source_file_name)

# Save JSON output
with open("trial_balance_processed.json", "w") as f:
    json.dump(json_data, f, indent=2)
print(f"✅ Saved JSON output to trial_balance_processed.json")

# Create train.jsonl
create_train_jsonl(json_data)

# Step 4: Prepare HuggingFace Dataset
dataset = Dataset.from_json("train.jsonl")
print(dataset[0])

# Step 5: HuggingFace login (replace with your token)
token = os.getenv("HFTOKEN")
if not token:
    raise RuntimeError("HFTOKEN not found in environment. Please check your .env file and its location.")
print("HFTOKEN loaded successfully.")
login(token=token)

# Step 6: Load model and tokenizer
model_id = "deepseek-ai/deepseek-coder-1.3b-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

# Setup quantization
bnb_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,
    llm_int8_skip_modules=None,
)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    trust_remote_code=True,
    quantization_config=bnb_config
)

# LoRA config
peft_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Apply LoRA
model = get_peft_model(model, peft_config)

# Tokenize dataset
def tokenize_with_labels(example):
    prompt = f"{example['instruction']}\nAnswer: {example['output']}"
    encoded = tokenizer(prompt, truncation=True, padding="max_length", max_length=512)
    encoded["labels"] = encoded["input_ids"].copy()
    return encoded

tokenized_dataset = dataset.map(tokenize_with_labels)

# Step 7: Training setup
os.environ["WANDB_DISABLED"] = "true"

training_args = TrainingArguments(
    output_dir="./deepseek_tb_lora",
    per_device_train_batch_size=4,
    num_train_epochs=3,
    logging_steps=10,
    save_strategy="epoch",
    learning_rate=2e-4,
    fp16=True
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset
)

# Train the model
trainer.train()

# Save the trained LoRA adapter
model.save_pretrained("deepseek_tb_lora")
print("✅ Model saved to deepseek_tb_lora")

# Step 8: Inference
base_model_id = model_id  # Use the same model_id as above
lora_model_path = "deepseek_tb_lora"  # Path to the saved LoRA adapter

base_model = AutoModelForCausalLM.from_pretrained(base_model_id, device_map="auto", trust_remote_code=True)
model = PeftModel.from_pretrained(base_model, lora_model_path)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto")

prompt = "Classify the account name 'Machinery' under Schedule III group.\nAnswer:"
output = pipe(
    prompt,
    max_new_tokens=20,
    temperature=0.0,
    do_sample=False,
    pad_token_id=tokenizer.eos_token_id,
)[0]["generated_text"]

print("🔍 Prompt:", prompt)
print("🧠 Prediction:", output.replace(prompt, "").strip())