const vscode = require("vscode");
const http = require("http");
const https = require("https");

let activeExercise = null;
let startedAt = null;
let lastTaskExitCode = 0;
let statusBar;

function serverUrl() {
  return vscode.workspace.getConfiguration("studyCoach").get("serverUrl", "http://127.0.0.1:8780");
}

function post(path, body) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, serverUrl());
    const transport = url.protocol === "https:" ? https : http;
    const raw = Buffer.from(JSON.stringify(body));
    const req = transport.request(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": raw.length
      },
      timeout: 3000
    }, (res) => {
      let data = "";
      res.setEncoding("utf8");
      res.on("data", chunk => data += chunk);
      res.on("end", () => {
        try {
          const parsed = data ? JSON.parse(data) : {};
          if (res.statusCode >= 200 && res.statusCode < 300) resolve(parsed);
          else reject(new Error(parsed.error || "HTTP " + res.statusCode));
        } catch (err) {
          reject(err);
        }
      });
    });
    req.on("timeout", () => req.destroy(new Error("Study Coach server timeout")));
    req.on("error", reject);
    req.write(raw);
    req.end();
  });
}

function updateStatus() {
  if (!statusBar) return;
  if (activeExercise) {
    statusBar.text = "$(book) Study Coach: Bài " + activeExercise;
    statusBar.tooltip = "Bài đang làm. Bấm để chọn bài khác.";
  } else {
    statusBar.text = "$(book) Study Coach";
    statusBar.tooltip = "Bấm để bắt đầu một bài.";
  }
  statusBar.show();
}

async function startExercise(context) {
  const value = await vscode.window.showInputBox({
    title: "Study Coach",
    prompt: "Nhập số bài (1–300)",
    value: activeExercise ? String(activeExercise) : "1",
    validateInput: (text) => {
      const n = Number(text);
      return Number.isInteger(n) && n >= 1 && n <= 300 ? null : "Số bài phải từ 1 đến 300.";
    }
  });
  if (!value) return;
  activeExercise = Number(value);
  startedAt = Date.now();
  lastTaskExitCode = 0;
  await context.globalState.update("activeExercise", activeExercise);
  await context.globalState.update("startedAt", startedAt);
  try {
    await post("/api/active", { exercise_id: activeExercise });
    vscode.window.showInformationMessage("Study Coach: bắt đầu bài " + activeExercise + ".");
  } catch (err) {
    vscode.window.showWarningMessage("Đã chọn bài " + activeExercise + " nhưng server chưa nhận được: " + err.message);
  }
  updateStatus();
}

async function mark(context, outcome) {
  if (!activeExercise) {
    await startExercise(context);
    if (!activeExercise) return;
  }
  const elapsed = startedAt ? Math.max(0, Math.round((Date.now() - startedAt) / 1000)) : 0;
  const labels = {
    independent: "Tự làm được",
    hint: "Cần gợi ý",
    solution: "Xem lời giải",
    failed: "Chưa làm được"
  };
  try {
    const result = await post("/api/attempt", {
      exercise_id: activeExercise,
      outcome,
      duration_sec: elapsed,
      compile_errors: lastTaskExitCode === 0 ? 0 : 1,
      notes: "Ghi từ VS Code extension"
    });
    const rec = result.dashboard && result.dashboard.recommendation;
    const extra = rec ? " Tiếp theo: " + rec.action + " · Bài " + rec.exercise_id + "." : "";
    vscode.window.showInformationMessage("Study Coach: " + labels[outcome] + "." + extra);
    startedAt = Date.now();
    lastTaskExitCode = 0;
    await context.globalState.update("startedAt", startedAt);
  } catch (err) {
    vscode.window.showErrorMessage("Study Coach chưa lưu được: " + err.message);
  }
}

function activate(context) {
  activeExercise = context.globalState.get("activeExercise", null);
  startedAt = context.globalState.get("startedAt", null);

  statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 50);
  statusBar.command = "studyCoach.startExercise";
  context.subscriptions.push(statusBar);
  updateStatus();

  context.subscriptions.push(
    vscode.commands.registerCommand("studyCoach.startExercise", () => startExercise(context)),
    vscode.commands.registerCommand("studyCoach.markIndependent", () => mark(context, "independent")),
    vscode.commands.registerCommand("studyCoach.markHint", () => mark(context, "hint")),
    vscode.commands.registerCommand("studyCoach.markSolution", () => mark(context, "solution")),
    vscode.commands.registerCommand("studyCoach.markFailed", () => mark(context, "failed")),
    vscode.tasks.onDidEndTaskProcess((event) => {
      if (activeExercise && typeof event.exitCode === "number") {
        lastTaskExitCode = event.exitCode;
      }
    })
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
