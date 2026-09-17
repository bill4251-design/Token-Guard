from __future__ import annotations
import argparse, json
from .config import GuardConfig, load_config, save_config
from .dashboard import serve
from .storage import Storage

def main(argv=None):
    p=argparse.ArgumentParser(prog="token-guard", description="Local-first AI token waste monitoring")
    p.add_argument("--db", default="token-guard.db", help="SQLite database path")
    sub=p.add_subparsers(dest="command", required=True)
    sub.add_parser("report"); sub.add_parser("usage")
    c=sub.add_parser("config"); c.add_argument("--strictness",type=int); c.add_argument("--action",choices=["warn","block"]); c.add_argument("--show",action="store_true")
    s=sub.add_parser("serve"); s.add_argument("--port",type=int,default=8787)
    a=p.parse_args(argv)
    if a.command in {"report","usage"}:
        data=Storage(a.db).summary()
        if a.command == "usage": data={k:data[k] for k in ("requests","tokens","cost")}
        print(json.dumps(data,indent=2)); return
    if a.command == "config":
        config=load_config()
        if a.strictness is not None: config.strictness=a.strictness
        if a.action is not None: config.action=a.action
        config.validate()
        if a.strictness is not None or a.action is not None: save_config(config)
        print(json.dumps(config.to_dict(),indent=2)); return
    serve(Storage(a.db),port=a.port)
if __name__ == "__main__": main()
