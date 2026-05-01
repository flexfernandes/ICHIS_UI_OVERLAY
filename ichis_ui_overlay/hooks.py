app_name = "ichis_ui_overlay"
app_title = "GF UI Overlay"
app_publisher = "GREENFARMS"
app_description = "UI Overlay Manager — Sobreposição e substituição de telas do ERPNext"
app_email = "contato@greenfarms.com.br"
app_license = "mit"
app_version = "1.0.0"

# ==============================================================
# ASSETS — carregados no Desk (usuário logado)
# ==============================================================

app_include_css = [
    "/assets/ichis_ui_overlay/css/gf_ui_overlay.css",
]

app_include_js = [
    "/assets/ichis_ui_overlay/js/gf_ui_overlay.js",
]

# ==============================================================
# INSTALAÇÃO
# ==============================================================

after_install = "ichis_ui_overlay.install.after_install"

# ==============================================================
# FIXTURES
# ==============================================================

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [["module", "=", "Gf Ui Overlay"]]
    }
]
