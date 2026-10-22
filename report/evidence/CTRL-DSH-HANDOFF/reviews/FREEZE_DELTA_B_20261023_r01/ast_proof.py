import ast, json, subprocess, textwrap
from pathlib import Path
w6=Path(r"D:\codex-worktrees\w6")
src=(w6/"verification/claim_verify.py").read_text(encoding="utf-8")
lines=src.splitlines()
print("### 原始缩进（第164-186行，repr 显示前导空白） ###")
for i in range(163,186):
    print("%4d|%s"%(i+1, repr(lines[i])[:120]))
print()
print("### AST 可达性判定 ###")
tree=ast.parse(src)
main_fn=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=="main"][0]
for_node=[n for n in ast.walk(main_fn) if isinstance(n,ast.For)][0]
print("for 循环体顶层语句（indent=8）:")
for s in for_node.body:
    print("   line %-4d %s"%(s.lineno, type(s).__name__))
print("  -> 循环体内是否含 results.append:", any(isinstance(s,ast.Expr) and isinstance(s.value,ast.Call)
        and getattr(s.value.func,'attr','')=='append' for s in for_node.body))
# 找 return 1 之后的语句
for n in ast.walk(main_fn):
    if isinstance(n,ast.If) and any(isinstance(s,ast.Return) for s in n.body):
        body=n.body
        idx=[i for i,s in enumerate(body) if isinstance(s,ast.Return)]
        for i in idx:
            after=body[i+1:]
            print("if 块 line %d 内 return 之后还有 %d 条语句: %s"%(
                n.lineno, len(after), [(type(x).__name__,x.lineno) for x in after]))
