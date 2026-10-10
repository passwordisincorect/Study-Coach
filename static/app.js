const state = {



  dashboard: null,



  problem: null,



  exerciseStartedAt: null,



  hintUsed: false,



};



const $ = (id) => document.getElementById(id);



const THEME_KEY = "studyCoachTheme";



const DRAFT_PREFIX = "studyCoachDraft:";



const outcomeLabels = {



  independent: "Tự làm",



  hint: "Có gợi ý",
  external_pass: "AC nguồn ngoài (tự xác nhận)",



  solution: "Xem lời giải",



  failed: "Chưa đạt",



};



async function api(path, options = {}) {



  const response = await fetch(path, {



    headers: { "Content-Type": "application/json" },



    ...options,



  });



  const data = await response.json();



  if (!response.ok || data.ok === false) {



    throw new Error(data.error || "Có lỗi xảy ra");



  }



  return data;



}



function escapeHtml(value) {



  return String(value ?? "")



    .replaceAll("&", "&amp;")



    .replaceAll("<", "&lt;")



    .replaceAll(">", "&gt;")



    .replaceAll('"', "&quot;");



}



function applyTheme(theme) {



  const dark = theme === "dark";



  document.body.classList.toggle("theme-dark", dark);



  $("themeLight").classList.toggle("active", !dark);



  $("themeDark").classList.toggle("active", dark);



  $("themeLight").setAttribute("aria-pressed", String(!dark));



  $("themeDark").setAttribute("aria-pressed", String(dark));



  try {



    localStorage.setItem(THEME_KEY, dark ? "dark" : "light");



  } catch (_) {}



}



function initTheme() {



  let theme = "light";



  try {



    theme = localStorage.getItem(THEME_KEY) || "light";



  } catch (_) {}



  applyTheme(theme);



  $("themeLight").addEventListener("click", () => applyTheme("light"));



  $("themeDark").addEventListener("click", () => applyTheme("dark"));



}



function setServerStatus(ok, message) {



  const el = $("serverStatus");



  el.textContent = message;



  el.className = "server-pill " + (ok ? "ok" : "bad");



}



function renderSummary(dashboard) {



  $("attemptedCount").textContent = dashboard.summary.attempted;



  $("masteredCount").textContent = dashboard.summary.mastered;



  $("masteredPercent").textContent = dashboard.summary.mastered_percent + "%";



  $("progressBar").style.width = Math.min(100, dashboard.summary.mastered_percent) + "%";



  $("currentVideo").textContent =



    "Video #" + dashboard.meta.current_video_number +



    " · " + dashboard.meta.current_video_title +



    " · " + dashboard.meta.current_video_percent + "%";



  $("videoNumber").value = dashboard.meta.current_video_number || 13;



  $("videoTitle").value = dashboard.meta.current_video_title || "Vector trong C++";



  $("videoPercent").value = dashboard.meta.current_video_percent || 0;



}



function renderRecommendation(dashboard) {

  const rec = dashboard.recommendation;

  const exercise = dashboard.exercises.find((x) => x.id === rec.exercise_id);

  $("nextTitle").textContent =

    exercise ? "Bài " + exercise.id + " · " + exercise.title : "Bài " + rec.exercise_id;

  $("recommendationReason").textContent = rec.reason;

  $("recommendationAction").textContent = rec.action;

  const button = $("useRecommendation");

  button.dataset.exerciseId = String(rec.exercise_id);

  button.dataset.autoJudge = exercise && exercise.auto_judge ? "1" : "0";

  button.dataset.sourceUrl = exercise ? (exercise.source_url || "") : "";

  button.disabled = false;

  button.textContent = exercise && !exercise.auto_judge ? "Mở đề gốc" : "Làm bài này";

}



function activeTopicLevel(dashboard) {



  const id = Number(dashboard.recommendation.exercise_id);



  const topic = dashboard.topics.find((t) => id >= t.range[0] && id <= t.range[1]);



  return topic ? topic.level : 1;



}



