# 📸 石門國小 AI 智慧拍貼機

> 桃園市龍潭區石門國民小學 · 鱻魚特色學園
>
> 一台「土炮」智慧拍貼機：**手勢張開手掌就倒數自拍**、可換主題邊框、拍完**自動上傳 Google 雲端硬碟**、手機**掃 QR Code 立刻下載照片**。純前端 HTML + Google Apps Script，全程免費，適合畢業典禮、校慶、成果發表會、節慶活動。

---

## ✨ 功能

| 功能 | 說明 |
|---|---|
| 📷 即時相機預覽 | 自動鏡像（像照鏡子），支援切換鏡頭 |
| 🖼️ 可換拍貼邊框 | 中央真透明、四周裝飾外框；附 6 款主題框（畢業快樂／歡慶校慶／運動會／鱻魚特色學園／鱻魚吉祥／歡樂佳節），可自行替換 |
| ⏱️ 倒數自拍 | 立即 / 3 / 5 / 10 秒，含倒數大數字 + 提示音 + 白閃快門 |
| ✋ 手勢自拍 | 對鏡頭張開手掌約 1 秒自動倒數（MediaPipe Hands，免安裝） |
| ☁️ 雲端上傳 | 拍完一鍵上傳到學校 Google 雲端硬碟 |
| 📱 QR Code 下載 | 上傳後產生 QR，手機掃描即可看圖、長按存檔 |
| 💾 本機儲存 | 也能直接把照片存到電腦 |
| 🔳 四格拍貼 | 連拍 4 張自動拼成經典四格拍貼（單張 / 四格可切換） |
| 🖼️ 即時相片牆 | 投影頁 [`wall.html`](wall.html)，拍完即上大螢幕、最新優先、附掃碼拍貼 QR |
| 🔒 防濫用 | 上傳需 token + 全站限流（40 張/分）+ 檔案大小上限，避免 `/exec` 被灌爆雲端硬碟 |
| 🔄 自動更新通知 | 部署新版後，已開著的平板會跳「重新整理載入」通知，不會卡舊版（Service Worker） |

---

## 🗂️ 專案結構

```
Photo/
├─ index.html              # 拍貼機網頁（前端，全部功能都在這）
├─ frames/                 # 透明邊框 PNG（中央挖空給相機入鏡）
│   ├─ frame_graduation.png
│   └─ frame_ocean.png
├─ gas/Code.gs             # Google Apps Script 後端（存雲端硬碟 + 回傳直連網址）
├─ tools/make_frames.py    # 邊框產生器（要改字、配色、重產時用）
└─ README.md
```

---

## 🚀 快速開始

### 1. 本機測試

相機需要 **https 或 localhost**（`file://` 直接開檔不給相機權限）。在專案資料夾開一個本機伺服器：

```bash
python -m http.server 5180
```

瀏覽器開 `http://localhost:5180`，允許相機權限即可試拍（此時雲端上傳還沒接，可先用「💾 存到本機」）。

### 2. 部署雲端後端（GAS）— 開啟「上傳 + QR」

> 教學專案請用學校帳號 **ipad@mail2.smes.tyc.edu.tw** 操作。

