# backend/main.py

import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# ─── 1. Device selection ──────────────────────────────────────────────────────
use_cuda = torch.cuda.is_available()
device = 0 if use_cuda else -1

# ─── 2. Load the fine-tuned DistilGPT2 model ─────────────────────────────────
MODEL_DIR = "fine_tuned_distilgpt2_windows_large"  # <-- ensure this matches your folder name

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR)

# ─── 3. Build the text-generation pipeline ──────────────────────────────────────
chat_pipeline = pipeline(
    task="text-generation",
    model=model,
    tokenizer=tokenizer,
    device=device
)

# ─── 4. Initialize FastAPI ─────────────────────────────────────────────────────
app = FastAPI()

# ─── 5. Enable CORS so the frontend can call /chat ─────────────────────────────
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, lock this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 6. Request schema ──────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str

# ─── 7. Apology text & greeting list ────────────────────────────────────────────
APOLOGY_TEXT = "Sorry, I provide technical support only for Windows 10 and later."
GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_input = request.message.strip()
    lower_input = user_input.lower()

    # 7a. If it’s a greeting or < 3 words, return apology
    if lower_input in GREETINGS or len(user_input.split()) < 3:
        return {"response": APOLOGY_TEXT}

    # 7b. If the user asks about Windows < 10, refuse
    if (
        "windows 7" in lower_input
        or "windows 8" in lower_input
        or "windows xp" in lower_input
        or "windows vista" in lower_input
    ):
        return {"response": "Sorry, I only provide technical support for Windows 10 and later."}

    # ─── 8. Otherwise, send the raw user_input to the fine-tuned model ───────────
    full_prompt = user_input

    outputs = chat_pipeline(
        full_prompt,
        max_new_tokens=150,
        num_beams=4,
        early_stopping=True,
        repetition_penalty=2.0,
        do_sample=False
    )

    answer = outputs[0]["generated_text"].strip()

    # 9. Fallback to apology if needed
    if not answer or answer.lower().startswith("sorry"):
        return {"response": APOLOGY_TEXT}

    return {"response": answer}

# ─── 10. (Optional) Serve frontend from here ───────────────────────────────────
# from fastapi.staticfiles import StaticFiles
# app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")
