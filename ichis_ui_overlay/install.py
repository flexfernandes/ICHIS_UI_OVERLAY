# Copyright (c) 2024, GREENFARMS and contributors
# GF UI Overlay — Instalação v3.0
# CSS e JS completos embutidos no registro GF Modern Desk

import frappe


def after_install():
    frappe.logger().info("GF UI Overlay v3: instalando...")
    try:
        _create_settings()
        _create_modern_desk()
        frappe.db.commit()
        frappe.logger().info("GF UI Overlay v3: concluído.")
    except Exception as e:
        frappe.logger().error(f"GF UI Overlay after_install ERRO: {e}")
        import traceback
        frappe.logger().error(traceback.format_exc())


# ─────────────────────────────────────────────────────────────
# SETTINGS GLOBAL
# ─────────────────────────────────────────────────────────────

def _create_settings():
    if not frappe.db.exists("DocType", "GF UI Overlay Settings"):
        return
    defaults = {
        "ativar_sobreposicoes":               1,
        "ativar_sobreposicao_desk":           1,
        "modo_padrao_sobreposicao":           "Substituir Tela",
        "permitir_fallback_tela_original":    1,
        "mostrar_botao_voltar_tela_original": 1,
        "usar_tema_gf":                       1,
        "animacao_entrada":                   "Suave",
        "tempo_animacao_ms":                  250,
        "diagnostico_console":                1,
        "aplicar_por_usuario":                0,
        "aplicar_por_perfil":                 0,
    }
    for fieldname, value in defaults.items():
        try:
            cur = frappe.db.get_single_value("GF UI Overlay Settings", fieldname)
            if cur is None:
                frappe.db.set_single_value("GF UI Overlay Settings", fieldname, value)
        except Exception as e:
            frappe.logger().warning(f"GF UI Overlay settings '{fieldname}': {e}")


# ─────────────────────────────────────────────────────────────
# GF MODERN DESK
# ─────────────────────────────────────────────────────────────

def _create_modern_desk():
    if not frappe.db.exists("DocType", "GF UI Overlay Page"):
        frappe.logger().warning("DocType 'GF UI Overlay Page' não encontrado.")
        return

    existing = frappe.db.get_value(
        "GF UI Overlay Page", {"nome_tecnico": "gf_modern_desk"}, "name"
    )

    if existing:
        frappe.logger().info(f"GF Modern Desk já existe ({existing}) — atualizando CSS/JS.")
        doc = frappe.get_doc("GF UI Overlay Page", existing)
        doc.css_customizado = DESK_CSS
        doc.js_customizado  = DESK_JS
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return

    frappe.logger().info("GF UI Overlay: criando GF Modern Desk v3...")

    doc = frappe.new_doc("GF UI Overlay Page")
    doc.nome_tecnico                       = "gf_modern_desk"
    doc.titulo                             = "GF Modern Desk"
    doc.descricao                          = "Home moderna corporativa — substitui o Desk padrão do ERPNext."
    doc.ativo                              = 1
    doc.tipo_alvo                          = "Desk"
    doc.rota_alvo                          = "/app"
    doc.modo_sobreposicao                  = "Substituir Tela"
    doc.ocultar_tela_original              = 1
    doc.preservar_tela_original_em_memoria = 1
    doc.permitir_retorno_original          = 1
    doc.aplicar_para_todos                 = 1
    doc.tipo_layout                        = "Home Moderna"
    doc.largura_maxima                     = "1280px"
    doc.usar_largura_total                 = 0
    doc.exibir_busca_global                = 1
    doc.exibir_area_boas_vindas            = 1
    doc.exibir_cards_atalhos               = 1
    doc.exibir_indicadores                 = 1
    doc.exibir_ultimas_atividades          = 1
    doc.titulo_pagina                      = "Central de Gestão GREENFARMS"
    doc.subtitulo_pagina                   = "Sistema de Gestão Integrada"
    doc.texto_boas_vindas                  = "Gerencie sua operação com eficiência e clareza."
    doc.prioridade_execucao                = 1
    doc.tempo_espera_ms                    = 100
    doc.carregar_ao_abrir_rota             = 1
    doc.recarregar_ao_mudar_rota           = 1
    doc.observar_dom                       = 1
    doc.habilitar_logs                     = 1
    doc.versao_overlay                     = "3.0.0"
    doc.css_customizado                    = DESK_CSS
    doc.js_customizado                     = DESK_JS

    # Fase 1: salva o pai
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    # Fase 2: adiciona cards
    doc2 = frappe.get_doc("GF UI Overlay Page", doc.name)
    for card in DESK_CARDS:
        doc2.append("cards", card)
    doc2.save(ignore_permissions=True)
    frappe.db.commit()

    frappe.logger().info(f"GF Modern Desk criado com {len(DESK_CARDS)} cards.")


