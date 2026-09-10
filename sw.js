/* Cadence service worker.

   Present mostly to satisfy install criteria: everything the app knows lives in
   localStorage, so offline already worked after first load. Bump VERSION when
   the shell changes; the fetch handler also revalidates in the background, so a
   deploy lands on the second launch even if the bump is forgotten. */
"use strict";

var VERSION = "cadence-v1";
var ASSETS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/maskable-192.png",
  "./icons/maskable-512.png",
  "./icons/apple-touch-icon.png"
];

self.addEventListener("install", function(e){
  e.waitUntil(
    caches.open(VERSION)
      .then(function(c){ return c.addAll(ASSETS); })
      .then(function(){ return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function(e){
  e.waitUntil(
    caches.keys()
      .then(function(keys){
        return Promise.all(keys.map(function(k){
          return k === VERSION ? null : caches.delete(k);
        }));
      })
      .then(function(){ return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function(e){
  var req = e.request;
  if (req.method !== "GET") return;
  if (new URL(req.url).origin !== self.location.origin) return;

  // Navigations always resolve to the one page, so a deep link still opens it.
  var key = req.mode === "navigate" ? "./index.html" : req;

  e.respondWith(
    caches.open(VERSION).then(function(cache){
      return cache.match(key).then(function(hit){
        var net = fetch(req).then(function(res){
          if (res && res.ok) cache.put(key, res.clone());
          return res;
        }).catch(function(){
          return hit || Response.error();
        });
        return hit || net;   // cache-first; the fetch above refreshes it behind us
      });
    })
  );
});
