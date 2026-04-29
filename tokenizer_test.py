from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")

print(tokenizer.tokenize("entailed"))
print(tokenizer.tokenize("not entailed"))

print(tokenizer("entailed").input_ids)
print(tokenizer("not entailed").input_ids)