# ═════════════════════════════════════════════════════════════
# CSS CUSTOMIZADO — integra com variáveis do GF Theme Settings
# ═════════════════════════════════════════════════════════════

DESK_CSS = """
/* GF Modern Desk — CSS v3.0
   Lê variáveis do ichis_theme_control se instalado,
   usa fallbacks elegantes caso contrário. */

#gf-ui-overlay-root {
  --desk-font:    var(--gf-font-main, Inter, "Segoe UI", system-ui, Arial, sans-serif);
  --desk-bg:      var(--gf-bg-main, #f1f5f9);
  --desk-surface: var(--gf-bg-card, #ffffff);
  --desk-border:  var(--gf-border, #e2e8f0);
  --desk-text:    var(--gf-text-main, #0f172a);
  --desk-muted:   var(--gf-text-secondary, #64748b);
  --desk-accent:  var(--gf-accent, #16a34a);
  --desk-accent2: var(--gf-accent-dark, #166534);
  --desk-shadow:  var(--gf-shadow, rgba(15,23,42,0.07));
  --desk-hover:   var(--gf-hover, #f0fdf4);
  --desk-r:       14px;
  font-family: var(--desk-font) !important;
  background:  var(--desk-bg) !important;
  color:       var(--desk-text) !important;
  -webkit-font-smoothing: antialiased;
}

#gf-ui-overlay-root, #gf-ui-overlay-root * { box-sizing: border-box; }

/* ── TOPBAR ── */
.gfd-topbar {
  height: 52px;
  display: flex; align-items: center; gap: 16px;
  padding: 0 24px;
  background: var(--desk-surface);
  border-bottom: 1px solid var(--desk-border);
  flex-shrink: 0;
  box-shadow: 0 1px 4px var(--desk-shadow);
}
.gfd-brand {
  font-size: 15px; font-weight: 800;
  letter-spacing: 0.04em; color: var(--desk-accent);
  white-space: nowrap; flex-shrink: 0;
  font-family: var(--desk-font);
}
.gfd-search-wrap {
  flex: 1; max-width: 480px; margin: 0 auto;
  display: flex; align-items: center; gap: 10px;
  background: var(--desk-bg);
  border: 1.5px solid var(--desk-border);
  border-radius: 10px; padding: 0 14px;
  transition: border-color .15s, box-shadow .15s;
}
.gfd-search-wrap:focus-within {
  border-color: var(--desk-accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--desk-accent) 12%, transparent);
  background: var(--desk-surface);
}
.gfd-search-ico { color: var(--desk-muted); font-size: 15px; }
.gfd-search-inp {
  flex: 1; border: none; outline: none; background: transparent;
  font-family: var(--desk-font); font-size: 13px;
  color: var(--desk-text); padding: 9px 0;
}
.gfd-search-inp::placeholder { color: var(--desk-muted); }
.gfd-search-kbd {
  font-size: 10px; color: var(--desk-muted);
  background: var(--desk-border); border-radius: 4px;
  padding: 2px 6px; white-space: nowrap;
}
.gfd-user-badge {
  width: 34px; height: 34px; border-radius: 50%;
  background: var(--desk-accent); color: #fff;
  font-size: 14px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; cursor: default;
}

/* ── LAYOUT ── */
.gfd-layout { display: flex; flex: 1; overflow: hidden; }

/* ── SIDEBAR ── */
.gfd-sidebar {
  width: 220px; flex-shrink: 0;
  background: var(--desk-surface);
  border-right: 1px solid var(--desk-border);
  overflow-y: auto;
  display: flex; flex-direction: column;
  padding: 12px 0 16px;
}
.gfd-sidebar::-webkit-scrollbar { width: 4px; }
.gfd-sidebar::-webkit-scrollbar-thumb { background: var(--desk-border); border-radius: 2px; }
.gfd-nav-grp { display: flex; flex-direction: column; padding: 4px 10px 8px; }
.gfd-nav-grp + .gfd-nav-grp { border-top: 1px solid var(--desk-border); margin-top: 4px; padding-top: 10px; }
.gfd-nav-grp.bottom { margin-top: auto; }
.gfd-nav-lbl {
  font-size: 9.5px; font-weight: 700; letter-spacing: 0.09em;
  text-transform: uppercase; color: var(--desk-muted);
  padding: 0 8px; margin: 0 0 4px;
  font-family: var(--desk-font);
}
.gfd-nav-a {
  display: flex; align-items: center; gap: 9px;
  padding: 8px 10px; border-radius: 8px;
  font-size: 13px; font-weight: 500;
  color: var(--desk-muted); text-decoration: none;
  cursor: pointer; border: none; background: transparent;
  width: 100%; text-align: left;
  font-family: var(--desk-font);
  transition: background .12s, color .12s;
}
.gfd-nav-a:hover, .gfd-nav-a.active {
  background: color-mix(in srgb, var(--desk-accent) 10%, transparent);
  color: var(--desk-accent2);
}
.gfd-nav-a.small { font-size: 11.5px; opacity: .65; }
.gfd-nav-a.small:hover { opacity: 1; }

/* ── CONTEÚDO ── */
.gfd-content {
  flex: 1; overflow-y: auto;
  padding: 28px 32px 56px;
  display: flex; flex-direction: column; gap: 28px;
}
.gfd-content::-webkit-scrollbar { width: 5px; }
.gfd-content::-webkit-scrollbar-track { background: transparent; }
.gfd-content::-webkit-scrollbar-thumb { background: var(--desk-border); border-radius: 3px; }
.gfd-content::-webkit-scrollbar-thumb:hover { background: var(--desk-accent); }

/* ── HERO ── */
.gfd-hero {
  background: linear-gradient(135deg,
    color-mix(in srgb, var(--desk-accent) 7%, var(--desk-surface)),
    var(--desk-surface) 70%);
  border: 1px solid var(--desk-border);
  border-radius: var(--desk-r);
  padding: 28px 32px;
  display: flex; align-items: flex-start;
  justify-content: space-between;
  gap: 24px; flex-wrap: wrap;
}
.gfd-hero-left { flex: 1; min-width: 240px; }
.gfd-greeting { font-size: 13px; color: var(--desk-muted); margin: 0 0 6px; font-family: var(--desk-font); }
.gfd-greeting strong { color: var(--desk-accent); font-weight: 600; }
.gfd-hero-title {
  font-size: 26px; font-weight: 800; color: var(--desk-text);
  margin: 0 0 8px; letter-spacing: -0.025em; line-height: 1.15;
  font-family: var(--desk-font);
}
.gfd-hero-sub {
  font-size: 13.5px; color: var(--desk-muted);
  margin: 0; line-height: 1.6; font-family: var(--desk-font);
}
.gfd-kpis { display: flex; gap: 12px; flex-wrap: wrap; }
.gfd-kpi {
  display: flex; flex-direction: column; align-items: center;
  gap: 5px; background: var(--desk-surface);
  border: 1px solid var(--desk-border); border-radius: 12px;
  padding: 16px 20px; min-width: 100px;
  box-shadow: 0 1px 3px var(--desk-shadow); text-align: center;
}
.gfd-kpi-val {
  font-size: 24px; font-weight: 800; color: var(--desk-text);
  line-height: 1; font-family: var(--desk-font);
}
.gfd-kpi-lbl {
  font-size: 10px; font-weight: 600; color: var(--desk-muted);
  text-transform: uppercase; letter-spacing: 0.06em;
  font-family: var(--desk-font);
}

/* ── SEÇÃO ── */
.gfd-section { display: flex; flex-direction: column; gap: 14px; }
.gfd-sec-hd { display: flex; align-items: center; justify-content: space-between; }
.gfd-sec-title {
  font-size: 14px; font-weight: 700; color: var(--desk-text);
  margin: 0; display: flex; align-items: center; gap: 8px;
  font-family: var(--desk-font); letter-spacing: -0.01em;
}
.gfd-sec-title::before {
  content: ""; display: block; width: 3px; height: 16px;
  background: var(--desk-accent); border-radius: 2px;
}
.gfd-sec-link {
  font-size: 12px; color: var(--desk-accent);
  text-decoration: none; font-weight: 600;
  font-family: var(--desk-font);
}
.gfd-sec-link:hover { text-decoration: underline; }

/* ── GRID DE MÓDULOS ── */
.gfd-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
.gfd-card {
  display: flex; align-items: center; gap: 14px;
  background: var(--desk-surface);
  border: 1.5px solid var(--desk-border);
  border-radius: var(--desk-r);
  padding: 16px 18px; text-decoration: none;
  color: var(--desk-text); cursor: pointer;
  transition: transform .15s, box-shadow .15s, border-color .15s;
  position: relative; overflow: hidden;
  font-family: var(--desk-font);
}
.gfd-card::before {
  content: ""; position: absolute; left: 0; top: 0; bottom: 0;
  width: 3px; background: var(--card-acc, var(--desk-accent));
  opacity: 0; transition: opacity .15s; border-radius: 3px 0 0 3px;
}
.gfd-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px var(--desk-shadow);
  border-color: color-mix(in srgb, var(--card-acc, var(--desk-accent)) 35%, var(--desk-border));
}
.gfd-card:hover::before { opacity: 1; }
.gfd-card-ic {
  width: 44px; height: 44px; border-radius: 11px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; flex-shrink: 0;
  background: color-mix(in srgb, var(--card-acc, var(--desk-accent)) 12%, transparent);
}
.gfd-card-info { flex: 1; display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.gfd-card-title {
  font-size: 13.5px; font-weight: 600; color: var(--desk-text);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  font-family: var(--desk-font);
}
.gfd-card-desc {
  font-size: 11.5px; color: var(--desk-muted);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  font-family: var(--desk-font);
}
.gfd-card-arr {
  color: var(--desk-muted); font-size: 16px;
  transition: color .15s, transform .15s; flex-shrink: 0;
}
.gfd-card:hover .gfd-card-arr { color: var(--card-acc, var(--desk-accent)); transform: translateX(3px); }

/* ── ATIVIDADES ── */
.gfd-acts {
  background: var(--desk-surface);
  border: 1.5px solid var(--desk-border);
  border-radius: var(--desk-r); overflow: hidden;
}
.gfd-act-row {
  display: flex; align-items: center; gap: 14px;
  padding: 13px 20px;
  border-bottom: 1px solid var(--desk-border);
  transition: background .12s; font-family: var(--desk-font);
}
.gfd-act-row:last-child { border-bottom: none; }
.gfd-act-row:hover { background: var(--desk-hover); }
.gfd-act-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--desk-accent); flex-shrink: 0; }
.gfd-act-body { flex: 1; min-width: 0; }
.gfd-act-title {
  font-size: 13px; font-weight: 500; color: var(--desk-text);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  margin: 0 0 2px; font-family: var(--desk-font);
}
.gfd-act-sub { font-size: 11.5px; color: var(--desk-muted); margin: 0; font-family: var(--desk-font); }
.gfd-act-time { font-size: 11px; color: var(--desk-muted); flex-shrink: 0; white-space: nowrap; }
.gfd-act-empty { padding: 28px; text-align: center; font-size: 13px; color: var(--desk-muted); font-family: var(--desk-font); }

/* ── SKELETON ── */
.gfd-sk {
  background: linear-gradient(90deg, var(--desk-border) 25%,
    color-mix(in srgb, var(--desk-border) 50%, transparent) 50%, var(--desk-border) 75%);
  background-size: 200% 100%; animation: gfdSk 1.4s infinite; border-radius: 4px;
}
@keyframes gfdSk { 0%{background-position:200% 0} 100%{background-position:-200% 0} }

/* ── TEMA BLACK ── */
body[data-gf-tema="Black"] #gf-ui-overlay-root {
  --desk-bg: #020617; --desk-surface: #0f172a; --desk-border: #1e293b;
  --desk-text: #f1f5f9; --desk-muted: #94a3b8;
  --desk-accent: #22c55e; --desk-accent2: #16a34a;
  --desk-shadow: rgba(0,0,0,.4); --desk-hover: #064e3b;
}

/* ── RESPONSIVO ── */
@media (max-width:900px) {
  .gfd-sidebar { display: none; }
  .gfd-content { padding: 18px 16px 40px; }
  .gfd-grid { grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); }
}
@media (max-width:600px) {
  .gfd-hero { padding: 20px; flex-direction: column; }
  .gfd-kpis { width: 100%; }
  .gfd-grid { grid-template-columns: 1fr 1fr; }
  .gfd-content { padding: 14px 12px 40px; gap: 20px; }
  .gfd-topbar { padding: 0 14px; }
}
"""

