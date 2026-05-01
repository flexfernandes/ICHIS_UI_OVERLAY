# Copyright (c) 2024, GREENFARMS and contributors
# GF UI Overlay — Instalação com dados padrão

import frappe


def after_install():
    frappe.logger().info("GF UI Overlay: instalando dados padrão...")
    try:
        _create_settings()
        _create_modern_desk()
        frappe.db.commit()
        frappe.logger().info("GF UI Overlay: instalação concluída com sucesso.")
    except Exception as e:
        frappe.logger().error(f"GF UI Overlay after_install ERRO: {e}")
        import traceback
        frappe.logger().error(traceback.format_exc())


# ─────────────────────────────────────────────
# SETTINGS GLOBAL
# ─────────────────────────────────────────────

def _create_settings():
    if not frappe.db.exists("DocType", "GF UI Overlay Settings"):
        frappe.logger().warning("GF UI Overlay: DocType 'GF UI Overlay Settings' não encontrado.")
        return

    defaults = {
        "ativar_sobreposicoes":              1,
        "ativar_sobreposicao_desk":          1,
        "modo_padrao_sobreposicao":          "Substituir Tela",
        "permitir_fallback_tela_original":   1,
        "mostrar_botao_voltar_tela_original":1,
        "usar_tema_gf":                      1,
        "animacao_entrada":                  "Suave",
        "tempo_animacao_ms":                 250,
        "diagnostico_console":               1,
        "aplicar_por_usuario":               0,
        "aplicar_por_perfil":                0,
    }

    for fieldname, value in defaults.items():
        try:
            current = frappe.db.get_single_value("GF UI Overlay Settings", fieldname)
            # Para campos Check (int), considera 0 como "não preenchido"
            # somente se o campo for de texto vazio
            needs_set = (current is None or current == "")
            if fieldname in ("ativar_sobreposicoes", "ativar_sobreposicao_desk",
                             "permitir_fallback_tela_original", "mostrar_botao_voltar_tela_original",
                             "usar_tema_gf", "diagnostico_console"):
                # Campos Check: só preenche se None (nunca foi setado)
                needs_set = (current is None)
            if needs_set:
                frappe.db.set_single_value("GF UI Overlay Settings", fieldname, value)
        except Exception as e:
            frappe.logger().warning(f"GF UI Overlay settings campo '{fieldname}': {e}")

    frappe.logger().info("GF UI Overlay: Settings configurado.")


# ─────────────────────────────────────────────
# GF MODERN DESK PAGE
# ─────────────────────────────────────────────

def _create_modern_desk():
    if not frappe.db.exists("DocType", "GF UI Overlay Page"):
        frappe.logger().warning("GF UI Overlay: DocType 'GF UI Overlay Page' não encontrado.")
        return

    # Não sobrescreve se já existe
    existing = frappe.db.get_value("GF UI Overlay Page", {"nome_tecnico": "gf_modern_desk"}, "name")
    if existing:
        frappe.logger().info(f"GF UI Overlay: GF Modern Desk já existe ({existing}), pulando.")
        return

    frappe.logger().info("GF UI Overlay: criando GF Modern Desk...")

    doc = frappe.new_doc("GF UI Overlay Page")
    doc.nome_tecnico                     = "gf_modern_desk"
    doc.titulo                           = "GF Modern Desk"
    doc.descricao                        = "Home moderna corporativa — substitui o Desk padrão do ERPNext."
    doc.ativo                            = 1
    doc.tipo_alvo                        = "Desk"
    doc.rota_alvo                        = "/app"
    doc.modo_sobreposicao                = "Substituir Tela"
    doc.ocultar_tela_original            = 1
    doc.preservar_tela_original_em_memoria = 1
    doc.permitir_retorno_original        = 1
    doc.aplicar_para_todos               = 1
    doc.tipo_layout                      = "Home Moderna"
    doc.largura_maxima                   = "1280px"
    doc.usar_largura_total               = 0
    doc.exibir_busca_global              = 1
    doc.exibir_area_boas_vindas          = 1
    doc.exibir_cards_atalhos             = 1
    doc.exibir_indicadores               = 1
    doc.exibir_ultimas_atividades        = 1
    doc.titulo_pagina                    = "Central de Gestão GREENFARMS"
    doc.subtitulo_pagina                 = "Sistema de Gestão Integrada"
    doc.texto_boas_vindas                = "Gerencie sua operação com eficiência e clareza."
    doc.prioridade_execucao              = 1
    doc.tempo_espera_ms                  = 100
    doc.carregar_ao_abrir_rota           = 1
    doc.recarregar_ao_mudar_rota         = 1
    doc.observar_dom                     = 1
    doc.habilitar_logs                   = 1
    doc.versao_overlay                   = "2.0.0"

    # Inserir SEM os cards primeiro para garantir que o pai existe no banco
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    # Agora inserir os cards separadamente via frappe.get_doc para recarregar
    doc_reloaded = frappe.get_doc("GF UI Overlay Page", doc.name)
    for card_data in _default_cards():
        doc_reloaded.append("cards", card_data)
    doc_reloaded.save(ignore_permissions=True)
    frappe.db.commit()

    frappe.logger().info(f"GF UI Overlay: GF Modern Desk criado com {len(_default_cards())} cards.")


