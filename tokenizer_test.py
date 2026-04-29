from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")

print(tokenizer.tokenize("yes"))
print(tokenizer.tokenize("no"))

print(tokenizer("yes").input_ids)
print(tokenizer("no").input_ids)