# ═════════════════════════════════════════════════════════════
# JS CUSTOMIZADO — renderiza HTML e carrega dados dinâmicos
# ═════════════════════════════════════════════════════════════

DESK_JS = """
/* GF Modern Desk — JS Customizado v3.0
   Executado pelo gf_ui_overlay.js após inserir o overlay.
   1. Injeta o HTML completo no root
   2. Aplica variáveis de fonte do GF Theme Settings
   3. Carrega KPIs e atividades reais via frappe.call */

(function gfModernDeskRender() {

  var root = document.getElementById("gf-ui-overlay-root");
  if (!root) return;

  // 1. Sincronizar variáveis de fonte e cor do GF Theme Settings
  try {
    var cs = getComputedStyle(document.documentElement);
    var themeVars = [
      ["--gf-font-main",      "--desk-font"],
      ["--gf-bg-main",        "--desk-bg"],
      ["--gf-bg-card",        "--desk-surface"],
      ["--gf-border",         "--desk-border"],
      ["--gf-text-main",      "--desk-text"],
      ["--gf-text-secondary", "--desk-muted"],
      ["--gf-accent",         "--desk-accent"],
      ["--gf-accent-dark",    "--desk-accent2"],
      ["--gf-shadow",         "--desk-shadow"],
      ["--gf-hover",          "--desk-hover"],
    ];
    themeVars.forEach(function(p) {
      var v = cs.getPropertyValue(p[0]).trim();
      if (v) {
        root.style.setProperty(p[1], v);
        // Aplicar fonte também no body do overlay
        if (p[0] === "--gf-font-main") root.style.fontFamily = v;
      }
    });
  } catch(e) {}

  // 2. Injetar HTML completo do Modern Desk
  var userName = "usuário";
  var fullName = "usuário";
  try {
    userName = (frappe.session.user || "").split("@")[0] || "usuário";
    fullName = frappe.session.full_name || frappe.boot.full_name || userName;
  } catch(e) {}

  var h = new Date().getHours();
  var greet = h < 12 ? "Bom dia" : h < 18 ? "Boa tarde" : "Boa noite";
  var dateStr = new Date().toLocaleDateString("pt-BR", {weekday:"short", day:"2-digit", month:"short"});

  // Cards vêm do objeto page carregado pelo overlay engine
  var page = window.gfCurrentPageData || {};
  var cards = (page.cards || []).filter(function(c){ return c.ativo !== 0; });
  var showBack = (window.gfOverlaySettings || {}).mostrar_botao_voltar_tela_original;

  var cardsHtml = cards.length ? cards.map(function(c) {
    var bg  = c.cor_fundo || "transparent";
    var acc = c.cor_icone || "var(--desk-accent)";
    var href = c.rota_destino || (c.doctype_destino
      ? "/app/" + (c.doctype_destino || "").toLowerCase().replace(/\\s+/g,"-")
      : "#");
    return (
      '<a class="gfd-card" href="' + href + '"' +
      ' onclick="return gfNav(\\'' + href + '\\',event)"' +
      ' style="--card-acc:' + acc + '">' +
        '<div class="gfd-card-ic" style="background:' + bg + '">' + (c.icone||"📌") + '</div>' +
        '<div class="gfd-card-info">' +
          '<span class="gfd-card-title">' + (c.titulo||"") + '</span>' +
          '<span class="gfd-card-desc">'  + (c.descricao||"") + '</span>' +
        '</div>' +
        '<span class="gfd-card-arr">→</span>' +
      '</a>'
    );
  }).join("") : _defaultCards();

  var skRows = "";
  for(var i=0;i<5;i++) skRows += (
    '<div class="gfd-act-row">' +
      '<div class="gfd-sk" style="width:7px;height:7px;border-radius:50%;flex-shrink:0"></div>' +
      '<div class="gfd-act-body">' +
        '<div class="gfd-sk" style="height:13px;width:58%;margin-bottom:5px"></div>' +
        '<div class="gfd-sk" style="height:11px;width:38%"></div>' +
      '</div>' +
      '<div class="gfd-sk" style="height:11px;width:28px"></div>' +
    '</div>'
  );

  root.innerHTML = (
    '<div class="gfd-topbar">' +
      '<span class="gfd-brand">&#127807; GREENFARMS</span>' +
      '<div class="gfd-search-wrap">' +
        '<span class="gfd-search-ico">&#128269;</span>' +
        '<input id="gfd-search" class="gfd-search-inp" type="text"' +
        ' placeholder="Buscar documentos, módulos... (pressione /)" autocomplete="off"/>' +
        '<span class="gfd-search-kbd">Enter</span>' +
      '</div>' +
      '<div class="gfd-user-badge" title="' + userName + '">' + fullName.charAt(0).toUpperCase() + '</div>' +
    '</div>' +

    '<div class="gfd-layout">' +

      '<nav class="gfd-sidebar">' +
        '<div class="gfd-nav-grp">' +
          '<p class="gfd-nav-lbl">Início</p>' +
          '<a class="gfd-nav-a active" href="/app" onclick="return gfNav(\\'/app\\',event)">&#127968; Início</a>' +
        '</div>' +
        '<div class="gfd-nav-grp">' +
          '<p class="gfd-nav-lbl">Operações</p>' +
          '<a class="gfd-nav-a" href="/app/selling"      onclick="return gfNav(\\'/app/selling\\',event)">&#128722; Vendas</a>' +
          '<a class="gfd-nav-a" href="/app/buying"       onclick="return gfNav(\\'/app/buying\\',event)">&#128230; Compras</a>' +
          '<a class="gfd-nav-a" href="/app/stock"        onclick="return gfNav(\\'/app/stock\\',event)">&#127981; Estoque</a>' +
          '<a class="gfd-nav-a" href="/app/accounts"     onclick="return gfNav(\\'/app/accounts\\',event)">&#128176; Financeiro</a>' +
          '<a class="gfd-nav-a" href="/app/hr"           onclick="return gfNav(\\'/app/hr\\',event)">&#128101; RH</a>' +
          '<a class="gfd-nav-a" href="/app/project"      onclick="return gfNav(\\'/app/project\\',event)">&#128203; Projetos</a>' +
          '<a class="gfd-nav-a" href="/app/crm"          onclick="return gfNav(\\'/app/crm\\',event)">&#129309; CRM</a>' +
        '</div>' +
        '<div class="gfd-nav-grp">' +
          '<p class="gfd-nav-lbl">Análises</p>' +
          '<a class="gfd-nav-a" href="/app/query-report" onclick="return gfNav(\\'/app/query-report\\',event)">&#128202; Relatórios</a>' +
        '</div>' +
        '<div class="gfd-nav-grp bottom">' +
          '<p class="gfd-nav-lbl">Sistema</p>' +
          '<a class="gfd-nav-a" href="/app/setup" onclick="return gfNav(\\'/app/setup\\',event)">&#9881; Configurações</a>' +
          (showBack ? '<button class="gfd-nav-a small" onclick="gfReturnToOriginalDesk()">&#8617; Desk Original</button>' : '') +
        '</div>' +
      '</nav>' +

      '<main class="gfd-content">' +

        '<div class="gfd-hero">' +
          '<div class="gfd-hero-left">' +
            '<p class="gfd-greeting">' + greet + ', <strong>' + fullName + '</strong> &#128075;</p>' +
            '<h1 class="gfd-hero-title">' + (page.titulo_pagina || "Central de Gestão GREENFARMS") + '</h1>' +
            '<p class="gfd-hero-sub">'   + (page.texto_boas_vindas || "Gerencie sua operação com eficiência e clareza.") + '</p>' +
          '</div>' +
          '<div class="gfd-kpis">' +
            '<div class="gfd-kpi"><span class="gfd-kpi-val" id="gfd-kpi-notif">—</span><span class="gfd-kpi-lbl">Notificações</span></div>' +
            '<div class="gfd-kpi"><span class="gfd-kpi-val" id="gfd-kpi-date">' + dateStr + '</span><span class="gfd-kpi-lbl">Hoje</span></div>' +
          '</div>' +
        '</div>' +

        '<div class="gfd-section">' +
          '<div class="gfd-sec-hd"><h2 class="gfd-sec-title">Módulos do Sistema</h2></div>' +
          '<div class="gfd-grid">' + cardsHtml + '</div>' +
        '</div>' +

        '<div class="gfd-section">' +
          '<div class="gfd-sec-hd">' +
            '<h2 class="gfd-sec-title">Atividades Recentes</h2>' +
            '<a class="gfd-sec-link" href="/app/activity" onclick="return gfNav(\\'/app/activity\\',event)">Ver todas →</a>' +
          '</div>' +
          '<div class="gfd-acts" id="gfd-activity-panel">' + skRows + '</div>' +
        '</div>' +

      '</main>' +
    '</div>'
  );

  // 3. Busca global
  var inp = document.getElementById("gfd-search");
  if (inp) {
    inp.addEventListener("keydown", function(e) {
      if (e.key !== "Enter") return;
      var q = inp.value.trim(); if (!q) return; e.preventDefault();
      try {
        if (typeof frappe !== "undefined" && frappe.utils && frappe.utils.global_search)
          frappe.utils.global_search(q);
        else window.location.href = "/app?q=" + encodeURIComponent(q);
      } catch(ex) { window.location.href = "/app?q=" + encodeURIComponent(q); }
    });
    document.addEventListener("keydown", function(e) {
      if (e.key === "/" && !["INPUT","TEXTAREA"].includes(document.activeElement.tagName)) {
        e.preventDefault(); inp.focus(); inp.select();
      }
    });
  }

  // 4. Notificações
  try {
    if (typeof frappe !== "undefined" && frappe.call) {
      frappe.call({
        method: "frappe.desk.notifications.get_open_count",
        callback: function(r) {
          var el = document.getElementById("gfd-kpi-notif");
          if (el && r && r.message) el.textContent = r.message.total_count || "0";
        }, error: function(){}
      });
    }
  } catch(e) {}

  // 5. Atividades
  try {
    if (typeof frappe !== "undefined" && frappe.call) {
      frappe.call({
        method: "frappe.client.get_list",
        args: {
          doctype: "Activity Log",
          fields: ["subject","full_name","user","creation"],
          filters: [["user","=",frappe.session.user]],
          limit: 7, order_by: "creation desc"
        },
        callback: function(r) {
          var panel = document.getElementById("gfd-activity-panel"); if (!panel) return;
          var items = (r && r.message) ? r.message : [];
          if (!items.length) { panel.innerHTML = '<div class="gfd-act-empty">Nenhuma atividade recente.</div>'; return; }
          panel.innerHTML = items.map(function(a) {
            var d = (Date.now() - new Date(a.creation).getTime()) / 1000;
            var t = d<60?"agora":d<3600?Math.floor(d/60)+"min":d<86400?Math.floor(d/3600)+"h":Math.floor(d/86400)+"d";
            return '<div class="gfd-act-row"><div class="gfd-act-dot"></div>' +
              '<div class="gfd-act-body">' +
                '<p class="gfd-act-title">' + (a.subject||"Atividade") + '</p>' +
                '<p class="gfd-act-sub">' + (a.full_name||a.user||"") + '</p>' +
              '</div><span class="gfd-act-time">' + t + '</span></div>';
          }).join("");
        }, error: function(){}
      });
    }
  } catch(e) {}

  function _defaultCards() {
    return [
      {t:"Vendas",       d:"Pedidos e faturamento",      i:"\\uD83D\\uDED2",r:"/app/selling",      c:"#16a34a"},
      {t:"Compras",      d:"Fornecedores e recebimentos", i:"\\uD83D\\uDCE6",r:"/app/buying",       c:"#2563eb"},
      {t:"Estoque",      d:"Produtos e armazéns",         i:"\\uD83C\\uDFED",r:"/app/stock",        c:"#ca8a04"},
      {t:"Financeiro",   d:"Contas e pagamentos",         i:"\\uD83D\\uDCB0",r:"/app/accounts",     c:"#db2777"},
      {t:"Projetos",     d:"Tarefas e cronogramas",       i:"\\uD83D\\uDCCB",r:"/app/project",      c:"#7c3aed"},
      {t:"CRM",          d:"Leads e oportunidades",       i:"\\uD83E\\uDD1D",r:"/app/crm",          c:"#ea580c"},
      {t:"RH",           d:"Colaboradores e folha",       i:"\\uD83D\\uDC65",r:"/app/hr",           c:"#0369a1"},
      {t:"Relatórios",   d:"Análises gerenciais",         i:"\\uD83D\\uDCCA",r:"/app/query-report", c:"#15803d"},
      {t:"Configurações",d:"Administração do sistema",    i:"\\u2699\\uFE0F",r:"/app/setup",        c:"#374151"},
    ].map(function(d){
      return '<a class="gfd-card" href="'+d.r+'" onclick="return gfNav(\\''+d.r+'\\',event)" style="--card-acc:'+d.c+'">' +
        '<div class="gfd-card-ic">'+d.i+'</div>' +
        '<div class="gfd-card-info"><span class="gfd-card-title">'+d.t+'</span><span class="gfd-card-desc">'+d.d+'</span></div>' +
        '<span class="gfd-card-arr">→</span></a>';
    }).join("");
  }

})();
"""


