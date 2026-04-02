from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import outlines
from outlines.types import CFG

login()

model = outlines.from_transformers(
    AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", device_map="auto"),
    AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct")
)


example_grammar = """
    start: definition " " entity

    definition: ("A" | "An") " " entity_name " has " attributes "."
    entity_name: "movie" | "book" |
    attributes: attribute ", " attribute | attribute
    attribute: "id" | "time duration" | "title" | "author" |

    entity: "a " name " with " entity_attributes "."
    name: entity_name " M" | entity_name " B"
    entity_attributes: attribute " " attribute_name ", with " entity_attributes | attribute " " attribute_name
    attribute_name: "MovieID" | "BookID" | "BookTitle" | "BookAuthor" |
"""

example_prompt = """Your task is to summarize natural language input into a controlled sublanguage of english.


          Input: Movies are organized by id and time duration. There is a movie with name M and id MovieID.
          Output: A movie has id, time duration. a movie M with id MovieID.

          Input: Books are organized by title and author. There is a book with name B that has the title BookTitle, and author BookAuthor.
          Output:

"""

logic_grammar = """
atom: "a" | "b" | "c"
literal: "not "? atom 
body: (literal ", ")* literal "."
head: atom? " :- "
basic: head body
fact: atom
rule: fact | basic
start: rule
"""

# output_type = CFG(example_grammar)
output_type = CFG(logic_grammar)

logic_prompt = """Your task is to generate a valid answer set programming (ASP) rule.


          Input: Encode the following condition into a valid answer set programming rule: we should believe a if b is not known to be true.
          Output: a :- not b.

          Input: Encode the following condition into a valid answer set programming rule: we should believe a if b is known to be true.
          Output: a :- b.

          Input: Encode the following condition into a valid answer set programming rule: we should believe a if c is not known to be true and b is known to be true.
          Output:

"""

grammar_output = model(logic_prompt, output_type)
# grammar_output = model(example_prompt, output_type)
print(grammar_output)