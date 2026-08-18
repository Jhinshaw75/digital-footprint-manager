const CACHE_NAME = 'safeguard-v1';
const assetsToCache = [
  './index.html',
  './elder-affairs-logo.png',
  './senior-shield-badge.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      cache.addAll(assetsToCache);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
