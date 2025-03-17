from transformers import AutoModelForCausalLM, AutoTokenizer
from llama_cpp import Llama
import torch
import gc
from typing import NamedTuple

class ModelInfo(NamedTuple):
    name: str
    path: str

MODEL_STACK = [
    ModelInfo("Gemma3 - 7B", "models/gemma-7b.safetensors"),
    ModelInfo("Gemma3 - 7B - Q5", "/app/models/gemma3-7b-Q5/gemma-7b.Q5_K_M.gguf"),
    ModelInfo("Mistral 7B Q5", "/app/models/Mistral-7b/Mistral-7B-Instruct-v0.3.Q5_K_M.gguf"),
    ModelInfo("DeepSeekR1 7B Q5", "/app/models/DeepSeek-R1/Distill-Qwen-7B-Q5_K_M/DeepSeek-R1-Distill-Qwen-7B-Q5_K_M.gguf")
    ]

current_model = None
current_tokenizer = None
current_model_name = None

def unload_model():
    """ Entfernt das aktuelle Modell aus dem Speicher. """
    global current_model, current_tokenizer, current_model_name
    if current_model:
        print(f"Entlade {current_model_name} ...")
        del current_model
        if current_tokenizer:
            del current_tokenizer
        current_model = None
        current_tokenizer = None
        current_model_name = None

        gc.collect()
        torch.cuda.empty_cache()


def load_LlamaModel(name:str, model_path:str):
    global current_model, current_model_name

    current_model = Llama(model_path)
    current_model_name = name

def load_TransformerModel(name:str,model_path:str):
    global current_model, current_tokenizer, current_model_name

    current_model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, device_map="auto", local_files_only=True)
    current_tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    current_model_name = name

def switch_model(model_name):
    """ Wechselt zwischen Gemma3 und Mistral7B zur Laufzeit. """
    global current_model_name
    
    if model_name == current_model_name:
        print(f"{model_name} ist bereits aktiv.")
        return

    unload_model() 
    
    if model_name == MODEL_STACK[0].name:                               # Gemma3-7B Transformer
        load_TransformerModel(MODEL_STACK[0].name,MODEL_STACK[0].path) 
         
    elif model_name == MODEL_STACK[1].name:                             # Gemma3-7B-Q5 Llama-cpp-python
        load_LlamaModel(MODEL_STACK[1].name,MODEL_STACK[1].path)

    elif model_name == MODEL_STACK[2].name:                             # Mistral-7B-Q5 Llama-cpp-python
        load_LlamaModel(MODEL_STACK[2].name,MODEL_STACK[2].path)

    elif model_name == MODEL_STACK[3].name:                             # DeepSeekR1-7B-Q5 Llama-cpp-python
        load_LlamaModel(MODEL_STACK[3].name,MODEL_STACK[3].path)        
    else:
        print("Ungültiges Modell!")


def generate_poem(city):

    prompt = f"""
        Schreibe einen Kreuzreim über die Ess- und Trinkgewohnheiten der Stadt {city}.
        Der Kreuzreim soll aus 4 Sätzen bestehen.
        """
    if current_model_name == MODEL_STACK[0].name:
        inputs = current_tokenizer(prompt, return_tensors="pt").to("cuda")
        output = current_model.generate(**inputs, max_length=200)
        return current_tokenizer.decode(output[0], skip_special_tokens=True)
    
    elif current_model_name == MODEL_STACK[1].name:
        output = current_model(prompt, max_tokens=100, temperature=0.6, top_p=0.9)
        return output["choices"][0]["text"].strip()
    
    elif current_model_name == MODEL_STACK[2].name:
        output = current_model(prompt, max_tokens=100, temperature=0.6, top_p=0.9)
        return output["choices"][0]["text"].strip()
    
    elif current_model_name == MODEL_STACK[3].name:
        output = current_model(prompt, max_tokens=100, temperature=0.6, top_p=0.9)
        return output["choices"][0]["text"].strip()
    else:
        return "Kein Modell geladen!"


switch_model(MODEL_STACK[1].name)