def _default_cards():
    return [
        {
            "titulo":          "Vendas",
            "descricao":       "Pedidos, clientes e faturamento",
            "icone":           "🛒",
            "tipo_acao":       "Abrir Rota",
            "rota_destino":    "/app/selling",
            "cor_fundo":       "#f0fdf4",
            "cor_icone":       "#16a34a",
            "ordem":           1,
            "ativo":           1,
            "abrir_em_nova_aba": 0,
        },
        {
            "titulo":          "Compras",
            "descricao":       "Fornecedores e recebimentos",
            "icone":           "📦",
            "tipo_acao":       "Abrir Rota",
            "rota_destino":    "/app/buying",
            "cor_fundo":       "#eff6ff",
            "cor_icone":       "#2563eb",
            "ordem":           2,
            "ativo":           1,
            "abrir_em_nova_aba": 0,
        },
        {
            "titulo":          "Estoque",
            "descricao":       "Produtos, armazéns e movimentações",
            "icone":           "🏭",
            "tipo_acao":       "Abrir Rota",
            "rota_destino":    "/app/stock",
            "cor_fundo":       "#fefce8",
            "cor_icone":       "#ca8a04",
            "ordem":           3,
            "ativo":           1,
            "abrir_em_nova_aba": 0,
        },
        {
            "titulo":          "Financeiro",
            "descricao":       "Contas, pagamentos e conciliação",
            "icone":           "💰",
            "tipo_acao":       "Abrir Rota",
            "rota_destino":    "/app/accounts",
            "cor_fundo":       "#fdf2f8",
            "cor_icone":       "#db2777",
            "ordem":           4,
            "ativo":           1,
            "abrir_em_nova_aba": 0,
        },
        {
            "titulo":          "Projetos",
            "descricao":       "Tarefas, cronogramas e equipes",
            "icone":           "📋",
            "tipo_acao":       "Abrir Rota",
            "rota_destino":    "/app/project",
            "cor_fundo":       "#f5f3ff",
            "cor_icone":       "#7c3aed",
            "ordem":           5,
            "ativo":           1,
            "abrir_em_nova_aba": 0,
        },
        {
            "titulo":          "CRM",
            "descricao":       "Leads, oportunidades e contatos",
            "icone":           "🤝",
            "tipo_acao":       "Abrir Rota",
            "rota_destino":    "/app/crm",
            "cor_fundo":       "#fff7ed",
            "cor_icone":       "#ea580c",
            "ordem":           6,
            "ativo":           1,
            "abrir_em_nova_aba": 0,
        },
        {
            "titulo":          "RH",
            "descricao":       "Colaboradores, folha e benefícios",
            "icone":           "👥",
            "tipo_acao":       "Abrir Rota",
            "rota_destino":    "/app/hr",
            "cor_fundo":       "#f0f9ff",
            "cor_icone":       "#0369a1",
            "ordem":           7,
            "ativo":           1,
            "abrir_em_nova_aba": 0,
        },
        {
            "titulo":          "Relatórios",
            "descricao":       "Análises e relatórios gerenciais",
            "icone":           "📊",
            "tipo_acao":       "Abrir Rota",
            "rota_destino":    "/app/query-report",
            "cor_fundo":       "#f0fdf4",
            "cor_icone":       "#15803d",
            "ordem":           8,
            "ativo":           1,
            "abrir_em_nova_aba": 0,
        },
        {
            "titulo":          "Configurações",
            "descricao":       "Administração e configurações do sistema",
            "icone":           "⚙️",
            "tipo_acao":       "Abrir Rota",
            "rota_destino":    "/app/setup",
            "cor_fundo":       "#f8fafc",
            "cor_icone":       "#374151",
            "ordem":           9,
            "ativo":           1,
            "abrir_em_nova_aba": 0,
        },
        {
            "titulo":          "Tema Visual",
            "descricao":       "Cores, fontes e identidade visual",
            "icone":           "🎨",
            "tipo_acao":       "Abrir Doctype",
            "doctype_destino": "GF Theme Settings",
            "rota_destino":    "/app/gf-theme-settings",
            "cor_fundo":       "#fdf4ff",
            "cor_icone":       "#a21caf",
            "ordem":           10,
            "ativo":           1,
            "abrir_em_nova_aba": 0,
        },
    ]
