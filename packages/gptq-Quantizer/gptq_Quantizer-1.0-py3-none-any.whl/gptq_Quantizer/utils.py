from accelerate import init_empty_weights
from transformers import AutoModelForCausalLM
from optimum.gptq import load_quantized_model

import torch

def Load(save_folder:str ,model_name:str ) : 
  with init_empty_weights():
    empty_model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
  empty_model.tie_weights()
  quantized_model = load_quantized_model(empty_model, save_folder=save_folder, device_map="auto")
  return quantized_model
