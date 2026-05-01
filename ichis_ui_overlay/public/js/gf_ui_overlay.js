/**
 * GF UI Overlay — gf_ui_overlay.js  v2.0
 * GREENFARMS | UI Overlay Manager
 * Diagnóstico: window.gfUIOverlayVersion / window.gfUIOverlayLoaded / window.gfCurrentRoute
 */

// CAMADA 0: bloquear Desk IMEDIATAMENTE (roda antes do Frappe renderizar qualquer coisa)
(function gfImmediateBoot() {
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
    "#gf-ui-overlay-root{display:none}" +
    "body.gf-overlay-active #gf-ui-overlay-root{display:flex!important;flex-direction:column}" +
    "body.gf-overlay-active .layout-main-section," +
    "body.gf-overlay-active #page-desktop," +
    "body.gf-overlay-active .desk-sidebar," +
    "body.gf-overlay-active .standard-sidebar," +
    "body.gf-overlay-active .page-container{visibility:hidden!important;pointer-events:none!important}";
  (document.head || document.documentElement).appendChild(s);
  if (document.body) document.body.classList.add("gf-overlay-booting");
  else document.addEventListener("DOMContentLoaded", function(){document.body.classList.add("gf-overlay-booting");},{once:true});
})();

window.gfUIOverlayVersion = "GF_UI_OVERLAY_V2";
window.gfCurrentRoute     = null;
window.gfOverlayActive    = false;
window.gfOverlayRendered  = false;
window.gfOverlaySettings  = null;
window.gfOverlayPages     = [];

if (window.gfUIOverlayLoaded) {
  console.log("[GF Overlay] já carregado.");
} else {
  window.gfUIOverlayLoaded = true;
  console.log("[GF Overlay] v2 iniciando...");
  _gfStart();
}

function _gfStart() {
  _gfPatchHistory();
  window.addEventListener("popstate", function(){setTimeout(_gfCheck,30);});
  if (document.readyState==="loading") document.addEventListener("DOMContentLoaded",_gfOnReady);
  else _gfOnReady();
  window.addEventListener("load",function(){setTimeout(_gfCheck,80);});
}

function _gfOnReady() {
  document.body.classList.add("gf-overlay-booting");
  if (typeof frappe!=="undefined" && frappe.ready) frappe.ready(_gfInit);
  setTimeout(_gfInit, 200);
  setTimeout(_gfCheck, 600);
  setTimeout(_gfCheck, 1200);
}

var _gfInitDone = false;
function _gfInit() {
  if (_gfInitDone){_gfCheck();return;} _gfInitDone=true;
  _gfFetchSettings(function(settings){
    window.gfOverlaySettings = settings || {ativar_sobreposicoes:0};
    if (!settings||!settings.ativar_sobreposicoes){console.log("[GF Overlay] Desativado.");_gfFallback();return;}
    _gfFetchPages(function(){
      try{if(typeof frappe!=="undefined"&&frappe.router&&frappe.router.on)frappe.router.on("change",function(){setTimeout(_gfCheck,30);});}catch(e){}
      _gfObserveDOM();
      var _lr="";
      setInterval(function(){var c=_gfRoute();if(c!==_lr){_lr=c;_gfCheck();}},400);
      _gfCheck();
    });
  });
}

function _gfCheck() {
  try {
    try{if(sessionStorage.getItem("gf_overlay_disabled")==="1"){_gfFallback();return;}}catch(e){}
    var route=_gfRoute(); window.gfCurrentRoute=route;
    var page=_gfMatch(route);
    if (page){if(!window.gfOverlayRendered||window.gfLastPage!==page.nome_tecnico)_gfApply(page);}
    else{if(window.gfOverlayActive)_gfRemove();else _gfFallback();}
  } catch(err){console.warn("[GF Overlay] _gfCheck:",err);_gfFallback();}
}

