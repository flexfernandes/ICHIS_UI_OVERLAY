/**
 * GF UI Overlay — gf_ui_overlay.js
 * GREENFARMS | UI Overlay Manager v1.0.0
 *
 * Responsabilidades:
 *  1. Interceptar rotas do ERPNext (pushState, popstate, frappe.router, setInterval)
 *  2. Ocultar o Desk original imediatamente (body.gf-overlay-booting)
 *  3. Renderizar o GF Modern Desk moderno em seu lugar
 *  4. Controlar fallback seguro para o Desk original
 *  5. Suportar cards configurados no Doctype GF UI Overlay Page
 *  6. Consumir variáveis visuais do GF Theme Settings quando disponível
 *  7. Diagnóstico no console
 *
 * Diagnóstico:
 *   window.gfUIOverlayVersion   → "GF_UI_OVERLAY_V1"
 *   window.gfUIOverlayLoaded    → true
 *   window.gfCurrentRoute       → rota atual normalizada
 */

// ─── DIAGNÓSTICO ─────────────────────────────────────────────
window.gfUIOverlayVersion = "GF_UI_OVERLAY_V1";

// Evita duplicidade total do script
if (window.gfUIOverlayLoaded) {
  _gfLog("Script já carregado — ignorando duplicata.");
} else {
  window.gfUIOverlayLoaded  = true;
  window.gfOverlayRendered  = false;
  window.gfCurrentRoute     = null;
  window.gfOverlaySettings  = null;
  window.gfOverlayPages     = [];
  window.gfOverlayActive    = false;

  _gfLog("GF UI Overlay iniciando...", window.gfUIOverlayVersion);
  _gfBootOverlay();
}

// ─── LOG HELPER ──────────────────────────────────────────────
function _gfLog() {
  // Só loga depois de ter settings; antes, sempre loga para depuração de boot
  if (window.gfOverlaySettings && !window.gfOverlaySettings.diagnostico_console) return;
  console.log("[GF Overlay]", ...arguments);
}

function _gfWarn() {
  console.warn("[GF Overlay]", ...arguments);
}

// ─── BOOT (IIFE imediata) ─────────────────────────────────────
function _gfBootOverlay() {
  // Aplica classe de boot imediatamente para esconder o Desk
  // antes mesmo de carregar configurações
  _gfApplyBootClass();

  // Múltiplos pontos de entrada para garantir execução
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", _gfOnDOMReady);
  } else {
    _gfOnDOMReady();
  }

  window.addEventListener("load", function () {
    _gfLog("window.load — verificando overlay...");
    setTimeout(_gfCheckAndApply, 80);
  });

  // Monkey-patch de history para capturar navegação SPA
  _gfPatchHistory();

  // Listener popstate (botão voltar/avançar)
  window.addEventListener("popstate", function () {
    _gfLog("popstate detectado");
    setTimeout(interceptRouteChange, 50);
  });
}

// ─── DOM READY ───────────────────────────────────────────────
function _gfOnDOMReady() {
  _gfLog("DOM pronto.");

  if (typeof frappe !== "undefined" && frappe.ready) {
    frappe.ready(function () {
      _gfLog("frappe.ready disparado.");
      _gfInitAfterFrappe();
    });
  } else {
    // frappe não disponível ainda — tenta logo
    setTimeout(_gfInitAfterFrappe, 200);
  }

  // Fallback agressivo: tentar em 100ms e 300ms
  setTimeout(_gfCheckAndApply, 100);
  setTimeout(_gfCheckAndApply, 350);
}

// ─── INICIALIZAÇÃO APÓS FRAPPE ───────────────────────────────
function _gfInitAfterFrappe() {
  loadOverlaySettings()
    .then(function (settings) {
      if (!settings || !settings.ativar_sobreposicoes) {
        _gfLog("Overlay desativado nas configurações.");
        fallbackToOriginalDesk();
        return;
      }

      window.gfOverlaySettings = settings;

      return loadActivePages().then(function () {
        // Registrar no frappe.router se disponível
        _gfRegisterFrappeRouter();
        // Observar mudanças de DOM
        observeDOMChanges();
        // Observar mudanças de rota via setInterval leve
        observeRouteChanges();
        // Verificar rota atual imediatamente
        interceptRouteChange();
      });
    })
    .catch(function (err) {
      _gfWarn("Erro ao inicializar:", err);
      fallbackToOriginalDesk();
    });
}

