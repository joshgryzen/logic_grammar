import pandas as pd
import ast
import subprocess
import tempfile
import re
from datasets import load_dataset

# ========================= Load files =========================
input_file = "Llama-3.2-3B-Instruct_piped_strong_negation_results.xlsx"
output_file = "Llama-3.2-3B-processed_results.xlsx"

df_excel = pd.read_excel(input_file)

# Load RuleTaker
ds = load_dataset("tasksource/ruletaker", split="train")

# ========================= Helpers =========================

def extract_asp(raw):
    try:
        data = ast.literal_eval(raw)
        return data[0]["generated_text"][1]["content"]
    except Exception:
        return None


def clean_asp(text):
    if text is None:
        return None
    
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\.\s*", ". ", text)
    
    return text.strip()


# ---------------- Query → Atom ----------------
def query_to_atom(query):
    query = query.lower().strip()
    query = query.replace("the ", "")
    query = query.replace(".", "")
    
    tokens = query.split()
    
    if "is" in tokens:
        subj = tokens[0]
        pred = tokens[-1]
        return f"{pred}({subj})"
    
    if len(tokens) == 3:
        subj, verb, obj = tokens
        return f"{verb}({subj}, {obj})"
    
    return None


# ---------------- Run Clingo ----------------
def run_clingo(program):
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".lp", delete=False) as f:
            f.write(program)
            fname = f.name
        
        result = subprocess.run(
            ["clingo", fname, "0"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout
        
        if "UNSATISFIABLE" in output:
            return "unsatisfiable"
        
        answers = []
        for line in output.split("\n"):
            if line.startswith("Answer"):
                continue
            if line.strip() and not line.startswith("clingo"):
                answers.append(line.strip())
        
        if not answers:
            return []
        
        return answers
    
    except Exception:
        return "error"


# ---------------- Check correctness ----------------
def check_correctness(answer_sets, atom, label):
    if isinstance(answer_sets, str):
        return False

    neg_atom = f"-{atom}"
    
    found_positive = False
    found_negative = False
    
    for ans in answer_sets:
        if "unsatisfiable" in ans:
            return False
        if atom in ans:
            found_positive = True
        if neg_atom in ans:
            found_negative = True
    
    if label == "entailment":  # entailed
        return found_positive
    else:  # not entailed
        return (not found_positive) or found_negative
# ========================= Main =========================

results = []
correct_count = 0
total = 0

excel_idx = 0

for i in range(1000):
    data_row = ds[i]
    
    context_ds = data_row["context"].strip()
    query = data_row["question"]
    label = data_row["label"]
    
    # Move Excel pointer until contexts match
    while excel_idx < len(df_excel):
        context_excel = str(df_excel.iloc[excel_idx]["context"]).strip()
        
        if context_excel == context_ds:
            break
        else:
            excel_idx += 1
    
    if excel_idx >= len(df_excel):
        print("Ran out of Excel rows.")
        break
    
    # Get ASP from matching Excel row
    raw = df_excel.iloc[excel_idx]["asp_raw"]
    
    asp = extract_asp(raw)
    asp_clean = clean_asp(asp)
    atom = query_to_atom(query)
    
    if asp_clean is None or atom is None:
        answer_sets = "error"
        correct = False
    else:
        answer_sets = run_clingo(asp_clean)
        correct = check_correctness(answer_sets, atom, label)
    
    total += 1
    if correct:
        correct_count += 1
    
    results.append({
        "context": context_ds,
        "asp_program": asp_clean,
        "query": query,
        "atom": atom,
        "label": label,
        "answer_sets": answer_sets,
        "correct": correct
    })

# ========================= Save =========================

out_df = pd.DataFrame(results)
out_df.to_excel(output_file, index=False)

accuracy = correct_count / total if total > 0 else 0
print(f"Accuracy: {accuracy:.4f}")
print(f"Saved to {output_file}")