# GateMap

GateMap is a local AI evidence planner for GatewayGS Hackathon 2. A builder gives it a competition brief and the evidence that actually exists. A local Ollama model returns a strict JSON gate map: the problem, three things to show, two unknowns, one next step, and one risk that must stay visible.

It is not a submission bot. It does not log in, upload, send messages, or claim that a missing public link exists. The browser exports a local JSON brief marked `externalData: false` and `notUploaded: true`.

## Run locally

1. Ensure Ollama is running with `qwen2.5:1.5b` available.
2. Run `python server.py`.
3. Open `http://127.0.0.1:8795/`.

The model call stays on `127.0.0.1:11434`; no hosted API key is used.

## Why this is distinct

GateMap is a submission-evidence planning tool, not a learner support classifier, a voice agent, a workload simulator, or a consent workflow. Its core technical boundary is local LLM output constrained and validated as a small JSON schema before it reaches the UI.
