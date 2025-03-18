from transformers import AutoModelForCausalLM, AutoTokenizer
from llama_cpp import Llama
import openai
import torch
import gc
from typing import NamedTuple
import re
import torch

current_model = None
current_tokenizer = None
current_model_name = None
GPU_Supported = False

class ModelInfo(NamedTuple):
    name: str
    path: str

MODEL_STACK = [
    ModelInfo("OpenAI API","OpenAI API"),
    ModelInfo("Gemma 3 12B API" , "Gemma 3 12B API"),
    ModelInfo("DeepSeek-R1 API" , "DeepSeek-R1 API"),
    ModelInfo("Mistral 7B Q5", "/app/models/Mistral-7b/Mistral-7B-Instruct-v0.3.Q5_K_M.gguf"),
    ModelInfo("DeepSeek-R1 Distill-Qwen-14b" , "/app/models/DeepSeek-R1/Distill-Qen-14B"),
    ModelInfo("Wiedervereinigung-7b-dpo-laser", "")

    ]


print("CUDA verfügbar:", torch.cuda.is_available())
print("Anzahl GPUs:", torch.cuda.device_count())
if torch.cuda.is_available():
    print("GPU Name:", torch.cuda.get_device_name(0))
    GPU_Supported = True

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


def load_LlamaModel(name:str, model_path:str, custCTX = 512 ):
    global current_model, current_model_name

    current_model = Llama(
        model_path, 
        n_gpu_layers=-1,
        chat_format=None,
        verbose=True
    )

    current_model_name = name

def load_TransformerModel(name:str,model_path:str):
    global current_model, current_tokenizer, current_model_name

    if GPU_Supported:
        current_model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, device_map="cuda:0", local_files_only=True)
    else:
        current_model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, device_map="cpu", local_files_only=True)
    
    current_tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    current_model_name = name

def switch_model(model_name):
    global current_model_name
    
    if model_name == current_model_name:
        print(f"{model_name} ist bereits aktiv.")
        return

    unload_model() 
    # Open AI API Call
    if model_name == MODEL_STACK[0].name:                             
         current_model_name = MODEL_STACK[0].name  

    # Gemma 3
    elif model_name == MODEL_STACK[1].name:                             
         current_model_name = MODEL_STACK[1].name  

    # DeepSeek-R1 API Call
    elif model_name == MODEL_STACK[2].name:                             
         current_model_name = MODEL_STACK[2].name 

    # Mistral-7B-Q5 Llama-cpp-python
    elif model_name == MODEL_STACK[3].name:                             
        load_LlamaModel(MODEL_STACK[3].name,MODEL_STACK[3].path)
    
    # DeepSeek-R1 14b
    elif model_name == MODEL_STACK[4].name:
        load_TransformerModel(MODEL_STACK[4].name,MODEL_STACK[4].path)

    #Wiedervereinigung 7b
    elif model_name == MODEL_STACK[4].name:
        load_TransformerModel(MODEL_STACK[4].name,MODEL_STACK[4].path)

    else:
        print("Ungültiges Modell!")


def generate_poem(city):

    prompt = f"""
        Schreibe einen kreativen Kreuzreim (a b a b) über die Ess- und Trinkgewohnheiten in {city}.
        Der Reim soll exakt 1 Strophe lang sein und aus 4 Zeilen bestehen.
        Antworte auf Deutsch.
        """

    # OpenAI API Call - requires API_Key, costs money :(
    if current_model_name == MODEL_STACK[0].name:
        client = openai.OpenAI(api_key="API_Key")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    # OpenRouter -> Gemma3 12b
    elif current_model_name == MODEL_STACK[1].name:
        openRouterClient = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="API_KEY",
            )
        completion = openRouterClient.chat.completions.create(
            model="google/gemma-3-12b-it:free",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{prompt}"
                    }]
             }]
        )
        return(completion.choices[0].message.content)
    
    #OpenRouter ->  DeepSeek-R1
    elif current_model_name == MODEL_STACK[2].name:
        openRouterClient = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="API_KEY",
            )
        
        completion = openRouterClient.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}"
                }
            ] 
         )
        return(completion.choices[0].message.content)

     # Mistral-7B-Q5 Llama-cpp-python "<s>[INST] Dein Prompt hier [/INST]</s>"
    elif current_model_name == MODEL_STACK[3].name:                                
        output = current_model(
            prompt, 
            max_tokens=100, 
            temperature=0.6, 
            top_p=0.9,
            )
        return output["choices"][0]["text"].strip()
    
    # DeepSeek-R1 14b Qwen
    elif current_model_name == MODEL_STACK[4].name:                                
        prompt_format = f"""
            <|im_start|>system
            Du bist ein kreativer KI-Poet. Schreibe **ausschließlich** ein Gedicht im ABAB-Reimschema.
            <|im_end|>
            <|im_start|>user
            {prompt}
            <|im_end|>
            <|im_start|>assistant
            """

        inputs = current_tokenizer(prompt_format, return_tensors="pt").to("cuda")
        output = current_model.generate(**inputs, max_length=200)
        return current_tokenizer.decode(output[0], skip_special_tokens=True)
    
    elif current_model_name == MODEL_STACK[5].name:   
        prompt_format = [{"role": "user", "content": f"{prompt}"}]                             
     

        inputs = current_tokenizer(prompt_format, return_tensors="pt").to("cuda")
        output = current_model.generate(**inputs, max_length=200)
        return current_tokenizer.decode(output[0], skip_special_tokens=True)
    else:
        return "Kein Modell geladen!"


switch_model(MODEL_STACK[0].name)