function renderTopics(dashboard) {



  const activeLevel = activeTopicLevel(dashboard);



  const grid = $("topicGrid");



  grid.innerHTML = "";



  dashboard.topics.forEach((topic) => {



    const step = document.createElement("div");



    const complete = topic.mastery >= 80;



    const active = topic.level === activeLevel;



    step.className =



      "topic-step" + (complete ? " complete" : "") + (active ? " active" : "");



    step.innerHTML =



      '<div class="topic-dot">' + (complete ? "✓" : topic.level) + "</div>" +



      '<span class="topic-name">' + escapeHtml(topic.topic) + "</span>" +



      '<span class="topic-mastery">' + topic.mastery + "%</span>";



    grid.appendChild(step);



  });



  if (window.matchMedia("(max-width: 820px)").matches) {



    requestAnimationFrame(() => {



      const active = grid.querySelector(".topic-step.active");



      if (active) active.scrollIntoView({ block: "nearest", inline: "center", behavior: "auto" });



    });



  }



}



function populateTopicFilter(dashboard) {



  const select = $("topicFilter");



  if (select.options.length > 1) return;



  dashboard.topics.forEach((topic) => {



    const option = document.createElement("option");



    option.value = topic.topic;



    option.textContent = topic.topic;



    select.appendChild(option);



  });



}



function exerciseMeta(exercise) {



  if (exercise.latest_outcome === "external_pass") return "AC nguồn ngoài (tự xác nhận)";
  if (exercise.status === "mastered") return "Đã đạt";



  if (exercise.status === "learning") return "Đang luyện";



  return "Chưa làm";



}



function renderExercises(dashboard) {

  const query = $("searchInput").value.trim().toLowerCase();

  const topic = $("topicFilter").value;

  const status = $("statusFilter").value;

  const list = $("exerciseList");

  list.innerHTML = "";



  const filtered = dashboard.exercises.filter((exercise) => {

    const haystack = ("bài " + exercise.id + " " + exercise.title).toLowerCase();

    return (!query || haystack.includes(query)) &&

      (!topic || exercise.topic === topic) &&

      (!status || exercise.status === status);

  });



  filtered.forEach((exercise) => {

    const row = document.createElement("article");

    row.className = "exercise-row " + exercise.status;

    const action = exercise.auto_judge ? "Làm bài" : "Đề gốc";

    row.innerHTML =

      '<div class="exercise-number">' + exercise.id + "</div>" +

      '<div class="exercise-copy"><strong>' + escapeHtml(exercise.title) + "</strong>" +

      "<small>" + escapeHtml(exercise.topic) + " · " + exerciseMeta(exercise) + "</small></div>" +

      '<button class="exercise-action" type="button" data-pick="' + exercise.id +

      '" data-auto-judge="' + (exercise.auto_judge ? "1" : "0") +

      '" data-source-url="' + escapeHtml(exercise.source_url || "") + '">' + action + "</button>";

    list.appendChild(row);

  });



  if (!filtered.length) {

    list.innerHTML = '<div class="empty-state">Không có bài phù hợp bộ lọc.</div>';

  }

}



function renderRecent(dashboard) {



  const list = $("recentList");



  list.innerHTML = "";



  if (!dashboard.recent.length) {



    list.innerHTML =



      '<div class="empty-state">Chưa có lần nộp bài nào. Kết quả Auto Judge sẽ xuất hiện ở đây.</div>';



    return;



  }



  dashboard.recent.slice(0, 7).forEach((attempt) => {



    const passed = attempt.outcome === "independent" || attempt.outcome === "hint";



    const item = document.createElement("div");



    item.className = "recent-item " + (passed ? "pass" : "fail");



    const minutes = attempt.duration_sec



      ? Math.max(1, Math.round(attempt.duration_sec / 60)) + " phút"



      : "—";



    item.innerHTML =



      '<div class="recent-badge">' + (passed ? "✓" : "×") + "</div>" +



      '<div class="recent-copy"><strong>Bài ' + attempt.exercise_id + " · " +



      escapeHtml(attempt.title) + "</strong><span>" +



      outcomeLabels[attempt.outcome] + " · " + minutes + "</span></div>";



    list.appendChild(item);



  });



}



function syncProgressReset(meta) {

  const resetId = meta && meta.progress_reset_id;

  if (!resetId) return;

  const appliedKey = "studyCoachAppliedResetId";

  let applied = "";

  try { applied = localStorage.getItem(appliedKey) || ""; } catch (_) {}

  if (applied === resetId) return;

  try {

    const keys = [];

    for (let i = 0; i < localStorage.length; i++) {

      const key = localStorage.key(i);

      if (key && key.startsWith(DRAFT_PREFIX)) keys.push(key);

    }

    keys.forEach((key) => localStorage.removeItem(key));

    localStorage.setItem(appliedKey, resetId);

  } catch (_) {}

}



