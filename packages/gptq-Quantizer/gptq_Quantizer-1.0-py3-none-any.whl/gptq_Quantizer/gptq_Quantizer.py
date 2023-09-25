from optimum.gptq import GPTQQuantizer
from transformers import AutoTokenizer , AutoModelForCausalLM
import torch



class Quantizer:
    def __init__(self , model_name:str) -> None:
        self.model_name = model_name
    
    def run(self , bits:int,block_name_to_quantize:str,model_seqlen :int,save_folder:str , dataset="c4") : 
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForCausalLM.from_pretrained(self.model_name, 
                                                     torch_dtype=torch.float16)
        quantizer = GPTQQuantizer(bits=bits, dataset=dataset,
                                  block_name_to_quantize=block_name_to_quantize,
                                  model_seqlen = model_seqlen)
        quantizer.quantize_model(model, 
                                tokenizer)
        quantizer.save(model,save_folder)
        print(f"{self.model_name.split('/')[1]} has been quantized successfully and saved here {save_folder}")
