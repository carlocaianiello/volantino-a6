#!/usr/bin/env python3
"""Esegue una lista di passi su `photocraft-cli serve` (stdio, radici = cartella progetto).
Uso: pc.py steps.json   |   pc.py '{"method":"session.list"}' '{"cmd":"layer.list"}'
Passo: {"method": "...", "params": {...}}  oppure  {"cmd": "<engine id>", "params": {...}} (= engine.execute).
Stampa una riga per risposta; si ferma al primo errore (a meno di "continue": true nel passo)."""
import json, subprocess, sys
import os
ROOT = os.environ.get("VOLANTINO_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def main():
    args = sys.argv[1:]
    steps = json.load(open(args[0])) if len(args) == 1 and args[0].endswith('.json') else [json.loads(a) for a in args]
    p = subprocess.Popen(["photocraft-cli", "serve", "--automation-read-root", ROOT, "--automation-write-root", ROOT],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT, text=True)
    rc = 0
    for i, st in enumerate(steps, 1):
        if "cmd" in st:
            msg = {"id": i, "method": "engine.execute", "params": {"command": st["cmd"], "params": st.get("params", {})}}
        else:
            msg = {"id": i, "method": st["method"], "params": st.get("params", {})}
        p.stdin.write(json.dumps(msg) + "\n"); p.stdin.flush()
        line = p.stdout.readline()
        if not line:
            print(json.dumps({"id": i, "ok": False, "error": "server chiuso", "stderr": p.stderr.read()[-2000:]})); rc = 3; break
        r = json.loads(line)
        if st.get("out") and isinstance(r.get("result"), dict) and r["result"].get("base64"):
            import base64; open(st["out"], "wb").write(base64.b64decode(r["result"].pop("base64"))); r["result"]["saved"] = st["out"]
        out = json.dumps(r, ensure_ascii=False)
        if len(out) > 2500: out = out[:2500] + "…"
        print(f"[{i}] {st.get('cmd') or st.get('method')}: {out}")
        if not r.get("ok", True) and not st.get("continue"):
            rc = 1; break
    try: p.stdin.close()
    except Exception: pass
    p.wait(timeout=120)
    err = p.stderr.read()
    if err.strip(): print("stderr:", err[-1500:], file=sys.stderr)
    sys.exit(rc)
if __name__ == "__main__": main()
