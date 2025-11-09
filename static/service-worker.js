const CACHE_NAME = 'farmer-market-v1';
const DATA_CACHE_NAME = 'farmer-market-data-v1';

// Static assets to cache immediately
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png'
];

// API endpoints to cache for offline access
const apiCachePatterns = [
  /api\.openweathermap\.org/,
  /agmarknet\.gov\.in/,
  /data\.gov\.in/
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
  self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Handle API requests with network-first, fallback to cache
  if (apiCachePatterns.some(pattern => pattern.test(request.url))) {
    event.respondWith(
      caches.open(DATA_CACHE_NAME).then((cache) => {
        return fetch(request)
          .then((response) => {
            // Cache successful API responses
            if (response.status === 200) {
              cache.put(request, response.clone());
            }
            return response;
          })
          .catch(() => {
            // Return cached data if offline
            return cache.match(request).then((cachedResponse) => {
              if (cachedResponse) {
                return cachedResponse;
              }
              // Return offline fallback
              return new Response(
                JSON.stringify({ 
                  offline: true, 
                  message: 'Offline data - may be outdated',
                  cached: true 
                }),
                { headers: { 'Content-Type': 'application/json' } }
              );
            });
          });
      })
    );
    return;
  }
  
  // Handle static assets with cache-first strategy
  event.respondWith(
    caches.match(request)
      .then((response) => {
        if (response) {
          return response;
        }
        return fetch(request).then((response) => {
          if (!response || response.status !== 200) {
            return response;
          }
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(request, responseToCache);
            });
          return response;
        }).catch(() => {
          // Return offline page for navigation requests
          if (request.mode === 'navigate') {
            return caches.match('/').then((response) => {
              return response || new Response('Offline');
            });
          }
        });
      })
  );
});

self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Push notification support
self.addEventListener('push', (event) => {
  const options = {
    icon: '/static/icon-192.png',
    badge: '/static/icon-192.png',
    vibrate: [200, 100, 200],
    requireInteraction: false
  };

  let notificationData = {
    title: 'Smart Farmer Marketplace',
    body: 'You have a new notification',
    ...options
  };

  if (event.data) {
    try {
      const data = event.data.json();
      notificationData = {
        title: data.title || notificationData.title,
        body: data.body || notificationData.body,
        icon: data.icon || options.icon,
        badge: data.badge || options.badge,
        data: data.data || {},
        tag: data.tag || 'default',
        ...options
      };
    } catch (e) {
      notificationData.body = event.data.text();
    }
  }

  event.waitUntil(
    self.registration.showNotification(notificationData.title, notificationData)
  );
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // If a window is already open, focus it
        for (let client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            return client.focus();
          }
        }
        // Otherwise open a new window
        if (clients.openWindow) {
          return clients.openWindow('/');
        }
      })
  );
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-data') {
    event.waitUntil(syncOfflineData());
  }
});

async function syncOfflineData() {
  // Sync logic would be implemented here
  console.log('Background sync triggered');
}
