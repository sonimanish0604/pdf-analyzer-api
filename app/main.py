from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from fastapi.responses import RedirectResponse, Response
# from app.api.v1.routes import router as v1_router  # your router

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="PDF Analyzer",
        version="1.0.0",
        docs_url="/docs" if settings.APP_ENV != "prod" else "/docs",  # keep docs on; you can disable in prod later
        openapi_url="/openapi.json",
    )

    # CORS (only if you actually need browser clients)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=False,
            allow_methods=["POST", "GET", "OPTIONS"],
            allow_headers=["*"],
        )

    # Mount routers
    # app.include_router(v1_router, prefix="/v1")

    @app.get("/v1/health")
    def health():
        return {"ok": True, "env": settings.APP_ENV}

    return app

app = create_app()

@app.get("/", include_in_schema=False)
def root():
    # send people to the docs
    return RedirectResponse(url="/docs")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    # no favicon; return 204 to avoid 404 spam in logs
    return Response(status_code=204)
