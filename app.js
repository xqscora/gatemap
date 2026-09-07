const $ = (id) => document.getElementById(id);
let lastResult = null;

const example = {
  brief: "Build an AI tool that solves a real-world problem. Judges need to understand the problem, why AI is core, how the prototype works, and what evidence supports the claim.",
  evidence: "GateMap has a local browser UI and a Python server. The server sends only this synthetic brief to Ollama on 127.0.0.1, validates a JSON schema, and shows must-show evidence, unknowns, and one next step. There is no public repository or live demo yet."
};

function setList(id, values) {
  const list = $(id);
  list.replaceChildren();
  values.forEach((value) => {
    const item = document.createElement("li");
    item.textContent = value;
    list.append(item);
  });
}

function offlineFallback() {
  return {
    provider: "offline-demo-fallback",
    model: "deterministic-rule-check",
    externalData: false,
    problem: "Ollama is not reachable in this browser context. This transparent fallback keeps the evidence boundary visible; it is not a model result.",
    must_show: [
      "Show the working prototype and the exact user path.",
      "Tie every important claim to evidence that is actually present.",
      "Show the local-only boundary and the claims that remain unverified."
    ],
    unknowns: [
      "A live Ollama response and strict schema validation are not available here.",
      "Public links, dates, and external claims still need independent verification."
    ],
    next_step: "Run GateMap locally with Ollama, then replace each unknown with a concrete link, test, or screenshot.",
    risk: "Do not present this fallback as Ollama output; it is only an honest offline demo aid."
  };
}

function render(result) {
  lastResult = result;
  $("output").hidden = false;
  $("model-label").textContent = `${result.provider} | ${result.model}`;
  $("problem").textContent = result.problem;
  setList("must-show", result.must_show);
  setList("unknowns", result.unknowns);
  $("next-step").textContent = result.next_step;
  $("risk").textContent = `Risk to keep visible: ${result.risk}`;
  $("status").textContent = "Structured locally. No upload occurred.";
  $("receipt-status").textContent = "Local result only.";
}

$("load-example").addEventListener("click", () => {
  $("brief").value = example.brief;
  $("evidence").value = example.evidence;
  $("status").textContent = "Synthetic example loaded.";
});

$("run").addEventListener("click", async () => {
  $("status").textContent = "Asking Ollama locally...";
  $("run").disabled = true;
  try {
    const response = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ brief: $("brief").value, evidence: $("evidence").value }) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "local model request failed");
    render(result);
  } catch (error) {
    render(offlineFallback());
    $("status").textContent = "Ollama is unavailable here. An honest offline fallback is shown; no upload occurred.";
  } finally {
    $("run").disabled = false;
  }
});

$("export").addEventListener("click", () => {
  if (!lastResult) return;
  const receipt = { product: "GateMap", generatedAt: new Date().toISOString(), externalData: false, notUploaded: true, brief: $("brief").value, evidence: $("evidence").value, result: lastResult };
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([JSON.stringify(receipt, null, 2)], { type: "application/json" }));
  link.download = "gatemap-local-brief.json";
  link.click();
  URL.revokeObjectURL(link.href);
  $("receipt-status").textContent = "Brief exported locally. It was not uploaded.";
});
