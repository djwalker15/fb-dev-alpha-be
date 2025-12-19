from __future__ import annotations

import base64
import hashlib
import secrets
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional

import httpx


FITBIT_AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
FITBIT_TOKEN_URL = "https://api.fitbit.com/oauth2/token"
FITBIT_API_BASE = "https://api.fitbit.com"


def _b64url_no_pad(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def make_code_verifier() -> str:
    # 43–128 chars; URL-safe, no padding
    return _b64url_no_pad(secrets.token_bytes(64))


def make_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return _b64url_no_pad(digest)


@dataclass(frozen=True)
class FitbitTokens:
    access_token: str
    refresh_token: str
    expires_in: int
    scope: str
    user_id: str


class FitbitClient:
    """
    Fitbit API client for a Personal app type using OAuth2 + PKCE.
    - Token exchange/refresh via form POST
    - API calls via Bearer access token
    """

    def __init__(self, client_id: str, redirect_uri: str):
        self.client_id = client_id
        self.redirect_uri = redirect_uri

    async def exchange_code_for_tokens(self, code: str, code_verifier: str) -> FitbitTokens:
        data = {
            "client_id": self.client_id,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "code_verifier": code_verifier,
        }

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                FITBIT_TOKEN_URL,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )
        resp.raise_for_status()
        j = resp.json()
        return FitbitTokens(
            access_token=j["access_token"],
            refresh_token=j["refresh_token"],
            expires_in=int(j["expires_in"]),
            scope=j.get("scope", ""),
            user_id=j.get("user_id", ""),
        )

    async def refresh_tokens(self, refresh_token: str) -> FitbitTokens:
        data = {
            "client_id": self.client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                FITBIT_TOKEN_URL,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )
        resp.raise_for_status()
        j = resp.json()
        return FitbitTokens(
            access_token=j["access_token"],
            refresh_token=j["refresh_token"],
            expires_in=int(j["expires_in"]),
            scope=j.get("scope", ""),
            user_id=j.get("user_id", ""),
        )

    async def api_get(self, access_token: str, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{FITBIT_API_BASE}{path}"
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
            )
        resp.raise_for_status()
        return resp.json()

    # Convenience endpoints

    async def get_profile(self, access_token: str) -> Dict[str, Any]:
        return await self.api_get(access_token, "/1/user/-/profile.json")

    async def get_daily_activity_summary(self, access_token: str, day: date) -> Dict[str, Any]:
        return await self.api_get(access_token, f"/1/user/-/activities/date/{day.isoformat()}.json")

    async def get_sleep(self, access_token: str, day: date) -> Dict[str, Any]:
        return await self.api_get(access_token, f"/1.2/user/-/sleep/date/{day.isoformat()}.json")

    async def get_heartrate_day(self, access_token: str, day: date) -> Dict[str, Any]:
        return await self.api_get(access_token, f"/1/user/-/activities/heart/date/{day.isoformat()}/1d.json")
