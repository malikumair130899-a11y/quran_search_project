# rag.py
import os
from typing import List, Dict

_SYS_RULES = """You are QuranGPT. Answer ONLY from the provided verses.
- Do not invent references or content.
- Cite verses like (Surah:Ayah).
- If unsure, say you don't know from the given verses."""

def _format_context(verses: List[Dict]) -> str:
    lines = []
    for v in verses:
        ref = f"{v.get('surah','')}:{v.get('ayah_number')}"
        en = v.get('english', '')
        ur = v.get('urdu', '')
        lines.append(f"[{ref}] EN: {en}")
        if ur:
            lines.append(f"[{ref}] UR: {ur}")
        lines.append("")
    return "\n".join(lines)

def make_extractive_answer(question: str, verses: List[Dict]) -> str:
    """Deterministic, safe answer that lists verses with citations."""
    if not verses:
        return "I could not find relevant verses for your question. Please try rephrasing."
    intro = f"Here are Quranic verses related to \"{question}\":\n\n"
    bullets = []
    for v in verses:
        ref = f"{v.get('surah','')}:{v.get('ayah_number')}"
        en = v.get('english','').strip()
        bullets.append(f"- ({ref}) {en}")
    closing = "\n\nThese verses are the basis of the answer. For tafsīr or more explanation, ask me to include it."
    return intro + "\n".join(bullets) + closing

def maybe_llm_answer(question: str, verses: List[Dict]) -> str | None:
    """
    Optional: use a local LLM to produce a more ChatGPT-like answer.
    Enable by setting environment variable USE_LLM=1 and LLM_ID to a model ID.
    NOTE: running a local model requires lots of RAM and transformers installed.
    """
    if os.getenv("USE_LLM", "0") != "1":
        return None

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        import torch

        model_id = os.getenv("LLM_ID", "microsoft/Phi-3-mini-4k-instruct")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")
        gen = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() else -1)

        prompt = f"""{_SYS_RULES}

Question: {question}

Context (verses):
{_format_context(verses)}

Write a concise answer grounded ONLY in the above verses. Use citations like (Surah:Ayah).
"""
        out = gen(prompt, max_new_tokens=256, do_sample=False)[0]["generated_text"]
        # Try to return the whole generation (caller should validate)
        return out.strip()
    except Exception as e:
        # If LLM fails, fallback to extractive answer (do not crash the app)
        print("LLM failed:", e)
        return None
