ASP_prompt = """Your task is to generate a valid answer set programming (ASP) rule. You should follow the closed world assumption and only encode rules that have explicit justification. Do not generate extra text. You should generate an output similar to the previous examples. 

Input: Encode the following condition into a valid answer set programming rule: we should believe a if b is not known to be true.
Output: a :- not b.

Input: Encode the following condition into a valid answer set programming rule: we should believe a if b is known to be true.
Output: a :- b.

Input: Encode the following condition into a valid answer set programming rule: we should believe a if b is known to be true and c is known to be true.
Output: a :- b, c.

Input: Encode the following condition into a valid answer set programming rule: we should believe a if b is not known to be true and c is known to be true.
Output: 

"""

FOL_prompt = """Your task is to generate a valid first order logic sentence. You should follow the closed world assumption and only encode formulas that have explicit justification. Do not generate extra text. You should generate an output similar to the previous examples. 

Input: Encode the following condition into a valid first order logic sentence: we should believe a if b is not known to be true.
Output: a <- not b

Input: Encode the following condition into a valid first order logic sentence: we should believe a if b is known to be true.
Output: a <- b

Input: Encode the following condition into a valid first order logic sentence: we should believe a if b is known to be true and c is known to be true.
Output: a <- b and c

Input: Encode the following condition into a valid first order logic sentence: we should believe a if b is not known to be true and c is known to be true.
Output: 

"""

SPEC_FOL_prompt = """Your task is to generate a valid first order logic sentence specification. You should follow the closed world assumption and only encode formulas that have explicit justification. Do not generate extra text. You should generate an output similar to the previous examples. 

Input: Encode the following condition into a valid first order logic sentence: we should believe a if b is not known to be true.
Output: spec: a <- not b.

Input: Encode the following condition into a valid first order logic sentence: we should believe a if b is known to be true.
Output: spec: a <- b.

Input: Encode the following condition into a valid first order logic sentence: we should believe a if b is known to be true and c is known to be true.
Output: spec: a <- (b and c).

Input: Encode the following condition into a valid first order logic sentence: we should believe a if b is not known to be true and c is known to be true.
Output: 

"""

CNL_prompt = """Your task is to translate natural language into controlled natural language. You should follow the closed world assumption and only encode formulas that have explicit justification. Do not generate extra text. You should generate an output similar to the previous examples.

Input: Encode the following condition into controlled natural language: we should believe a if b is not known to be true.
Output: a is true if not b

Input: Encode the following condition into controlled natural language: we should believe a if b is known to be true.
Output: a is true if b

Input: Encode the following condition into controlled natural language: we should believe a if b is known to be true and c is known to be true.
Output: a is true if b and c

Input: Encode the following condition into controlled natural language: we should believe a if b is not known to be true and c is known to be true.
Output: 
"""

ACE_prompt = """Your task is to translate natural language into controlled natural language. You should follow the closed world assumption and only encode formulas that have explicit justification. Do not generate extra text. You should generate an output similar to the previous examples.

Input: Encode the following condition into controlled natural language: we should believe a if b is not known to be true.
Output: a if not b

Input: Encode the following condition into controlled natural language: we should believe a if b is known to be true.
Output: a if b

Input: Encode the following condition into controlled natural language: we should believe a if b is known to be true and c is known to be true.
Output: a if b and c

Input: Encode the following condition into controlled natural language: we should believe a if b is not known to be true and c is known to be true.
Output: 
"""

Ruletaker_Prompt = """
### Task
Translate the following statements into an Answer Set Programming (ASP) program.

### Rules:
- Each sentence of the form "Name is property" becomes a fact: property(name).
- Each sentence of the form "Name is not property" becomes: not property(name).
- Names must be lowercase constants.
- Properties become lowercase predicates.
- General statements like "P, Q things are R" become rules: r(X) :- p(X), q(X).
- If the conclusion is negated (e.g., "are not smart"), use: not smart(X).
- Use exactly one variable X in rules.
- Separate all facts and rules with a period and a space.
- Do not include any extra text or explanations.
- Output only a valid ASP program.

### Examples:

Input: John is quiet. John is not young. Steve is kind. Steve is young. Dan is rough. Dan is round. Dan is smart. Dan is not young. Jane is quiet. Jane is not round. Kind, young things are not smart.
Output: quiet(john). not young(john). kind(steve). young(steve). rough(dan). round(dan). smart(dan). not young(dan). quiet(jane). not round(jane). not smart(X) :- kind(X), young(X).

Input: Tom is tall. Tom is not kind. Sara is kind. Sara is tall. Kind, tall things are happy.
Output: tall(tom). not kind(tom). kind(sara). tall(sara). happy(X) :- kind(X), tall(X).

Input: Liam is strong. Liam is young. Emma is strong. Emma is not young. Strong, young things are brave.
Output: strong(liam). young(liam). strong(emma). not young(emma). brave(X) :- strong(X), young(X).

Input: Noah is smart. Noah is quiet. Ava is quiet. Ava is not smart. Quiet things are calm.
Output: smart(noah). quiet(noah). quiet(ava). not smart(ava). calm(X) :- quiet(X).

Input: Mia is kind. Mia is young. Ethan is kind. Ethan is not young. Kind things are friendly.
Output: kind(mia). young(mia). kind(ethan). not young(ethan). friendly(X) :- kind(X).

### Now translate:

Input: Anne is quiet. Anne is not young. Bob is kind. Bob is young. Dave is rough. Dave is round. Dave is smart. Dave is not young. Fiona is quiet. Fiona is not round. Kind, young things are not smart.
Output:
"""