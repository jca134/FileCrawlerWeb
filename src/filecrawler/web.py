"""FastAPI app for the hosted FileCrawler demo.

Visitors sign in with Google, then scan a Drive folder with the same logic
as the CLI. Only the short-lived access token is kept, in a signed cookie.
"""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.errors import HttpError
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from filecrawler.api.api_utils import SCOPES, scan_folder

app = FastAPI(title="FileCrawler")
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SESSION_SECRET", "dev-only-secret"),
    https_only=os.environ.get("VERCEL") == "1",
    max_age=60 * 60,
)


def base_url(request: Request) -> str:
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.url.netloc)
    return f"{scheme}://{host}"


def make_flow(request: Request, state: str | None = None) -> Flow:
    redirect_uri = f"{base_url(request)}/auth/callback"
    if redirect_uri.startswith("http://localhost"):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    client_config = {
        "web": {
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    return Flow.from_client_config(
        client_config, SCOPES, redirect_uri=redirect_uri, state=state
    )


@app.get("/auth/login")
def login(request: Request):
    flow = make_flow(request)
    url, state = flow.authorization_url(
        access_type="online", prompt="select_account"
    )
    request.session["state"] = state
    request.session["code_verifier"] = flow.code_verifier
    return RedirectResponse(url)


@app.get("/auth/callback")
def callback(request: Request):
    state = request.session.pop("state", None)
    if not state or request.query_params.get("state") != state:
        raise HTTPException(400, "Invalid OAuth state")

    flow = make_flow(request, state=state)
    flow.code_verifier = request.session.pop("code_verifier", None)
    flow.fetch_token(code=request.query_params["code"])
    request.session["token"] = flow.credentials.token
    return RedirectResponse("/")


@app.get("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")


@app.get("/api/me")
def me(request: Request):
    return {"signed_in": "token" in request.session}


class ScanRequest(BaseModel):
    folder_url: str


@app.post("/api/scan")
def scan(body: ScanRequest, request: Request):
    token = request.session.get("token")
    if not token:
        raise HTTPException(401, "Sign in first")
    try:
        return scan_folder(body.folder_url, Credentials(token))
    except ValueError as e:
        raise HTTPException(400, str(e))
    except (RefreshError, HttpError) as e:
        if isinstance(e, RefreshError) or e.status_code == 401:
            request.session.clear()
            raise HTTPException(401, "Session expired, sign in again")
        raise HTTPException(e.status_code, e.reason)


# Local dev only: on Vercel, public/ is served by the CDN before this app.
PUBLIC_DIR = Path(__file__).resolve().parents[2] / "public"
if PUBLIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True))
