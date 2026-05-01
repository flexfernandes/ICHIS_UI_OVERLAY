from setuptools import setup, find_packages

setup(
    name="ichis_ui_overlay",
    version="1.0.0",
    description="UI Overlay Manager — Sobreposição e substituição de telas do ERPNext - GREENFARMS",
    author="GREENFARMS",
    author_email="contato@greenfarms.com.br",
    packages=find_packages(include=["ichis_ui_overlay", "ichis_ui_overlay.*"]),
    include_package_data=True,
    zip_safe=False,
)
