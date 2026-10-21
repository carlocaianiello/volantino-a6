#!/usr/bin/env python3
"""Esegue una lista di passi su `photocraft-cli serve` (server headless con radici di lettura e
scrittura sulla cartella del progetto). Serve quando i tool MCP di PhotoCraft non sono disponibili
o rifiutano di scrivere ("write authority is absent").

Uso:  python3 pc.py ricetta.json
      python3 pc.py '{"method":"doc.open","params":{"path":"lavoro/fronte.pcraft"}}' '{"cmd":"layer.list"}'
Passo: {"method": "doc.open|doc.new|doc.place|doc.save|doc.inspect|doc.render|doc.close|...", "params": {...}}
   o   {"cmd": "<id comando engine>", "params": {...}}            (= engine.execute)
   opzioni: "continue": true  -> non fermarsi se il passo fallisce (es. select.deselect senza selezione)
            "out": "file.png" -> salva il PNG restituito da doc.render
La radice è la cartella corrente (o la variabile VOLANTINO_ROOT). I percorsi nei passi sono relativi a essa."""
import base64, json, os, subprocess, sys

ROOT = os.environ.get("VOLANTINO_ROOT", os.getcwd())

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(2)
    steps = json.load(open(args[0])) if len(args) == 1 and args[0].endswith(".json") else [json.loads(a) for a in args]
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
            open(st["out"], "wb").write(base64.b64decode(r["result"].pop("base64"))); r["result"]["saved"] = st["out"]
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
