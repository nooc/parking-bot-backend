import logging

import firebase_admin
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.staticfiles import StaticFiles

import app.util.http_error as err
from app.config import conf
from app.routing import api_router


def create_app():
    args = {
        "title": conf.PROJECT_NAME,
        "description": conf.PROJECT_DESC,
        "openapi_url": f"/openapi/openapi.json",
        "redoc_url": None,
        "docs_url": "/docs" if conf.SWAGGER_UI else None,
    }
    if conf.DEBUG:
        logging.getLogger().level = logging.INFO
    else:
        logging.getLogger().level = logging.DEBUG

    app = FastAPI(**args)
    app.add_middleware(HTTPSRedirectMiddleware)
    app.include_router(api_router, prefix=conf.API_ENDPOINT)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    return app


firebase_admin.initialize_app()
parkingbot = create_app()


@parkingbot.get("/_ah/warmup", include_in_schema=False)
def warmup():
    pass


@parkingbot.get("/", include_in_schema=False)
def root():
    err.forbidden("Bye")
