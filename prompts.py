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