// ─── CARREGAR CONFIGURAÇÕES ──────────────────────────────────
function loadOverlaySettings() {
  return new Promise(function (resolve) {
    try {
      if (typeof frappe !== "undefined" && frappe.call) {
        frappe.call({
          method: "ichis_ui_overlay.api.overlay.get_overlay_settings",
          callback: function (r) { resolve(r && r.message ? r.message : null); },
          error:    function ()  { resolve(null); },
        });
      } else {
        fetch("/api/method/ichis_ui_overlay.api.overlay.get_overlay_settings", {
          credentials: "same-origin",
        })
          .then(function (r) { return r.json(); })
          .then(function (d) { resolve(d && d.message ? d.message : null); })
          .catch(function ()  { resolve(null); });
      }
    } catch (e) {
      resolve(null);
    }
  });
}

// ─── CARREGAR PÁGINAS ATIVAS ─────────────────────────────────
function loadActivePages() {
  return new Promise(function (resolve) {
    try {
      const call = typeof frappe !== "undefined" && frappe.call ? frappe.call : null;
      if (call) {
        frappe.call({
          method: "ichis_ui_overlay.api.overlay.get_active_overlay_pages",
          callback: function (r) {
            window.gfOverlayPages = (r && r.message) ? r.message : [];
            _gfLog("Páginas carregadas:", window.gfOverlayPages.length);
            resolve();
          },
          error: function () { window.gfOverlayPages = []; resolve(); },
        });
      } else {
        fetch("/api/method/ichis_ui_overlay.api.overlay.get_active_overlay_pages", {
          credentials: "same-origin",
        })
          .then(function (r) { return r.json(); })
          .then(function (d) {
            window.gfOverlayPages = (d && d.message) ? d.message : [];
            resolve();
          })
          .catch(function () { window.gfOverlayPages = []; resolve(); });
      }
    } catch (e) {
      window.gfOverlayPages = [];
      resolve();
    }
  });
}

// ─── ROTA ATUAL ──────────────────────────────────────────────
function getCurrentRoute() {
  return _gfNormalizeRoute(window.location.pathname);
}

