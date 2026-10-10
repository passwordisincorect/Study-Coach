const SERVER = "http://127.0.0.1:8780";

async function sendProgress(data) {
  try {
    const response = await fetch(SERVER + "/api/video", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        number: data.number,
        title: data.title,
        percent: data.percent
      })
    });
    if (!response.ok) throw new Error("HTTP " + response.status);
    await chrome.storage.local.set({
      lastSync: {
        ok: true,
        at: Date.now(),
        number: data.number,
        title: data.title,
        percent: data.percent
      }
    });
  } catch (err) {
    await chrome.storage.local.set({
      lastSync: { ok: false, at: Date.now(), error: String(err.message || err) }
    });
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message && message.type === "studyCoachProgress") {
    sendProgress(message.data).then(() => sendResponse({ ok: true }));
    return true;
  }
});