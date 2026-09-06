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
    $("status").textContent = `No result: ${error.message}`;
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
