"""Minimal wrapper around the Crypto Pay API.
Replace or extend this module to integrate other payment providers.
"""
from __future__ import annotations

import requests
from typing import Any, Dict

from ..config import get_settings

settings = get_settings()

BASE_URL = "https://pay.crypt.bot/api"

class CryptoPayError(RuntimeError):
    pass


def _request(method: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    headers = {"Crypto-Pay-API-Token": settings.cryptopay_token}
    r = requests.post(f"{BASE_URL}/{method}", json=params or {}, headers=headers, timeout=30)
    data = r.json()
    if not data.get("ok"):
        raise CryptoPayError(data)
    return data["result"]


def create_invoice(amount: float, currency: str = "TON", description: str | None = None) -> Dict[str, Any]:
    params = {
        "asset": currency,
        "amount": amount,
        "desc": description or "VPN access purchase",
    }
    return _request("createInvoice", params)