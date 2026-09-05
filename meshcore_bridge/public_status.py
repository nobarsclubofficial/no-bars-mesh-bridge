"""Public read-only status API for No Bars Mesh Bridge.

The public API intentionally exposes only coarse operational health data.
It MUST NOT expose message bodies, sender names, channel names, channel
secrets, serial ports, device identifiers, configuration contents, or
administrative actions.

SPDX-License-Identifier: MIT
"""

from datetime import datetime, timezone
from typing import Any, Dict

from nicegui import app
from starlette.requests import Request
from starlette.responses import JSONResponse

from meshcore_gui.core.shared_data import SharedData
from meshcore_bridge.bridge_engine import BridgeEngine
from meshcore_bridge.config import BridgeConfig


_ALLOWED_ORIGINS = {
    "https://nobarsclub.com",
    "https://www.nobarsclub.com",
}


def _device_health(shared: SharedData) -> Dict[str, bool]:
    """Return only the public-safe connection state for one device."""
    snap = shared.get_snapshot()
    return {"connected": bool(snap.get("connected", False))}


def _cors_headers(request: Request) -> Dict[str, str]:
    """Allow the No Bars Club website to read the status endpoint."""
    origin = request.headers.get("origin", "")
    headers = {
        "Cache-Control": "no-store, max-age=0",
        "X-Content-Type-Options": "nosniff",
    }
    if origin in _ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Vary"] = "Origin"
    return headers


def register_public_status_routes(
    shared_a: SharedData,
    shared_b: SharedData,
    engine: BridgeEngine,
    config: BridgeConfig,
) -> None:
    """Register public read-only health endpoints on the NiceGUI app."""

    async def status(request: Request) -> JSONResponse:
        stats = engine.stats
        device_a = _device_health(shared_a)
        device_b = _device_health(shared_b)
        both_connected = device_a["connected"] and device_b["connected"]

        payload: Dict[str, Any] = {
            "service": "No Bars Mesh Bridge",
            "status": "online" if both_connected else "degraded",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": int(stats.get("uptime_seconds", 0)),
            "devices": {
                "a": device_a,
                "b": device_b,
            },
            "bridges_configured": len(config.bridges),
            "messages_forwarded": engine.get_total_forwarded(),
            "forwarded_a_to_b": int(stats.get("forwarded_a_to_b", 0)),
            "forwarded_b_to_a": int(stats.get("forwarded_b_to_a", 0)),
            "duplicates_blocked": int(stats.get("duplicates_blocked", 0)),
            "last_activity": stats.get("last_forward_time") or None,
        }
        return JSONResponse(payload, headers=_cors_headers(request))

    async def healthz(request: Request) -> JSONResponse:
        device_a = _device_health(shared_a)
        device_b = _device_health(shared_b)
        healthy = device_a["connected"] and device_b["connected"]
        return JSONResponse(
            {"ok": healthy, "service": "No Bars Mesh Bridge"},
            status_code=200 if healthy else 503,
            headers=_cors_headers(request),
        )

    app.add_api_route("/api/status", status, methods=["GET"], include_in_schema=False)
    app.add_api_route("/healthz", healthz, methods=["GET"], include_in_schema=False)