function render(dashboard) {



  state.dashboard = dashboard;

  syncProgressReset(dashboard.meta);



  renderSummary(dashboard);



  renderRecommendation(dashboard);



  renderTopics(dashboard);



  populateTopicFilter(dashboard);



  renderExercises(dashboard);



  renderRecent(dashboard);



}



async function loadDashboard() {



  try {



    const dashboard = await api("/api/dashboard");



    render(dashboard);



    setServerStatus(true, "Đang hoạt động");



  } catch (error) {



    setServerStatus(false, "Mất kết nối");



    console.error(error);



  }



}



function renderSamples(problem) {



  const root = $("sampleTests");



  root.innerHTML = "";



  problem.samples.forEach((sample, index) => {



    const card = document.createElement("div");



    card.className = "sample-card";



    card.innerHTML =



      "<strong>Test " + (index + 1) + "</strong>" +



      '<div class="sample-grid">' +



      '<div><small>Input</small><pre>' +



      escapeHtml(sample.input || "(không có input)") +



      "</pre></div>" +



      '<div><small>Output</small><pre>' +



      escapeHtml(sample.output || "(không có output)") +



      "</pre></div>" +



      "</div>";



    root.appendChild(card);



  });



}



function draftKey(id) {



  return DRAFT_PREFIX + id;



}



function loadDraft(problem) {



  try {



    return localStorage.getItem(draftKey(problem.id)) || problem.starter;



  } catch (_) {



    return problem.starter;



  }



}



function saveDraft() {



  if (!state.problem) return;



  try {



    localStorage.setItem(draftKey(state.problem.id), $("codeEditor").value);



  } catch (_) {}



}



const EDITOR_INDENT = "    ";



const PAIRS = { "(": ")", "[": "]", "{": "}", '"': '"', "'": "'" };



const CLOSERS = new Set(Object.values(PAIRS));



function editorLineInfo(editor) {



  const pos = editor.selectionStart;



  const before = editor.value.slice(0, pos);



  const lines = before.split("\n");



  return { line: lines.length, col: lines[lines.length - 1].length + 1 };



}



function updateEditorChrome() {



  const editor = $("codeEditor");



  const gutter = $("lineNumbers");



  if (!editor || !gutter) return;



  const count = Math.max(1, editor.value.split("\n").length);



  gutter.textContent = Array.from({ length: count }, (_, i) => i + 1).join("\n");



  gutter.scrollTop = editor.scrollTop;



  const pos = editorLineInfo(editor);



  $("cursorPosition").textContent = "Ln " + pos.line + ", Col " + pos.col;



}



function replaceEditorRange(start, end, text, caretOffset = text.length) {



  const editor = $("codeEditor");



  editor.value = editor.value.slice(0, start) + text + editor.value.slice(end);



  const caret = start + caretOffset;



  editor.selectionStart = editor.selectionEnd = caret;



  editor.dispatchEvent(new Event("input", { bubbles: true }));



}



function selectedLineRange(editor) {



  const value = editor.value;



  const start = value.lastIndexOf("\n", Math.max(0, editor.selectionStart - 1)) + 1;



  let end = value.indexOf("\n", editor.selectionEnd);



  if (end < 0) end = value.length;



  return { start, end };



}



function indentSelection(unindent = false) {



  const editor = $("codeEditor");



  const range = selectedLineRange(editor);



  const block = editor.value.slice(range.start, range.end);



  const lines = block.split("\n");



  const changed = lines.map((line) => {



    if (!unindent) return EDITOR_INDENT + line;



    const m = line.match(/^( {1,4}|\t)/);



    return m ? line.slice(m[0].length) : line;



  }).join("\n");



  editor.value = editor.value.slice(0, range.start) + changed + editor.value.slice(range.end);



  editor.selectionStart = range.start;



  editor.selectionEnd = range.start + changed.length;



  editor.dispatchEvent(new Event("input", { bubbles: true }));



}



