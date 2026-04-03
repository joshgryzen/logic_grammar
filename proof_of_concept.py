from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import outlines
from outlines.types import CFG
from grammars import ASP_GRAMMAR, SMALL_FOL_GRAMMAR, ENTIRE_FOL_GRAMMAR
# Validate with full grammar
from lark import Lark

login()

# Hide warnings
logging.set_verbosity_error()

# tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
model = outlines.from_transformers(
    AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", device_map="auto"),
    AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
)

ASP_prompt = """Your task is to generate a valid answer set programming (ASP) rule. You should follow the closed world assumption and only encode rules that have explicit justification.


          Input: Encode the following condition into a valid answer set programming rule: we should believe a if b is not known to be true.
          Output: a :- not b.

          Input: Encode the following condition into a valid answer set programming rule: we should believe a if b is known to be true.
          Output: a :- b.

          Input: Encode the following condition into a valid answer set programming rule: we should believe a if c is not known to be true and b is known to be true.
          Output:

"""

ASP_output_type = CFG(ASP_GRAMMAR)

# Can add stop_strings=["\n", "."], tokenizer=tokenizer to just generate one rule and ending at period
ASP_output = model(
    ASP_prompt,
    ASP_output_type,
    max_new_tokens=20
)
print(f"ASP Program: {ASP_output}")

FOL_prompt = """Your task is to generate a valid first order logic sentence. You should follow the closed world assumption and only encode formulas that have explicit justification.

          Input: Encode the following condition into a valid first order logic sentence: we should believe a if b is not known to be true.
          Output: a <- not b

          Input: Encode the following condition into a valid first order logic sentence: we should believe a if b is known to be true.
          Output: a <- b

          Input: Encode the following condition into a valid first order logic sentence: we should believe a if c is not known to be true and b is known to be true.
          Output:

"""
FOL_output_type = CFG(SMALL_FOL_GRAMMAR)

# Can add stop_strings=["\n", "."], tokenizer=tokenizer to just generate one formula and ending at new line
FOL_output = model(FOL_prompt, FOL_output_type, max_new_tokens=20)

# parser = Lark(ENTIRE_FOL_GRAMMAR, start="start", parser="earley")

# try:
#     parser.parse(FOL_output)
#     print("Valid FOL under full grammar")
# except:
#     print("Invalid under full grammar")

print(f"FOL Program: {FOL_output}")