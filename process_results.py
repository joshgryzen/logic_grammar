import pandas as pd
import ast
import subprocess
import tempfile
import re

# ========================= Load file =========================
input_file = "Llama-3.1-8B-Instruct_piped_strong_negation_results.xlsx"   # your file
output_file = "Llama-3.1-8B-Instruct_piped_strong_negation_results_processed_results.xlsx"

df = pd.read_excel(input_file)

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
    
    # remove newlines, extra spaces
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    
    # ensure proper spacing after periods
    text = re.sub(r"\.\s*", ". ", text)
    
    return text.strip()


# ---------------- Query → Atom ----------------
def query_to_atom(query):
    query = query.lower().strip()
    
    # remove "the"
    query = query.replace("the ", "")
    query = query.replace(".", "")
    
    tokens = query.split()
    
    # case: "bob is kind"
    if "is" in tokens:
        subj = tokens[0]
        pred = tokens[-1]
        return f"{pred}({subj})"
    
    # case: "dog sees cow"
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
        
        # extract answer sets
        answers = []
        for line in output.split("\n"):
            if line.startswith("Answer"):
                continue
            if line.strip() and not line.startswith("clingo"):
                answers.append(line.strip())
        
        if not answers:
            return "unsatisfiable"
        
        return answers
    
    except Exception:
        return "error"


# ---------------- Check correctness ----------------
def check_correctness(answer_sets, atom):
    if isinstance(answer_sets, str):
        return False
    
    for ans in answer_sets:
        if atom in ans:
            return True
    
    return False


# ========================= Main =========================

results = []

correct_count = 0
total = 0

for i, row in df.iterrows():
    raw = row["asp_raw"]
    query = row["question"]
    
    asp = extract_asp(raw)
    asp_clean = clean_asp(asp)
    
    atom = query_to_atom(query)
    
    if asp_clean is None or atom is None:
        answer_sets = "error"
        correct = False
    else:
        answer_sets = run_clingo(asp_clean)
        correct = check_correctness(answer_sets, atom)
    
    total += 1
    if correct:
        correct_count += 1
    
    results.append({
        "asp_program": asp_clean,
        "query": query,
        "atom": atom,
        "answer_sets": answer_sets,
        "correct": correct
    })

# ========================= Save =========================

out_df = pd.DataFrame(results)
out_df.to_excel(output_file, index=False)

accuracy = correct_count / total
print(f"Accuracy: {accuracy:.4f}")
print(f"Saved to {output_file}")