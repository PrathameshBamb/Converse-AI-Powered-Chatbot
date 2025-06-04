# backend/train.py

import os
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments
)

# ─── Constants ───────────────────────────────────────────────────────────────
DATA_PATH = "windows_tech_support_dataset_small.csv"    # CSV you downloaded
MODEL_NAME = "distilgpt2"                              # small, CPU/GPU‐friendly
OUTPUT_DIR = "fine_tuned_distilgpt2_windows_large"     # output folder
NUM_EPOCHS = 2                                         # 2 epochs for ~100k examples
BATCH_SIZE = 16                                        # adjust if you run out of memory

# ─── 1. Load the CSV into a Hugging Face Dataset ─────────────────────────────
dataset = load_dataset("csv", data_files=DATA_PATH)["train"]

# ─── 2. Initialize tokenizer & model (DistilGPT2) ─────────────────────────────
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# 2a. Add a dedicated PAD token and resize embeddings
tokenizer.add_special_tokens({"pad_token": "<|pad|>"})
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.resize_token_embeddings(len(tokenizer))

# 2b. Ensure pad_token_id is set properly
tokenizer.pad_token = "<|pad|>"

# ─── 3. Preprocessing: concatenate prompt + completion ─────────────────────────
def preprocess_function(examples):
    full_texts = [
        ex_prompt + "\n" + ex_completion
        for ex_prompt, ex_completion in zip(examples["prompt"], examples["completion"])
    ]
    tokenized = tokenizer(
        full_texts,
        truncation=True,
        max_length=256,
        padding="max_length"
    )
    # Labels are the same as input_ids (causal LM)
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

tokenized_dataset = dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=["prompt", "completion"]
)

# ─── 4. Data collator (for dynamic padding) ────────────────────────────────────
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False  # causal LM
)

# ─── 5. Training arguments ─────────────────────────────────────────────────────
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    overwrite_output_dir=True,
    num_train_epochs=NUM_EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    save_steps=2000,
    save_total_limit=2,
    logging_steps=500,
    logging_dir=os.path.join(OUTPUT_DIR, "logs"),
    report_to="none",  # disable WandB/Comet/etc.
    fp16=True,  
)

# ─── 6. Initialize Trainer ─────────────────────────────────────────────────────
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

# ─── 7. Start fine-tuning ──────────────────────────────────────────────────────
trainer.train()

# ─── 8. Save the final model & tokenizer ───────────────────────────────────────
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
