/**
 * GF UI Overlay — gf_ui_overlay.js v3.0
 * GREENFARMS | UI Overlay Manager
 *
 * Diagnóstico:
 *   window.gfUIOverlayVersion   → "GF_UI_OVERLAY_V3"
 *   window.gfUIOverlayLoaded    → true
 *   window.gfCurrentRoute       → rota atual
 *   window.gfCurrentPageData    → dados da página ativa (inclui cards)
 */

// ── CAMADA 0: bloquear Desk ANTES de qualquer render ─────────
(function() {
  var s = document.createElement("style");
  s.id  = "gf-boot-blocker";
  s.textContent =
    "body.gf-overlay-booting .layout-main-section," +
    "body.gf-overlay-booting .desk-sidebar," +
    "body.gf-overlay-booting .standard-sidebar," +
    "body.gf-overlay-booting .page-container," +
    "body.gf-overlay-booting .layout-main," +
    "body.gf-overlay-booting #page-desktop," +
    "body.gf-overlay-booting .frappe-app{visibility:hidden!important;pointer-events:none!important}" +
    "#gf-ui-overlay-root{display:none;position:fixed;top:56px;left:0;right:0;bottom:0;z-index:900;overflow:hidden}" +
    "body.gf-overlay-active #gf-ui-overlay-root{display:flex!important;flex-direction:column}" +
    "body.gf-overlay-active .layout-main-section," +
    "body.gf-overlay-active #page-desktop," +
    "body.gf-overlay-active .desk-sidebar," +
    "body.gf-overlay-active .standard-sidebar," +
    "body.gf-overlay-active .page-container{visibility:hidden!important;pointer-events:none!important}";
  (document.head || document.documentElement).appendChild(s);
  if (document.body) document.body.classList.add("gf-overlay-booting");
  else document.addEventListener("DOMContentLoaded", function(){
    document.body.classList.add("gf-overlay-booting");
  }, {once: true});
})();

// ── DIAGNÓSTICO ───────────────────────────────────────────────
window.gfUIOverlayVersion = "GF_UI_OVERLAY_V3";
window.gfCurrentRoute     = null;
window.gfCurrentPageData  = null;
window.gfOverlayActive    = false;
window.gfOverlayRendered  = false;
window.gfOverlaySettings  = null;
window.gfOverlayPages     = [];

if (window.gfUIOverlayLoaded) {
  console.log("[GF Overlay] já carregado.");
} else {
  window.gfUIOverlayLoaded = true;
  console.log("[GF Overlay] v3 iniciando...");
  _gfStart();
}

// ═══════════════════════════════════════════════════════════════
// BOOT
// ═══════════════════════════════════════════════════════════════
function _gfStart() {
  _gfPatchHistory();
  window.addEventListener("popstate", function(){ setTimeout(_gfCheck, 30); });
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", _gfOnReady);
  else
    _gfOnReady();
  window.addEventListener("load", function(){ setTimeout(_gfCheck, 100); });
}

function _gfOnReady() {
  document.body.classList.add("gf-overlay-booting");
  if (typeof frappe !== "undefined" && frappe.ready) frappe.ready(_gfInit);
  setTimeout(_gfInit, 250);
  setTimeout(_gfCheck, 700);
  setTimeout(_gfCheck, 1400);
}

var _initDone = false;
function _gfInit() {
  if (_initDone) { _gfCheck(); return; } _initDone = true;
  _gfFetch("ichis_ui_overlay.api.overlay.get_overlay_settings", {}, function(s) {
    window.gfOverlaySettings = s || { ativar_sobreposicoes: 0 };
    if (!s || !s.ativar_sobreposicoes) { console.log("[GF Overlay] Desativado."); _gfFallback(); return; }
    _gfFetch("ichis_ui_overlay.api.overlay.get_active_overlay_pages", {}, function(pages) {
      window.gfOverlayPages = Array.isArray(pages) ? pages : [];
      console.log("[GF Overlay] Páginas carregadas:", window.gfOverlayPages.length);
      try {
        if (typeof frappe !== "undefined" && frappe.router && frappe.router.on)
          frappe.router.on("change", function(){ setTimeout(_gfCheck, 30); });
      } catch(e) {}
      _gfObserveDOM();
      var _lr = "";
      setInterval(function(){ var c=_gfRoute(); if(c!==_lr){_lr=c;_gfCheck();} }, 400);
      _gfCheck();
    });
  });
}

