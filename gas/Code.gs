/**
 * 石門國小 AI 智慧拍貼機 — Google Apps Script 後端
 * ====================================================
 * 功能：接收前端拍貼機 POST 上來的照片（base64）→ 存進 Google 雲端硬碟
 *      → 設成「知道連結的任何人可檢視」→ 回傳「可直接存取的圖片網址」給前端產 QR Code。
 *
 * 部署步驟（詳見 ../README.md）：
 *   1. https://script.google.com → 新增專案，把本檔內容整段貼上
 *   2.（可選）填 FOLDER_ID 指定相簿資料夾；留空會自動建一個「石門國小拍貼機」資料夾
 *   3. 右上「部署」→「新增部署作業」→ 類型選「網頁應用程式」
 *      - 執行身分：我自己
 *      - 具有存取權的使用者：「任何人」(Anyone)   ← 一定要選這個，前端才連得上
 *   4. 複製產生的 /exec 網址 → 貼到拍貼機網頁右上「⚙️ 設定」
 */

// ====== 設定 ======
var CONFIG = {
  FOLDER_ID: "",                       // 指定資料夾 ID（雲端硬碟網址 /folders/ 後那串）；留空=自動建立
  FOLDER_NAME: "石門國小拍貼機",        // 自動建立時的資料夾名稱
};

// ====== 接收上傳（前端用 text/plain 送 JSON，避免 CORS preflight）======
function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    var dataUrl = body.image || "";
    var filename = body.filename || ("石門拍貼_" + nowStamp() + ".jpg");

    // 去掉 "data:image/jpeg;base64," 前綴，解碼成圖片
    var m = dataUrl.match(/^data:(image\/[a-zA-Z+]+);base64,(.*)$/);
    if (!m) return json({ ok: false, error: "影像格式錯誤（需 data URL）" });
    var contentType = m[1];
    var bytes = Utilities.base64Decode(m[2]);
    var blob = Utilities.newBlob(bytes, contentType, filename);

    // 存進資料夾
    var folder = getFolder();
    var file = folder.createFile(blob);

    // 設「知道連結的任何人可檢視」→ 直連網址才開得了
    try {
      file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    } catch (shareErr) {
      // 部分網域政策限制公開分享時，照片仍存得進去，只是連結需登入
    }

    var id = file.getId();
    return json({
      ok: true,
      id: id,
      downloadUrl: "https://lh3.googleusercontent.com/d/" + id,   // 手機可直接看圖（最穩）
      url: "https://drive.google.com/uc?export=view&id=" + id,    // 備用直連
      viewUrl: "https://drive.google.com/file/d/" + id + "/view", // 雲端硬碟預覽頁
    });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

// ====== 瀏覽器直接打開 /exec 時顯示狀態頁 ======
function doGet() {
  var folder = getFolder();
  var html = "<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>" +
    "<style>body{font-family:sans-serif;text-align:center;padding:50px;color:#3a2a18;background:#fff7ec}" +
    "h1{font-size:22px}code{background:#ffe7d0;padding:2px 6px;border-radius:6px;word-break:break-all}</style></head><body>" +
    "<h1>📸 石門國小拍貼機後端運作中</h1>" +
    "<p>照片資料夾：<b>" + folder.getName() + "</b></p>" +
    "<p>請把本頁的 <code>/exec</code> 網址，貼到拍貼機網頁右上「⚙️ 設定」。</p>" +
    "<p style='color:#7a6650;font-size:13px'>桃園市龍潭區石門國民小學 · Made with ❤️ by 阿凱老師</p>" +
    "</body></html>";
  return HtmlService.createHtmlOutput(html);
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
