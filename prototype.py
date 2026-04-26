from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
from grammars import ASP_GRAMMAR
from outlines.types import CFG
import outlines
import clingo
import re
import argparse

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

login()

# ========================================== Load model ==========================================
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
"""

Rules:
- Basic rules are of the form: head :- body.
- Basic facts are of the form: head.
- Use lowercase predicates
- Use X for variables
- Use 'not' for negation
- End each rule with a period

Examples:
"""
def build_prompt(context):
    return f"""
Translate the following statements into an Answer Set Programming (ASP) program.

Rules:
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

Input: Olivia is fast. Olivia is strong. Lucas is fast. Lucas is not strong. Fast, strong things are powerful.
Output: fast(olivia). strong(olivia). fast(lucas). not strong(lucas). powerful(X) :- fast(X), strong(X).

Input: James is tall. James is quiet. Sophia is tall. Sophia is not quiet. Tall things are visible.
Output: tall(james). quiet(james). tall(sophia). not quiet(sophia). visible(X) :- tall(X).

Input: Henry is kind. Henry is young. Lucy is kind. Lucy is not young. Kind, young things are not rude.
Output: kind(henry). young(henry). kind(lucy). not young(lucy). not rude(X) :- kind(X), young(X).

Input: Jack is smart. Jack is tall. Jack is strong. Ella is smart. Ella is tall. Ella is not strong. Smart, tall, strong things are leaders.
Output: smart(jack). tall(jack). strong(jack). smart(ella). tall(ella). not strong(ella). leader(X) :- smart(X), tall(X), strong(X).

Input: Ava is kind. Ava is young. Ben is tall. Ben is strong. Kind things are friendly. Tall, strong things are powerful.
Output: kind(ava). young(ava). tall(ben). strong(ben). friendly(X) :- kind(X). powerful(X) :- tall(X), strong(X).

Input: Leo is smart. Leo is quiet. Mila is quiet. Mila is not smart. Quiet things are thoughtful. Smart, quiet things are focused.
Output: smart(leo). quiet(leo). quiet(mila). not smart(mila). thoughtful(X) :- quiet(X). focused(X) :- smart(X), quiet(X).

Input: {context}
Output:
"""

# ========================================== NL → ASP ==========================================
def nl_to_asp(context):
    prompt = build_prompt(context)
    print("Prompt: ", prompt)
    output = model(
        prompt,
        CFG(ASP_GRAMMAR),
        # max_new_tokens=150,
    )
    print("Output:", output)
    return output.strip()

# ========================================== Clean ASP output ==========================================
def clean_asp(program):
    lines = program.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()

        # keep only ASP-like lines
        if ":-" in line or line.endswith("."):
            line = re.sub(r"[^a-zA-Z0-9_().,:\\- ]", "", line)
            cleaned.append(line)

    return "\n".join(cleaned)

# ========================================== Parse question → query atom ==========================================
def question_to_query(question):
    question = question.lower()

    # very simple heuristics
    if "does" in question or "is" in question:
        words = re.findall(r"[a-z]+", question)

        if len(words) >= 3:
            subj = words[1]
            pred = words[-1]

            return f"{pred}({subj})"

    return None

# ========================================== Run Clingo ==========================================
def run_clingo(program, query):
    ctl = clingo.Control()

    full_program = program + f"\n#show {query}/1."

    ctl.add("base", [], full_program)
    ctl.ground([("base", [])])

    result_atoms = []

    with ctl.solve(yield_=True) as handle:
        for model in handle:
            result_atoms.extend([str(atom) for atom in model.symbols(shown=True)])

    return result_atoms

# ========================================== Run evaluation ==========================================
def evaluate(n_examples=5):
    correct = 0

    for i, example in enumerate(ds.select(range(n_examples))):
        context = example["context"]
        question = example["question"]
        label = example["label"]  # True / False

        print("\n============================")
        print(f"Example {i+1}")
        print("Context:", context)
        print("Question:", question)

        asp_raw = nl_to_asp(context)
        print("Raw asp: ", asp_raw)
        try:
            asp_program = clean_asp(asp_raw)
        except:
            asp_program = "error"

        print("\nGenerated ASP:")
        print(asp_program)

        query = question_to_query(question)
        print("\nQuery:", query)

        if not query:
            print("⚠️ Could not parse query")
            continue

        try:
            atoms = run_clingo(asp_program, query)
            print("\nAnswer Set:", atoms)

            prediction = query in atoms

            print("Prediction:", prediction)
            print("Gold:", label)

            if prediction == label:
                correct += 1

        except Exception as e:
            print("❌ Clingo error:", e)

    print("\n============================")
    print(f"Accuracy: {correct}/{n_examples} = {correct/n_examples:.2f}")

# ========================================== Run ==========================================
if __name__ == "__main__":
    evaluate(5)