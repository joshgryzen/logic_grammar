def build_asp_prompt(context):
    return f"""
### Task
Translate the following statements into an Answer Set Programming (ASP) program.

### Rules:
- Answer Set Programming (ASP) rules are of the form "Head :- Body."
- Use strong negation "-" for facts and rule heads when something is explicitly false.
- Use default negation "not" only in rule bodies to represent lack of knowledge.
- Each sentence of the form "Name is property" becomes a fact: property(name).
- Each sentence of the form "Name is not property" becomes a fact: -property(name).
- Each sentence of the form "The object is attribute" becomes: attribute(object).
- Each sentence of the form "The object is not attribute" becomes: -attribute(object).
- Each sentence of the form "Entity1 verb entity2" becomes: verb(entity1, entity2).
- Each sentence of the form "Entity1 does not verb entity2" becomes: -verb(entity1, entity2).
- Names must be lowercase constants.
- Properties become lowercase predicates.
- General statements like "P, Q things are R" become rules: r(X) :- p(X), q(X).
- General statements like "P, Q things are not R" become rules: -r(X) :- p(X), q(X).
- If the conclusion is negated (e.g., "are not smart"), use: -smart(X).
- Separate all facts and rules with a period and a space.
- Do not include any extra text or explanations.
- Output only a valid Answer Set Programming (ASP) program.

### Examples:

Input: John is quiet. John is not young. Steve is kind. Steve is young. Dan is rough. Dan is round. Dan is smart. Dan is not young. Jane is quiet. Jane is not round. Kind, young things are not smart.
Output: quiet(john). -young(john). kind(steve). young(steve). rough(dan). round(dan). smart(dan). -young(dan). quiet(jane). -round(jane). -smart(X) :- kind(X), young(X).

Input: Tom is tall. Tom is not kind. Sara is kind. Sara is tall. Kind, tall things are happy.
Output: tall(tom). -kind(tom). kind(sara). tall(sara). happy(X) :- kind(X), tall(X).

Input: Liam is strong. Liam is young. Emma is strong. Emma is not young. Strong, young things are brave.
Output: strong(liam). young(liam). strong(emma). -young(emma). brave(X) :- strong(X), young(X).

Input: Noah is smart. Noah is quiet. Ava is quiet. Ava is not smart. Quiet things are calm.
Output: smart(noah). quiet(noah). quiet(ava). -smart(ava). calm(X) :- quiet(X).

Input: John visits Sam. Anna needs Sam. Sam is nice. Anna is not young. If something visits Sam then Sam needs John.
Output: visits(john, sam). needs(anna, sam). nice(sam). -young(anna). needs(sam, john) :- visits(X, sam).

### Now translate:

Input: {context}
Output:
"""

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