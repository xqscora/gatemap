import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).parent
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen2.5:1.5b"


def extract_object(text):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").replace("json", "", 1).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("model did not return a JSON object")
    return json.loads(cleaned[start : end + 1])


def analyze(brief, evidence):
    prompt = f"""You are GateMap, a local evidence-planning assistant for a student builder.
Read the synthetic competition brief and project evidence below. Return JSON only with exactly these keys:
problem (string), must_show (array of 3 short strings), unknowns (array of 2 short strings), next_step (string), risk (string).
Do not invent external verification. Treat missing links, dates, and claims as unknown. Keep the plan concrete and under 80 words total.

COMPETITION BRIEF:
{brief}

PROJECT EVIDENCE:
{evidence}
"""
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False, "format": "json"}).encode()
    request = Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=45) as response:
        result = json.loads(response.read().decode("utf-8"))
    parsed = extract_object(result.get("response", ""))
    required = {"problem", "must_show", "unknowns", "next_step", "risk"}
    if not required.issubset(parsed):
        raise ValueError("model response missed the GateMap schema")
    return {"model": MODEL, "provider": "ollama-local", "externalData": False, **parsed}


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        relative = self.path.split("?", 1)[0].lstrip("/") or "index.html"
        target = (ROOT / relative).resolve()
        if ROOT not in target.parents and target != ROOT:
            self.send_error(403)
            return
        if not target.is_file():
            self.send_error(404)
            return
        data = target.read_bytes()
        content_type = "text/html; charset=utf-8" if target.suffix == ".html" else "text/css; charset=utf-8" if target.suffix == ".css" else "application/javascript; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/api/analyze":
            self.send_error(404)
            return
        try:
            length = min(int(self.headers.get("Content-Length", "0")), 20000)
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            brief = str(payload.get("brief", "")).strip()
            evidence = str(payload.get("evidence", "")).strip()
            if len(brief) < 20 or len(evidence) < 20:
                raise ValueError("add a brief and evidence before running GateMap")
            self.send_json(200, analyze(brief, evidence))
        except Exception as exc:
            self.send_json(502, {"error": str(exc), "externalData": False, "notUploaded": True})

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8795), Handler).serve_forever()
