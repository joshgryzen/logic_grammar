from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login, InferenceClient
import outlines
from outlines.types import CFG
from grammars import SMALL_ASP_GRAMMAR, ASP_GRAMMAR, SMALL_FOL_GRAMMAR, ENTIRE_FOL_GRAMMAR, MINI_CNL_GRAMMAR, ENTIRE_CNL_GRAMMAR, MINI_ACE_GRAMMAR
from prompts import Ruletaker_Prompt, FOL_prompt, SPEC_FOL_prompt, ASP_prompt, CNL_prompt, ACE_prompt
from converters import cnl_to_asp, ace_to_fol

login()
pipe = pipeline("text-generation", model="meta-llama/Llama-3.2-3B-Instruct")


# ===================================== LLM TO ASP =====================================
messages = [{"role": "user", "content": Ruletaker_Prompt}]
ASP_output = pipe(messages)
print(ASP_output)

# ===================================== LLM TO FOL =====================================

# FOL_output_type = CFG(SMALL_FOL_GRAMMAR)

# # Can add stop_strings=["\n", "."], tokenizer=tokenizer to just generate one formula and ending at new line
# FOL_output = model(SPEC_FOL_prompt, FOL_output_type, max_new_tokens=20)

# print(f"FOL Program: {FOL_output}")

# ===================================== LLM TO CNL TO ASP =====================================

# CNL_output_type = CFG(ENTIRE_CNL_GRAMMAR)

# cnl_output = model(
#     CNL_prompt,
#     CNL_output_type,
#     max_new_tokens=30
# )

# print(f"CNL: {cnl_output}")
# CNL_to_asp_program = cnl_to_asp(cnl_output)
# print(f"ASP program after parsing CNL output: {CNL_to_asp_program}")

# # ===================================== LLM TO ACE TO FOL =====================================

# ACE_output_type = CFG(MINI_ACE_GRAMMAR)

# ace_output = model(
#     ACE_prompt,
#     ACE_output_type,
#     max_new_tokens=30
# )

# print(f"ACE: {ace_output}")
# ace_to_FOL_formula = ace_to_fol(ace_output)
# print(f"FOL formula after parsing ACE output: {ace_to_FOL_formula}")