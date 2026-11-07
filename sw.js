// Offline cache: the page itself is network-first (so updates show at once), pictures are cache-first.
var C = 'adr-c55d96f036';
var FILES = ['./', 'index.html'].concat(["img/v101_0.jpg", "img/v102_0.jpg", "img/v103_0.jpg", "img/v104_0.jpg", "img/v105_0.jpg", "img/v106_0.jpg", "img/v107_0.jpg", "img/v108_0.jpg", "img/v109_0.jpg", "img/v110_0.jpg", "img/v111_0.jpg", "img/v112_0.jpg", "img/v113_0.jpg", "img/v114_0.jpg", "img/v115_0.jpg", "img/v116_0.jpg", "img/v117_0.jpg", "img/v118_0.jpg", "img/v119_0.jpg", "img/v120_0.jpg", "img/v121_0.jpg", "img/v122_0.jpg", "img/v123_0.jpg", "img/v124_0.jpg", "img/v125_0.jpg", "img/v126_0.jpg", "img/v127_0.jpg", "img/v128_0.jpg", "img/v129_0.jpg", "img/v130_0.jpg", "img/v131_0.jpg", "img/v132_0.jpg", "img/v133_0.jpg", "img/v134_0.jpg", "img/v135_0.jpg", "img/v136_0.jpg", "img/v137_0.jpg", "img/v138_0.jpg", "img/v139_0.jpg", "img/v140_0.jpg", "img/v141_0.jpg", "img/v142_0.jpg", "img/v143_0.jpg", "img/v144_0.jpg", "img/v145_0.jpg", "img/v146_0.jpg", "img/v147_0.jpg", "img/v148_0.jpg", "img/v149_0.jpg", "img/v150_0.jpg", "img/v151_0.jpg", "img/v152_0.jpg", "img/v153_0.jpg", "img/v154_0.jpg", "img/v155_0.jpg", "img/v156_0.jpg", "img/v157_0.jpg", "img/v158_0.jpg", "img/v159_0.jpg", "img/v160_0.jpg", "img/v161_0.jpg", "img/v162_0.jpg", "img/v163_0.jpg", "img/v164_0.jpg", "img/v165_0.jpg", "img/v166_0.jpg", "img/v167_0.jpg", "img/v168_0.jpg", "img/v169_0.jpg", "img/v170_0.jpg", "img/v171_0.jpg", "img/v172_0.jpg", "img/v173_0.jpg", "img/v174_0.jpg", "img/v175_0.jpg", "img/v176_0.jpg", "img/v177_0.jpg", "img/v178_0.jpg", "img/v179_0.jpg", "img/v180_0.jpg", "img/v181_0.jpg", "img/v182_0.jpg", "img/v183_0.jpg", "img/v184_0.jpg", "img/v185_0.jpg", "img/v186_0.jpg", "img/v187_0.jpg", "img/v188_0.jpg", "img/v189_0.jpg", "img/v190_0.jpg", "img/v191_0.jpg", "img/v192_0.jpg", "img/v193_0.jpg", "img/v194_0.jpg", "img/v195_0.jpg", "img/v196_0.jpg", "img/v197_0.jpg", "img/v198_0.jpg", "img/v259_0.jpg", "img/v261_0.jpg", "img/v262_0.jpg", "img/v263_0.jpg", "img/v267_0.jpg", "img/v269_0.jpg", "img/v270_0.jpg", "img/v271_0.jpg", "img/v272_0.jpg", "img/v273_0.jpg"]);
self.addEventListener('install', function (e) {
  self.skipWaiting();
  e.waitUntil(caches.open(C).then(function (c) { return c.addAll(FILES); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== C; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var r = e.request;
  if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  if (r.mode === 'navigate' || /\/$|index\.html$/.test(new URL(r.url).pathname)) {
    e.respondWith(fetch(r).then(function (res) {
      var copy = res.clone(); caches.open(C).then(function (c) { c.put(r, copy); }); return res;
    }).catch(function () { return caches.match(r).then(function (m) { return m || caches.match('index.html'); }); }));
    return;
  }
  e.respondWith(caches.match(r).then(function (m) { return m || fetch(r); }));
});
