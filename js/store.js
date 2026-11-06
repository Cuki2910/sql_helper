/* Local persistence: IndexedDB (user entries + settings), fallback to in-memory if unavailable. Nothing leaves the machine. */
(function () {
  'use strict';
  const DB = 'nw_sql_finder', V = 1;
  let db = null; const mem = { entries: new Map(), settings: new Map() };
  function open() {
    return new Promise((res) => {
      try {
        const r = indexedDB.open(DB, V);
        r.onupgradeneeded = () => { r.result.createObjectStore('entries', { keyPath: 'id' }); r.result.createObjectStore('settings'); };
        r.onsuccess = () => { db = r.result; res(true); };
        r.onerror = () => res(false); r.onblocked = () => res(false);
      } catch (e) { res(false); }
    });
  }
  const tx = (store, mode, fn) => new Promise((res, rej) => {
    const t = db.transaction(store, mode), s = t.objectStore(store); const out = fn(s);
    t.oncomplete = () => res(out && out.result !== undefined ? out.result : undefined); t.onerror = () => rej(t.error);
  });
  window.NWStore = {
    persistent: false,
    async init() { this.persistent = await open(); return this.persistent; },
    async all() { return db ? tx('entries', 'readonly', (s) => s.getAll()) : [...mem.entries.values()]; },
    async put(e) { if (db) await tx('entries', 'readwrite', (s) => s.put(e)); else mem.entries.set(e.id, e); },
    async putMany(a) { if (db) await tx('entries', 'readwrite', (s) => a.forEach((e) => s.put(e))); else a.forEach((e) => mem.entries.set(e.id, e)); },
    async del(id) { if (db) await tx('entries', 'readwrite', (s) => s.delete(id)); else mem.entries.delete(id); },
    async clear() { if (db) await tx('entries', 'readwrite', (s) => s.clear()); else mem.entries.clear(); },
    async getSetting(k) { return db ? tx('settings', 'readonly', (s) => s.get(k)) : mem.settings.get(k); },
    async setSetting(k, v) { if (db) await tx('settings', 'readwrite', (s) => s.put(v, k)); else mem.settings.set(k, v); },
  };
})();
