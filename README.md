# GF UI Overlay — GREENFARMS

**UI Overlay Manager para ERPNext**

Sistema administrável por Doctype para substituição visual de telas do ERPNext por páginas modernas e configuráveis, sem alterar o core do sistema.

---

## Estrutura

```
ichis_ui_overlay/
├── ichis_ui_overlay/
│   ├── __init__.py
│   ├── hooks.py
│   ├── install.py                         ← cria dados padrão
│   ├── modules.txt                        ← "Gf Ui Overlay"
│   ├── api/
│   │   └── overlay.py                     ← API Python
│   ├── gf_ui_overlay/
│   │   └── doctype/
│   │       ├── gf_ui_overlay_settings/   ← Single: configuração global
│   │       ├── gf_ui_overlay_page/       ← Cadastro de páginas de overlay
│   │       └── gf_ui_overlay_card/       ← Child: cards de atalho
│   └── public/
│       ├── css/gf_ui_overlay.css
│       └── js/gf_ui_overlay.js
├── pyproject.toml
├── setup.py
├── MANIFEST.in
└── README.md
```

---

## Instalação no Frappe Cloud

```
1. Publicar em repositório Git
2. Frappe Cloud → Sites → Apps → Add App
3. Informar o repositório
```

**Self-hosted:**
```bash
bench get-app ichis_ui_overlay <url-do-repo>
bench --site seusite.com install-app ichis_ui_overlay
bench --site seusite.com migrate
bench build --app ichis_ui_overlay
bench restart
```

---

## Após instalação

O app cria automaticamente:

- **GF UI Overlay Settings** — configuração global ativa
- **GF UI Overlay Page** — "GF Modern Desk" configurado para `/app`
- **10 cards padrão**: Vendas, Compras, Estoque, Financeiro, Projetos, CRM, Relatórios, RH, Configurações, Tema Visual

---

## Doctypes

| Doctype | Tipo | Função |
|---|---|---|
| GF UI Overlay Settings | Single | Liga/desliga o sistema, define comportamento global |
| GF UI Overlay Page | Normal | Cada registro define uma tela sobreposta |
| GF UI Overlay Card | Child | Cards de atalho dentro de uma página |

---

## Diagnóstico no Console

```javascript
window.gfUIOverlayVersion   // → "GF_UI_OVERLAY_V1"
window.gfUIOverlayLoaded    // → true
window.gfCurrentRoute       // → rota atual normalizada
window.gfOverlayActive      // → true/false
window.gfOverlayPages       // → array com páginas carregadas
```

---

## API Python

| Método | Descrição |
|---|---|
| `ichis_ui_overlay.api.overlay.get_overlay_settings` | Configurações globais |
| `ichis_ui_overlay.api.overlay.get_active_overlay_pages` | Páginas ativas com cards |
| `ichis_ui_overlay.api.overlay.get_overlay_page` | Detalhe de uma página |
| `ichis_ui_overlay.api.overlay.get_default_desk_overlay` | Configuração do GF Modern Desk |

---

## Compatibilidade

- Funciona com ou sem o app `ichis_theme_control`
- Usa variáveis CSS `--gf-*` do tema se disponível, com fallback elegante
- Não altera core do ERPNext
- Compatível com Frappe Cloud

---

GREENFARMS — contato@greenfarms.com.br
