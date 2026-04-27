from datasets import load_dataset
from transformers import pipeline
from huggingface_hub import login
import argparse
import pandas as pd
import re

# ========================================== Args ==========================================
parser = argparse.ArgumentParser()
parser.add_argument(
    "-m",
    "--model",
    required=True,
    type=str,
    help="Hugging Face model id",
)
args = vars(parser.parse_args())

model_id = args["model"]
model_name = model_id.split("/")[-1]
output_file = model_name + "_baseline_results.xlsx"

login()

# ========================================== Load model ==========================================
pipe = pipeline("text-generation", model=model_id)

# ========================================== Load dataset ==========================================
ds = load_dataset("tasksource/ruletaker", split="train")

# ========================================== Prompt ==========================================
def build_baseline_prompt(context, question):
    return f"""
### Task
Determine whether the query is logically entailed by the given context.

### Instructions
- Use logical reasoning.
- Answer with ONLY one word: "entailed" or "not entailed".
- Do not include explanations.

### Examples

Context: John is quiet. John is not young. Steve is kind. Steve is young. Dan is rough. Dan is round. Dan is smart. Dan is not young. Jane is quiet. Jane is not round. Kind, young things are not smart.
Query: Steven is smart.
Answer: not entailed

Context: John is quiet. John is not young. Steve is kind. Steve is young. Dan is rough. Dan is round. Dan is smart. Dan is not young. Jane is quiet. Jane is not round. Kind, young things are not smart.
Query: Steven is not smart.
Answer: entailed

Context: Tom is tall. Tom is not kind. Sara is kind. Sara is tall. Kind, tall things are happy.
Query: Sara is happy.
Answer: entailed

Context: Tom is tall. Tom is not kind. Sara is kind. Sara is tall. Kind, tall things are happy.
Query: Tom is happy.
Answer: not entailed

Context: Liam is strong. Liam is young. Emma is strong. Emma is not young. Strong, young things are brave.
Query: Liam is brave.
Answer: entailed

Context: Liam is strong. Liam is young. Emma is strong. Emma is not young. Strong, young things are brave.
Query: Emma is brave.
Answer: not entailed

Context: Noah is smart. Noah is quiet. Ava is quiet. Ava is not smart. Quiet things are calm.
Query: Noah is calm.
Answer: entailed

Context: Noah is smart. Noah is quiet. Ava is quiet. Ava is not smart. Quiet things are calm.
Query: Ava is calm.
Answer: entailed

Context: John visits Sam. Anna needs Sam. Sam is nice. Anna is not young. If something visits Sam then Sam needs John.
Query: Sam needs John.
Answer: entailed

Context: John visits Sam. Anna needs Sam. Sam is nice. Anna is not young. If something visits Sam then Sam needs John.
Query: Anna needs John.
Answer: not entailed

### Now solve

Context: {context}
Query: {question}
Answer:
"""

# ========================================== LLM inference ==========================================
def predict_entailment(context, question):
    prompt = build_baseline_prompt(context, question)

    output = pipe(
        prompt,
        max_new_tokens=5,
        do_sample=False,
        return_full_text=False
    )

    text = output[0]["generated_text"].strip().lower()

    # Extract clean label
    if "entailed" in text:
        return "entailed"
    elif "not" in text:
        return "not entailed"
    else:
        return "unknown"

# ========================================== Evaluation ==========================================
def evaluate(n_examples=100):
    results = []

    for i, example in enumerate(ds.select(range(n_examples))):
        context = example["context"]
        question = example["question"]
        label = example.get("answer", "unknown")  # dataset label

        print("\n============================")
        print(f"Example {i+1}")
        print("Context:", context)
        print("Question:", question)

        pred = predict_entailment(context, question)

        print("Prediction:", pred)
        print("Gold:", label)

        results.append({
            "context": context,
            "question": question,
            "prediction": pred,
            "gold": label
        })

    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)

    print(f"\nSaved results to: {output_file}")

# ========================================== Run ==========================================
if __name__ == "__main__":
    evaluate(1000)