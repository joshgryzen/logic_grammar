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

### Rules:
- Answer with ONLY: "entailed" or "not entailed". 
- Do not include explanations. 
- Do not generate any code. 
- Do not generate anything other than "entailed" or "not entailed".

### Examples:

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

### Now answer:

Context: {context}
Query: {question}
Answer: 
"""

# ========================================== LLM inference ==========================================
def predict_entailment(context, question):
    prompt = build_baseline_prompt(context, question)
    print("Prompt: ", prompt)
    newline_token_id = pipe.tokenizer("\n", add_special_tokens=False)["input_ids"][0]

    output = pipe(
        prompt,
        max_new_tokens=3,
        # do_sample=False,
        # temperature=0.0,
        # eos_token_id=newline_token_id,
        return_full_text=False
    )
    print("Output: ", output)
    text = output[0]["generated_text"].strip().lower()
    cleaned_text = re.sub(r'[^a-zA-Z]', '', text)
    print("Text: ", text)
    print("Cleaned Text: ", cleaned_text)

    return cleaned_text

# ========================================== Evaluation ==========================================
def evaluate(n_examples=100):
    results = []
    num_correct = 0

    for i, example in enumerate(ds.select(range(n_examples))):
        context = example["context"]
        question = example["question"]
        label = example["label"]  # dataset label

        print("\n============================")
        print(f"Example {i+1}")
        print("Context:", context)
        print("Question:", question)

        pred = predict_entailment(context, question)

        print("Prediction:", pred)
        print("Label:", label)

        if pred == label: num_correct += 1

        results.append({
            "context": context,
            "question": question,
            "prediction": pred,
            "label": label
        })
    accuracy = num_correct/n_examples
    results.append({
            "accuracy": accuracy
        })
    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)

    print(f"\nSaved results to: {output_file}")

# ========================================== Run ==========================================
if __name__ == "__main__":
    evaluate(1)