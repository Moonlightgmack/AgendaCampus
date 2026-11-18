"""Documentation interactive de l'API (/docs) utilisable SANS connexion Internet.

Par défaut, FastAPI fait charger Swagger UI depuis un CDN (cdn.jsdelivr.net) :
sans Internet, la page /docs reste blanche. Ce module sert les mêmes fichiers
depuis app/static/docs.
"""
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html

CHEMINS_PAR_DEFAUT = {"/docs", "/docs/oauth2-redirect", "/redoc"}


def activer_docs_hors_ligne(app: FastAPI) -> None:
    # On retire les pages de documentation créées par FastAPI (qui utilisent le CDN)
    app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", None) not in CHEMINS_PAR_DEFAUT]

    @app.get("/docs", include_in_schema=False)
    def documentation():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} : documentation",
            oauth2_redirect_url="/docs/oauth2-redirect",
            swagger_js_url="/static/docs/swagger-ui-bundle.js",
            swagger_css_url="/static/docs/swagger-ui.css",
            swagger_favicon_url="/static/docs/favicon-32x32.png",
        )

    @app.get("/docs/oauth2-redirect", include_in_schema=False)
    def redirection_oauth2():
        return get_swagger_ui_oauth2_redirect_html()