# ─────────────────────────────────────────────────────────────
# CARDS PADRÃO
# ─────────────────────────────────────────────────────────────

DESK_CARDS = [
    {"titulo": "Vendas",        "descricao": "Pedidos, clientes e faturamento",    "icone": "🛒", "tipo_acao": "Abrir Rota",    "rota_destino": "/app/selling",      "cor_fundo": "#f0fdf4", "cor_icone": "#16a34a", "ordem": 1,  "ativo": 1, "abrir_em_nova_aba": 0},
    {"titulo": "Compras",       "descricao": "Fornecedores e recebimentos",        "icone": "📦", "tipo_acao": "Abrir Rota",    "rota_destino": "/app/buying",       "cor_fundo": "#eff6ff", "cor_icone": "#2563eb", "ordem": 2,  "ativo": 1, "abrir_em_nova_aba": 0},
    {"titulo": "Estoque",       "descricao": "Produtos, armazéns e movimentações", "icone": "🏭", "tipo_acao": "Abrir Rota",    "rota_destino": "/app/stock",        "cor_fundo": "#fefce8", "cor_icone": "#ca8a04", "ordem": 3,  "ativo": 1, "abrir_em_nova_aba": 0},
    {"titulo": "Financeiro",    "descricao": "Contas, pagamentos e conciliação",   "icone": "💰", "tipo_acao": "Abrir Rota",    "rota_destino": "/app/accounts",     "cor_fundo": "#fdf2f8", "cor_icone": "#db2777", "ordem": 4,  "ativo": 1, "abrir_em_nova_aba": 0},
    {"titulo": "Projetos",      "descricao": "Tarefas, cronogramas e equipes",     "icone": "📋", "tipo_acao": "Abrir Rota",    "rota_destino": "/app/project",      "cor_fundo": "#f5f3ff", "cor_icone": "#7c3aed", "ordem": 5,  "ativo": 1, "abrir_em_nova_aba": 0},
    {"titulo": "CRM",           "descricao": "Leads, oportunidades e contatos",    "icone": "🤝", "tipo_acao": "Abrir Rota",    "rota_destino": "/app/crm",          "cor_fundo": "#fff7ed", "cor_icone": "#ea580c", "ordem": 6,  "ativo": 1, "abrir_em_nova_aba": 0},
    {"titulo": "RH",            "descricao": "Colaboradores, folha e benefícios",  "icone": "👥", "tipo_acao": "Abrir Rota",    "rota_destino": "/app/hr",           "cor_fundo": "#f0f9ff", "cor_icone": "#0369a1", "ordem": 7,  "ativo": 1, "abrir_em_nova_aba": 0},
    {"titulo": "Relatórios",    "descricao": "Análises e relatórios gerenciais",   "icone": "📊", "tipo_acao": "Abrir Rota",    "rota_destino": "/app/query-report", "cor_fundo": "#f0fdf4", "cor_icone": "#15803d", "ordem": 8,  "ativo": 1, "abrir_em_nova_aba": 0},
    {"titulo": "Configurações", "descricao": "Administração e configurações",      "icone": "⚙️", "tipo_acao": "Abrir Rota",    "rota_destino": "/app/setup",        "cor_fundo": "#f8fafc", "cor_icone": "#374151", "ordem": 9,  "ativo": 1, "abrir_em_nova_aba": 0},
    {"titulo": "Tema Visual",   "descricao": "Cores, fontes e identidade visual",  "icone": "🎨", "tipo_acao": "Abrir Doctype", "doctype_destino": "GF Theme Settings", "cor_fundo": "#fdf4ff", "cor_icone": "#a21caf", "ordem": 10, "ativo": 1, "abrir_em_nova_aba": 0},
]