function _gfRoute() {
  return (window.location.pathname||"/app").replace(/\/$/,"").replace(/#.*$/,"").replace(/\?.*$/,"")||"/app";
}

var GF_DESK_ROUTES=["/app","/app/workspace","/desk","/app/workspace/home"];
function _gfMatch(route){
  var pages=window.gfOverlayPages||[]; var norm=route.toLowerCase();
  for(var i=0;i<pages.length;i++){
    var p=pages[i]; if(!p.ativo&&p.ativo!==1)continue;
    if(p.tipo_alvo==="Desk"){for(var d=0;d<GF_DESK_ROUTES.length;d++)if(norm===GF_DESK_ROUTES[d]||norm.startsWith(GF_DESK_ROUTES[d]+"/"))return p;}
    var pr=(p.rota_alvo||"").toLowerCase().replace(/\/$/,"");
    if(pr&&(norm===pr||norm.startsWith(pr+"/")))return p;
  }
  return null;
}

function _gfApply(page){
  window.gfOverlayRendered=true; window.gfOverlayActive=true; window.gfLastPage=page.nome_tecnico;
  var old=document.getElementById("gf-ui-overlay-root"); if(old)old.remove();
  var oldcss=document.getElementById("gf-overlay-page-css"); if(oldcss)oldcss.remove();
  var root=document.createElement("div"); root.id="gf-ui-overlay-root";
  var settings=window.gfOverlaySettings||{};
  var animMap={"Suave":"gf-anim-suave","Fade":"gf-anim-fade","Slide":"gf-anim-slide"};
  root.classList.add(animMap[settings.animacao_entrada]||"gf-anim-suave");
  if(page.html_customizado&&page.html_customizado.trim().length>50) root.innerHTML=page.html_customizado;
  else root.innerHTML=_gfBuildHTML(page,settings);
  document.body.appendChild(root);
  if(page.css_customizado&&page.css_customizado.trim()){var sc=document.createElement("style");sc.id="gf-overlay-page-css";sc.textContent=page.css_customizado;document.head.appendChild(sc);}
  document.body.classList.remove("gf-overlay-booting");
  document.body.classList.add("gf-overlay-active");
  _gfBindEvents(root,page);
  if(page.exibir_ultimas_atividades)_gfLoadActivities();
  if(page.js_customizado&&page.js_customizado.trim()){try{(new Function(page.js_customizado))();}catch(e){console.warn("[GF Overlay] JS customizado:",e);}}
  console.log("[GF Overlay] Ativo:",page.titulo);
}

function _gfRemove(){
  window.gfOverlayActive=false;window.gfOverlayRendered=false;window.gfLastPage=null;
  var r=document.getElementById("gf-ui-overlay-root");if(r)r.remove();
  document.body.classList.remove("gf-overlay-active","gf-overlay-booting");
}

function _gfFallback(){
  document.body.classList.remove("gf-overlay-booting","gf-overlay-active");
  window.gfOverlayActive=false;window.gfOverlayRendered=false;
}

// ───────────────────────────────────────────────────────────────
// HTML DO MODERN DESK
// ───────────────────────────────────────────────────────────────
function _gfBuildHTML(page,settings){
  var fullName=_gfUserFullName();
  var hour=new Date().getHours();
  var greet=hour<12?"Bom dia":hour<18?"Boa tarde":"Boa noite";
  var showBack=settings.mostrar_botao_voltar_tela_original;
  var cards=(page.cards||[]).filter(function(c){return c.ativo!==0;});
  var cardsHTML=cards.length?cards.map(_gfCardHTML).join(""):_gfDefaultCardsHTML();

  return(
    '<div class="gf-desk-root">' +
    '<div class="gf-desk-topbar">' +
      '<div class="gf-desk-topbar-left">' +
        '<div class="gf-desk-logo-area">&#127807; GREENFARMS</div>' +
      '</div>' +
      '<div class="gf-desk-topbar-center">' +
        '<div class="gf-desk-search-box">' +
          '<span class="gf-search-ico">&#128269;</span>' +
          '<input id="gf-search-input" class="gf-desk-search-input" type="text" placeholder="Buscar... (pressione / para focar)" autocomplete="off"/>' +
        '</div>' +
      '</div>' +
      '<div class="gf-desk-topbar-right">' +
        '<span class="gf-desk-user-badge" title="'+_gfUserName()+'">' + _gfUserName().charAt(0).toUpperCase() + '</span>' +
      '</div>' +
    '</div>' +

    '<div class="gf-desk-layout">' +

      '<nav class="gf-desk-sidebar">' +
        '<div class="gf-sidebar-group">' +
          '<p class="gf-sidebar-label">Início</p>' +
          '<a class="gf-sidebar-link gf-sidebar-active" href="/app" onclick="return gfNav(\'/app\',event)">&#127968; Início</a>' +
        '</div>' +
        '<div class="gf-sidebar-group">' +
          '<p class="gf-sidebar-label">Operações</p>' +
          '<a class="gf-sidebar-link" href="/app/selling"      onclick="return gfNav(\'/app/selling\',event)">&#128722; Vendas</a>' +
          '<a class="gf-sidebar-link" href="/app/buying"       onclick="return gfNav(\'/app/buying\',event)">&#128230; Compras</a>' +
          '<a class="gf-sidebar-link" href="/app/stock"        onclick="return gfNav(\'/app/stock\',event)">&#127981; Estoque</a>' +
          '<a class="gf-sidebar-link" href="/app/accounts"     onclick="return gfNav(\'/app/accounts\',event)">&#128176; Financeiro</a>' +
          '<a class="gf-sidebar-link" href="/app/hr"           onclick="return gfNav(\'/app/hr\',event)">&#128101; RH</a>' +
          '<a class="gf-sidebar-link" href="/app/project"      onclick="return gfNav(\'/app/project\',event)">&#128203; Projetos</a>' +
          '<a class="gf-sidebar-link" href="/app/crm"          onclick="return gfNav(\'/app/crm\',event)">&#129309; CRM</a>' +
        '</div>' +
        '<div class="gf-sidebar-group">' +
          '<p class="gf-sidebar-label">Análises</p>' +
          '<a class="gf-sidebar-link" href="/app/query-report" onclick="return gfNav(\'/app/query-report\',event)">&#128202; Relatórios</a>' +
        '</div>' +
        '<div class="gf-sidebar-group gf-sidebar-bottom">' +
          '<p class="gf-sidebar-label">Sistema</p>' +
          '<a class="gf-sidebar-link" href="/app/setup" onclick="return gfNav(\'/app/setup\',event)">&#9881; Configurações</a>' +
          (showBack?'<button class="gf-sidebar-link gf-sidebar-original-btn" onclick="gfReturnToOriginalDesk()">&#8617; Desk Original</button>':'')+
        '</div>' +
      '</nav>' +

      '<main class="gf-desk-content">' +

        '<div class="gf-desk-hero">' +
          '<div class="gf-desk-hero-text">' +
            '<p class="gf-desk-hero-greeting">' + greet + ', <strong>' + fullName + '</strong> 👋</p>' +
            '<h1 class="gf-desk-hero-title">' + (page.titulo_pagina||'Central de Gestão') + '</h1>' +
            '<p class="gf-desk-hero-sub">' + (page.texto_boas_vindas||'Gerencie sua operação com eficiência e clareza.') + '</p>' +
          '</div>' +
          '<div class="gf-desk-hero-stats">' +
            '<div class="gf-kpi-card" id="gf-stat-open-tasks"><span class="gf-kpi-val">—</span><span class="gf-kpi-label">Tarefas Abertas</span></div>' +
            '<div class="gf-kpi-card" id="gf-stat-notif"><span class="gf-kpi-val">—</span><span class="gf-kpi-label">Notificações</span></div>' +
            '<div class="gf-kpi-card"><span class="gf-kpi-val">' + new Date().toLocaleDateString("pt-BR",{weekday:"short",day:"2-digit",month:"short"}) + '</span><span class="gf-kpi-label">Hoje</span></div>' +
          '</div>' +
        '</div>' +

        '<section class="gf-desk-section">' +
          '<div class="gf-desk-section-hd">' +
            '<h2 class="gf-desk-section-title">Módulos do Sistema</h2>' +
          '</div>' +
          '<div class="gf-modules-grid">' + cardsHTML + '</div>' +
        '</section>' +

        '<section class="gf-desk-section">' +
          '<div class="gf-desk-section-hd">' +
            '<h2 class="gf-desk-section-title">Atividades Recentes</h2>' +
            '<a class="gf-desk-more-link" href="/app/activity" onclick="return gfNav(\'/app/activity\',event)">Ver todas →</a>' +
          '</div>' +
          '<div class="gf-activity-panel" id="gf-activity-panel">' + _gfSkeleton(5) + '</div>' +
        '</section>' +

      '</main>' +
    '</div>' +
    '</div>'
  );
}

function _gfCardHTML(c){
  var bg=c.cor_fundo||"transparent";
  var acc=c.cor_icone||"var(--gf-accent,#16a34a)";
  var href=_gfCardHref(c);
  var tgt=c.abrir_em_nova_aba?' target="_blank"':"";
  var data=(JSON.stringify(c)||"{}").replace(/"/g,"&quot;");
  return(
    '<a class="gf-mod-card" href="'+href+'"'+tgt+
    ' onclick="return gfCardClick(this,&quot;'+data+'&quot;,event)"'+
    ' style="--card-acc:'+acc+';--card-bg:'+bg+'">' +
      '<div class="gf-mod-icon">'+( c.icone||"📌")+'</div>'+
      '<div class="gf-mod-info">'+
        '<span class="gf-mod-title">'+(c.titulo||"")+'</span>'+
        '<span class="gf-mod-desc">'+(c.descricao||"")+'</span>'+
      '</div>'+
      '<span class="gf-mod-arrow">→</span>'+
    '</a>'
  );
}

function _gfCardHref(c){
  if(c.tipo_acao==="Abrir Doctype"&&c.doctype_destino) return "/app/"+c.doctype_destino.toLowerCase().replace(/\s+/g,"-");
  if(c.tipo_acao==="Abrir Rota"&&c.rota_destino)       return c.rota_destino;
  if(c.tipo_acao==="Abrir URL"&&c.url_destino)          return c.url_destino;
  if(c.tipo_acao==="Abrir Report"&&c.report_destino)    return "/app/query-report/"+encodeURIComponent(c.report_destino);
  return c.rota_destino||"#";
}

function _gfDefaultCardsHTML(){
  return [
    {t:"Vendas",       d:"Pedidos e faturamento",       i:"🛒", r:"/app/selling",      c:"#16a34a"},
    {t:"Compras",      d:"Fornecedores e recebimentos",  i:"📦", r:"/app/buying",       c:"#2563eb"},
    {t:"Estoque",      d:"Produtos e armazéns",          i:"🏭", r:"/app/stock",        c:"#ca8a04"},
    {t:"Financeiro",   d:"Contas e pagamentos",          i:"💰", r:"/app/accounts",     c:"#db2777"},
    {t:"Projetos",     d:"Tarefas e cronogramas",        i:"📋", r:"/app/project",      c:"#7c3aed"},
    {t:"CRM",          d:"Leads e oportunidades",        i:"🤝", r:"/app/crm",          c:"#ea580c"},
    {t:"RH",           d:"Colaboradores e folha",        i:"👥", r:"/app/hr",           c:"#0369a1"},
    {t:"Relatórios",   d:"Análises gerenciais",          i:"📊", r:"/app/query-report", c:"#15803d"},
    {t:"Configurações",d:"Administração do sistema",     i:"⚙️", r:"/app/setup",        c:"#374151"},
  ].map(function(d){
    return '<a class="gf-mod-card" href="'+d.r+'" onclick="return gfNav(\''+d.r+'\',event)" style="--card-acc:'+d.c+';--card-bg:transparent">'+
      '<div class="gf-mod-icon">'+d.i+'</div>'+
      '<div class="gf-mod-info"><span class="gf-mod-title">'+d.t+'</span><span class="gf-mod-desc">'+d.d+'</span></div>'+
      '<span class="gf-mod-arrow">→</span></a>';
  }).join("");
}

function _gfSkeleton(n){var h="";for(var i=0;i<n;i++)h+='<div class="gf-act-item"><div class="gf-sk" style="width:8px;height:8px;border-radius:50%;flex-shrink:0"></div><div style="flex:1;display:flex;flex-direction:column;gap:5px"><div class="gf-sk" style="height:13px;width:55%"></div><div class="gf-sk" style="height:11px;width:35%"></div></div><div class="gf-sk" style="height:11px;width:32px"></div></div>';return h;}

function _gfBindEvents(root,page){
  var inp=root.querySelector("#gf-search-input");
  if(inp){
    inp.addEventListener("keydown",function(e){
      if(e.key!=="Enter")return; var q=inp.value.trim(); if(!q)return; e.preventDefault();
      try{if(typeof frappe!=="undefined"&&frappe.utils&&frappe.utils.global_search)frappe.utils.global_search(q);else window.location.href="/app?q="+encodeURIComponent(q);}
      catch(ex){window.location.href="/app?q="+encodeURIComponent(q);}
    });
    document.addEventListener("keydown",function(e){
      if(e.key==="/"&&!["INPUT","TEXTAREA"].includes(document.activeElement.tagName)){e.preventDefault();inp.focus();inp.select();}
    });
  }
  _gfLoadStats();
}

function _gfLoadStats(){
  try{if(typeof frappe==="undefined"||!frappe.call)return;
  frappe.call({method:"frappe.desk.notifications.get_open_count",
    callback:function(r){if(!r||!r.message)return;var el=document.getElementById("gf-stat-notif");if(el)el.querySelector(".gf-kpi-val").textContent=r.message.total_count||"0";},error:function(){}});}catch(e){}
}

function _gfLoadActivities(){
  try{if(typeof frappe==="undefined"||!frappe.call)return;
  frappe.call({method:"frappe.client.get_list",
    args:{doctype:"Activity Log",fields:["subject","full_name","user","creation"],filters:[["user","=",frappe.session.user]],limit:7,order_by:"creation desc"},
    callback:function(r){
      var panel=document.getElementById("gf-activity-panel"); if(!panel)return;
      var items=(r&&r.message)?r.message:[];
      if(!items.length){panel.innerHTML='<div class="gf-act-empty">Nenhuma atividade recente.</div>';return;}
      panel.innerHTML=items.map(function(a){return(
        '<div class="gf-act-item"><div class="gf-act-dot"></div>'+
        '<div class="gf-act-text"><span class="gf-act-title">'+(a.subject||"Atividade")+'</span>'+
        '<span class="gf-act-sub">'+(a.full_name||a.user||"")+'</span></div>'+
        '<span class="gf-act-time">'+_gfRelTime(a.creation)+'</span></div>');}).join("");},
    error:function(){}});}catch(e){}
}

function _gfRelTime(s){try{var d=(Date.now()-new Date(s).getTime())/1000;if(d<60)return"agora";if(d<3600)return Math.floor(d/60)+"min";if(d<86400)return Math.floor(d/3600)+"h";return Math.floor(d/86400)+"d";}catch(e){return"";}}

function _gfFetchSettings(cb){_gfAPI("ichis_ui_overlay.api.overlay.get_overlay_settings",{},cb);}
function _gfFetchPages(cb){_gfAPI("ichis_ui_overlay.api.overlay.get_active_overlay_pages",{},function(data){window.gfOverlayPages=Array.isArray(data)?data:[];console.log("[GF Overlay] Páginas:",window.gfOverlayPages.length);cb();});}
function _gfAPI(method,args,cb){
  try{if(typeof frappe!=="undefined"&&frappe.call){frappe.call({method:method,args:args||{},callback:function(r){cb(r&&r.message!==undefined?r.message:null);},error:function(){cb(null);}});}
  else{fetch("/api/method/"+method,{credentials:"same-origin"}).then(function(r){return r.json();}).then(function(d){cb(d&&d.message!==undefined?d.message:null);}).catch(function(){cb(null);});}}
  catch(e){cb(null);}
}

window.gfNav=function(route,event){
  if(event)event.preventDefault();
  try{if(typeof frappe!=="undefined"&&frappe.set_route){var p=route.replace(/^\/app\/?/,"").split("/").filter(Boolean);if(p.length)frappe.set_route(p);else frappe.set_route("workspace");}else window.location.href=route;}
  catch(e){window.location.href=route;}return false;
};

window.gfCardClick=function(el,dataStr,event){
  try{var c=JSON.parse(dataStr);
    if(c.tipo_acao==="Executar Script"&&c.script_acao){event.preventDefault();try{(new Function(c.script_acao))();}catch(e){}return false;}
    if(!c.abrir_em_nova_aba){var href=_gfCardHref(c);if(href&&href!=="#"){event.preventDefault();gfNav(href,null);return false;}}}catch(e){}
};

window.gfReturnToOriginalDesk=function(){
  try{sessionStorage.setItem("gf_overlay_disabled","1");}catch(e){}
  _gfRemove();
  try{if(typeof frappe!=="undefined"&&frappe.set_route)frappe.set_route("workspace");else window.location.href="/app";}catch(e){window.location.href="/app";}
};

function _gfUserName(){try{return(frappe.session.user||"").split("@")[0]||"usuário";}catch(e){return"usuário";}}
function _gfUserFullName(){try{return frappe.session.full_name||frappe.boot.full_name||_gfUserName();}catch(e){return _gfUserName();}}
function _gfPatchHistory(){try{["pushState","replaceState"].forEach(function(fn){var o=history[fn].bind(history);history[fn]=function(){o.apply(history,arguments);setTimeout(_gfCheck,40);});});}catch(e){}}
function _gfObserveDOM(){new MutationObserver(function(muts){if(!window.gfOverlayActive)return;muts.forEach(function(m){m.addedNodes.forEach(function(n){if(n.nodeType!==1)return;if(n.id==="page-desktop"||(n.classList&&n.classList.contains("layout-main-section")))setTimeout(function(){document.body.classList.add("gf-overlay-active");},20);});});}).observe(document.documentElement,{childList:true,subtree:true});}
