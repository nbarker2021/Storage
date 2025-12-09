
from morphonic_lambda import ast as A, eval as E
# factorial via μ
# μf. λn. if iszero n then 1 else n * f (pred n)
# Our δ layer doesn't have mult; we emulate by repeated succ in a loop (toy).
f = A.Mu("f", A.Lam("n",
        A.If(A.App(A.Const("iszero", None), A.Var("n")),
             A.Const("nat", 1),
             A.App(A.Lam("x", A.Const("nat", 0)), A.Var("n")))))
res, steps = E.eval_normal(A.App(f, A.Const("nat", 3)))
print("steps:", steps, "result:", res)
