"""
No Bars Mesh Bridge operator dashboard.

The dashboard remains operationally compatible with the upstream DOMCA
layout while presenting this fork with the No Bars Club visual system.

                 Author: PE1HVH
                Version: 2.0.0
SPDX-License-Identifier: MIT
              Copyright: (c) 2026 PE1HVH
"""

from pathlib import Path
from typing import List, Optional

from nicegui import ui

from meshcore_gui.core.shared_data import SharedData

from meshcore_bridge.bridge_engine import BridgeEngine
from meshcore_bridge.config import BridgeConfig, BridgePair, DEFAULT_CONFIG_PATH
from meshcore_bridge.device_reader import read_device_channels
from meshcore_bridge.gui.panels.status_panel import StatusPanel
from meshcore_bridge.gui.panels.log_panel import LogPanel
from meshcore_bridge.gui.panels.bridge_config_panel import BridgeConfigPanel


# No Bars Club website palette.
# Source of truth: nobarsclub.com / assets/styles.css
_NBC_BG = "#080b0a"
_NBC_PANEL = "#0f1412"
_NBC_PANEL_2 = "#141b18"
_NBC_TEXT = "#eee9dc"
_NBC_MUTED = "#9aa8a0"
_NBC_BRONZE = "#9a6f35"
_NBC_OLIVE = "#7f8f6a"
_NBC_LINE = "#253129"
_NBC_DANGER = "#ff5b67"

_NBC_HEAD = f'''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root {{
  --nbc-bg: {_NBC_BG};
  --nbc-panel: {_NBC_PANEL};
  --nbc-panel-2: {_NBC_PANEL_2};
  --nbc-text: {_NBC_TEXT};
  --nbc-muted: {_NBC_MUTED};
  --nbc-accent: {_NBC_BRONZE};
  --nbc-accent-2: {_NBC_OLIVE};
  --nbc-line: {_NBC_LINE};
  --nbc-danger: {_NBC_DANGER};
}}

body {{
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
body.body--dark,
body.body--dark .q-page {{
  background:
    radial-gradient(circle at 80% -20%, rgba(127,143,106,.10), transparent 35%),
    radial-gradient(circle at 0 10%, rgba(154,111,53,.10), transparent 28%),
    var(--nbc-bg) !important;
  color: var(--nbc-text) !important;
}}
body.body--light,
body.body--light .q-page {{
  background: #f3f1e9 !important;
  color: #151a17 !important;
}}

body.body--dark .q-header {{
  background: rgba(8,11,10,.92) !important;
  border-bottom: 1px solid rgba(255,255,255,.06);
  backdrop-filter: blur(18px);
}}
body.body--light .q-header {{
  background: #171d19 !important;
}}

body.body--dark .q-card {{
  background: linear-gradient(145deg, rgba(255,255,255,.035), rgba(255,255,255,.012)), var(--nbc-panel) !important;
  color: var(--nbc-text) !important;
  border: 1px solid var(--nbc-line) !important;
  border-radius: 20px !important;
  box-shadow: 0 20px 55px rgba(0,0,0,.22) !important;
}}
body.body--light .q-card {{
  background: #fffdf6 !important;
  border: 1px solid #d8d4c7 !important;
  border-radius: 20px !important;
  box-shadow: 0 16px 40px rgba(25,30,27,.08) !important;
}}

body.body--dark .q-card .text-gray-600,
body.body--dark .q-card .text-xs {{ color: #b9b4a4 !important; }}
body.body--dark .q-card .text-sm {{ color: #ded9cb !important; }}

body.body--dark .q-field__control {{
  background: #0b100e !important;
  color: var(--nbc-text) !important;
  border-radius: 12px !important;
}}
body.body--dark .q-field__native,
body.body--dark .q-field__input {{ color: var(--nbc-text) !important; }}
body.body--dark .q-field__label {{ color: var(--nbc-muted) !important; }}

.q-btn {{ border-radius: 999px !important; font-weight: 800; }}
.q-btn.bg-primary {{ color: #080b0a !important; }}
.q-separator {{ background: var(--nbc-line) !important; }}

.bridge-header-text {{ color: white; }}
.nbc-kicker {{
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: .16em;
  text-transform: uppercase;
}}
.nbc-wordmark {{
  font-weight: 900;
  letter-spacing: -.035em;
}}
.nbc-shell {{
  min-height: calc(100vh - 64px);
}}
.nbc-topline {{
  border: 1px solid var(--nbc-line);
  background: rgba(255,255,255,.018);
  border-radius: 16px;
}}
.nbc-brand-dot {{
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--nbc-accent);
  box-shadow: 0 0 18px rgba(154,111,53,.45);
}}
.nbc-footer {{
  color: var(--nbc-muted);
  font-size: 11px;
  text-align: center;
  padding: 8px 0 24px;
}}
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

        ui.add_head_html(_NBC_HEAD)
        ui.colors(
            primary=_NBC_BRONZE,
            secondary=_NBC_OLIVE,
            accent=_NBC_TEXT,
            dark=_NBC_BG,
            positive=_NBC_OLIVE,
            negative=_NBC_DANGER,
            info=_NBC_MUTED,
            warning="#c49552",
        )
        dark = ui.dark_mode(True)

        with ui.header().classes("items-center px-4 py-2 shadow-none"):
            with ui.row().classes("items-center gap-3"):
                ui.element("div").classes("nbc-brand-dot")
                with ui.column().classes("gap-0"):
                    ui.label("NO BARS CLUB").classes(
                        "text-[10px] opacity-70 bridge-header-text nbc-kicker"
                    )
                    ui.label("No Bars Mesh Bridge").classes(
                        "text-lg bridge-header-text nbc-wordmark"
                    )

            ui.label(
                f"{self._cfg.device_a.label} ↔ {self._cfg.device_b.label}"
            ).classes("text-xs ml-3 bridge-header-text").style("opacity: 0.55")

            ui.space()

            self._header_status = ui.label("Starting...").classes(
                "text-sm opacity-70 bridge-header-text"
            )

            ui.button(
                icon="brightness_6",
                on_click=lambda: dark.toggle(),
            ).props("flat round dense color=white").tooltip("Toggle dark / light")

        with ui.column().classes("w-full max-w-5xl mx-auto p-4 gap-4 nbc-shell"):
            with ui.row().classes("w-full items-center justify-between px-4 py-3 nbc-topline"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("hub", color="primary").classes("text-lg")
                    ui.label("BRIDGE CONTROL").classes(
                        "text-xs font-bold nbc-kicker"
                    )
                ui.label("No towers. No bars. No problem.").classes(
                    "text-xs opacity-60"
                )

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

            ui.label("No Bars Club • nobarsclub.com • Community built mesh infrastructure").classes(
                "w-full nbc-footer"
            )

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
            status = f"Both connected • {total} forwarded"
        elif conn_a:
            status = f"Device B disconnected • {total} forwarded"
        elif conn_b:
            status = f"Device A disconnected • {total} forwarded"
        else:
            status = "Both devices disconnected"

        if self._header_status:
            self._header_status.set_text(status)

        if self._status:
            self._status.update()
        if self._log:
            self._log.update()
