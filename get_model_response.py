from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
from grammars import ASP_GRAMMAR
from outlines.types import CFG
import outlines
import clingo
import re
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument(
    "-m",
    "--model",
    required=True,
    type=str,
    help="Link to Hugging Face Model, i.e.: bigscience/bloom-560m",
)

args = vars(parser.parse_args())

model_id = args["model"]
model_name = pred = args["model"][args["model"].rfind("/") + 1 :].strip()
output_file = model_name + "_results.xlsx"

login()

# ========================================== Load model ==========================================
ASP_output_type = CFG(ASP_GRAMMAR)

model = outlines.from_transformers(
    AutoModelForCausalLM.from_pretrained(
        # "meta-llama/Llama-3.2-3B-Instruct",
        model_id,
        device_map="auto"
    ),
    AutoTokenizer.from_pretrained(model_id)
)

# ========================================== Load RuleTaker ==========================================
ds = load_dataset("tasksource/ruletaker", split="train")

# ========================================== Prompt for ASP generation ==========================================
def build_prompt(context):
    return f"""
### Task
Translate the following statements into an Answer Set Programming (ASP) program.

### Rules:
- Each sentence of the form "Name is property" becomes a fact: property(name).
- Each sentence of the form "Name is not property" becomes: not property(name).
- Names must be lowercase constants.
- Properties become lowercase predicates.
- General statements like "P, Q things are R" become rules: r(X) :- p(X), q(X).
- If the conclusion is negated (e.g., "are not smart"), use: not smart(X).
- Use exactly one variable X in rules.
- Separate all facts and rules with a period and a space.
- Do not include any extra text or explanations.
- Output only a valid ASP program.

### Examples:

Input: John is quiet. John is not young. Steve is kind. Steve is young. Dan is rough. Dan is round. Dan is smart. Dan is not young. Jane is quiet. Jane is not round. Kind, young things are not smart.
Output: quiet(john). not young(john). kind(steve). young(steve). rough(dan). round(dan). smart(dan). not young(dan). quiet(jane). not round(jane). not smart(X) :- kind(X), young(X).

Input: Tom is tall. Tom is not kind. Sara is kind. Sara is tall. Kind, tall things are happy.
Output: tall(tom). not kind(tom). kind(sara). tall(sara). happy(X) :- kind(X), tall(X).

Input: Liam is strong. Liam is young. Emma is strong. Emma is not young. Strong, young things are brave.
Output: strong(liam). young(liam). strong(emma). not young(emma). brave(X) :- strong(X), young(X).

Input: Noah is smart. Noah is quiet. Ava is quiet. Ava is not smart. Quiet things are calm.
Output: smart(noah). quiet(noah). quiet(ava). not smart(ava). calm(X) :- quiet(X).

Input: Mia is kind. Mia is young. Ethan is kind. Ethan is not young. Kind things are friendly.
Output: kind(mia). young(mia). kind(ethan). not young(ethan). friendly(X) :- kind(X).

### Now translate:

Input: {context}
Output:
"""

# ========================================== NL → ASP ==========================================
def nl_to_asp(context):
    prompt = build_prompt(context)
    print("Prompt: ", prompt)
    output = model(
        prompt,
        ASP_output_type,
    )
    print("Output:", output)
    return output.strip()


# ========================================== Run evaluation ==========================================
def evaluate():
    results = []

    for i, example in enumerate(ds):
        context = example["context"]
        question = example["question"]

        print("\n============================")
        print(f"Example {i+1}")
        print("Context:", context)
        print("Question:", question)
        asp_raw = nl_to_asp(context)
        print("Raw ASP from model: ", asp_raw)
        results.append({
            "context": context,
            "question": question,
            "asp_raw": asp_raw
        })
    # save to Excel
    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)

    print(f"Saved results to: {output_file}")

# ========================================== Run ==========================================
if __name__ == "__main__":
    evaluate()