function toggleLineComment() {



  const editor = $("codeEditor");



  const range = selectedLineRange(editor);



  const lines = editor.value.slice(range.start, range.end).split("\n");



  const nonEmpty = lines.filter((line) => line.trim());



  const uncomment = nonEmpty.length > 0 && nonEmpty.every((line) => /^\s*\/\//.test(line));



  const changed = lines.map((line) => {



    if (!line.trim()) return line;



    if (uncomment) return line.replace(/^(\s*)\/\/ ?/, "$1");



    return line.replace(/^(\s*)/, "$1// ");



  }).join("\n");



  editor.value = editor.value.slice(0, range.start) + changed + editor.value.slice(range.end);



  editor.selectionStart = range.start;



  editor.selectionEnd = range.start + changed.length;



  editor.dispatchEvent(new Event("input", { bubbles: true }));



}



function handleEditorEnter(event) {



  const editor = $("codeEditor");



  const start = editor.selectionStart;



  const end = editor.selectionEnd;



  const before = editor.value.slice(0, start);



  const after = editor.value.slice(end);



  const lineStart = before.lastIndexOf("\n") + 1;



  const currentLine = before.slice(lineStart);



  const baseIndent = (currentLine.match(/^\s*/) || [""])[0].replace(/\t/g, EDITOR_INDENT);



  const opensBlock = currentLine.trimEnd().endsWith("{");



  const nextIsClosingBrace = after.startsWith("}");



  event.preventDefault();



  if (opensBlock && nextIsClosingBrace) {



    const inserted = "\n" + baseIndent + EDITOR_INDENT + "\n" + baseIndent;



    replaceEditorRange(start, end, inserted, 1 + baseIndent.length + EDITOR_INDENT.length);



  } else {



    const indent = baseIndent + (opensBlock ? EDITOR_INDENT : "");



    replaceEditorRange(start, end, "\n" + indent);



  }



}



function handleEditorPair(event) {



  const editor = $("codeEditor");



  const key = event.key;



  const start = editor.selectionStart;



  const end = editor.selectionEnd;



  const next = editor.value[start] || "";



  if (CLOSERS.has(key) && start === end && next === key) {



    event.preventDefault();



    editor.selectionStart = editor.selectionEnd = start + 1;



    updateEditorChrome();



    return true;



  }



  if (!Object.prototype.hasOwnProperty.call(PAIRS, key)) return false;



  if ((key === '"' || key === "'") && start > 0 && editor.value[start - 1] === "\\") return false;



  event.preventDefault();



  const selected = editor.value.slice(start, end);



  const inserted = key + selected + PAIRS[key];



  replaceEditorRange(start, end, inserted, selected ? inserted.length : 1);



  return true;



}



function handleSmartBackspace(event) {



  const editor = $("codeEditor");



  if (editor.selectionStart !== editor.selectionEnd || editor.selectionStart === 0) return false;



  const pos = editor.selectionStart;



  const left = editor.value[pos - 1];



  const right = editor.value[pos];



  if (PAIRS[left] !== right) return false;



  event.preventDefault();



  replaceEditorRange(pos - 1, pos + 1, "", 0);



  return true;



}



function formatCppCode() {



  const editor = $("codeEditor");



  const source = editor.value.replace(/\r\n?/g, "\n");



  let depth = 0;



  let inBlockComment = false;



  const lines = source.split("\n");



  const formatted = lines.map((raw) => {



    const trimmed = raw.trim();



    if (!trimmed) return "";



    const startsClose = /^[}\])]/.test(trimmed);



    if (startsClose) depth = Math.max(0, depth - 1);



    const line = EDITOR_INDENT.repeat(depth) + trimmed;



    let delta = 0;



    let inString = null;



    let escape = false;



    for (let i = 0; i < trimmed.length; i++) {



      const ch = trimmed[i];



      const next = trimmed[i + 1];



      if (inBlockComment) {



        if (ch === "*" && next === "/") { inBlockComment = false; i++; }



        continue;



      }



      if (!inString && ch === "/" && next === "*") { inBlockComment = true; i++; continue; }



      if (!inString && ch === "/" && next === "/") break;



      if (inString) {



        if (escape) { escape = false; continue; }



        if (ch === "\\") { escape = true; continue; }



        if (ch === inString) inString = null;



        continue;



      }



      if (ch === '"' || ch === "'") { inString = ch; continue; }



      if (ch === "{") delta++;



      if (ch === "}") delta--;



    }



    if (startsClose) delta++;



    depth = Math.max(0, depth + delta);



    return line;



  }).join("\n");



  editor.value = formatted;



  editor.selectionStart = editor.selectionEnd = formatted.length;



  editor.dispatchEvent(new Event("input", { bubbles: true }));



  setJudgeStatus("Đã căn lề");



}



