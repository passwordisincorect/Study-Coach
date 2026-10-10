let lastKey = "";

function cleanTitle() {
  return (document.title || "").replace(/\s*-\s*YouTube\s*$/i, "").trim();
}

function courseInfo() {
  const url = new URL(location.href);
  const playlistId = url.searchParams.get("list");
  const index = Number(url.searchParams.get("index") || "0");
  const video = document.querySelector("video");
  if (!playlistId || !video || !Number.isFinite(video.duration) || video.duration <= 0) return null;
  const percent = Math.max(0, Math.min(100, Math.round((video.currentTime / video.duration) * 100)));
  return {
    playlistId,
    number: index > 0 ? index : 1,
    title: cleanTitle(),
    percent
  };
}

async function tick() {
  const info = courseInfo();
  if (!info) return;
  const stored = await chrome.storage.local.get(["coursePlaylistId"]);
  if (!stored.coursePlaylistId || stored.coursePlaylistId !== info.playlistId) return;

  const bucket = Math.floor(info.percent / 5) * 5;
  const key = info.playlistId + "|" + info.number + "|" + bucket;
  if (key === lastKey && info.percent < 99) return;
  lastKey = key;

  chrome.runtime.sendMessage({
    type: "studyCoachProgress",
    data: { number: info.number, title: info.title, percent: info.percent }
  }).catch(() => {});
}

setInterval(tick, 15000);
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "hidden") tick();
});
window.addEventListener("beforeunload", tick);
tick();