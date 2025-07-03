import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# You can change this to the local path or HuggingFace repo for DeepSeek Coder 1.3B
MODEL_NAME = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-ai/deepseek-coder-1.3b-base")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

_model = None
_tokenizer = None
_pipe = None

def get_llm_pipeline():
    global _model, _tokenizer, _pipe
    if _pipe is not None:
        return _pipe
    _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    _model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16 if DEVICE=="cuda" else torch.float32)
    _model.to(DEVICE)
    _pipe = pipeline("text-generation", model=_model, tokenizer=_tokenizer, device=0 if DEVICE=="cuda" else -1)
    return _pipe

def generate_code_with_llm(prompt: str, max_new_tokens: int = 512, temperature: float = 0.2) -> str:
    pipe = get_llm_pipeline()
    output = pipe(prompt, max_new_tokens=max_new_tokens, temperature=temperature, do_sample=True)
    return output[0]["generated_text"][len(prompt):].strip() 