function setJudgeStatus(text, kind = "") {



  const el = $("judgeStatus");



  el.textContent = text;



  el.className = "judge-status" + (kind ? " " + kind : "");



}



async function openExercise(exerciseId) {



  try {



    setJudgeStatus("Đang tải…");



    const data = await api("/api/exercise/" + exerciseId);



    const problem = data.problem;



    state.problem = problem;



    state.exerciseStartedAt = Date.now();



    state.hintUsed = false;



    $("workspaceTitle").textContent = "Bài " + problem.id + " · " + problem.title;
    const sourceLink = $("workspaceSourceLink");
    sourceLink.href = problem.source_url || (state.dashboard?.exercises.find((x) => x.id === problem.id)?.source_url || "#");



    $("problemStatement").textContent = problem.statement;



    $("problemInput").textContent = problem.input;



    $("problemOutput").textContent = problem.output;



    $("hiddenTestCount").textContent =



      problem.hidden_count > 0



        ? problem.hidden_count + " test ẩn khi nộp"



        : problem.test_count + " test";



    $("hintText").hidden = true;



    $("hintText").textContent = "";



    $("judgeResults").innerHTML = "";



    $("codeEditor").value = loadDraft(problem);



    updateEditorChrome();



    renderSamples(problem);



    setJudgeStatus("Chưa chạy");



    $("exerciseModal").hidden = false;



    document.body.classList.add("exercise-open");



    $("exerciseModal").scrollTop = 0;



    if (window.matchMedia("(min-width: 821px)").matches) {



      $("codeEditor").focus({ preventScroll: true });



    } else {



      $("closeExercise").focus({ preventScroll: true });



    }



    await api("/api/active", {



      method: "POST",



      body: JSON.stringify({ exercise_id: exerciseId }),



    });



  } catch (error) {



    setJudgeStatus("Lỗi", "fail");



    alert(error.message);



  }



}



function closeExercise() {



  saveDraft();



  $("exerciseModal").hidden = true;



  document.body.classList.remove("exercise-open");



}



function renderJudgeResult(judge) {



  const root = $("judgeResults");



  root.innerHTML = "";



  if (!judge.ok) {



    const summary = document.createElement("div");



    summary.className = "judge-summary fail";



    summary.textContent = judge.stage === "compile" ? "Compile Error" : (judge.error || "Không thể chấm bài");



    root.appendChild(summary);



    if (judge.compile_error) {



      const pre = document.createElement("pre");



      pre.className = "compile-error";



      pre.textContent = judge.compile_error;



      root.appendChild(pre);



    }



    setJudgeStatus("Chưa đạt", "fail");



    return;



  }



  const summary = document.createElement("div");



  summary.className = "judge-summary " + (judge.passed ? "pass" : "fail");



  summary.textContent = judge.passed



    ? "PASS · " + judge.passed_count + "/" + judge.total_count + " test"



    : "CHƯA ĐẠT · " + judge.passed_count + "/" + judge.total_count + " test";



  root.appendChild(summary);



  setJudgeStatus(judge.passed ? "PASS" : "Cần sửa", judge.passed ? "pass" : "fail");



  judge.results.forEach((test) => {



    const item = document.createElement("div");



    item.className = "test-result";



    const title = document.createElement("strong");



    title.className = test.passed ? "pass" : "fail";



    title.textContent =



      "Test " + test.index + (test.hidden ? " · ẩn" : "") +



      " · " + (test.passed ? "PASS" : "FAIL");



    item.appendChild(title);



    if (!test.passed && test.hidden) {



      const message = document.createElement("p");



      message.textContent = "Test ẩn chưa qua. Kiểm tra các trường hợp biên và định dạng output.";



      item.appendChild(message);



    } else if (!test.hidden) {



      const pre = document.createElement("pre");



      pre.textContent =



        "Input:\n" + (test.input || "(không có)") +



        "\n\nMong đợi:\n" + (test.expected || "(trống)") +



        "\n\nCode của bạn:\n" + (test.actual || "(trống)");



      item.appendChild(pre);



    }



    if (test.runtime_error) {



      const pre = document.createElement("pre");



      pre.textContent = "Runtime error:\n" + test.runtime_error;



      item.appendChild(pre);



    }



    root.appendChild(item);



  });



}



