
from morphonic_lambda import ast as A, eval as E
def test_beta():
    e = A.App(A.Lam("x", A.Var("x")), A.Const("nat", 7))
    v, steps = E.eval_normal(e)
    assert isinstance(v, A.Const) and v.value == 7

def test_delta_succ():
    e = A.App(A.Const("succ", None), A.Const("nat", 2))
    v, steps = E.eval_normal(e)
    assert isinstance(v, A.Const) and v.value == 3

def test_pair_proj():
    e = A.Fst(A.Pair(A.Const("nat", 1), A.Const("nat", 2)))
    v, steps = E.eval_normal(e)
    assert isinstance(v, A.Const) and v.value == 1

def test_mu_unrolls():
    # μx.x -> diverges by unrolling until fuel ends; we test single step occurs.
    v, steps = E.eval_normal(A.Mu("x", A.Var("x")), fuel=1)
    assert steps == 1
