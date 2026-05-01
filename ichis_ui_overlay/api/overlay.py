# Copyright (c) 2024, GREENFARMS and contributors
# GF UI Overlay — API Python

import frappe


@frappe.whitelist()
def get_overlay_settings():
    """Retorna configurações globais do GF UI Overlay Settings."""
    try:
        if not frappe.db.exists("DocType", "GF UI Overlay Settings"):
            return {"ativar_sobreposicoes": 0}

        doc = frappe.get_single("GF UI Overlay Settings")
        return {
            "ativar_sobreposicoes":          doc.ativar_sobreposicoes,
            "ativar_sobreposicao_desk":       doc.ativar_sobreposicao_desk,
            "modo_padrao_sobreposicao":       doc.modo_padrao_sobreposicao,
            "aplicar_por_usuario":            doc.aplicar_por_usuario,
            "aplicar_por_perfil":             doc.aplicar_por_perfil,
            "permitir_fallback_tela_original":doc.permitir_fallback_tela_original,
            "mostrar_botao_voltar_tela_original": doc.mostrar_botao_voltar_tela_original,
            "usar_tema_gf":                   doc.usar_tema_gf,
            "animacao_entrada":               doc.animacao_entrada,
            "tempo_animacao_ms":              doc.tempo_animacao_ms or 250,
            "diagnostico_console":            doc.diagnostico_console,
        }
    except Exception as e:
        frappe.logger().error(f"GF UI Overlay [get_overlay_settings]: {e}")
        return {"ativar_sobreposicoes": 0, "error": str(e)}


@frappe.whitelist()
def get_active_overlay_pages():
    """
    Retorna lista de páginas de overlay ativas para o usuário atual.
    Respeita permissões do Frappe e filtro aplicar_para_todos.
    """
    try:
        if not frappe.db.exists("DocType", "GF UI Overlay Page"):
            return []

        pages = frappe.get_all(
            "GF UI Overlay Page",
            filters={"ativo": 1},
            fields=[
                "name", "titulo", "nome_tecnico", "tipo_alvo", "rota_alvo",
                "doctype_alvo", "workspace_alvo", "report_alvo",
                "modo_sobreposicao", "ocultar_tela_original",
                "preservar_tela_original_em_memoria", "permitir_retorno_original",
                "aplicar_para_todos", "tipo_layout", "largura_maxima",
                "usar_largura_total", "exibir_busca_global",
                "exibir_area_boas_vindas", "exibir_cards_atalhos",
                "exibir_indicadores", "exibir_ultimas_atividades",
                "titulo_pagina", "subtitulo_pagina", "texto_boas_vindas",
                "icone_pagina", "imagem_fundo",
                "carregar_ao_abrir_rota", "recarregar_ao_mudar_rota",
                "observar_dom", "prioridade_execucao", "tempo_espera_ms",
                "habilitar_logs", "marcador_js", "versao_overlay",
                "html_customizado", "css_customizado", "js_customizado",
            ],
            order_by="prioridade_execucao asc",
        )

        # Enriquecer cada página com seus cards
        for page in pages:
            page["cards"] = _get_page_cards(page["name"])

        return pages

    except Exception as e:
        frappe.logger().error(f"GF UI Overlay [get_active_overlay_pages]: {e}")
        return []


@frappe.whitelist()
def get_overlay_page(name):
    """Retorna detalhes completos de uma página de overlay específica."""
    try:
        if not frappe.db.exists("GF UI Overlay Page", name):
            return None

        doc = frappe.get_doc("GF UI Overlay Page", name)
        data = doc.as_dict()
        data["cards"] = _get_page_cards(name)
        return data

    except Exception as e:
        frappe.logger().error(f"GF UI Overlay [get_overlay_page]: {e}")
        return None


@frappe.whitelist()
def get_default_desk_overlay():
    """
    Retorna a configuração padrão da tela GF Modern Desk.
    Busca o registro com nome_tecnico = 'gf_modern_desk'.
    """
    try:
        if not frappe.db.exists("DocType", "GF UI Overlay Page"):
            return None

        name = frappe.db.get_value(
            "GF UI Overlay Page",
            {"nome_tecnico": "gf_modern_desk", "ativo": 1},
            "name"
        )
        if not name:
            return None

        return get_overlay_page(name)

    except Exception as e:
        frappe.logger().error(f"GF UI Overlay [get_default_desk_overlay]: {e}")
        return None


def _get_page_cards(page_name):
    """Retorna cards de uma página, ordenados por ordem."""
    try:
        return frappe.get_all(
            "GF UI Overlay Card",
            filters={"parent": page_name, "ativo": 1},
            fields=[
                "titulo", "descricao", "icone", "tipo_acao",
                "rota_destino", "doctype_destino", "report_destino",
                "url_destino", "script_acao",
                "cor_fundo", "cor_texto", "cor_icone",
                "ordem", "abrir_em_nova_aba",
            ],
            order_by="ordem asc",
        )
    except Exception:
        return []
