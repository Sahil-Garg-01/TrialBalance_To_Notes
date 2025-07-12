import pandas as pd
import json
import jsonlines
import os

# 1. Ensure all dependencies are installed via requirements.txt:
# transformers, peft, accelerate, bitsandbytes, datasets, jsonlines, huggingface_hub

# 2. Place your Excel and JSON files in the same directory as this script or provide full paths.

# Step 1: Convert Excel files to instruction/output
df1 = pd.read_excel("In Lakhs  BS_FY 23-24 V5 - Final.xlsx", skiprows=4)
df2 = pd.read_excel("Trail Balance FY 24-25.xlsx", skiprows=5)

df1 = df1.rename(columns={"Unnamed: 2": "Account Name", "Unnamed: 5": "Schedule III Group"})
df1 = df1[["Account Name", "Schedule III Group"]].dropna()

df2 = df2.rename(columns={"Unnamed: 0": "Account Name"})
df2["Schedule III Group"] = "TO_LABEL"
df2 = df2[["Account Name", "Schedule III Group"]].dropna()

excel_df = pd.concat([df1, df2], ignore_index=True).drop_duplicates()

excel_jsonl = [
    {
        "instruction": f"Classify the account name '{row['Account Name']}' under Schedule III group.",
        "output": row["Schedule III Group"]
    }
    for _, row in excel_df.iterrows()
]

# Step 2: Load parsed_trial_balance.json
with open("parsed_trial_balance2.json", "r") as f:
    parsed_data = json.load(f)

parsed_jsonl = [
    {
        "instruction": f"Classify the account name '{row['account_name']}' under Schedule III group.",
        "output": row.get("group", "TO_LABEL")
    }
    for row in parsed_data if row.get("account_name")
]

# Step 3: Combine and save all to train.jsonl
combined_jsonl = excel_jsonl + parsed_jsonl
with jsonlines.open("train.jsonl", "w") as writer:
    writer.write_all(combined_jsonl)

print(f"✅ Combined and saved {len(combined_jsonl)} samples to train.jsonl")

# Step 4: Prepare HuggingFace Dataset
from datasets import Dataset

dataset = Dataset.from_json("train.jsonl")
print(dataset[0])

# Step 5: (Optional) Re-create train.jsonl from parsed_trial_balance2.json
# (Uncomment if you want to overwrite train.jsonl with only parsed_trial_balance2.json data)
# with open("parsed_trial_balance2.json", "r") as f:
#     data = json.load(f)
# jsonl_data = []
# for row in data:
#     entry = {
#         "instruction": f"Classify the account name '{row['account_name']}' under Schedule III group.",
#         "output": "TO_LABEL"
#     }
#     jsonl_data.append(entry)
# with open("train.jsonl", "w") as f:
#     for item in jsonl_data:
#         f.write(json.dumps(item) + "\n")
# print("✅ Converted to train.jsonl with", len(jsonl_data), "entries")

# Step 6: HuggingFace login (set your token as an environment variable or paste here)
from huggingface_hub import login
login(token="hf_HoTAeLXYpTcVRlhlIEWgI")  # Replace with your token

from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "deepseek-ai/deepseek-coder-1.3b-instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    load_in_8bit=True,  # optional
    device_map="auto"
)

# Step 7: Prepare dataset for training
def tokenize(example):
    prompt = f"{example['instruction']}\nAnswer: {example['output']}"
    return tokenizer(prompt, truncation=True, padding="max_length", max_length=512)

tokenized_dataset = dataset.map(tokenize)

from transformers import BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, TaskType

# Setup quantization (8-bit)
bnb_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,
    llm_int8_skip_modules=None,
)

# Load the DeepSeek model in 8-bit
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    trust_remote_code=True,
    quantization_config=bnb_config
)

# LoRA config for parameter-efficient fine-tuning
peft_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

# Apply LoRA on top of base model
model = get_peft_model(model, peft_config)

def tokenize_with_labels(example):
    prompt = f"{example['instruction']}\nAnswer: {example['output']}"
    encoded = tokenizer(prompt, truncation=True, padding="max_length", max_length=512)
    encoded["labels"] = encoded["input_ids"].copy()
    return encoded

tokenized_dataset = dataset.map(tokenize_with_labels)

import os
os.environ["WANDB_DISABLED"] = "true"

from transformers import TrainingArguments, Trainer

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

trainer.train()

# ✅ Save the trained LoRA adapter properly
model.save_pretrained("deepseek_tb_lora")

# Step 8: Inference with the trained model
from transformers import pipeline
from peft import PeftModel

base_model_id = "deepseek-ai/deepseek-coder-1.3b-instruct"
lora_model_path = "./deepseek_tb_lora"

tokenizer = AutoTokenizer.from_pretrained(base_model_id, trust_remote_code=True)
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
