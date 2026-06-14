const stages = [
  ["task", "Task", "TaskStarted"],
  ["run", "Run", "Command events"],
  ["diagnose", "Diagnose", "ErrorDetected"],
  ["memory", "Memory", "FailureMemory"],
  ["plan", "Plan", "PatchPlan"],
  ["review", "Review", "Safety"],
  ["approval", "Approval", "Human gate"],
  ["apply", "Apply", "Workspace"],
  ["verify", "Verify", "Verifier"],
  ["result", "Result", "TaskFinished"],
];

const stageByEvent = {
  TaskStarted: "task",
  CommandStarted: "run",
  CommandOutput: "run",
  CommandFinished: "run",
  ErrorDetected: "diagnose",
  FailureMemoryCreated: "memory",
  EnvRepairPlanCreated: "plan",
  PatchProposed: "plan",
  PatchReviewCreated: "review",
  PatchApprovalRequired: "approval",
  PatchApplied: "apply",
  VerificationStarted: "verify",
  VerificationFinished: "verify",
  TaskFinished: "result",
};

let tasks = [];
let eventSource = null;
let transcriptLines = [];

const $ = (id) => document.getElementById(id);

function setText(id, value) {
  $(id).textContent = value === undefined || value === null || value === "" ? "-" : String(value);
}

function setBadge(id, label, kind = "neutral") {
  const element = $(id);
  element.textContent = label;
  element.className = `badge ${kind}`;
}

function renderStages() {
  const track = $("stage-track");
  track.innerHTML = "";
  for (const [id, label, detail] of stages) {
    const node = document.createElement("div");
    node.className = "stage";
    node.id = `stage-${id}`;
    node.innerHTML = `<strong>${label}</strong><span>${detail}</span>`;
    track.appendChild(node);
  }
}

function resetStages() {
  for (const [id] of stages) {
    $("stage-" + id).className = "stage";
  }
}

function setStage(id, status) {
  const stage = $("stage-" + id);
  if (!stage) return;
  stage.className = `stage ${status}`;
}

function completePreviousStages(activeId) {
  const activeIndex = stages.findIndex(([id]) => id === activeId);
  stages.forEach(([id], index) => {
    if (index < activeIndex) {
      setStage(id, "done");
    }
  });
}

function updateStageForEvent(event) {
  const stageId = stageByEvent[event.type];
  if (!stageId) return;
  completePreviousStages(stageId);

  if (event.type === "TaskFinished") {
    const failed = event.status === "failed";
    setStage(stageId, failed ? "failed" : "done");
    return;
  }

  if (event.type === "PatchReviewCreated" && event.blocked) {
    setStage(stageId, "blocked");
    return;
  }

  setStage(stageId, event.type.endsWith("Finished") ? "done" : "running");
}

