/* 石門國小 AI 拍貼機 — Service Worker
   - 版本鎖 prompt-to-refresh：偵測新版 → 進 waiting → 前端跳「重新整理」通知
   - 只攔同源 GET（index.html / frames）；相機、MediaPipe/QR 的 CDN、跨域 GAS 上傳一律不碰
*/
const BUILD_VERSION = '2026.06.15-4';            // 每次部署改它（或跑 scripts/bump-version.ps1）
const CACHE = 'photobooth-' + BUILD_VERSION;
const PRECACHE = [
  './', './index.html', './wall.html',
  './frames/frame_graduation.png', './frames/frame_anniversary.png',
  './frames/frame_sports.png', './frames/frame_ocean.png',
  './frames/frame_fishmascot.png', './frames/frame_festival.png',
  './favicon.ico', './favicon.svg', './apple-touch-icon.png',
  './manifest.json', './icon-192.png', './icon-512.png',
  './icon-192-maskable.png', './icon-512-maskable.png',
  './og-preview.png'
];

self.addEventListener('install', (e) => {
  // 鐵則 A：不自動 skipWaiting → 留 waiting 狀態，由使用者在通知列決定何時套用
  e.waitUntil(caches.open(CACHE).then((c) =>
    Promise.allSettled(PRECACHE.map((u) => c.add(u).catch(() => {})))));
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k.startsWith('photobooth-') && k !== CACHE)
      .map((k) => caches.delete(k)));
    await self.clients.claim();
    (await self.clients.matchAll({ type: 'window' }))
      .forEach((c) => c.postMessage({ type: 'SW_ACTIVATED', version: BUILD_VERSION }));
  })());
});

self.addEventListener('message', (e) => {
  if (e.data && e.data.type === 'SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;                 // 上傳 GAS 是 POST → 不碰
  let url; try { url = new URL(req.url); } catch { return; }
  if (url.origin !== self.location.origin) return;  // MediaPipe / QR / GAS 等 CDN → 不碰

  if (url.pathname.endsWith('version.json')) {       // 版本檔永遠拿最新
    e.respondWith(fetch(req).catch(() => caches.match(req))); return;
  }
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {
    e.respondWith(fetch(req).then((res) => {         // HTML network-first（部署即拿新版）
      const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); return res;
    }).catch(() => caches.match(req).then((r) => r || caches.match('./index.html')))); return;
  }
  e.respondWith(caches.match(req).then((cached) => { // 邊框等資源 cache-first + 背景更新
    const net = fetch(req).then((res) => {
      if (res && res.status === 200 && res.type === 'basic') {
        const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy));
      } return res;
    }).catch(() => cached);
    return cached || net;
  }));
});
