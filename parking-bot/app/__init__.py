import logging
import os

import httpx
from fastapi import Depends, FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.config import conf


def create_app():
    extra = {}
    if conf.DEBUG:
        logging.getLogger().level = logging.INFO
    else:
        logging.getLogger().level = logging.DEBUG
    app = FastAPI(
        title=conf.PROJECT_NAME,
        description=conf.PROJECT_DESC,
        openapi_url=f"{conf.API_ENDPOINT}/openapi.json",
        redoc_url=None,
        **extra,
    )
    # app.add_middleware(HTTPSRedirectMiddleware)
    app.include_router(api_router, prefix=conf.API_ENDPOINT)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    return app


parkingbot = create_app()


@parkingbot.get("/_ah/warmup", include_in_schema=False)
def warmup():
    resp = httpx.get(
        url="http://metadata/computeMetadata/v1/instance/region",
        headers={"Metadata-Flavor": "google"},
        follow_redirects=True,
    )
    os.environ["GAE_REGION"] = resp.text


@parkingbot.get("/", include_in_schema=False)
def root():
    redirect = RedirectResponse(url=conf.APP_URL)
    return redirect
