SMALL_FOL_GRAMMAR = r"""
start: formula

formula: atom
       | "not" formula
       | formula "and" formula
       | formula "or" formula
       | formula "->" formula
       | formula "<-" formula
       | "forall" VAR formula
       | "exists" VAR formula
       | "(" formula ")"

atom: PRED
    | PRED "(" VAR ")"

PRED: "a" | "b" | "c"
VAR: "X" | "Y" | "Z"

%import common.WS
%ignore WS
"""

ENTIRE_FOL_GRAMMAR = r"""
// --------------------
// Imports + Ignore
// --------------------

%import common.WS_INLINE
%import common.NEWLINE
%ignore WS_INLINE
%ignore NEWLINE

COMMENT: "%" /[^\n]*/
%ignore COMMENT

// --------------------
// Character classes
// --------------------

ASCII_NONZERO_DIGIT: /[1-9]/
ASCII_DIGIT: /[0-9]/
ASCII_ALPHA_LOWER: /[a-z]/
ASCII_ALPHA_UPPER: /[A-Z]/
ASCII_ALPHANUMERIC: /[a-zA-Z0-9]/

// --------------------
// Primitives / Keywords
// --------------------

DOLLAR: "$"
infimum: "#inf"
supremum: "#sup"

primitive: infimum | supremum

// --------------------
// Sorts
// --------------------

general_sort: "g" "eneral"?
integer_sort: "i" "nteger"?
symbolic_sort: "s" "ymbol"?

sort: general_sort | integer_sort | symbolic_sort

// --------------------
// Variables / constants
// --------------------

unsorted_variable: "_" ? ASCII_ALPHA_UPPER (ASCII_ALPHANUMERIC | "_")*

symbolic_constant: "_" ? ASCII_ALPHA_LOWER (ASCII_ALPHANUMERIC | "_")*

numeral: "0" | "-"? ASCII_NONZERO_DIGIT ASCII_DIGIT*

integer_function_constant: symbolic_constant DOLLAR integer_sort

integer_variable: unsorted_variable DOLLAR integer_sort
                | unsorted_variable DOLLAR

symbolic_function_constant: symbolic_constant DOLLAR symbolic_sort

symbolic_variable: unsorted_variable DOLLAR symbolic_sort

general_variable: unsorted_variable (DOLLAR general_sort)?

general_function_constant: symbolic_constant DOLLAR general_sort

// --------------------
// Integer terms
// --------------------

negative: "-"

unary_operator: negative

add: "+"
subtract: "-"
multiply: "*"

binary_operator: add | subtract | multiply

basic_integer_term: numeral
                  | integer_function_constant
                  | integer_variable

integer_term: unary_operator* n_primary (binary_operator unary_operator* n_primary)*

n_primary: basic_integer_term
         | "(" integer_term ")"

// --------------------
// Symbolic / general terms
// --------------------

symbolic_term: symbolic_function_constant
             | symbolic_constant
             | symbolic_variable

general_term: general_function_constant
            | integer_term
            | symbolic_term
            | general_variable
            | infimum
            | supremum

function_constant: integer_function_constant
                 | symbolic_function_constant
                 | general_function_constant

variable: integer_variable
        | symbolic_variable
        | general_variable

// --------------------
// Predicate / atom
// --------------------

arity: "0" | ASCII_NONZERO_DIGIT ASCII_DIGIT*

predicate_symbol: symbolic_constant

predicate: predicate_symbol "/" arity

term_tuple: "(" [general_term ("," general_term)*] ")"

atom: predicate_symbol term_tuple?

// --------------------
// Relations
// --------------------

greater_equal: ">="
less_equal: "<="
greater: ">"
less: "<"
not_equal: "!="
equal: "="

relation: greater_equal
        | less_equal
        | greater
        | less
        | not_equal
        | equal

guard: relation general_term

comparison: general_term guard+

// --------------------
// Atomic formulas
// --------------------

truth: "#true"
falsity: "#false"

atomic_formula: truth
              | falsity
              | comparison
              | atom

// --------------------
// Quantifiers
// --------------------

forall: "forall"
exists: "exists"

quantifier: forall | exists

quantification: quantifier variable+

// --------------------
// Connectives
// --------------------

negation: "not"

unary_connective: negation

equivalence: "<->"
implication: "->"
reverse_implication: "<-"
conjunction: "and"
disjunction: "or"

binary_connective: equivalence
                 | implication
                 | reverse_implication
                 | conjunction
                 | disjunction

// --------------------
// Formula
// --------------------

prefix: quantification
      | unary_connective

infix: binary_connective

primary: "(" formula ")"
       | atomic_formula

formula: prefix* primary (infix prefix* primary)*

// --------------------
// Theory
// --------------------

theory: (formula ".")*

// --------------------
// Roles / annotations
// --------------------

assumption: "assumption"
spec: "spec"
lemma: "lemma"
definition: "definition"
inductive_lemma: "inductive-lemma"

role: assumption
    | spec
    | lemma
    | definition
    | inductive_lemma

universal: "universal"
forward: "forward"
backward: "backward"

direction: universal
         | forward
         | backward

annotated_formula: role ("(" direction ")")? ("[" symbolic_constant "]")? ":" formula

specification: (annotated_formula ".")*

// --------------------
// User guide
// --------------------

input_predicate: "input" ":" predicate

output_predicate: "output" ":" predicate

placeholder_declaration: "input" ":" symbolic_constant ("->" sort)?

user_guide_entry: input_predicate
                | output_predicate
                | placeholder_declaration
                | annotated_formula

user_guide: (user_guide_entry ".")*

// --------------------
// Entry points (EOI equivalents)
// --------------------

start_formula: formula
start_theory: theory
start_specification: specification
start_user_guide: user_guide

// Default start
start: formula
"""

