import argparse
import re
import pandas as pd
from prompts import build_asp_prompt, build_baseline_prompt
from datasets import load_dataset
from transformers import pipeline
from huggingface_hub import login

# ========================================== Args ==========================================
parser = argparse.ArgumentParser()

parser.add_argument(
    "-m",
    "--model",
    required=True,
    type=str,
    help="Hugging Face model id",
)

parser.add_argument(
    "--baseline",
    action="store_true",
    help="Run baseline entailment instead of NL→ASP pipeline",
)

parser.add_argument(
    "--n_tests",
    type=int,
    default=1000,
    help="Number of examples to evaluate",
)

args = parser.parse_args()

model_id = args.model
model_name = model_id.split("/")[-1]

# Output file based on mode
if args.baseline:
    output_file = model_name + "_baseline_results.xlsx"
else:
    output_file = model_name + "_piped_strong_negation_results.xlsx"

# ========================================== Setup ==========================================
login()

pipe = pipeline("text-generation", model=model_id)
ds = load_dataset("tasksource/ruletaker", split="train")

# ========================================== BASELINE INFERENCE ==========================================
def predict_entailment(context, question):
    prompt = build_baseline_prompt(context, question)

    output = pipe(
        prompt,
        max_new_tokens=3,
        return_full_text=False
    )

    text = output[0]["generated_text"].strip().lower()
    cleaned_text = re.sub(r'[^a-zA-Z]', '', text).strip().lower()

    return cleaned_text


# ========================================== NL → ASP ==========================================
def nl_to_asp(context):
    prompt = build_asp_prompt(context)

    output = pipe(
        prompt,
        max_new_tokens=200,
        return_full_text=False
    )

    text = output[0]["generated_text"].strip()
    return text


# ========================================== Evaluation ==========================================
def evaluate(n_tests):
    results = []
    num_correct = 0

    for i, example in enumerate(ds.select(range(n_tests))):
        context = example["context"]
        question = example["question"]
        label = example["label"].strip().lower()

        if label == "entailment":
            label = "entailed"
        if label == "not entailment":
            label = "not entailed"

        print("\n============================")
        print(f"Example {i+1}")

        if args.baseline:
            pred = predict_entailment(context, question)

            print("Prediction:", pred)
            print("Label:", label)

            if pred == label:
                num_correct += 1

            results.append({
                "context": context,
                "question": question,
                "prediction": pred,
                "label": label
            })

        else:
            asp_output = nl_to_asp(context)

            print("ASP Output:", asp_output)

            results.append({
                "context": context,
                "question": question,
                "asp_output": asp_output
            })

    # Accuracy only for baseline
    if args.baseline:
        accuracy = num_correct / n_tests
        results.append({"accuracy": accuracy})
        print(f"\nAccuracy: {accuracy}")

    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)

    print(f"\nSaved results to: {output_file}")


# ========================================== Run ==========================================
if __name__ == "__main__":
    evaluate(args.n_tests)