function formatList(items) {
  if (!items || items.length === 0) return "<li>none</li>";
  return items.map((item) => `<li>${escapeHtml(String(item))}</li>`).join("");
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderDiff(diff) {
  if (!diff) return "No patch proposed yet.";
  return diff
    .split("\n")
    .map((line) => {
      const safe = escapeHtml(line);
      if (line.startsWith("+") && !line.startsWith("+++")) {
        return `<span class="diff-add">${safe}</span>`;
      }
      if (line.startsWith("-") && !line.startsWith("---")) {
        return `<span class="diff-remove">${safe}</span>`;
      }
      if (line.startsWith("@@")) {
        return `<span class="diff-hunk">${safe}</span>`;
      }
      return safe;
    })
    .join("\n");
}

function timelineDetail(event) {
  switch (event.type) {
    case "TranscriptCreated":
      return `transcript=${event.path}`;
    case "TaskStarted":
      return event.task_name || event.task_id;
    case "PlanCreated":
      return `${(event.steps || []).length} steps`;
    case "StepStarted":
      return `${event.step_index}. ${event.step_name}`;
    case "CommandStarted":
      return `$ ${event.command}`;
    case "CommandOutput":
      return `${event.stream}: ${event.content}`;
    case "CommandFinished":
      return `return_code=${event.return_code} success=${event.success}`;
    case "ErrorDetected":
      return `${event.error_type}: ${event.summary}`;
    case "FailureMemoryCreated":
      return `${event.error_type}: ${event.root_cause_hypothesis}`;
    case "EnvRepairPlanCreated":
      return `${event.issue_category}: ${event.summary}`;
    case "PatchProposed":
      return `target=${event.target_file} confidence=${event.confidence}`;
    case "PatchReviewCreated":
      return `approved=${event.approved} blocked=${event.blocked} risk=${event.risk_level}`;
    case "PatchApprovalRequired":
      return event.message || "Human confirmation required";
    case "PatchApplied":
      return `success=${event.success} ${event.message || ""}`;
    case "VerificationStarted":
      return `$ ${event.command}`;
    case "VerificationFinished":
      return `success=${event.success} return_code=${event.return_code} ${event.summary || ""}`;
    case "TaskFinished":
      return `${event.status}: ${event.summary}`;
    case "FrontendStreamError":
      return event.message;
    default:
      return JSON.stringify(event);
  }
}

function addTimelineEvent(event) {
  const timestamp = event.timestamp || new Date().toISOString();
  const time = timestamp.length >= 19 ? timestamp.slice(11, 19) : "--:--:--";
  const detail = timelineDetail(event);
  const item = document.createElement("li");
  item.innerHTML = `
    <span class="time">${escapeHtml(time)}</span>
    <span class="event-name">${escapeHtml(event.type || "UnknownEvent")}</span>
    <span class="detail">${escapeHtml(detail)}</span>
  `;
  $("timeline").appendChild(item);
  $("timeline").scrollTop = $("timeline").scrollHeight;
  transcriptLines.push(`[${time}] ${event.type} ${detail}`);
}

function resetCards() {
  setBadge("failure-badge", "waiting");
  setText("error-type", "-");
  setText("error-summary", "No failure analyzed yet.");
  $("error-evidence").innerHTML = "";
  setText("root-cause", "-");
  setText("repair-action", "-");

  setBadge("patch-badge", "waiting");
  setText("patch-target", "-");
  setText("patch-confidence", "-");
  setText("patch-change", "-");
  $("patch-diff").innerHTML = "No patch proposed yet.";

  setBadge("review-badge", "waiting");
  setText("review-approved", "-");
  setText("review-blocked", "-");
  setText("review-risk", "-");
  $("review-reasons").innerHTML = "";
  $("review-warnings").innerHTML = "";

  setBadge("verify-badge", "waiting");
  setText("verify-command", "-");
  setText("verify-return-code", "-");
  setText("verify-success", "-");
  setText("final-status", "-");
  setText("final-summary", "-");
}

function updateCards(event) {
  switch (event.type) {
    case "TranscriptCreated":
      $("transcript-note").textContent = `Transcript saved to ${event.path}`;
      break;
    case "ErrorDetected":
      setBadge("failure-badge", "detected", "warning");
      setText("error-type", event.error_type);
      setText("error-summary", event.summary);
      $("error-evidence").innerHTML = formatList(event.evidence);
      break;
    case "FailureMemoryCreated":
      setBadge("failure-badge", "created", "success");
      setText("error-type", event.error_type);
      $("error-evidence").innerHTML = formatList(event.evidence);
      setText("root-cause", event.root_cause_hypothesis);
      setText("repair-action", event.repair_action);
      break;
    case "EnvRepairPlanCreated":
      setBadge("patch-badge", "env plan", "warning");
      setText("patch-target", event.issue_category);
      setText("patch-confidence", event.confidence);
      setText("patch-change", event.summary);
      $("patch-diff").innerHTML = escapeHtml((event.suggested_actions || []).join("\n"));
      break;
    case "PatchProposed":
      setBadge("patch-badge", "proposed", "success");
      setText("patch-target", event.target_file);
      setText("patch-confidence", event.confidence);
      setText("patch-change", event.proposed_change);
      $("patch-diff").innerHTML = renderDiff(event.unified_diff);
      break;
    case "PatchReviewCreated":
      setBadge("review-badge", event.blocked ? "blocked" : "reviewed", event.blocked ? "danger" : "success");
      setText("review-approved", event.approved);
      setText("review-blocked", event.blocked);
      setText("review-risk", event.risk_level);
      $("review-reasons").innerHTML = formatList(event.reasons);
      $("review-warnings").innerHTML = formatList(event.warnings);
      break;
    case "PatchApprovalRequired":
      setBadge("review-badge", "approval required", "warning");
      $("confirm-button").disabled = false;
      setStatus("Waiting for human confirmation.");
      break;
    case "PatchApplied":
      setBadge("patch-badge", event.success ? "applied" : "apply failed", event.success ? "success" : "danger");
      break;
    case "VerificationStarted":
      setBadge("verify-badge", "running", "warning");
      setText("verify-command", event.command);
      break;
    case "VerificationFinished":
      setBadge("verify-badge", event.success ? "passed" : "failed", event.success ? "success" : "danger");
      setText("verify-command", event.command);
      setText("verify-return-code", event.return_code);
      setText("verify-success", event.success);
      setText("final-summary", event.summary);
      break;
    case "TaskFinished":
      setText("final-status", event.status);
      setText("final-summary", event.summary);
      setStatus(`Finished: ${event.status}`);
      setBadge("connection-badge", "Finished", event.status === "failed" ? "danger" : "success");
      $("run-button").disabled = false;
      if (event.status !== "demo_finished") {
        $("confirm-button").disabled = true;
      }
      break;
    case "FrontendStreamError":
      setStatus(`Stream failed: ${event.message}`);
      setBadge("connection-badge", "Error", "danger");
      $("run-button").disabled = false;
      break;
  }
}

function setStatus(message) {
  setText("status-text", message);
}

function resetRunState() {
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  transcriptLines = [];
  $("timeline").innerHTML = "";
  $("transcript-note").textContent = "Transcript will be saved under outputs/frontend_logs.";
  resetStages();
  resetCards();
  $("confirm-button").disabled = true;
}

function handleEvent(event) {
  addTimelineEvent(event);
  updateStageForEvent(event);
  updateCards(event);
}

function startRun(confirmApply = false) {
  if (eventSource) {
    eventSource.close();
  }

  if (!confirmApply) {
    resetRunState();
  }

  const taskId = $("task-select").value;
  const mode = confirmApply ? "repair" : $("mode-select").value;
  $("mode-select").value = mode;
  $("run-mode-badge").textContent = mode;
  $("run-button").disabled = true;
  $("confirm-button").disabled = true;
  setStatus(confirmApply ? "Confirming and verifying patch..." : `Running ${mode}...`);
  setBadge("connection-badge", "Running", "warning");

  const url = `/api/run/stream?task_id=${encodeURIComponent(taskId)}&mode=${encodeURIComponent(mode)}&confirm_apply=${confirmApply}`;
  eventSource = new EventSource(url);
  eventSource.onmessage = (message) => {
    const event = JSON.parse(message.data);
    handleEvent(event);
    if (event.type === "TaskFinished" || event.type === "FrontendStreamError") {
      eventSource.close();
      eventSource = null;
    }
  };
  eventSource.onerror = () => {
    setStatus("Event stream disconnected.");
    setBadge("connection-badge", "Disconnected", "danger");
    $("run-button").disabled = false;
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
  };
}

function updateSelectedTaskCard() {
  const task = tasks.find((item) => item.task_id === $("task-select").value);
  if (!task) return;
  setText("task-name", task.task_name || task.task_id);
  setText(
    "task-meta",
    `id=${task.task_id} | category=${task.category} | difficulty=${task.difficulty} | requires=${(task.requires || []).join(", ") || "none"}`
  );
}

async function loadTasks() {
  const response = await fetch("/api/tasks");
  const data = await response.json();
  tasks = data.tasks || [];
  const select = $("task-select");
  select.innerHTML = "";
  for (const task of tasks) {
    const option = document.createElement("option");
    option.value = task.task_id;
    option.textContent = task.task_id;
    select.appendChild(option);
  }

  const preferred = tasks.find((task) => task.task_id === "repair_device_mismatch_007") || tasks[0];
  if (preferred) {
    select.value = preferred.task_id;
  }
  $("task-count").textContent = `${tasks.length} tasks`;
  updateSelectedTaskCard();
}

function copyTranscript() {
  const text = transcriptLines.join("\n");
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    setStatus("Timeline copied to clipboard.");
  });
}

