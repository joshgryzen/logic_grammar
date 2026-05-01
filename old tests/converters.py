def cnl_to_asp(cnl):
    if " is true if " in cnl:
        head, body = cnl.split(" is true if ")
        body = body.replace(" and ", ", ")
        return f"{head} :- {body}."
    else:
        return cnl.replace(" is true", ".")

def ace_to_fol(ace):
    if " if " in ace:
        head, body = ace.split(" if ")
        return f"{head} <- {body}"
    
    if "every" in ace:
        parts = ace.split()
        var = parts[1]
        return f"forall {var} (...)"
    
    return ace