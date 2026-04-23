import clingo 

ctl = clingo.Control()

full_program = "kind(anne). young(anne). - smart(X) :- kind(X), young(X)." + f"\n#show young/1."

ctl.add("base", [], full_program)
ctl.ground([("base", [])])

result_atoms = []

with ctl.solve(yield_=True) as handle:
    for model in handle:
        result_atoms.extend([str(atom) for atom in model.symbols(shown=True)])

print(result_atoms)