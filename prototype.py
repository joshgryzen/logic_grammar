from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
from grammars import ASP_GRAMMAR
from outlines.types import CFG
import outlines
import clingo
import re

login()

# ========================================== Load model ==========================================
model = outlines.from_transformers(
    AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-3.2-3B-Instruct",
        device_map="auto"
    ),
    AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
)

# ========================================== Load RuleTaker ==========================================
ds = load_dataset("tasksource/ruletaker", split="train")

# ========================================== Prompt for ASP generation ==========================================
def build_prompt(context):
    return f"""
Translate the following statements into an Answer Set Programming (ASP) program.

Rules:
- Use format: head :- body.
- Use lowercase predicates
- Use X for variables
- Use 'not' for negation in the body of a rule
- Use '-' for negation in the head of a rule
- End each rule with a period

Examples:
Input: Anne is quiet.
Output: quiet(anne).

Input: Anne is not young.
Output: - young(anne).

Input: Kind, young things are not smart.
Output: - smart(X) :- kind(X), young(X).

Input: Anne is quiet. Anne is not young. Bob is kind. Bob is young. Dave is rough. Dave is round. Dave is smart. Dave is not young. Fiona is quiet. Fiona is not round. Kind, young things are not smart.
Output: quiet(anne). - young(anne). kind(bob). young(bob). rough(dave). round(dave). smart(dave). - young(dave). quiet(fiona). - round(fiona). - smart(X) :- kind(X), young(X).

Input: {context}
Output:
"""

# ========================================== NL → ASP ==========================================
def nl_to_asp(context):
    prompt = build_prompt(context)
    print(prompt)
    output = model(
        prompt,
        CFG(ASP_GRAMMAR),
        # max_new_tokens=150,
    )
    print(output)
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
        print()
        label = example["label"]  # True / False

        print("\n============================")
        print(f"Example {i+1}")
        print("Context:", context)
        print("Question:", question)

        asp_raw = nl_to_asp(context)
        asp_program = clean_asp(asp_raw)

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