ASP_GRAMMAR = r"""
// --------------------
// Terminals
// --------------------

%import common.WS_INLINE
%import common.NEWLINE
%import common.DIGIT
%import common.LETTER
%import common.INT

%ignore WS_INLINE
%ignore NEWLINE
%ignore COMMENT

COMMENT: "%" /[^\n]*/

// Character classes
ASCII_NONZERO_DIGIT: /[1-9]/
ASCII_DIGIT: /[0-9]/
ASCII_ALPHA_LOWER: /[a-z]/
ASCII_ALPHA_UPPER: /[A-Z]/
ASCII_ALPHANUMERIC: /[a-zA-Z0-9]/

// --------------------
// Precomputed terms
// --------------------

infimum: "#infimum" | "#inf"
supremum: "#supremum" | "#sup"

integer: "0" | "-"? ASCII_NONZERO_DIGIT ASCII_DIGIT*
symbol: "_" ? ASCII_ALPHA_LOWER (ASCII_ALPHANUMERIC | "_")*

precomputed_term: infimum | integer | symbol | supremum

// --------------------
// Variables
// --------------------

variable: ASCII_ALPHA_UPPER ASCII_ALPHANUMERIC*

// --------------------
// Operators
// --------------------

negative: "-"

unary_operator: negative

add: "+"
subtract: "-"
multiply: "*"
divide: "/"
modulo: "\\"
interval: ".."

binary_operator: add | subtract | multiply | divide | modulo | interval

// --------------------
// Terms
// --------------------

term: unary_operator* primary_term (binary_operator unary_operator* primary_term)*

primary_term: precomputed_term
            | variable
            | "(" term ")"

// --------------------
// Predicate
// --------------------

arity: "0" | ASCII_NONZERO_DIGIT ASCII_DIGIT*
predicate: symbol "/" arity

// --------------------
// Atom
// --------------------

atom: symbol term_tuple?

term_tuple: "(" [term ("," term)*] ")"

// --------------------
// Sign / Negation
// --------------------

negation: "not"

sign: negation? negation?

// --------------------
// Literal
// --------------------

literal: sign atom

// --------------------
// Relations
// --------------------

equal: "="
not_equal: "!="
less: "<"
less_equal: "<="
greater: ">"
greater_equal: ">="

relation: equal | not_equal | less_equal | less | greater_equal | greater

// --------------------
// Comparison
// --------------------

comparison: term relation term

atomic_formula: comparison | literal

// --------------------
// Head
// --------------------

basic_head: atom
choice_head: "{" atom "}"
falsity: "#false"?

head: basic_head | choice_head | falsity

// --------------------
// Body
// --------------------

body: [atomic_formula (("," | ";") atomic_formula)*]

// --------------------
// Rule
// --------------------

rule: head (":-" body)? "."

// --------------------
// Program
// --------------------

program: rule*

start: program
"""