function _gfNormalizeRoute(path) {
  if (!path) return "/app";
  // Remove trailing slash, hash, query string
  return path.replace(/\/$/, "").replace(/#.*$/, "").replace(/\?.*$/, "") || "/app";
}

// ─── MATCH DE ROTA ───────────────────────────────────────────
function matchOverlayPage(route) {
  if (!window.gfOverlayPages || !window.gfOverlayPages.length) return null;

  const normalized = _gfNormalizeRoute(route);

  // Rotas que correspondem ao Desk inicial
  const deskRoutes = ["/app", "/app/workspace", "/app/workspace/home", "/desk"];

  for (const page of window.gfOverlayPages) {
    if (!page.ativo && page.ativo !== 1) continue;

    const pageRoute = _gfNormalizeRoute(page.rota_alvo || "");

    // Match por tipo_alvo = Desk
    if (page.tipo_alvo === "Desk") {
      if (deskRoutes.includes(normalized.toLowerCase())) {
        return page;
      }
    }

    // Match por rota exata
    if (pageRoute && normalized === pageRoute) return page;

    // Match por workspace
    if (page.tipo_alvo === "Workspace" && page.workspace_alvo) {
      const ws = "/app/workspace/" + page.workspace_alvo.toLowerCase().replace(/\s+/g, "-");
      if (normalized.toLowerCase().startsWith(ws)) return page;
    }

    // Match por doctype (List View)
    if (page.tipo_alvo === "List View" && page.doctype_alvo) {
      const dt = "/app/" + page.doctype_alvo.toLowerCase().replace(/\s+/g, "-");
      if (normalized.toLowerCase().startsWith(dt)) return page;
    }
  }

  return null;
}

// ─── INTERCEPTAÇÃO DE ROTA ───────────────────────────────────
function interceptRouteChange() {
  try {
    const route = getCurrentRoute();
    window.gfCurrentRoute = route;
    _gfLog("Rota atual:", route);

    const page = matchOverlayPage(route);

    if (page) {
      _gfLog("Match encontrado:", page.titulo, "— aplicando overlay...");
      applyOverlay(page);
    } else {
      // Fora das rotas com overlay — restaura tela original
      if (window.gfOverlayActive) {
        _gfLog("Rota sem overlay — removendo...");
        removeOverlay();
      } else {
        // Remove classe de boot para não travar a tela
        _gfRemoveBootClass();
      }
    }
  } catch (err) {
    _gfWarn("Erro em interceptRouteChange:", err);
    fallbackToOriginalDesk();
  }
}

// ─── OBSERVAR MUDANÇAS DE ROTA ───────────────────────────────
function observeRouteChanges() {
  let lastRoute = getCurrentRoute();

  // Verificação leve a cada 400ms
  setInterval(function () {
    const cur = getCurrentRoute();
    if (cur !== lastRoute) {
      _gfLog("Mudança de rota detectada:", lastRoute, "→", cur);
      lastRoute = cur;
      interceptRouteChange();
    }
  }, 400);
}

// ─── OBSERVAR DOM ─────────────────────────────────────────────
function observeDOMChanges() {
  const target = document.body || document.documentElement;
  let debounce = null;

  const observer = new MutationObserver(function (mutations) {
    // Se overlay está ativo, verificar se o Desk tentou se mostrar
    if (window.gfOverlayActive) {
      const hasDeskNodes = mutations.some(function (m) {
        return Array.from(m.addedNodes).some(function (n) {
          return n.nodeType === 1 &&
            (n.id === "page-desktop" || n.classList.contains("layout-main-section"));
        });
      });
      if (hasDeskNodes) {
        clearTimeout(debounce);
        debounce = setTimeout(hideOriginalDesk, 50);
      }
    }
  });

  observer.observe(target, { childList: true, subtree: true });
}

// ─── MONKEY PATCH DE HISTORY ─────────────────────────────────
function _gfPatchHistory() {
  try {
    const origPush    = history.pushState.bind(history);
    const origReplace = history.replaceState.bind(history);

    history.pushState = function () {
      origPush(...arguments);
      setTimeout(interceptRouteChange, 30);
    };

    history.replaceState = function () {
      origReplace(...arguments);
      setTimeout(interceptRouteChange, 30);
    };
  } catch (e) {
    _gfWarn("Não foi possível patchar history:", e);
  }
}

// ─── FRAPPE ROUTER ───────────────────────────────────────────
function _gfRegisterFrappeRouter() {
  try {
    if (typeof frappe !== "undefined" && frappe.router && frappe.router.on) {
      frappe.router.on("change", function () {
        _gfLog("frappe.router change disparado");
        setTimeout(interceptRouteChange, 30);
      });
      _gfLog("frappe.router registrado.");
    }
  } catch (e) {
    _gfWarn("frappe.router indisponível:", e);
  }
}

// ─── APLICAR OVERLAY ─────────────────────────────────────────
function applyOverlay(page) {
  try {
    if (window.gfOverlayRendered && window.gfLastOverlayPage === page.nome_tecnico) return;

    window.gfOverlayRendered  = true;
    window.gfLastOverlayPage  = page.nome_tecnico;
    window.gfOverlayActive    = true;

    if (page.ocultar_tela_original) hideOriginalDesk();

    if (page.tipo_alvo === "Desk" || page.tipo_alvo === "Workspace") {
      renderModernDesk(page);
    } else {
      _renderGenericOverlay(page);
    }
  } catch (err) {
    _gfWarn("Erro em applyOverlay:", err);
    fallbackToOriginalDesk();
  }
}

// ─── REMOVER OVERLAY ─────────────────────────────────────────
function removeOverlay() {
  try {
    window.gfOverlayActive   = false;
    window.gfOverlayRendered = false;
    window.gfLastOverlayPage = null;

    const root = document.getElementById("gf-ui-overlay-root");
    if (root) root.remove();

    _gfRemoveBootClass();
    document.body.classList.remove("gf-overlay-active");
    showOriginalScreen();

    _gfLog("Overlay removido.");
  } catch (err) {
    _gfWarn("Erro em removeOverlay:", err);
  }
}

// ─── MOSTRAR / OCULTAR TELA ORIGINAL ─────────────────────────
function showOriginalScreen() {
  document.body.classList.remove("gf-overlay-active");
  document.body.classList.remove("gf-overlay-booting");
  _gfLog("Tela original visível.");
}

function hideOriginalScreen() {
  document.body.classList.add("gf-overlay-active");
}

function hideOriginalDesk() {
  document.body.classList.remove("gf-overlay-booting");
  document.body.classList.add("gf-overlay-active");
  _gfLog("Desk original ocultado.");
}

function _gfApplyBootClass() {
  document.body && document.body.classList.add("gf-overlay-booting");
}

function _gfRemoveBootClass() {
  document.body && document.body.classList.remove("gf-overlay-booting");
}

// ─── FALLBACK ────────────────────────────────────────────────
function fallbackToOriginalDesk() {
  try {
    _gfWarn("Fallback ativado — restaurando Desk original.");
    const root = document.getElementById("gf-ui-overlay-root");
    if (root) root.remove();

    document.body.classList.remove("gf-overlay-booting");
    document.body.classList.remove("gf-overlay-active");

    window.gfOverlayActive   = false;
    window.gfOverlayRendered = false;
  } catch (e) {
    // Silencioso para não travar o ERPNext
  }
}

// ─── VERIFICAÇÃO REDUNDANTE ──────────────────────────────────
function _gfCheckAndApply() {
  if (!window.gfOverlaySettings) return; // settings ainda não carregadas
  interceptRouteChange();
}

// =============================================================
// RENDERIZAÇÃO DO GF MODERN DESK
// =============================================================

function renderModernDesk(page) {
  try {
    _gfLog("Renderizando GF Modern Desk:", page.titulo);

    // Remove instância anterior se existir
    const existing = document.getElementById("gf-ui-overlay-root");
    if (existing) existing.remove();

    const settings = window.gfOverlaySettings || {};
    const anim     = settings.animacao_entrada || "Suave";
    const animClass = {
      "Suave": "gf-anim-suave",
      "Fade":  "gf-anim-fade",
      "Slide": "gf-anim-slide",
    }[anim] || "";

    const root = document.createElement("div");
    root.id = "gf-ui-overlay-root";
    if (animClass) root.classList.add(animClass);

    // Aplicar tema black no body se detectado
    _gfApplyThemeMode();

    const maxWidth   = page.largura_maxima || "1280px";
    const fullWidth  = page.usar_largura_total ? "gf-full-width" : "";
    const userName   = _gfGetUserName();
    const cards      = (page.cards || []).filter(function (c) { return c.ativo !== 0; });

    root.innerHTML = _buildModernDeskHTML({
      page, settings, userName, cards, maxWidth, fullWidth,
    });

    document.body.appendChild(root);

    // Eventos após inserção no DOM
    _gfBindOverlayEvents(root, page, settings);

    // Aplicar CSS customizado da página
    if (page.css_customizado) {
      const style = document.createElement("style");
      style.id    = "gf-overlay-custom-css";
      style.textContent = page.css_customizado;
      document.head.appendChild(style);
    }

    // Executar JS customizado da página
    if (page.js_customizado) {
      try { new Function(page.js_customizado)(); } catch (e) { _gfWarn("JS customizado com erro:", e); }
    }

    // Carregar últimas atividades de forma assíncrona
    if (page.exibir_ultimas_atividades) {
      _gfLoadRecentActivities(root);
    }

    // Transição final
    hideOriginalDesk();
    _gfLog("GF Modern Desk renderizado com sucesso.");

  } catch (err) {
    _gfWarn("Erro em renderModernDesk:", err);
    fallbackToOriginalDesk();
  }
}

// ─── BUILD HTML DA HOME MODERNA ──────────────────────────────
function _buildModernDeskHTML(opts) {
  const { page, settings, userName, cards, maxWidth, fullWidth } = opts;

  const titulo    = page.titulo_pagina    || "Bem-vindo";
  const subtitulo = page.subtitulo_pagina || "";
  const boasvindas= page.texto_boas_vindas|| "";
  const showSearch = page.exibir_busca_global !== 0;
  const showHero   = page.exibir_area_boas_vindas !== 0;
  const showCards  = page.exibir_cards_atalhos !== 0;
  const showInds   = page.exibir_indicadores !== 0;
  const showActs   = page.exibir_ultimas_atividades !== 0;
  const showBack   = settings.mostrar_botao_voltar_tela_original;

  const now = new Date();
  const hour = now.getHours();
  const greetWord = hour < 12 ? "Bom dia" : hour < 18 ? "Boa tarde" : "Boa noite";
  const greeting  = `${greetWord}, ${userName}`;

  return `
<div class="gf-overlay-wrapper${fullWidth ? " " + fullWidth : ""}" style="max-width:${maxWidth}">

  ${showHero ? `
  <div class="gf-hero">
    <div class="gf-hero-text">
      <div class="gf-greeting">${greeting}</div>
      <h1>${titulo}</h1>
      ${subtitulo ? `<p>${subtitulo}</p>` : ""}
      ${boasvindas ? `<p style="margin-top:6px;">${boasvindas}</p>` : ""}
    </div>
    ${showSearch ? `
    <div class="gf-search-bar">
      <div class="gf-search-inner">
        <span class="gf-search-icon">🔍</span>
        <input
          type="text"
          class="gf-search-input"
          id="gf-overlay-search"
          placeholder="Buscar em todo o sistema..."
          autocomplete="off"
        />
      </div>
    </div>` : ""}
  </div>` : ""}

  ${showCards && cards.length ? `
  <div class="gf-section">
    <div class="gf-section-header">
      <h2 class="gf-section-title">Módulos</h2>
    </div>
    <div class="gf-cards-grid">
      ${cards.map(function (c) { return _buildCardHTML(c); }).join("")}
    </div>
  </div>` : ""}

  ${showInds ? `
  <div class="gf-section" id="gf-indicators-section">
    <div class="gf-section-header">
      <h2 class="gf-section-title">Visão Geral</h2>
    </div>
    <div class="gf-indicators-grid">
      ${_buildSkeletonIndicators()}
    </div>
  </div>` : ""}

  ${showActs ? `
  <div class="gf-section">
    <div class="gf-section-header">
      <h2 class="gf-section-title">Atividades Recentes</h2>
      <a class="gf-section-link" href="/app/activity" onclick="return gfNavigate('/app/activity', event)">Ver todas</a>
    </div>
    <div class="gf-activity-list" id="gf-activity-list">
      ${_buildSkeletonActivities()}
    </div>
  </div>` : ""}

</div>

${showBack ? `
<button class="gf-back-to-desk" onclick="gfReturnToOriginalDesk()" title="Voltar ao Desk Original do ERPNext">
  <span class="gf-back-to-desk-icon">⬡</span>
  Desk Original
</button>` : ""}
  `;
}

// ─── HTML DE UM CARD ─────────────────────────────────────────
function _buildCardHTML(c) {
  const bgIcon  = c.cor_fundo  || "#f0fdf4";
  const corIcon = c.cor_icone  || "#16a34a";
  const corText = c.cor_texto  || "";
  const href    = _gfCardHref(c);
  const target  = c.abrir_em_nova_aba ? ' target="_blank"' : "";

  return `
<a class="gf-card"
   href="${href}"
   ${target}
   onclick="return gfCardClick(this, '${_gfEsc(JSON.stringify(c))}', event)"
   style="--card-accent:${corIcon}; ${corText ? "color:" + corText : ""}">
  <div class="gf-card-icon-wrap" style="background:${bgIcon}; color:${corIcon}">
    ${c.icone || "📌"}
  </div>
  <div class="gf-card-body">
    <p class="gf-card-title">${c.titulo || ""}</p>
    <p class="gf-card-desc">${c.descricao || ""}</p>
  </div>
  <span class="gf-card-arrow">→</span>
</a>`;
}

function _gfCardHref(c) {
  if (c.tipo_acao === "Abrir Doctype" && c.doctype_destino) {
    return "/app/" + c.doctype_destino.toLowerCase().replace(/\s+/g, "-");
  }
  if (c.tipo_acao === "Abrir Rota" && c.rota_destino)   return c.rota_destino;
  if (c.tipo_acao === "Abrir URL"  && c.url_destino)    return c.url_destino;
  if (c.tipo_acao === "Abrir Report" && c.report_destino) {
    return "/app/query-report/" + encodeURIComponent(c.report_destino);
  }
  return c.rota_destino || "#";
}

// ─── SKELETON LOADERS ────────────────────────────────────────
function _buildSkeletonIndicators() {
  return Array(4).fill(0).map(function () {
    return `<div class="gf-indicator-card">
      <div class="gf-skeleton" style="height:11px;width:70%;margin-bottom:8px;"></div>
      <div class="gf-skeleton" style="height:28px;width:50%;margin-bottom:8px;"></div>
      <div class="gf-skeleton" style="height:18px;width:35%;border-radius:20px;"></div>
    </div>`;
  }).join("");
}

function _buildSkeletonActivities() {
  return Array(4).fill(0).map(function () {
    return `<div class="gf-activity-item" style="cursor:default;">
      <div class="gf-activity-dot" style="background:#e5e7eb;"></div>
      <div class="gf-activity-text">
        <div class="gf-skeleton" style="height:13px;width:60%;margin-bottom:5px;"></div>
        <div class="gf-skeleton" style="height:11px;width:40%;"></div>
      </div>
    </div>`;
  }).join("");
}

// ─── ÚLTIMAS ATIVIDADES REAIS ─────────────────────────────────
function _gfLoadRecentActivities(root) {
  try {
    if (typeof frappe === "undefined" || !frappe.call) return;

    frappe.call({
      method: "frappe.desk.notifications.get_open_count",
      callback: function () {},
      error:    function () {},
    });

    // Busca as últimas atividades via log
    frappe.call({
      method: "frappe.client.get_list",
      args: {
        doctype: "Activity Log",
        fields:  ["subject", "user", "full_name", "creation"],
        filters: [["user", "=", frappe.session.user]],
        limit:   6,
        order_by: "creation desc",
      },
      callback: function (r) {
        const list = root.querySelector("#gf-activity-list");
        if (!list) return;

        const items = r && r.message ? r.message : [];
        if (!items.length) {
          list.innerHTML = `<div class="gf-activity-item" style="cursor:default;justify-content:center;">
            <p style="color:var(--gf-text-secondary);font-size:13px;margin:0;">Nenhuma atividade recente.</p>
          </div>`;
          return;
        }

        list.innerHTML = items.map(function (act) {
          const time = _gfRelativeTime(act.creation);
          return `<div class="gf-activity-item">
            <div class="gf-activity-dot"></div>
            <div class="gf-activity-text">
              <p class="gf-activity-title">${act.subject || "Atividade"}</p>
              <p class="gf-activity-sub">${act.full_name || act.user || ""}</p>
            </div>
            <span class="gf-activity-time">${time}</span>
          </div>`;
        }).join("");
      },
      error: function () {},
    });
  } catch (e) {
    _gfWarn("Erro ao carregar atividades:", e);
  }
}

// ─── TEMPO RELATIVO ───────────────────────────────────────────
function _gfRelativeTime(dateStr) {
  try {
    const diff = (Date.now() - new Date(dateStr).getTime()) / 1000;
    if (diff < 60)    return "agora";
    if (diff < 3600)  return Math.floor(diff / 60) + "min";
    if (diff < 86400) return Math.floor(diff / 3600) + "h";
    return Math.floor(diff / 86400) + "d";
  } catch (e) { return ""; }
}

// ─── EVENTOS DO OVERLAY ──────────────────────────────────────
function _gfBindOverlayEvents(root, page, settings) {
  // Busca global
  const searchInput = root.querySelector("#gf-overlay-search");
  if (searchInput) {
    let searchDebounce = null;
    searchInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        const q = searchInput.value.trim();
        if (q) {
          if (typeof frappe !== "undefined" && frappe.utils && frappe.utils.global_search) {
            frappe.utils.global_search(q);
          } else {
            window.location.href = "/app?q=" + encodeURIComponent(q);
          }
        }
      }
    });

    // Atalho de teclado global: / abre busca
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== searchInput
          && !["INPUT","TEXTAREA"].includes(document.activeElement.tagName)) {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
    });
  }
}

