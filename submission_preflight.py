from pathlib import Path
import struct
import subprocess

import cv2


ROOT = Path(__file__).parent
required = [
    "server.py", "index.html", "styles.css", "app.js", "README.md", "SUBMISSION_PACK.md", "DEVPOST_OPERATOR_CARD.md",
    "demo/gatemap_start.png", "demo/gatemap_result.png", "demo/gatemap_receipt.png", "demo/gatemap_demo_2026-09-06.webm",
]
missing = [name for name in required if not (ROOT / name).is_file()]
if missing:
    raise SystemExit(f"missing: {', '.join(missing)}")
subprocess.run(["python", "-m", "py_compile", str(ROOT / "server.py")], check=True)
subprocess.run(["node", "--check", str(ROOT / "app.js")], check=True)
for name in required:
    path = ROOT / name
    if path.suffix in {".md", ".html", ".css", ".js", ".py"} and not path.read_text(encoding="utf-8").strip():
        raise SystemExit(f"empty file: {name}")
for name in ["demo/gatemap_start.png", "demo/gatemap_result.png", "demo/gatemap_receipt.png"]:
    data = (ROOT / name).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit(f"invalid PNG: {name}")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1440, 900):
        raise SystemExit(f"{name} is {width}x{height}; expected 1440x900")
capture = cv2.VideoCapture(str(ROOT / "demo/gatemap_demo_2026-09-06.webm"))
fps = capture.get(cv2.CAP_PROP_FPS)
frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
opened = capture.isOpened()
capture.release()
if not opened or not fps or not frames:
    raise SystemExit("GateMap demo video metadata unavailable")
duration = frames / fps
if duration > 180:
    raise SystemExit(f"demo video is {duration:.2f}s; expected at most 180s")
server = (ROOT / "server.py").read_text(encoding="utf-8")
app = (ROOT / "app.js").read_text(encoding="utf-8")
for marker in ["ollama-local", "externalData", "notUploaded", "format"]:
    if marker.lower() not in (server + app).lower():
        raise SystemExit(f"missing local-AI marker: {marker}")
if "http://127.0.0.1:11434" not in server:
    raise SystemExit("Ollama endpoint is not local")
print(f"GateMap submission preflight: OK ({duration:.2f}s video)")
