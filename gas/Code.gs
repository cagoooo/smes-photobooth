/**
 * 石門國小 AI 智慧拍貼機 — Google Apps Script 後端
 * ====================================================
 * doPost：收前端 base64 照片 → 存 Google 雲端硬碟 → 設公開檢視 → 回傳直連網址（給前端產 QR）
 * doGet ?action=list：給「即時相片牆」拉最新照片清單（最新優先）
 * 防濫用：輕量 token + 全站限流 + 檔案大小/型別上限（因 /exec 公開，避免被陌生人灌爆雲端硬碟）
 *
 * 部署：右上「部署 → 管理部署作業 → 編輯 → 新版本」，或用 clasp（見 skill gas-clasp-update-deploy）。
 */

// ====== 設定 ======
var CONFIG = {
  FOLDER_ID: "",                         // 指定資料夾 ID；留空=自動建立
  FOLDER_NAME: "石門國小拍貼機",
  UPLOAD_TOKEN: "smes-pb-7n3x9q2",       // 前端上傳要帶的 token（擋亂槍掃描的 bot；非加密級，真正上限靠限流）
  RATE_MAX: 40,                          // 每個時間窗全站最多上傳數
  RATE_WINDOW_SEC: 60,                   // 限流時間窗（秒）→ 40 張/分鐘，正常拍貼夠用、可擋洪水
  MAX_BYTES: 8 * 1024 * 1024,            // 單張上限 8MB
  LIST_MAX: 80,                          // 相片牆一次最多回傳張數
};

// ====== 接收上傳（前端用 text/plain 送 JSON，避免 CORS preflight）======
function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);

    // 防濫用 1：token
    if (CONFIG.UPLOAD_TOKEN && body.token !== CONFIG.UPLOAD_TOKEN) {
      return json({ ok: false, error: "unauthorized" });
    }
    // 防濫用 2：全站限流（CacheService 滾動時間窗）
    if (!checkRate()) {
      return json({ ok: false, error: "rate_limited", message: "上傳太頻繁，請稍候再試" });
    }

    var dataUrl = body.image || "";
    var filename = body.filename || ("石門拍貼_" + nowStamp() + ".jpg");
    var m = dataUrl.match(/^data:(image\/[a-zA-Z+]+);base64,(.*)$/);
    if (!m) return json({ ok: false, error: "影像格式錯誤（需 data URL）" });

    // 防濫用 3：大小上限（base64 長度約 = bytes / 0.75）
    if (m[2].length * 0.75 > CONFIG.MAX_BYTES) {
      return json({ ok: false, error: "too_large", message: "檔案過大" });
    }

    var blob = Utilities.newBlob(Utilities.base64Decode(m[2]), m[1], filename);
    var file = getFolder().createFile(blob);
    try {
      file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    } catch (shareErr) { /* 網域政策限制公開分享時，照片仍存得進去 */ }

    var id = file.getId();
    return json({
      ok: true,
      id: id,
      downloadUrl: "https://lh3.googleusercontent.com/d/" + id,
      url: "https://drive.google.com/uc?export=view&id=" + id,
      viewUrl: "https://drive.google.com/file/d/" + id + "/view",
    });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

// 全站限流：同一時間窗 bucket 計數，超過上限即擋
function checkRate() {
  try {
    var cache = CacheService.getScriptCache();
    var key = "rate_" + Math.floor(Date.now() / 1000 / CONFIG.RATE_WINDOW_SEC);
    var n = parseInt(cache.get(key) || "0", 10);
    if (n >= CONFIG.RATE_MAX) return false;
    cache.put(key, String(n + 1), CONFIG.RATE_WINDOW_SEC * 2);
    return true;
  } catch (e) {
    return true; // cache 故障不擋正常使用
  }
}

// ====== 相片牆清單 / 狀態頁 ======
function doGet(e) {
  if (e && e.parameter && e.parameter.action === "list") return listPhotos(e);

  var folder = getFolder();
  var html = "<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>" +
    "<style>body{font-family:sans-serif;text-align:center;padding:50px;color:#3a2a18;background:#fff7ec}" +
    "h1{font-size:22px}code{background:#ffe7d0;padding:2px 6px;border-radius:6px;word-break:break-all}</style></head><body>" +
    "<h1>📸 石門國小拍貼機後端運作中</h1>" +
    "<p>照片資料夾：<b>" + folder.getName() + "</b></p>" +
    "<p>相片牆清單：<code>?action=list&n=40</code></p>" +
    "<p style='color:#7a6650;font-size:13px'>桃園市龍潭區石門國民小學 · Made with ❤️ by 阿凱老師</p>" +
    "</body></html>";
  return HtmlService.createHtmlOutput(html);
}

// 回傳最新照片清單（最新優先）給即時相片牆
function listPhotos(e) {
  try {
    var n = Math.min(parseInt((e.parameter && e.parameter.n) || "40", 10) || 40, CONFIG.LIST_MAX);
    var it = getFolder().getFiles(), arr = [];
    while (it.hasNext()) {
      var f = it.next();
      if (f.getMimeType().indexOf("image/") !== 0) continue;
      arr.push({ id: f.getId(), name: f.getName(), t: f.getDateCreated().getTime() });
    }
    arr.sort(function (a, b) { return b.t - a.t; });          // 最新優先
    arr = arr.slice(0, n).map(function (x) {
      return { id: x.id, name: x.name, t: x.t, url: "https://lh3.googleusercontent.com/d/" + x.id };
    });
    return json({ ok: true, count: arr.length, photos: arr });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

// ====== 工具 ======
function getFolder() {
  if (CONFIG.FOLDER_ID) {
    try { return DriveApp.getFolderById(CONFIG.FOLDER_ID); } catch (e) {}
  }
  var it = DriveApp.getFoldersByName(CONFIG.FOLDER_NAME);
  return it.hasNext() ? it.next() : DriveApp.createFolder(CONFIG.FOLDER_NAME);
}
function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
function nowStamp() {
  return Utilities.formatDate(new Date(), Session.getScriptTimeZone() || "Asia/Taipei", "yyyyMMdd_HHmmss");
}
