import pandas as pd
import ast
import subprocess
import tempfile
import re

# ========================= Load =========================
input_file = "Llama-3.1-8B-Instruct_piped_strong_negation_results_processed_results.xlsx"
output_file = "Llama-3.1-8B-Instruct_piped_strong_negation_results_cleaned_results.xlsx"

df = pd.read_excel(input_file)

# ========================= Rule Cleaning =========================

def split_rules(program):
    if program is None:
        return []
    return [r.strip() for r in program.split(".") if r.strip()]


def is_valid_rule(rule):
    # must not contain illegal arrow
    if "->" in rule:
        return False
    
    # basic structure sanity
    if len(rule) == 0:
        return False
    
    # avoid weird tokens
    if any(x in rule for x in ["```", "Output:", "Input:"]):
        return False
    
    return True


def clean_program(program):
    if program is None:
        return None
    
    rules = split_rules(program)
    
    valid_rules = []
    removed_rules = []
    
    for r in rules:
        if is_valid_rule(r):
            valid_rules.append(r)
        else:
            removed_rules.append(r)
    
    # rebuild program
    cleaned = ". ".join(valid_rules)
    if cleaned:
        cleaned += "."
    
    return cleaned, removed_rules


# ========================= Clingo =========================

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
        capture = False
        
        for line in output.split("\n"):
            if line.startswith("Answer"):
                capture = True
                continue
            if capture and line.strip():
                answers.append(line.strip())
                capture = False
        
        if not answers:
            return "unsatisfiable"
        
        return answers
    
    except Exception:
        return "error"


# ========================= Correctness =========================

def check_correctness(answer_sets, atom):
    if isinstance(answer_sets, str):
        return False
    
    for ans in answer_sets:
        if atom and isinstance(atom, str) and atom in ans:
            return True
    
    return False


# ========================= Main =========================

results = []

orig_correct = 0
new_correct = 0
total = 0

for i, row in df.iterrows():
    print(row)
    program = row["asp_program"]
    atom = row["atom"]
    
    # original correctness (already computed)
    if row["correct"] == True:
        orig_correct += 1
    
    # clean program
    cleaned_program, removed_rules = clean_program(program)
    
    # run clingo again
    if cleaned_program is None or atom is None:
        new_answer = "error"
        new_is_correct = False
    else:
        new_answer = run_clingo(cleaned_program)
        new_is_correct = check_correctness(new_answer, atom)
    
    if new_is_correct:
        new_correct += 1
    
    total += 1
    
    results.append({
        "original_program": program,
        "cleaned_program": cleaned_program,
        "removed_rules": "; ".join(removed_rules),
        "atom": atom,
        "original_correct": row["correct"],
        "new_answer_sets": new_answer,
        "new_correct": new_is_correct
    })


# ========================= Save =========================

out_df = pd.DataFrame(results)
out_df.to_excel(output_file, index=False)

print(f"Original Accuracy: {orig_correct / total:.4f}")
print(f"New Accuracy: {new_correct / total:.4f}")
print(f"Saved to {output_file}")