function openSourceExercise(exerciseId, sourceUrl) {
  const item = state.dashboard?.exercises.find((x) => x.id === exerciseId);
  if (!item || item.auto_judge || !sourceUrl) return;
  state.sourceExerciseId = exerciseId;
  $("sourceProgress").hidden = false;
  $("sourceProgressTitle").textContent = "Bài " + exerciseId + " · " + item.title;
  $("sourceConfirm").checked = false;
  $("sourceRecordAC").disabled = true;
  $("sourceStatus").textContent =
    "Chỉ ghi nhận khi trang gốc hiển thị Accepted (AC). Đây không phải chấm tự động.";
  $("sourceOpenLink").href = sourceUrl;
  window.open(sourceUrl, "_blank", "noopener");
}

async function saveSourceAC() {
  const exerciseId = state.sourceExerciseId;
  if (!Number.isInteger(exerciseId) || !$("sourceConfirm").checked) return;
  const button = $("sourceRecordAC");
  button.disabled = true;
  $("sourceStatus").textContent = "Đang lưu xác nhận…";
  try {
    const result = await api("/api/source-result", {
      method: "POST",
      body: JSON.stringify({ exercise_id: exerciseId, confirmed: true }),
    });
    state.sourceExerciseId = null;
    $("sourceProgress").hidden = true;
    render(result.dashboard);
  } catch (error) {
    $("sourceStatus").textContent = "Không ghi được kết quả: " + error.message;
    button.disabled = false;
  }
}

function appendNextAction(dashboard) {
  const judgeRoot = $("judgeResults");
  const rec = dashboard.recommendation;
  const exercise = dashboard.exercises.find((x) => x.id === rec.exercise_id);
  if (!exercise) return;

  const wrapper = document.createElement("div");
  wrapper.className = "next-after-pass";

  const button = document.createElement("button");
  button.className = "button button-primary";
  button.type = "button";
  if (exercise.auto_judge) {
    button.textContent = "Tiếp tục: Bài " + exercise.id;
    button.addEventListener("click", () => openExercise(exercise.id));
  } else {
    button.textContent = "Mở đề gốc: Bài " + exercise.id;
    button.addEventListener("click", () => {
      if (exercise.source_url) openSourceExercise(exercise.id, exercise.source_url);
    });
  }
  wrapper.appendChild(button);

  if (!exercise.auto_judge) {
    const note = document.createElement("p");
    note.className = "next-after-pass-note";
    note.textContent = "Bài này chưa có Auto Judge local; Study Coach sẽ mở đề gốc để bạn tiếp tục.";
    wrapper.appendChild(note);
  }
  judgeRoot.appendChild(wrapper);
}

async function judgeCurrent(record) {



  if (!state.problem) return;



  saveDraft();



  const elapsed = state.exerciseStartedAt



    ? Math.max(0, Math.round((Date.now() - state.exerciseStartedAt) / 1000))



    : 0;



  $("runTests").disabled = true;



  $("submitCode").disabled = true;



  setJudgeStatus(record ? "Đang nộp…" : "Đang chạy…");



  try {



    const result = await api("/api/judge", {



      method: "POST",



      body: JSON.stringify({



        exercise_id: state.problem.id,



        code: $("codeEditor").value,



        record,



        hint_used: state.hintUsed,



        duration_sec: elapsed,



      }),



    });



    renderJudgeResult(result.judge);



    if (record && result.dashboard) {



      render(result.dashboard);



      if (result.judge.ok && result.judge.passed) {



        try {



          localStorage.removeItem(draftKey(state.problem.id));



        } catch (_) {}



        const next = result.dashboard.recommendation;



        const nextExercise = result.dashboard.exercises.find((x) => x.id === next.exercise_id);



        if (nextExercise && nextExercise.auto_judge && nextExercise.id !== state.problem.id) {



          setJudgeStatus("PASS · sang bài " + nextExercise.id, "pass");



          await new Promise((resolve) => setTimeout(resolve, 650));



          await openExercise(nextExercise.id);



        } else {



          appendNextAction(result.dashboard);



        }



      }



    }



  } catch (error) {



    $("judgeResults").innerHTML =



      '<div class="judge-summary fail">' + escapeHtml(error.message) + "</div>";



    setJudgeStatus("Lỗi chấm", "fail");



  } finally {



    $("runTests").disabled = false;



    $("submitCode").disabled = false;



  }



}



async function showHint() {



  if (!state.problem) return;



  try {



    const data = await api("/api/hint/" + state.problem.id);



    state.hintUsed = true;



    $("hintText").textContent = data.hint;



    $("hintText").hidden = false;



    $("showHint").textContent = "Đã mở gợi ý";



  } catch (error) {



    $("hintText").textContent = error.message;



    $("hintText").hidden = false;



  }



}



