const CACHE_NAME = 'map-miner-v1';
const ASSETS = [
  '/',
  '/static/style.css',
  '/static/app.js',
  '/static/map_miner_logo.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
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
