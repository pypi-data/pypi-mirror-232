from z3 import *
from typing import Iterable,Union

T = Union[BitVecRef,BoolRef,ArithRef]

def model_count(solver: Solver,terms: Iterable[T])->int: 
    def count_rec(solver: Solver,terms: Iterable[T],
                  count: int)->int:
        """see https://theory.stanford.edu/%7Enikolaj/programmingz3.html#sec-blocking-evaluations"""
        if solver.check() == sat:
            m = solver.model()
            count += 1
            for i,term in enumerate(terms):
                solver.push()
                solver.add(term != m.eval(term,True))       
                for t in terms[:i]:
                    solver.add(t == m.eval(t,True))
                count = count_rec(solver,terms[i:],count)
                solver.pop()
        return count
    return count_rec(solver,terms,0)




def all_models(solver: Solver,terms: Iterable[T]): 
    def all_models_rec(solver: Solver,terms: Iterable[T]):
        if solver.check() == sat:
            m = solver.model()
            yield m
            for i,term in enumerate(terms):
                solver.push()
                solver.add(term != m.eval(term,True))
                for t in terms[:i]:
                    solver.add(t == m.eval(t,True))
                yield from all_models_rec(solver,terms[i:])
                solver.pop()
    yield from all_models_rec(solver,terms)
