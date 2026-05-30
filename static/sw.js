/**
 * RoadSoS — Service Worker
 * ────────────────────────
 *  Strategy:
 *    1. PRECACHE — the offline emergency page + its data + icons.
 *       Cached on install, available immediately even on first visit.
 *    2. NETWORK-FIRST for navigation requests — try the live Streamlit
 *       app; if the network fails, fall back to the cached emergency page.
 *    3. CACHE-FIRST for static assets (icons, manifest, contacts JSON) —
 *       cheap and reliable; updates served from network when available.
 *
 *  Bump CACHE_VERSION whenever the precached files change.
 */

const CACHE_VERSION = "roadsos-v1";
const PRECACHE_URLS = [
  "/app/static/emergency.html",
  "/app/static/contacts.json",
  "/app/static/manifest.json",
  "/app/static/icons/icon-192.png",
  "/app/static/icons/icon-512.png",
  "/app/static/icons/icon-maskable-512.png",
  "/app/static/icons/favicon.png",
];

// ── Install: precache the offline shell ──────────────────────────────────────
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_VERSION)
      .then((cache) =>
        // addAll fails atomically — use individual adds so a single 404
        // (e.g. missing icon) doesn't break the whole install.
        Promise.allSettled(
          PRECACHE_URLS.map((url) =>
            cache.add(url).catch((err) => {
              console.warn("[sw] precache miss:", url, err.message);
            })
          )
        )
      )
      .then(() => self.skipWaiting())
  );
});

// ── Activate: drop old caches ────────────────────────────────────────────────
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((names) =>
        Promise.all(
          names
            .filter((n) => n !== CACHE_VERSION)
            .map((n) => caches.delete(n))
        )
      )
      .then(() => self.clients.claim())
  );
});

// ── Fetch handler ────────────────────────────────────────────────────────────
self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Only handle GETs from our origin
  if (req.method !== "GET" || url.origin !== self.location.origin) return;

  // ── Navigation request: network-first, fall back to emergency page ────────
  // Streamlit uses websockets for interactivity; if the network is gone, the
  // app shell would load but nothing would work. So instead of caching the
  // shell, we serve our self-contained emergency page when offline.
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req).catch(() =>
        caches.match("/app/static/emergency.html").then(
          (cached) =>
            cached ||
            new Response(
              "<h1>Offline — emergency page not cached. Visit once with internet to install.</h1>",
              { headers: { "Content-Type": "text/html" } }
            )
        )
      )
    );
    return;
  }

  // ── Static asset: cache-first, update from network in background ──────────
  if (url.pathname.startsWith("/app/static/")) {
    event.respondWith(
      caches.match(req).then((cached) => {
        const fresh = fetch(req)
          .then((resp) => {
            if (resp && resp.status === 200) {
              const copy = resp.clone();
              caches.open(CACHE_VERSION).then((c) => c.put(req, copy));
            }
            return resp;
          })
          .catch(() => cached); // offline → return whatever we have
        return cached || fresh;
      })
    );
    return;
  }

  // ── Everything else: pass through (WebSocket, Streamlit XHRs, etc.) ───────
  // These all need the network — caching them would break interactivity.
});
