from lark import Lark
from grammars import FOL_GRAMMAR

parser = Lark(FOL_GRAMMAR, start="start")

print(parser.parse("p"))
print(parser.parse("forall X p(X)"))