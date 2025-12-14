# src/script.py
import os
from huggingface_hub import InferenceClient

def generate_script(idea_text: str) -> str:
    """Hugging Face Inference API ile İngilizce senaryo üretir."""
    client = InferenceClient(
        "meta-llama/Llama-3.2-1B",
        token=os.environ.get("HF_TOKEN")
    )
    
    prompt = f"""
    You are a professional YouTube scriptwriter. Write a 60-second engaging script about: {idea_text}
    Rules:
    - Start with: "Hey everyone!"
    - Include intro, main content, call-to-action
    - No markdown, no explanations, just the script
    - Keep it under 200 words
    Script:
    """
    
    response = client.text_generation(
        prompt,
        max_new_tokens=300,
        temperature=0.7,
        repetition_penalty=1.2
    )
    
    return response.strip()