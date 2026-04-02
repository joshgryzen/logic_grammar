from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import outlines
from outlines.types import CFG

login()

model = outlines.from_transformers(
    AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", device_map="auto"),
    AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
)

logic_grammar = """
atom: "a" | "b" | "c"
literal: "not "? atom 
body: (literal ", ")* literal "."
head: atom? " :- "
basic: head body
fact: atom
rule: fact | basic
start: rule
"""

logic_prompt = """Your task is to generate a valid answer set programming (ASP) rule.


          Input: Encode the following condition into a valid answer set programming rule: we should believe a if b is not known to be true.
          Output: a :- not b.

          Input: Encode the following condition into a valid answer set programming rule: we should believe a if b is known to be true.
          Output: a :- b.

          Input: Encode the following condition into a valid answer set programming rule: we should believe a if c is not known to be true and b is known to be true.
          Output:

"""

output_type = CFG(logic_grammar)

output = model(logic_prompt, output_type)
print(output)