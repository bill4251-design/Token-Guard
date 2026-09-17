from __future__ import annotations
import html, json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .storage import Storage

PAGE = """<!doctype html><meta charset=utf-8><title>Token Guard</title><style>body{font:16px system-ui;margin:40px;background:#10131a;color:#eef}h1{color:#70e0a5}.cards{display:flex;gap:14px;flex-wrap:wrap}.card{background:#1b2230;padding:16px;border-radius:10px;min-width:150px}table{width:100%;border-collapse:collapse;margin-top:24px}td,th{padding:9px;border-bottom:1px solid #30394a;text-align:left}</style><h1>🛡 Token Guard</h1><div class=cards>{cards}</div><h2>Recent requests</h2><table><tr><th>Time</th><th>Provider / model</th><th>Tokens</th><th>Cost</th><th>Task</th></tr>{rows}</table>"""
def serve(storage: Storage, host="127.0.0.1", port=8787):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/api/summary":
                body=json.dumps({"summary":storage.summary(),"timeline":storage.timeline(),"violations":storage.violations()}).encode(); self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(body); return
            s=storage.summary(); labels={"requests":"Requests","tokens":"Token usage","cost":"Cost (USD)","violations":"Violations","waste_tokens":"Estimated waste"}
            cards="".join(f"<div class=card><small>{labels[k]}</small><br><b>{v:,.2f}</b></div>" if isinstance(v,float) else f"<div class=card><small>{labels[k]}</small><br><b>{v:,}</b></div>" for k,v in s.items() if k in labels)
            rows="".join(f"<tr><td>{html.escape(str(r['created_at']))}</td><td>{html.escape(r['provider']+'/'+r['model'])}</td><td>{r['total_tokens']:,}</td><td>${r['cost_usd']:.4f}</td><td>{html.escape(str(r['task_id'] or '—'))}</td></tr>" for r in storage.timeline()) or "<tr><td colspan=5>No requests recorded yet.</td></tr>"
            body=PAGE.format(cards=cards,rows=rows).encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.end_headers(); self.wfile.write(body)
        def log_message(self, *_): pass
    print(f"Token Guard dashboard: http://{host}:{port}")
    ThreadingHTTPServer((host,port), Handler).serve_forever()
