const $ = (id) => document.getElementById(id);
let currentPlaylistId = null;

function parseYoutube(urlText) {
  try {
    const url = new URL(urlText);
    if (!/(^|\.)youtube\.com$/i.test(url.hostname)) return null;
    const playlistId = url.searchParams.get("list");
    const index = Number(url.searchParams.get("index") || "0");
    if (!playlistId) return null;
    return { playlistId, index };
  } catch {
    return null;
  }
}

async function refresh() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const info = tab && tab.url ? parseYoutube(tab.url) : null;
  const stored = await chrome.storage.local.get(["coursePlaylistId", "lastSync"]);

  $("pageTitle").textContent = tab ? (tab.title || "YouTube") : "Không có tab";
  if (info) {
    currentPlaylistId = info.playlistId;
    $("pageInfo").innerHTML =
      "Playlist: <code>" + info.playlistId + "</code><br>Video #" + (info.index || "?") +
      (stored.coursePlaylistId === info.playlistId ? "<br><b>Đang theo dõi</b>" : "");
    $("track").disabled = false;
  } else {
    currentPlaylistId = null;
    $("pageInfo").textContent = "Hãy mở một video nằm trong playlist YouTube.";
    $("track").disabled = true;
  }

  if (stored.lastSync) {
    const s = stored.lastSync;
    $("sync").className = "status " + (s.ok ? "ok" : "bad");
    $("sync").textContent = s.ok
      ? ("Video #" + s.number + " · " + s.percent + "% · " + s.title)
      : ("Lỗi: " + (s.error || "không rõ"));
  }
}

$("track").addEventListener("click", async () => {
  if (!currentPlaylistId) return;
  await chrome.storage.local.set({ coursePlaylistId: currentPlaylistId });
  $("message").className = "status ok";
  $("message").textContent = "Đã bật theo dõi playlist này.";
  refresh();
});

$("stop").addEventListener("click", async () => {
  await chrome.storage.local.remove(["coursePlaylistId"]);
  $("message").className = "status";
  $("message").textContent = "Đã ngừng theo dõi.";
  refresh();
});

refresh();