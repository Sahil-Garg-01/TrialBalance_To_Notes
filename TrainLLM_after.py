import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from peft import PeftModel

# Load your fine-tuned model and tokenizer
model_id = "deepseek-ai/deepseek-coder-1.3b-instruct"
lora_model_path = "deepseek_tb_lora"  # Path to your saved LoRA adapter

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
base_model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", trust_remote_code=True)
model = PeftModel.from_pretrained(base_model, lora_model_path)

# Create inference pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto")

# Example inference
account_name = "Machinery"
prompt = f"Classify the account name '{account_name}' under Schedule III group.\nAnswer:"

output = pipe(
    prompt,
    max_new_tokens=20,
    temperature=0.0,
    do_sample=False,
    pad_token_id=tokenizer.eos_token_id,
)[0]["generated_text"]

print("🔍 Prompt:", prompt)
print("🧠 Prediction:", output.replace(prompt, "").strip())