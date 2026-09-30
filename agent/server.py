"""표준 라이브러리만 쓰는 JSON API. 사용: python -m agent.server  (POST /ask, POST /feedback)"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from . import feedback
from .router import Agent

AGENT = None


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        global AGENT
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
            if self.path == "/ask":
                q = data.get("question", "").strip()
                if not q:
                    return self._send(400, {"error": "question 필요"})
                AGENT = AGENT or Agent()
                return self._send(200, AGENT.ask(q))
            if self.path == "/feedback":
                row = feedback.save_feedback(data["question"], data.get("answer", ""),
                                             data["rating"], data.get("correction", ""),
                                             path=feedback.DEFAULT_PATH)
                return self._send(200, row)
            self._send(404, {"error": "not found"})
        except (ValueError, KeyError) as e:
            self._send(400, {"error": str(e)})

    def log_message(self, *args):
        pass


def make_server(port=8000):
    return HTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    print("http://127.0.0.1:8000  POST /ask {\"question\": \"...\"}")
    make_server().serve_forever()
