from transformers import AutoTokenizer, pipeline

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-8B-Instruct")

print(tokenizer.tokenize("entailed"))
print(tokenizer.tokenize("not entailed"))
print(tokenizer.tokenize("\n"))

print(tokenizer("entailed").input_ids)
print(tokenizer("not entailed").input_ids)
print(tokenizer("\n").input_ids)

pipe = pipeline("text-generation", model="meta-llama/Llama-3.2-8B-Instruct")

print(pipe.tokenizer("entailed"))
print(pipe.tokenizer("not entailed"))
print(pipe.tokenizer("\n"))