$("videoForm").addEventListener("submit", async (event) => {



  event.preventDefault();



  try {



    $("videoMessage").textContent = "Đang lưu…";



    const result = await api("/api/video", {



      method: "POST",



      body: JSON.stringify({



        number: $("videoNumber").value,



        title: $("videoTitle").value.trim(),



        percent: Number($("videoPercent").value || 0),



      }),



    });



    render(result.dashboard);



    $("videoMessage").textContent = "Đã cập nhật.";



  } catch (error) {



    $("videoMessage").textContent = error.message;



  }



});



$("useRecommendation").addEventListener("click", () => {

  const button = $("useRecommendation");

  if (button.dataset.autoJudge === "1") {

    openExercise(Number(button.dataset.exerciseId));

  } else if (button.dataset.sourceUrl) {

    openSourceExercise(Number(button.dataset.exerciseId), button.dataset.sourceUrl);

  }

});

$("exerciseList").addEventListener("click", (event) => {

  const button = event.target.closest("[data-pick]");

  if (!button) return;

  if (button.dataset.autoJudge === "1") {

    openExercise(Number(button.dataset.pick));

  } else if (button.dataset.sourceUrl) {

    openSourceExercise(Number(button.dataset.pick), button.dataset.sourceUrl);

  }

});

$("sourceConfirm").addEventListener("change", () => {
  $("sourceRecordAC").disabled = !$("sourceConfirm").checked;
});
$("sourceRecordAC").addEventListener("click", saveSourceAC);
$("sourceClose").addEventListener("click", () => {
  state.sourceExerciseId = null;
  $("sourceProgress").hidden = true;
  $("sourceConfirm").checked = false;
});
$("closeExercise").addEventListener("click", closeExercise);



$("exerciseModal").addEventListener("click", (event) => {



  if (event.target === $("exerciseModal")) closeExercise();



});



$("runTests").addEventListener("click", () => judgeCurrent(false));



$("submitCode").addEventListener("click", () => judgeCurrent(true));



$("showHint").addEventListener("click", showHint);



$("codeEditor").addEventListener("input", () => { saveDraft(); updateEditorChrome(); });

$("codeEditor").addEventListener("scroll", () => { $("lineNumbers").scrollTop = $("codeEditor").scrollTop; });

$("codeEditor").addEventListener("click", updateEditorChrome);

$("codeEditor").addEventListener("keyup", updateEditorChrome);

$("formatCode").addEventListener("click", formatCppCode);



document.addEventListener("keydown", (event) => {

  const modalOpen = !$("exerciseModal").hidden;

  const inEditor = document.activeElement === $("codeEditor");

  if (event.key === "Escape" && modalOpen) { closeExercise(); return; }

  if (event.ctrlKey && event.key === "Enter" && modalOpen) {

    event.preventDefault(); judgeCurrent(event.shiftKey); return;

  }

  if (event.shiftKey && event.altKey && event.key.toLowerCase() === "f" && modalOpen) {

    event.preventDefault(); formatCppCode(); return;

  }

  if (!inEditor) return;

  if (event.ctrlKey && event.key === "/") { event.preventDefault(); toggleLineComment(); return; }

  if (event.ctrlKey && event.key.toLowerCase() === "s") {

    event.preventDefault(); saveDraft(); setJudgeStatus("Đã lưu nháp"); return;

  }

  if (event.key === "Tab") {

    event.preventDefault();

    if ($("codeEditor").selectionStart !== $("codeEditor").selectionEnd) indentSelection(event.shiftKey);

    else if (event.shiftKey) indentSelection(true);

    else replaceEditorRange($("codeEditor").selectionStart, $("codeEditor").selectionEnd, EDITOR_INDENT);

    return;

  }

  if (event.key === "Enter") { handleEditorEnter(event); return; }

  if (event.key === "Backspace" && handleSmartBackspace(event)) return;

  handleEditorPair(event);

});



["searchInput", "topicFilter", "statusFilter"].forEach((id) => {



  $(id).addEventListener(id === "searchInput" ? "input" : "change", () => {



    if (state.dashboard) renderExercises(state.dashboard);



  });



});



initTheme();



loadDashboard();



setInterval(loadDashboard, 30000);



