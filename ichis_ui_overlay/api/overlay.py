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
            "ativar_sobreposicoes":              int(doc.ativar_sobreposicoes or 0),
            "ativar_sobreposicao_desk":           int(doc.ativar_sobreposicao_desk or 0),
            "modo_padrao_sobreposicao":           doc.modo_padrao_sobreposicao or "Substituir Tela",
            "aplicar_por_usuario":               int(doc.aplicar_por_usuario or 0),
            "aplicar_por_perfil":                int(doc.aplicar_por_perfil or 0),
            "permitir_fallback_tela_original":   int(doc.permitir_fallback_tela_original or 0),
            "mostrar_botao_voltar_tela_original":int(doc.mostrar_botao_voltar_tela_original or 0),
            "usar_tema_gf":                      int(doc.usar_tema_gf or 0),
            "animacao_entrada":                  doc.animacao_entrada or "Suave",
            "tempo_animacao_ms":                 int(doc.tempo_animacao_ms or 250),
            "diagnostico_console":               int(doc.diagnostico_console or 0),
        }
    except Exception as e:
        frappe.logger().error(f"GF UI Overlay [get_overlay_settings]: {e}")
        return {"ativar_sobreposicoes": 0, "error": str(e)}


@frappe.whitelist()
def get_active_overlay_pages():
    """
    Retorna lista de páginas de overlay ativas com seus cards.
    Usa frappe.get_doc para garantir que os child rows sejam carregados corretamente.
    """
    try:
        if not frappe.db.exists("DocType", "GF UI Overlay Page"):
            return []

        # Busca os names das páginas ativas
        page_names = frappe.get_all(
            "GF UI Overlay Page",
            filters={"ativo": 1},
            fields=["name"],
            order_by="prioridade_execucao asc",
        )

        result = []
        for row in page_names:
            # Usa get_doc para carregar o documento completo COM child rows
            doc = frappe.get_doc("GF UI Overlay Page", row["name"])
            data = {
                "name":                          doc.name,
                "titulo":                        doc.titulo,
                "nome_tecnico":                  doc.nome_tecnico,
                "tipo_alvo":                     doc.tipo_alvo,
                "rota_alvo":                     doc.rota_alvo or "",
                "doctype_alvo":                  doc.doctype_alvo or "",
                "workspace_alvo":                doc.workspace_alvo or "",
                "report_alvo":                   doc.report_alvo or "",
                "modo_sobreposicao":             doc.modo_sobreposicao,
                "ocultar_tela_original":         int(doc.ocultar_tela_original or 0),
                "preservar_tela_original_em_memoria": int(doc.preservar_tela_original_em_memoria or 0),
                "permitir_retorno_original":     int(doc.permitir_retorno_original or 0),
                "aplicar_para_todos":            int(doc.aplicar_para_todos or 0),
                "tipo_layout":                   doc.tipo_layout or "Home Moderna",
                "largura_maxima":                doc.largura_maxima or "1280px",
                "usar_largura_total":            int(doc.usar_largura_total or 0),
                "exibir_busca_global":           int(doc.exibir_busca_global or 0),
                "exibir_area_boas_vindas":       int(doc.exibir_area_boas_vindas or 0),
                "exibir_cards_atalhos":          int(doc.exibir_cards_atalhos or 0),
                "exibir_indicadores":            int(doc.exibir_indicadores or 0),
                "exibir_ultimas_atividades":     int(doc.exibir_ultimas_atividades or 0),
                "titulo_pagina":                 doc.titulo_pagina or "",
                "subtitulo_pagina":              doc.subtitulo_pagina or "",
                "texto_boas_vindas":             doc.texto_boas_vindas or "",
                "icone_pagina":                  doc.icone_pagina or "",
                "imagem_fundo":                  doc.imagem_fundo or "",
                "carregar_ao_abrir_rota":        int(doc.carregar_ao_abrir_rota or 0),
                "recarregar_ao_mudar_rota":      int(doc.recarregar_ao_mudar_rota or 0),
                "observar_dom":                  int(doc.observar_dom or 0),
                "prioridade_execucao":           int(doc.prioridade_execucao or 10),
                "tempo_espera_ms":               int(doc.tempo_espera_ms or 100),
                "habilitar_logs":                int(doc.habilitar_logs or 0),
                "marcador_js":                   doc.marcador_js or "",
                "versao_overlay":                doc.versao_overlay or "",
                "html_customizado":              doc.html_customizado or "",
                "css_customizado":               doc.css_customizado or "",
                "js_customizado":                doc.js_customizado or "",
                # Child rows de cards — carregados pelo get_doc
                "cards": _extract_cards(doc),
            }
            result.append(data)

        return result

    except Exception as e:
        frappe.logger().error(f"GF UI Overlay [get_active_overlay_pages]: {e}")
        return []


@frappe.whitelist()
def get_overlay_page(name):
    """Retorna detalhes completos de uma página específica."""
    try:
        if not frappe.db.exists("GF UI Overlay Page", name):
            return None

        doc  = frappe.get_doc("GF UI Overlay Page", name)
        data = doc.as_dict()
        # as_dict() já inclui os child rows, mas garantimos o formato correto
        data["cards"] = _extract_cards(doc)
        return data

    except Exception as e:
        frappe.logger().error(f"GF UI Overlay [get_overlay_page]: {e}")
        return None


@frappe.whitelist()
def get_default_desk_overlay():
    """Retorna o registro GF Modern Desk."""
    try:
        if not frappe.db.exists("DocType", "GF UI Overlay Page"):
            return None

        name = frappe.db.get_value(
            "GF UI Overlay Page",
            {"nome_tecnico": "gf_modern_desk", "ativo": 1},
            "name",
        )
        if not name:
            return None

        return get_overlay_page(name)

    except Exception as e:
        frappe.logger().error(f"GF UI Overlay [get_default_desk_overlay]: {e}")
        return None


def _extract_cards(doc):
    """
    Extrai os cards do documento já carregado pelo get_doc.
    O get_doc popula doc.cards automaticamente como lista de child rows.
    Filtra apenas ativos e ordena por ordem.
    """
    cards = []
    try:
        for c in (doc.cards or []):
            if int(c.ativo or 0) == 0:
                continue
            cards.append({
                "titulo":           c.titulo or "",
                "descricao":        c.descricao or "",
                "icone":            c.icone or "",
                "tipo_acao":        c.tipo_acao or "Abrir Rota",
                "rota_destino":     c.rota_destino or "",
                "doctype_destino":  c.doctype_destino or "",
                "report_destino":   c.report_destino or "",
                "url_destino":      c.url_destino or "",
                "script_acao":      c.script_acao or "",
                "cor_fundo":        c.cor_fundo or "",
                "cor_texto":        c.cor_texto or "",
                "cor_icone":        c.cor_icone or "",
                "ordem":            int(c.ordem or 0),
                "ativo":            int(c.ativo or 0),
                "abrir_em_nova_aba":int(c.abrir_em_nova_aba or 0),
            })
        cards.sort(key=lambda x: x["ordem"])
    except Exception as e:
        frappe.logger().error(f"GF UI Overlay [_extract_cards]: {e}")
    return cards
