import logging
import os

import firebase_admin
import httpx
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from google.cloud.tasks_v2 import CloudTasksClient

import app.util.http_error as err
from app.config import conf
from app.routing import api_router

resp = httpx.get(
        url="http://metadata/computeMetadata/v1/instance/region",
        headers={"Metadata-Flavor": "google"},
        follow_redirects=True,
    )
os.environ["GAE_REGION"] = resp.text

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
tasks: CloudTasksClient = CloudTasksClient()
parkingbot = create_app()


@parkingbot.get("/_ah/warmup", include_in_schema=False)
def warmup():

@parkingbot.get("/", include_in_schema=False)
def root():
    err.forbidden("Bye")
