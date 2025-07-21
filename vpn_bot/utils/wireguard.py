"""Utility helpers for managing WireGuard peers via `wg` CLI.

This implementation assumes the bot runs on the same server as the WG interface.
Elevated privileges (root or CAP_NET_ADMIN) are required.
"""
from __future__ import annotations

import subprocess
import secrets
import base64
from pathlib import Path
from typing import Tuple

from ..config import get_settings

settings = get_settings()

PRIVATE_KEY_CMD = ["wg", "genkey"]
PUBLIC_KEY_CMD = ["wg", "pubkey"]


def _run(cmd: list[str], input_data: bytes | None = None) -> bytes:
    result = subprocess.run(cmd, input=input_data, capture_output=True, check=True)
    return result.stdout.strip()


def generate_keypair() -> Tuple[str, str]:
    private_key = _run(PRIVATE_KEY_CMD)
    public_key = _run(PUBLIC_KEY_CMD, input_data=private_key + b"\n")
    return private_key.decode(), public_key.decode()


def add_peer(public_key: str) -> str:
    """Add peer to WireGuard and return allocated IP address."""
    # This is a naive allocator -> 10.66.66.X/32
    last_octet = secrets.randbelow(200) + 2
    ip = f"10.66.66.{last_octet}/32"
    subprocess.run([
        "wg", "set", settings.wg_interface,
        "peer", public_key,
        "allowed-ips", ip,
    ], check=True)
    return ip


def remove_peer(public_key: str) -> None:
    subprocess.run([
        "wg", "set", settings.wg_interface,
        "peer", public_key, "remove",
    ], check=True)


def build_client_config(private_key: str, peer_public_key: str, client_ip: str) -> str:
    """Return WireGuard client configuration string."""
    return f"""[Interface]
PrivateKey = {private_key}
Address = {client_ip}
DNS = 1.1.1.1

[Peer]
PublicKey = {peer_public_key}
Endpoint = {settings.wg_server_public_ip}:{settings.wg_server_port}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""