1. 到 [script.google.com](https://script.google.com) → **新增專案**
2. 把 [`gas/Code.gs`](gas/Code.gs) 內容整段貼進去，存檔
3. （可選）把 `CONFIG.FOLDER_ID` 填成你要存照片的資料夾 ID；留空會自動建一個「石門國小拍貼機」資料夾
4. 右上 **部署 → 新增部署作業**
   - 類型：**網頁應用程式**
   - 執行身分：**我自己**
   - 具有存取權的使用者：**任何人 (Anyone)** ← 一定要選，前端才連得上
5. 第一次部署會要求**授權**（同意存取你的雲端硬碟）
6. 複製產生的 **`/exec` 網址**

> ⚠️ 改完 `Code.gs` 後要「**管理部署作業 → 編輯 → 版本選新版本**」重新部署，新版才會生效。

### 3. 把後端網址接進拍貼機

> ✅ 本專案的 `index.html` 已**內建預設 `/exec` 網址**（最上方 `CONFIG.gasUrl`），任何裝置打開
> https://cagoooo.github.io/smes-photobooth/ **即可直接上傳，不必設定**。

只有在你要接「**自己的**」後端時才需要：打開網頁 → 右上 **⚙️ 設定** → 貼上你自己的 `/exec` 網址 →
**儲存**（存在該裝置瀏覽器、會覆蓋預設值）。改後端程式不必動這裡——clasp `update-deployment` 會保留同一網址。

### 4. 部署上線（GitHub Pages）

把整個資料夾推到 GitHub repo，啟用 **Settings → Pages**（branch = `main`、資料夾 = `/root`）。
GitHub Pages 是 https，相機與 MediaPipe 手勢都能正常運作。

---

## 🖼️ 換邊框

**方法 A（最快）**：把你的透明 PNG 放進 `frames/`，再到 `index.html` 最上方 `CONFIG.frames` 補一行：

```js
frames: [
  { src: "frames/frame_graduation.png", name: "畢業快樂" },
  { src: "frames/frame_ocean.png",      name: "鱻魚學園" },
  { src: "frames/你的新框.png",          name: "顯示名稱" },   // ← 新增這行
  { src: "",                            name: "無邊框"   },
],
```

> 邊框是**中央透明**的 PNG：透明處顯示相機畫面，不透明處是裝飾外框。建議尺寸 1080×1440（3:4 直版）。

**方法 B（改範例框的字/配色）**：編輯 `tools/make_frames.py` 後重產：

```bash
python tools/make_frames.py     # Windows 若終端亂碼：PYTHONIOENCODING=utf-8 python tools/make_frames.py
```

---

## 🖼️ 即時相片牆（投影用）

活動現場用單槍投影打開 👉 https://cagoooo.github.io/smes-photobooth/wall.html

- 每 15 秒自動抓最新照片、**最新優先**，新照片動畫進場
- 右上 ⛶ 全螢幕；右下 QR 讓觀眾掃碼直接去拍貼
- 資料來自後端 `?action=list`（唯讀，照片本就是公開連結）

## 🔒 防濫用（已內建）

因為 `/exec` 公開，後端 `Code.gs` 已內建三層保護：**上傳需 token**（前端 `CONFIG.uploadToken` 與後端 `CONFIG.UPLOAD_TOKEN` 一致）＋**全站限流**（預設 40 張/分鐘）＋**檔案大小上限**（8MB）。
想更嚴格可改 `Code.gs` 的 `RATE_MAX` / `RATE_WINDOW_SEC`，或日後加 Cloudflare Turnstile 人機驗證（見 skill `cloudflare-turnstile-integration`）。

## 🔄 更新網站內容（推新版）

改完任何檔案（`index.html`、邊框…）後，**升版號**讓已開著的裝置自動跳「重新整理載入」通知：

```powershell
powershell -File scripts/bump-version.ps1 -Notes "這次改了什麼"   # 同步 version.json / sw.js / index.html 三處版本號
git add -A; git commit -m "更新說明"; git push
```

> 原理：Service Worker 偵測到 `sw.js` 的版本號（byte）改變 → 安裝新版 → 提示使用者重新整理。
> **沒升版號，通知不會出現**（瀏覽器當成同一版）。GitHub Pages 對 `sw.js` 有約 10 分鐘 CDN 快取，剛部署的前 10 分鐘可能還偵測不到，屬正常窗口。
>
> 改「後端」(`gas/Code.gs`) 不必升版——那是用 clasp 部署、跟前端版本無關。

## 🧯 疑難排解

| 症狀 | 原因 / 解法 |
|---|---|
| 無法開啟相機 | 網址不是 https/localhost，或瀏覽器沒給權限。改用 localhost 或 GitHub Pages |
| 上傳失敗 / CORS 錯誤 | GAS 沒部署成「任何人可存取」，或網址不是 `/exec` 結尾。重新部署並確認權限 |
| 改了 Code.gs 沒效果 | GAS 要「管理部署作業 → 編輯 → 新版本」重新部署 |
| 手機掃 QR 看不到圖 | 照片未設成公開。`Code.gs` 已自動設「知道連結的人可檢視」；若學校網域禁止公開分享，需請管理員放寬，或改存個人雲端硬碟 |
| 手勢沒反應 | 手勢功能需連網載入模型；張開**整個手掌**正對鏡頭、停約 1 秒 |
| 邊框中央不透明 | 該 PNG 中央沒挖空。用 `make_frames.py` 重產，或確認 PNG 有 alpha 透明 |

---

## 🔐 隱私與安全

- 照片存進**你自己**授權的 Google 雲端硬碟，前端不經過任何第三方伺服器。
- 上傳的照片預設為「知道連結的人可檢視」（QR 才能下載）。活動結束後可整個資料夾刪除或改回私人。
- 建議活動現場張貼告示，告知會拍照上傳，尊重師生肖像權。

---

Made with ❤️ by [阿凱老師](https://www.smes.tyc.edu.tw/modules/tadnews/page.php?ncsn=11&nsn=16#a5) · 桃園市龍潭區石門國民小學
