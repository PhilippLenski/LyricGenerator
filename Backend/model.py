from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 📌 Modell und Tokenizer laden
MODEL_PATH = "/app/models/google/gemma-3-4b-it"

# **Modell und Tokenizer von Hugging Face laden**
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map="auto", torch_dtype=torch.float16)

def generate_poem(city: str) -> str:
    """Generiert ein humorvolles Gedicht über eine Stadt mit Gemma 3 4B IT."""
    prompt = f"""
    Schreibe ein humorvolles Gedicht über {city}, das sich auf die lokalen Ess- und Trinkgewohnheiten bezieht.
    Das Gedicht muss genau eine Strophe mit vier Zeilen enthalten.
    Verwende das Kreuzreim-Schema (abab).
    Die Sätze dürfen nicht auf das gleiche Wort enden und müssen sich sinnvoll reimen.

    Beispiel:
    **Hamburg**
    Frischer Fisch vom Hafensteg,
    ein Astra kühlt die Seele fein.
    Labskaus liegt mir oft im Magen,
    doch 'nen Franzbrötchen darf es sein.

    Jetzt schreibe ein Gedicht über {city}:
    """

    # **Tokenisierung**
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")

    # **Generierung**
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_length=100,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            repetition_penalty=1.2
        )

    # **Ergebnis dekodieren**
    poem = tokenizer.decode(output[0], skip_special_tokens=True)

    # **Nur den relevanten Teil zurückgeben**
    return poem.split("Jetzt schreibe ein Gedicht über")[-1].strip()