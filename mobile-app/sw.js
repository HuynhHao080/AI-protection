// Service Worker for AI Child Protection Mobile App
const CACHE_NAME = 'ai-protection-v1';
const urlsToCache = [
    '/mobile',
    '/mobile/',
    '/mobile/manifest.json',
    '/mobile/sw.js'
];

// Install Service Worker
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Opened cache');
                return cache.addAll(urlsToCache);
            })
            .catch((error) => {
                console.log('[SW] Cache failed:', error);
            })
    );
});

// Fetch Service Worker
self.addEventListener('fetch', (event) => {
    // Only handle GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Cache hit - return response
                if (response) {
                    console.log('[SW] Cache hit for:', event.request.url);
                    return response;
                }

                // Try to fetch from network
                return fetch(event.request).then(
                    (response) => {
                        // Check if we received a valid response
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clone the response
                        const responseToCache = response.clone();

                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                cache.put(event.request, responseToCache);
                            });

                        return response;
                    }
                ).catch((error) => {
                    console.log('[SW] Fetch failed:', error);
                    // Return offline page or error response
                    return new Response('Offline content not available', {
                        status: 503,
                        statusText: 'Service Unavailable'
                    });
                });
            })
    );
});

// Activate Service Worker
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Handle background sync (if supported)
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync:', event.tag);
    if (event.tag === 'background-sync') {
        event.waitUntil(
            // Perform background sync operations
            console.log('[SW] Performing background sync...')
        );
    }
});

// Handle push notifications (if supported)
self.addEventListener('push', (event) => {
    console.log('[SW] Push notification received');
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.body,
            icon: '/mobile/icon-192.png',
            badge: '/mobile/icon-192.png',
            data: data.url
        };

        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
    console.log('[SW] Notification clicked');
    event.notification.close();

    if (event.notification.data) {
        event.waitUntil(
            clients.openWindow(event.notification.data)
        );
    }
});
