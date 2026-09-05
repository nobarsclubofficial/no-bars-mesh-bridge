"""
Bridge status dashboard — NiceGUI page with No Bars Club identity.

The dashboard remains operationally compatible with the upstream DOMCA
layout while presenting this fork as No Bars Mesh Bridge.

                 Author: PE1HVH
                Version: 2.0.0
SPDX-License-Identifier: MIT
              Copyright: (c) 2026 PE1HVH
"""

from pathlib import Path
from typing import List, Optional

from nicegui import ui

from meshcore_gui.core.shared_data import SharedData
from meshcore_gui import config as gui_config

from meshcore_bridge.bridge_engine import BridgeEngine
from meshcore_bridge.config import BridgeConfig, BridgePair, DEFAULT_CONFIG_PATH
from meshcore_bridge.device_reader import read_device_channels
from meshcore_bridge.gui.panels.status_panel import StatusPanel
from meshcore_bridge.gui.panels.log_panel import LogPanel
from meshcore_bridge.gui.panels.bridge_config_panel import BridgeConfigPanel


# ── Upstream-compatible DOMCA base theme with NBC identity ─────────

_DOMCA_HEAD = '''
<link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
body.body--dark {
  --bg: #0A1628;
  --title: #48CAE4;  --subtitle: #48CAE4;
}
body.body--light {
  --bg: #FFFFFF;
  --title: #0077B6;  --subtitle: #0077B6;
}

body.body--dark  { background: #0A1628 !important; }
body.body--light { background: #f4f8fb !important; }
body.body--dark .q-page  { background: #0A1628 !important; }
body.body--light .q-page { background: #f4f8fb !important; }

body.body--dark .q-header  { background: #0d1f35 !important; }
body.body--light .q-header { background: #0077B6 !important; }

body.body--dark .q-card {
  background: #112240 !important;
  color: #e0f0f8 !important;
  border: 1px solid rgba(0,119,182,0.15) !important;
}
body.body--dark .q-card .text-gray-600 { color: #48CAE4 !important; }
body.body--dark .q-card .text-xs       { color: #c0dce8 !important; }
body.body--dark .q-card .text-sm       { color: #d0e8f2 !important; }

body.body--dark .q-field__control { background: #0c1a2e !important; color: #e0f0f8 !important; }
body.body--dark .q-field__native  { color: #e0f0f8 !important; }

.bridge-header-text {
  font-family: 'JetBrains Mono', monospace;
  color: white;
}
.nbc-kicker {
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
</style>
'''


class BridgeDashboard:
    """No Bars Mesh Bridge private operator dashboard."""

    def __init__(
        self,
        shared_a: SharedData,
        shared_b: SharedData,
        engine: BridgeEngine,
        config: BridgeConfig,
    ) -> None:
        self._shared_a = shared_a
        self._shared_b = shared_b
        self._engine = engine
        self._cfg = config

        self._status: Optional[StatusPanel] = None
        self._log: Optional[LogPanel] = None
        self._bridge_config: Optional[BridgeConfigPanel] = None
        self._header_status = None

    def render(self) -> None:
        """Build the complete private operator dashboard."""

        channels_a = read_device_channels(self._cfg.device_a.port)
        channels_b = read_device_channels(self._cfg.device_b.port)

        self._status = StatusPanel(
            self._shared_a, self._shared_b, self._engine, self._cfg,
        )
        self._log = LogPanel(self._engine)
        self._bridge_config = BridgeConfigPanel(
            config=self._cfg,
            channels_a=channels_a,
            channels_b=channels_b,
            on_save=self._on_bridges_saved,
            config_path=(
                Path(self._cfg.config_path)
                if self._cfg.config_path
                else DEFAULT_CONFIG_PATH
            ),
        )

        ui.add_head_html(_DOMCA_HEAD)
        dark = ui.dark_mode(True)

        with ui.header().classes("items-center px-4 py-2 shadow-md"):
            ui.icon("hub").classes("text-white text-2xl")
            with ui.column().classes("gap-0 ml-2"):
                ui.label("NO BARS CLUB").classes(
                    "text-[10px] opacity-60 bridge-header-text nbc-kicker"
                )
                ui.label("No Bars Mesh Bridge").classes(
                    "text-lg font-bold bridge-header-text"
                )

            ui.label(
                f"({self._cfg.device_a.label} ↔ {self._cfg.device_b.label})"
            ).classes("text-xs ml-3 bridge-header-text").style("opacity: 0.65")

            ui.space()

            self._header_status = ui.label("Starting...").classes(
                "text-sm opacity-70 bridge-header-text"
            )

            ui.button(
                icon="brightness_6",
                on_click=lambda: dark.toggle(),
            ).props("flat round dense color=white").tooltip("Toggle dark / light")

        with ui.column().classes("w-full max-w-5xl mx-auto p-4 gap-4"):
            with ui.card().classes("w-full"):
                with ui.row().classes("items-center gap-2 mb-2"):
                    ui.icon("settings", color="primary").classes("text-lg")
                    ui.label("Bridge Configuration").classes(
                        "text-sm font-bold"
                    ).style("font-family: 'JetBrains Mono', monospace")

                with ui.row().classes("gap-4 flex-wrap"):
                    for lbl, val in [
                        ("Config file", str(
                            Path(self._cfg.config_path).name
                            if self._cfg.config_path else "defaults"
                        )),
                        ("Poll interval", f"{self._cfg.poll_interval_ms}ms"),
                        ("Prefix", "ON" if self._cfg.forward_prefix else "OFF"),
                        ("Loop cache", str(self._cfg.max_forwarded_cache)),
                        ("Bridges", str(len(self._cfg.bridges))),
                    ]:
                        with ui.column().classes("gap-0"):
                            ui.label(lbl).classes("text-xs opacity-50")
                            ui.label(val).classes("text-xs font-bold").style(
                                "font-family: 'JetBrains Mono', monospace"
                            )

            self._status.render()
            self._bridge_config.render()
            self._log.render()

        ui.timer(0.5, self._on_timer)

    def _on_bridges_saved(self, bridges: List[BridgePair]) -> None:
        """Hot-reload the bridge engine after the user saves config."""
        self._engine.reload_bridges(bridges)

    def _on_timer(self) -> None:
        """Periodic UI update callback."""
        snap_a = self._shared_a.get_snapshot()
        snap_b = self._shared_b.get_snapshot()
        conn_a = snap_a.get("connected", False)
        conn_b = snap_b.get("connected", False)
        total = self._engine.get_total_forwarded()

        if conn_a and conn_b:
            status = f"✅ Both connected — {total} forwarded"
        elif conn_a:
            status = f"⚠️ Device B disconnected — {total} forwarded"
        elif conn_b:
            status = f"⚠️ Device A disconnected — {total} forwarded"
        else:
            status = "❌ Both devices disconnected"

        if self._header_status:
            self._header_status.set_text(status)

        if self._status:
            self._status.update()
        if self._log:
            self._log.update()