// ─── CLIQUE EM CARD ──────────────────────────────────────────
window.gfCardClick = function (el, cardJson, event) {
  try {
    const card = JSON.parse(cardJson);

    if (card.tipo_acao === "Executar Script" && card.script_acao) {
      event.preventDefault();
      try { new Function(card.script_acao)(); } catch (e) { _gfWarn("Script do card com erro:", e); }
      return false;
    }

    // Navegação interna via frappe.set_route
    if (!card.abrir_em_nova_aba && card.tipo_acao !== "Abrir URL") {
      const href = el.getAttribute("href");
      if (href && href !== "#" && typeof frappe !== "undefined" && frappe.set_route) {
        event.preventDefault();
        const route = href.replace(/^\/app\//, "").split("/");
        frappe.set_route(route);
        return false;
      }
    }
  } catch (e) {
    _gfWarn("Erro em gfCardClick:", e);
  }
};

// ─── NAVEGAÇÃO GENÉRICA ──────────────────────────────────────
window.gfNavigate = function (route, event) {
  try {
    if (event) event.preventDefault();
    if (typeof frappe !== "undefined" && frappe.set_route) {
      const parts = route.replace(/^\/app\//, "").split("/");
      frappe.set_route(parts);
    } else {
      window.location.href = route;
    }
  } catch (e) {
    window.location.href = route;
  }
  return false;
};

// ─── RETORNO AO DESK ORIGINAL ────────────────────────────────
window.gfReturnToOriginalDesk = function () {
  _gfLog("Usuário solicitou retorno ao Desk original.");
  removeOverlay();

  // Marca sessão para não reaplicar overlay nesta sessão
  try { sessionStorage.setItem("gf_overlay_disabled", "1"); } catch (e) {}

  // Força reload limpo do Desk
  if (typeof frappe !== "undefined" && frappe.set_route) {
    frappe.set_route("workspace");
  } else {
    window.location.href = "/app";
  }
};

// ─── OVERLAY GENÉRICO (não-Desk) ─────────────────────────────
function _renderGenericOverlay(page) {
  const existing = document.getElementById("gf-ui-overlay-root");
  if (existing) existing.remove();

  const root = document.createElement("div");
  root.id = "gf-ui-overlay-root";
  root.innerHTML = `<div class="gf-overlay-wrapper">
    <div class="gf-hero">
      <div class="gf-hero-text">
        <h1>${page.titulo_pagina || page.titulo}</h1>
        ${page.subtitulo_pagina ? `<p>${page.subtitulo_pagina}</p>` : ""}
      </div>
    </div>
    ${page.html_customizado || ""}
  </div>`;

  document.body.appendChild(root);
  hideOriginalDesk();
}

// ─── UTILIDADES ───────────────────────────────────────────────
function _gfGetUserName() {
  try {
    if (typeof frappe !== "undefined") {
      return frappe.session.full_name || frappe.session.user || "usuário";
    }
  } catch (e) {}
  return "usuário";
}

function _gfApplyThemeMode() {
  try {
    if (typeof frappe !== "undefined") {
      const tema = frappe.boot && frappe.boot.gf_tema_ativo;
      if (tema) document.body.setAttribute("data-gf-tema", tema);
    }
  } catch (e) {}
}

function _gfEsc(str) {
  return String(str).replace(/'/g, "\\'").replace(/"/g, "&quot;");
}
