from __future__ import annotations

import os
import time
from datetime import date, datetime
from typing import Dict, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.integrations.secret_store import SecretStore
from app.integrations.fitbit_client import (
    FitbitClient,
    FITBIT_AUTH_URL,
    make_code_challenge,
    make_code_verifier,
)

router = APIRouter(prefix="/fitbit", tags=["fitbit"])

# NOTE: For Cloud Run (multi-instance), replace this with Redis/DB.
# For a single-user personal integration, this can still work if you do auth quickly.
_pkce_store: Dict[str, Dict[str, float | str]] = {}

PROJECT_ID = os.environ["PROJECT_ID"]
REDIRECT_URI = os.environ["FITBIT_REDIRECT_URI"]
SCOPE = os.environ.get("FITBIT_SCOPE", "activity heartrate sleep profile weight")

secrets_store = SecretStore(PROJECT_ID)


def _get_fitbit_client() -> FitbitClient:
    client_id = secrets_store.read("fitbit_client_id").strip()
    if not client_id:
        raise HTTPException(status_code=500, detail="fitbit_client_id secret is empty")
    return FitbitClient(client_id=client_id, redirect_uri=REDIRECT_URI)


async def _get_fresh_access_token() -> str:
    """
    Always refresh using the stored refresh token.
    This avoids having to persist an access token at all.
    """
    refresh_token = secrets_store.read("fitbit_refresh_token").strip()
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Fitbit not connected yet. Run /auth/start.")

    client = _get_fitbit_client()
    tokens = await client.refresh_tokens(refresh_token)

    # Rotate refresh token (critical)
    secrets_store.write_new_version("fitbit_refresh_token", tokens.refresh_token)
    return tokens.access_token


@router.get("/auth/start")
def auth_start():
    """
    Start OAuth2 PKCE flow.
    Redirects user to Fitbit consent screen.
    """
    client = _get_fitbit_client()

    state = os.urandom(24).hex()
    verifier = make_code_verifier()
    challenge = make_code_challenge(verifier)

    _pkce_store[state] = {"verifier": verifier, "created_at": time.time()}

    params = {
        "client_id": client.client_id,
        "response_type": "code",
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    print("Params:", params)
    return RedirectResponse(FITBIT_AUTH_URL + "?" + urlencode(params))


@router.get("/auth/callback")
async def auth_callback(code: Optional[str] = None, state: Optional[str] = None):
    """
    Fitbit redirects here with ?code=...&state=...
    Exchanges code for tokens and persists refresh token in Secret Manager.
    """
    print("Callback:", code, state)
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code/state")

    rec = _pkce_store.pop(state, None)
    if not rec:
        raise HTTPException(status_code=400, detail="Invalid or expired state")

    verifier = str(rec["verifier"])
    client = _get_fitbit_client()

    tokens = await client.exchange_code_for_tokens(code=code, code_verifier=verifier)

    # Persist refresh token (as a new secret version)
    secrets_store.write_new_version("fitbit_refresh_token", tokens.refresh_token)
    print("Tokens:", tokens)

    return {
        "ok": True,
        "message": "Fitbit connected. You can now call /profile or /daily-summary.",
        "scope": tokens.scope,
        "user_id": tokens.user_id,
    }


@router.get("/profile")
async def profile():
    access_token = await _get_fresh_access_token()
    client = _get_fitbit_client()
    return await client.get_profile(access_token)


@router.get("/daily-summary")
async def daily_summary(
    day: str = Query(default_factory=lambda: date.today().isoformat(), description="YYYY-MM-DD")
):
    access_token = await _get_fresh_access_token()
    client = _get_fitbit_client()
    d = datetime.strptime(day, "%Y-%m-%d").date()

    activity = await client.get_daily_activity_summary(access_token, d)
    sleep = await client.get_sleep(access_token, d)
    heartrate = await client.get_heartrate_day(access_token, d)

    return {
        "date": d.isoformat(),
        "activity": activity,
        "sleep": sleep,
        "heartrate": heartrate,
    }