function bindUi() {
  $("run-button").addEventListener("click", () => startRun(false));
  $("confirm-button").addEventListener("click", () => startRun(true));
  $("task-select").addEventListener("change", updateSelectedTaskCard);
  $("mode-select").addEventListener("change", () => {
    $("run-mode-badge").textContent = $("mode-select").value;
    $("confirm-button").disabled = true;
  });
  $("copy-transcript-button").addEventListener("click", copyTranscript);
  bindImageModal();
}

function bindImageModal() {
  const modal = $("image-modal");
  const modalImg = $("image-modal-img");
  const modalCaption = $("image-modal-caption");
  const closeButton = $("image-modal-close");
  if (!modal || !modalImg || !modalCaption || !closeButton) return;

  document.querySelectorAll("figure img").forEach((img) => {
    img.addEventListener("click", () => {
      modalImg.src = img.src;
      modalImg.alt = img.alt || "";
      const caption = img.closest("figure")?.querySelector("figcaption")?.textContent;
      modalCaption.textContent = caption || img.alt || "Figure";
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
    });
  });

  const closeModal = () => {
    modal.classList.remove("open");
    modal.setAttribute("aria-hidden", "true");
    modalImg.src = "";
  };

  closeButton.addEventListener("click", closeModal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal.classList.contains("open")) {
      closeModal();
    }
  });
}

async function boot() {
  renderStages();
  resetCards();
  bindUi();
  try {
    await loadTasks();
    setStatus("Ready.");
    setBadge("connection-badge", "Ready", "neutral");
  } catch (error) {
    setStatus(`Failed to load tasks: ${error}`);
    setBadge("connection-badge", "Error", "danger");
  }
}

boot();
