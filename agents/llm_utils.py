import os
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# === Agent-to-model configuration ===
# You can set a different model (and token/key) for each agent here.
AGENT_LLM_CONFIG = {
    'planner': {
        'model_name': os.getenv('PLANNER_MODEL', 'HuggingFaceH4/zephyr-1.3b'),
        'token': os.getenv('PLANNER_TOKEN', None),
    },
    'backend_agent': {
        'model_name': os.getenv('BACKEND_AGENT_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2'),
        'token': os.getenv('BACKEND_AGENT_TOKEN', None),
    },
    'frontend_agent': {
        'model_name': os.getenv('FRONTEND_AGENT_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2'),
        'token': os.getenv('FRONTEND_AGENT_TOKEN', None),
    },
    'database_agent': {
        'model_name': os.getenv('DATABASE_AGENT_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2'),
        'token': os.getenv('DATABASE_AGENT_TOKEN', None),
    },
    'integration_agent': {
        'model_name': os.getenv('INTEGRATION_AGENT_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2'),
        'token': os.getenv('INTEGRATION_AGENT_TOKEN', None),
    },
    'refiner_agent': {
        'model_name': os.getenv('REFINER_AGENT_MODEL', 'WizardLM/WizardCoder-1B-V1.0'),
        'token': os.getenv('REFINER_AGENT_TOKEN', None),
    },
}

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Cache for loaded pipelines per model
_llm_pipes = {}

def get_llm_pipeline(agent_name: str):
    config = AGENT_LLM_CONFIG.get(agent_name, AGENT_LLM_CONFIG['backend_agent'])
    model_name = config['model_name']
    token = config['token']
    cache_key = (model_name, token)
    if cache_key in _llm_pipes:
        return _llm_pipes[cache_key]
    # If using HuggingFace Hub with a token, pass it to from_pretrained
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=token) if token else AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if DEVICE=="cuda" else torch.float32, token=token) if token else AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if DEVICE=="cuda" else torch.float32)
    model.to(DEVICE)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0 if DEVICE=="cuda" else -1)
    _llm_pipes[cache_key] = pipe
    return pipe

def generate_code_with_llm(prompt: str, agent_name: str = 'backend_agent', max_new_tokens: int = 512, temperature: float = 0.2) -> str:
    pipe = get_llm_pipeline(agent_name)
    output = pipe(prompt, max_new_tokens=max_new_tokens, temperature=temperature, do_sample=True)
    return output[0]["generated_text"][len(prompt):].strip() 