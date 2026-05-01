# Copyright (c) 2024, GREENFARMS and contributors
# GF UI Overlay — Instalação com dados padrão

import frappe


def after_install():
    """Popula dados padrão após instalação do app."""
    frappe.logger().info("GF UI Overlay: iniciando população de dados padrão...")

    try:
        _create_overlay_settings()
        _create_modern_desk_page()
        frappe.db.commit()
        frappe.logger().info("GF UI Overlay: instalação concluída com sucesso.")
    except Exception as e:
        frappe.logger().error(f"GF UI Overlay [after_install]: {e}")


# ─────────────────────────────────────────────
# SETTINGS GLOBAL
# ─────────────────────────────────────────────

def _create_overlay_settings():
    if not frappe.db.exists("DocType", "GF UI Overlay Settings"):
        return

    defaults = {
        "ativar_sobreposicoes": 1,
        "ativar_sobreposicao_desk": 1,
        "modo_padrao_sobreposicao": "Substituir Tela",
        "permitir_fallback_tela_original": 1,
        "mostrar_botao_voltar_tela_original": 1,
        "usar_tema_gf": 1,
        "animacao_entrada": "Suave",
        "tempo_animacao_ms": 250,
        "diagnostico_console": 1,
        "aplicar_por_usuario": 0,
        "aplicar_por_perfil": 0,
    }

    for field, value in defaults.items():
        current = frappe.db.get_single_value("GF UI Overlay Settings", field)
        if current is None or current == "" or current == 0:
            frappe.db.set_single_value("GF UI Overlay Settings", field, value)


# ─────────────────────────────────────────────
# GF MODERN DESK PAGE
# ─────────────────────────────────────────────

def _create_modern_desk_page():
    if not frappe.db.exists("DocType", "GF UI Overlay Page"):
        return

    # Não sobrescrever se já existe
    if frappe.db.exists("GF UI Overlay Page", "gf_modern_desk"):
        return

    doc = frappe.new_doc("GF UI Overlay Page")
    doc.nome_tecnico              = "gf_modern_desk"
    doc.titulo                    = "GF Modern Desk"
    doc.descricao                 = "Tela inicial moderna em estilo corporativo, substitui o Desk padrão do ERPNext."
    doc.ativo                     = 1
    doc.tipo_alvo                 = "Desk"
    doc.rota_alvo                 = "/app"
    doc.modo_sobreposicao         = "Substituir Tela"
    doc.ocultar_tela_original     = 1
    doc.preservar_tela_original_em_memoria = 1
    doc.permitir_retorno_original = 1
    doc.aplicar_para_todos        = 1
    doc.tipo_layout               = "Home Moderna"
    doc.largura_maxima            = "1280px"
    doc.usar_largura_total        = 0
    doc.exibir_busca_global       = 1
    doc.exibir_area_boas_vindas   = 1
    doc.exibir_cards_atalhos      = 1
    doc.exibir_indicadores        = 1
    doc.exibir_ultimas_atividades = 1
    doc.titulo_pagina             = "Bem-vindo ao GREENFARMS"
    doc.subtitulo_pagina          = "Sistema de Gestão Integrada"
    doc.texto_boas_vindas         = "Selecione um módulo para começar ou use a busca rápida acima."
    doc.prioridade_execucao       = 1
    doc.tempo_espera_ms           = 100
    doc.carregar_ao_abrir_rota    = 1
    doc.recarregar_ao_mudar_rota  = 1
    doc.observar_dom              = 1
    doc.habilitar_logs            = 1
    doc.versao_overlay            = "1.0.0"

    # Cards padrão
    cards = [
        {
            "titulo": "Vendas",
            "descricao": "Pedidos, clientes e faturamento",
            "icone": "🛒",
            "tipo_acao": "Abrir Rota",
            "rota_destino": "/app/selling",
            "cor_fundo": "#dcfce7",
            "cor_icone": "#16a34a",
            "ordem": 1,
            "ativo": 1,
        },
        {
            "titulo": "Compras",
            "descricao": "Fornecedores, pedidos e recebimentos",
            "icone": "📦",
            "tipo_acao": "Abrir Rota",
            "rota_destino": "/app/buying",
            "cor_fundo": "#dbeafe",
            "cor_icone": "#2563eb",
            "ordem": 2,
            "ativo": 1,
        },
        {
            "titulo": "Estoque",
            "descricao": "Produtos, armazéns e movimentações",
            "icone": "🏭",
            "tipo_acao": "Abrir Rota",
            "rota_destino": "/app/stock",
            "cor_fundo": "#fef9c3",
            "cor_icone": "#ca8a04",
            "ordem": 3,
            "ativo": 1,
        },
        {
            "titulo": "Financeiro",
            "descricao": "Contas, pagamentos e conciliação",
            "icone": "💰",
            "tipo_acao": "Abrir Rota",
            "rota_destino": "/app/accounts",
            "cor_fundo": "#fce7f3",
            "cor_icone": "#db2777",
            "ordem": 4,
            "ativo": 1,
        },
        {
            "titulo": "Projetos",
            "descricao": "Tarefas, cronogramas e equipes",
            "icone": "📋",
            "tipo_acao": "Abrir Rota",
            "rota_destino": "/app/project",
            "cor_fundo": "#ede9fe",
            "cor_icone": "#7c3aed",
            "ordem": 5,
            "ativo": 1,
        },
        {
            "titulo": "CRM",
            "descricao": "Leads, oportunidades e contatos",
            "icone": "🤝",
            "tipo_acao": "Abrir Rota",
            "rota_destino": "/app/crm",
            "cor_fundo": "#ffedd5",
            "cor_icone": "#ea580c",
            "ordem": 6,
            "ativo": 1,
        },
        {
            "titulo": "Relatórios",
            "descricao": "Análises e relatórios gerenciais",
            "icone": "📊",
            "tipo_acao": "Abrir Rota",
            "rota_destino": "/app/query-report",
            "cor_fundo": "#f0fdf4",
            "cor_icone": "#15803d",
            "ordem": 7,
            "ativo": 1,
        },
        {
            "titulo": "RH",
            "descricao": "Colaboradores, folha e benefícios",
            "icone": "👥",
            "tipo_acao": "Abrir Rota",
            "rota_destino": "/app/hr",
            "cor_fundo": "#f0f9ff",
            "cor_icone": "#0369a1",
            "ordem": 8,
            "ativo": 1,
        },
        {
            "titulo": "Configurações",
            "descricao": "Administração e configurações do sistema",
            "icone": "⚙️",
            "tipo_acao": "Abrir Rota",
            "rota_destino": "/app/setup",
            "cor_fundo": "#f3f4f6",
            "cor_icone": "#374151",
            "ordem": 9,
            "ativo": 1,
        },
        {
            "titulo": "Tema Visual",
            "descricao": "Cores, fontes e identidade visual",
            "icone": "🎨",
            "tipo_acao": "Abrir Doctype",
            "doctype_destino": "GF Theme Settings",
            "rota_destino": "/app/gf-theme-settings",
            "cor_fundo": "#fdf4ff",
            "cor_icone": "#a21caf",
            "ordem": 10,
            "ativo": 1,
        },
    ]

    for c in cards:
        doc.append("cards", c)

    doc.insert(ignore_permissions=True)