// ═══════════════════════════════════════════════════════════════
// VERIFICAÇÃO DE ROTA
// ═══════════════════════════════════════════════════════════════
function _gfCheck() {
  try {
    try { if (sessionStorage.getItem("gf_overlay_disabled")==="1"){ _gfFallback(); return; } } catch(e){}
    var route = _gfRoute(); window.gfCurrentRoute = route;
    var page  = _gfMatch(route);
    if (page) {
      if (!window.gfOverlayRendered || window.gfLastPage !== page.nome_tecnico)
        _gfApply(page);
    } else {
      if (window.gfOverlayActive) _gfRemove(); else _gfFallback();
    }
  } catch(err) { console.warn("[GF Overlay] _gfCheck:", err); _gfFallback(); }
}

function _gfRoute() {
  return (window.location.pathname||"/app").replace(/\/$/,"").replace(/#.*$/,"").replace(/\?.*$/,"")||"/app";
}

var DESK_ROUTES = ["/app","/app/workspace","/desk","/app/workspace/home"];
function _gfMatch(route) {
  var pages = window.gfOverlayPages||[]; var n = route.toLowerCase();
  for (var i=0; i<pages.length; i++) {
    var p = pages[i]; if (!p.ativo && p.ativo!==1) continue;
    if (p.tipo_alvo==="Desk") {
      for (var d=0; d<DESK_ROUTES.length; d++)
        if (n===DESK_ROUTES[d]||n.startsWith(DESK_ROUTES[d]+"/")) return p;
    }
    var pr = (p.rota_alvo||"").toLowerCase().replace(/\/$/,"");
    if (pr && (n===pr||n.startsWith(pr+"/"))) return p;
  }
  return null;
}

// ═══════════════════════════════════════════════════════════════
// APLICAR OVERLAY
// ═══════════════════════════════════════════════════════════════
function _gfApply(page) {
  window.gfOverlayRendered  = true;
  window.gfOverlayActive    = true;
  window.gfLastPage         = page.nome_tecnico;
  window.gfCurrentPageData  = page;  // Expõe para o JS customizado

  // Remove instância anterior
  var old = document.getElementById("gf-ui-overlay-root"); if (old) old.remove();
  var ocs = document.getElementById("gf-overlay-page-css"); if (ocs) ocs.remove();

  // Cria container
  var root = document.createElement("div");
  root.id  = "gf-ui-overlay-root";
  var animMap = {"Suave":"gf-anim-suave","Fade":"gf-anim-fade","Slide":"gf-anim-slide"};
  root.classList.add(animMap[(window.gfOverlaySettings||{}).animacao_entrada]||"gf-anim-suave");

  // Conteúdo inicial mínimo (o JS customizado vai substituir)
  root.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#64748b;font-family:Inter,sans-serif;font-size:14px;">Carregando...</div>';

  document.body.appendChild(root);

  // CSS customizado da página
  if (page.css_customizado && page.css_customizado.trim()) {
    var sc = document.createElement("style");
    sc.id  = "gf-overlay-page-css";
    sc.textContent = page.css_customizado;
    document.head.appendChild(sc);
  }

  // Ativar overlay
  document.body.classList.remove("gf-overlay-booting");
  document.body.classList.add("gf-overlay-active");

  // Executar JS customizado — ele renderiza o HTML real
  if (page.js_customizado && page.js_customizado.trim()) {
    try { (new Function(page.js_customizado))(); }
    catch(e) { console.warn("[GF Overlay] JS customizado erro:", e); _gfFallbackHTML(root, page); }
  } else {
    // Sem JS customizado: renderiza HTML embutido se existir, senão fallback
    if (page.html_customizado && page.html_customizado.trim().length > 50)
      root.innerHTML = page.html_customizado;
    else
      _gfFallbackHTML(root, page);
  }

  console.log("[GF Overlay] v3 ativo:", page.titulo);
}

// Fallback visual simples se o JS customizado falhar
function _gfFallbackHTML(root, page) {
  var cards = (page.cards||[]).filter(function(c){return c.ativo!==0;});
  var cardsHtml = cards.map(function(c){
    var href = c.rota_destino || (c.doctype_destino ? "/app/"+c.doctype_destino.toLowerCase().replace(/\s+/g,"-") : "#");
    return '<a href="'+href+'" onclick="return gfNav(\''+href+'\',event)" style="display:flex;align-items:center;gap:12px;padding:14px 16px;background:#fff;border:1px solid #e2e8f0;border-radius:12px;text-decoration:none;color:#0f172a;transition:transform .15s" onmouseover="this.style.transform=\'translateY(-2px)\'" onmouseout="this.style.transform=\'\'">' +
      '<span style="font-size:22px">'+(c.icone||"📌")+'</span>' +
      '<span style="display:flex;flex-direction:column"><strong style="font-size:13px">'+c.titulo+'</strong><small style="font-size:11px;color:#64748b">'+c.descricao+'</small></span>' +
    '</a>';
  }).join("");
  root.innerHTML = '<div style="padding:32px;font-family:Inter,sans-serif;max-width:1200px;margin:0 auto">' +
    '<h1 style="font-size:24px;font-weight:800;color:#0f172a;margin:0 0 8px">'+( page.titulo_pagina||"GREENFARMS")+'</h1>' +
    '<p style="color:#64748b;margin:0 0 28px">'+(page.texto_boas_vindas||"")+'</p>' +
    '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px">'+cardsHtml+'</div>' +
  '</div>';
}

// ─── REMOVER / FALLBACK ───────────────────────────────────────
function _gfRemove() {
  window.gfOverlayActive=false; window.gfOverlayRendered=false;
  window.gfLastPage=null; window.gfCurrentPageData=null;
  var r=document.getElementById("gf-ui-overlay-root"); if(r)r.remove();
  document.body.classList.remove("gf-overlay-active","gf-overlay-booting");
}

function _gfFallback() {
  document.body.classList.remove("gf-overlay-booting","gf-overlay-active");
  window.gfOverlayActive=false; window.gfOverlayRendered=false;
}

// ─── FUNÇÕES PÚBLICAS ────────────────────────────────────────
window.gfNav = function(route, event) {
  if (event) event.preventDefault();
  try {
    if (typeof frappe!=="undefined" && frappe.set_route) {
      var p = route.replace(/^\/app\/?/,"").split("/").filter(Boolean);
      if (p.length) frappe.set_route(p); else frappe.set_route("workspace");
    } else window.location.href = route;
  } catch(e) { window.location.href = route; }
  return false;
};

window.gfReturnToOriginalDesk = function() {
  try { sessionStorage.setItem("gf_overlay_disabled","1"); } catch(e){}
  _gfRemove();
  try {
    if (typeof frappe!=="undefined"&&frappe.set_route) frappe.set_route("workspace");
    else window.location.href="/app";
  } catch(e) { window.location.href="/app"; }
};

// ─── UTILITÁRIOS ─────────────────────────────────────────────
function _gfFetch(method, args, cb) {
  try {
    if (typeof frappe!=="undefined"&&frappe.call) {
      frappe.call({method:method,args:args||{},
        callback:function(r){cb(r&&r.message!==undefined?r.message:null);},
        error:function(){cb(null);}});
    } else {
      fetch("/api/method/"+method,{credentials:"same-origin"})
        .then(function(r){return r.json();})
        .then(function(d){cb(d&&d.message!==undefined?d.message:null);})
        .catch(function(){cb(null);});
    }
  } catch(e){cb(null);}
}

function _gfPatchHistory() {
  try {
    ["pushState","replaceState"].forEach(function(fn){
      var o=history[fn].bind(history);
      history[fn]=function(){o.apply(history,arguments);setTimeout(_gfCheck,40);};
    });
  } catch(e){}
}

function _gfObserveDOM() {
  new MutationObserver(function(muts){
    if (!window.gfOverlayActive) return;
    muts.forEach(function(m){
      m.addedNodes.forEach(function(n){
        if (n.nodeType!==1) return;
        if (n.id==="page-desktop"||(n.classList&&n.classList.contains("layout-main-section")))
          setTimeout(function(){document.body.classList.add("gf-overlay-active");},20);
      });
    });
  }).observe(document.documentElement,{childList:true,subtree:true});
}

// ── ANIMAÇÕES CSS injetadas ───────────────────────────────────
(function(){
  var s=document.createElement("style");
  s.textContent=
    ".gf-anim-suave{animation:gfSuave 280ms ease both}" +
    ".gf-anim-fade{animation:gfFade 280ms ease both}" +
    ".gf-anim-slide{animation:gfSlide 320ms ease both}" +
    "@keyframes gfSuave{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}" +
    "@keyframes gfFade{from{opacity:0}to{opacity:1}}" +
    "@keyframes gfSlide{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:none}}";
  document.head.appendChild(s);
})();
