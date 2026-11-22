# =============================================================================
# FILE: ui/widgets/traffic_chart.py
# PURPOSE: High-Performance Real-Time Network Traffic Waveform Visualizer.
#          - Extended 600-point historical telemetry buffer.
#          - Interactive Horizontal Panning & Scrolling (Slider + Mousewheel + Step Buttons).
#          - Live Stream mode with instantaneous 1-click 'Return to Live'.
#          - Autonomous Exfiltration Spike Detection with 'Jump to Spike' locator.
#          - Vector-based callouts rendering peak spike throughput in alert red.
#          - Persistent canvas vector objects with 0ms flicker-free updates.
# =============================================================================

import tkinter as tk
import customtkinter as ctk
import datetime
import random
from typing import List, Dict, Any, Tuple, Optional

from ui.theme import (
    COLOR_CYAN as C_CYAN,
    COLOR_DANGER as C_DANGER,
    COLOR_WARNING as C_WARNING,
    COLOR_SUCCESS as C_SUCCESS,
    COLOR_BORDER as C_BORDER,
    COLOR_SURFACE as C_SURFACE,
    COLOR_CARD as C_CARD,
    COLOR_TEXT_PRIMARY as C_TEXT,
    COLOR_TEXT_SECONDARY as C_SUBTEXT,
    COLOR_TEXT_MUTED as C_MUTED,
    FONT_MONO, FONT_BODY, FONT_TITLE
)


class NetworkTrafficCanvas(ctk.CTkFrame):
    """
    Real-time interactive network throughput waveform graph with horizontal scrolling,
    historical replay, and exfiltration spike jump capabilities.
    """

    def __init__(self, parent, max_history: int = 600, visible_points: int = 40, height: int = 125, **kwargs):
        super().__init__(parent, fg_color=C_SURFACE, corner_radius=8, border_width=1, border_color=C_BORDER, **kwargs)
        self.max_history = max_history
        self.visible_points = visible_points
        self.canvas_height = height

        # Full history buffer: list of dicts: {'val': float, 'anomaly': bool, 'time': str, 'label': str}
        self.history_buffer: List[Dict[str, Any]] = []
        now = datetime.datetime.now()
        for i in range(visible_points):
            t_str = (now - datetime.timedelta(seconds=(visible_points - i) * 2)).strftime("%H:%M:%S")
            self.history_buffer.append({
                "val": round(1.25 + random.uniform(0.1, 0.4), 2),
                "anomaly": False,
                "time": t_str,
                "label": ""
            })

        self.spike_indices: List[int] = []
        self.scroll_offset: int = 0  # 0 means live (viewing newest points)
        self.is_live: bool = True
        self._updating_slider: bool = False

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ---------------------------------------------------------------------
        # ROW 0: Header with metrics & interactive scroll controls
        # ---------------------------------------------------------------------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 2))
        header.grid_columnconfigure(1, weight=1)

        left_h = ctk.CTkFrame(header, fg_color="transparent")
        left_h.grid(row=0, column=0, sticky="w")

        self.lbl_title = ctk.CTkLabel(
            left_h, text="Network Traffic Activity",
            font=ctk.CTkFont(family=FONT_TITLE, size=11, weight="bold"), text_color=C_SUBTEXT
        )
        self.lbl_title.pack(side="left", padx=(0, 6))

        self.lbl_mode_badge = ctk.CTkLabel(
            left_h, text="● LIVE",
            font=ctk.CTkFont(family=FONT_BODY, size=9, weight="bold"),
            fg_color="#06281E", text_color=C_SUCCESS, corner_radius=4, width=54, height=18
        )
        self.lbl_mode_badge.pack(side="left", padx=2)

        # Right-side controls
        right_h = ctk.CTkFrame(header, fg_color="transparent")
        right_h.grid(row=0, column=1, sticky="e")

        # Exfiltration spike jump button (lights up when spikes are recorded)
        self.btn_spike = ctk.CTkButton(
            right_h, text="🚨 Spike Jump", width=95, height=20,
            fg_color="#330C15", hover_color="#4D1422", text_color=C_DANGER,
            font=ctk.CTkFont(family=FONT_BODY, size=9, weight="bold"),
            border_width=1, border_color="#551525", corner_radius=4,
            command=self._jump_to_latest_spike
        )

        # Pan left (earlier) button
        self.btn_prev = ctk.CTkButton(
            right_h, text="◀ Earlier", width=56, height=20,
            fg_color="#10192A", hover_color="#1B2A47", text_color=C_SUBTEXT,
            font=ctk.CTkFont(family=FONT_BODY, size=9),
            border_width=1, border_color=C_BORDER, corner_radius=4,
            command=lambda: self._step_scroll(8)
        )
        self.btn_prev.pack(side="left", padx=2)

        # Pan right (later) button
        self.btn_next = ctk.CTkButton(
            right_h, text="▶ Later", width=50, height=20,
            fg_color="#10192A", hover_color="#1B2A47", text_color=C_SUBTEXT,
            font=ctk.CTkFont(family=FONT_BODY, size=9),
            border_width=1, border_color=C_BORDER, corner_radius=4,
            command=lambda: self._step_scroll(-8)
        )
        self.btn_next.pack(side="left", padx=2)

        # Live return button
        self.btn_live = ctk.CTkButton(
            right_h, text="● Live", width=46, height=20,
            fg_color="#0E2A1E", hover_color="#14402E", text_color=C_SUCCESS,
            font=ctk.CTkFont(family=FONT_BODY, size=9, weight="bold"),
            border_width=1, border_color="#1A4732", corner_radius=4,
            command=self.reset_to_live
        )
        self.btn_live.pack(side="left", padx=(2, 8))

        self.lbl_current_rate = ctk.CTkLabel(
            right_h, text="Throughput: 1.45 MB/s",
            font=ctk.CTkFont(family=FONT_BODY, size=11, weight="bold"), text_color=C_CYAN
        )
        self.lbl_current_rate.pack(side="left")

        # ---------------------------------------------------------------------
        # ROW 1: Native Canvas with persistent vectors
        # ---------------------------------------------------------------------
        self.canvas = tk.Canvas(
            self, height=self.canvas_height, bg="#060b14",
            highlightthickness=0, bd=0
        )
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 2))

        # Persistent vector items to eliminate any screen flicker
        self._grid_lines = [
            self.canvas.create_line(0, 0, 0, 0, fill="#0f1d33", dash=(2, 4))
            for _ in range(3)
        ]
        self._poly_fill = self.canvas.create_polygon([0, 0, 0, 0], fill="#081324", outline="")
        self._curve_glow = self.canvas.create_line([0, 0, 0, 0], fill="#00334d", width=3.5, smooth=True)
        self._curve_line = self.canvas.create_line([0, 0, 0, 0], fill=C_CYAN, width=1.8, smooth=True)
        self._dot_pulse = self.canvas.create_oval(0, 0, 0, 0, fill="#ffffff", outline=C_CYAN, width=1.5)

        # Spike marker items for exfiltration highlights
        self._spike_line = self.canvas.create_line(0, 0, 0, 0, fill=C_DANGER, dash=(3, 3), width=1.5, state="hidden")
        self._spike_marker = self.canvas.create_oval(0, 0, 0, 0, fill=C_DANGER, outline="#ffffff", width=2, state="hidden")
        self._spike_text = self.canvas.create_text(0, 0, text="", fill=C_DANGER, font=(FONT_BODY, 9, "bold"), state="hidden")

        # Bind canvas resize and horizontal mouse scroll
        self.canvas.bind("<Configure>", lambda e: self._draw_graph())
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", lambda e: self._step_scroll(4))
        self.canvas.bind("<Button-5>", lambda e: self._step_scroll(-4))

        # ---------------------------------------------------------------------
        # ROW 2: Horizontal Timeline Scrubber
        # ---------------------------------------------------------------------
        scrub_frame = ctk.CTkFrame(self, fg_color="transparent")
        scrub_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(1, 5))
        scrub_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            scrub_frame, text="⏮ Past",
            font=ctk.CTkFont(family=FONT_BODY, size=8), text_color=C_MUTED
        ).grid(row=0, column=0, padx=(2, 6))

        self.slider = ctk.CTkSlider(
            scrub_frame, from_=0.0, to=1.0, height=12,
            progress_color=C_CYAN, button_color=C_CYAN, button_hover_color="#69BFFF",
            command=self._on_slider_change
        )
        self.slider.set(1.0)
        self.slider.grid(row=0, column=1, sticky="ew")

        ctk.CTkLabel(
            scrub_frame, text="Live ●",
            font=ctk.CTkFont(family=FONT_BODY, size=8), text_color=C_SUCCESS
        ).grid(row=0, column=2, padx=(6, 2))

        self.lbl_scrub_info = ctk.CTkLabel(
            scrub_frame, text="Live Real-Time View",
            font=ctk.CTkFont(family=FONT_BODY, size=8), text_color=C_MUTED
        )
        self.lbl_scrub_info.grid(row=0, column=3, padx=(10, 2))

    # -------------------------------------------------------------------------
    # Scroll & Navigation Logic
    # -------------------------------------------------------------------------

    def _on_mouse_wheel(self, event):
        """Scroll left/right through waveform history using mouse wheel."""
        delta = 4 if event.delta < 0 else -4
        self._step_scroll(delta)

    def _step_scroll(self, delta: int):
        """Step scroll offset by delta items."""
        total = len(self.history_buffer)
        max_offset = max(0, total - self.visible_points)
        new_offset = max(0, min(max_offset, self.scroll_offset + delta))
        self.scroll_offset = new_offset
        self.is_live = (self.scroll_offset == 0)
        self._update_slider_from_offset()
        self._draw_graph()

    def _on_slider_change(self, val: float):
        """Handle user dragging horizontal timeline slider."""
        if self._updating_slider:
            return
        total = len(self.history_buffer)
        max_offset = max(0, total - self.visible_points)
        self.scroll_offset = int((1.0 - float(val)) * max_offset)
        self.is_live = (self.scroll_offset == 0)
        self._draw_graph()

    def _update_slider_from_offset(self):
        """Reflect scroll_offset onto the slider position."""
        self._updating_slider = True
        try:
            total = len(self.history_buffer)
            max_offset = max(0, total - self.visible_points)
            if max_offset > 0:
                val = 1.0 - (self.scroll_offset / max_offset)
                self.slider.set(val)
            else:
                self.slider.set(1.0)
        finally:
            self._updating_slider = False

    def reset_to_live(self):
        """1-click snap back to live real-time telemetry."""
        self.scroll_offset = 0
        self.is_live = True
        self._update_slider_from_offset()
        self._draw_graph()

    def _jump_to_latest_spike(self):
        """Instantly center the waveform viewport on the latest exfiltration spike."""
        if not self.spike_indices:
            return
        last_spike_idx = self.spike_indices[-1]
        total = len(self.history_buffer)
        target_end = min(total, last_spike_idx + self.visible_points // 2)
        target_offset = total - target_end
        max_offset = max(0, total - self.visible_points)
        self.scroll_offset = max(0, min(max_offset, target_offset))
        self.is_live = (self.scroll_offset == 0)
        self._update_slider_from_offset()
        self._draw_graph()

    # -------------------------------------------------------------------------
    # Telemetry Ingestion & Vector Rendering
    # -------------------------------------------------------------------------

    def add_point(self, value: float, is_anomaly: bool = False, custom_label: str = None):
        """Append a real-time data point and preserve history for horizontal scrolling."""
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        idx = len(self.history_buffer)
        self.history_buffer.append({
            "val": value,
            "anomaly": is_anomaly,
            "time": ts,
            "label": custom_label or ""
        })

        if len(self.history_buffer) > self.max_history:
            self.history_buffer.pop(0)
            self.spike_indices = [i - 1 for i in self.spike_indices if i - 1 >= 0]
            idx -= 1

        if is_anomaly:
            self.spike_indices.append(idx)
            if not self.btn_spike.winfo_ismapped():
                self.btn_spike.pack(side="left", padx=3, before=self.btn_prev)
            self.btn_spike.configure(text=f"🚨 Spike ({len(self.spike_indices)})")

        if self.is_live:
            self.scroll_offset = 0
            self._update_slider_from_offset()

        self._draw_graph()

    def _get_visible_slice(self) -> Tuple[List[Dict[str, Any]], int]:
        """Extract the 40-point window currently visible on the canvas."""
        total = len(self.history_buffer)
        if total <= self.visible_points:
            return self.history_buffer, 0
        end_idx = total - self.scroll_offset
        start_idx = max(0, end_idx - self.visible_points)
        return self.history_buffer[start_idx:end_idx], start_idx

    def _draw_graph(self):
        """Perform flicker-free vector coordinate updates on persistent Canvas objects."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return

        visible_data, start_idx = self._get_visible_slice()
        n = len(visible_data)
        if n < 2:
            return

        # Position grid lines
        for idx, y_pct in enumerate((0.25, 0.5, 0.75)):
            y_pos = int(h * y_pct)
            self.canvas.coords(self._grid_lines[idx], 0, y_pos, w, y_pos)

        # Dynamic amplitude scale with minimum ceiling of 4.0 MB/s
        max_val = max(max(pt["val"] for pt in visible_data) * 1.25, 4.0)
        dx = w / (n - 1)
        coords = []
        has_anomaly = False
        peak_anomaly_val = 0.0
        peak_anomaly_pt = None

        for i, pt in enumerate(visible_data):
            x = i * dx
            y = h - 6 - ((pt["val"] / max_val) * (h - 16))
            coords.extend([x, y])
            if pt["anomaly"]:
                has_anomaly = True
                if pt["val"] > peak_anomaly_val:
                    peak_anomaly_val = pt["val"]
                    peak_anomaly_pt = (x, y, pt["time"])

        # Update filled polygon under curve
        poly_points = [0, h] + coords + [w, h]
        self.canvas.coords(self._poly_fill, *poly_points)

        # Update smooth bezier curves
        self.canvas.coords(self._curve_glow, *coords)
        self.canvas.coords(self._curve_line, *coords)

        # Update telemetry endpoint node
        last_x, last_y = coords[-2], coords[-1]
        self.canvas.coords(self._dot_pulse, last_x - 3.5, last_y - 3.5, last_x + 3.5, last_y + 3.5)

        # Render exfiltration spike callouts
        if has_anomaly:
            self.canvas.itemconfig(self._poly_fill, fill="#220814")
            self.canvas.itemconfig(self._curve_glow, fill="#660018")
            self.canvas.itemconfig(self._curve_line, fill=C_DANGER)
            self.canvas.itemconfig(self._dot_pulse, fill=C_DANGER, outline="#ffffff")

            if peak_anomaly_pt:
                px, py, pts = peak_anomaly_pt
                self.canvas.coords(self._spike_line, px, 0, px, h)
                self.canvas.itemconfig(self._spike_line, state="normal")
                self.canvas.coords(self._spike_marker, px - 5, py - 5, px + 5, py + 5)
                self.canvas.itemconfig(self._spike_marker, state="normal")
                text_x = min(max(px, 85), w - 85)
                self.canvas.coords(self._spike_text, text_x, max(14, py - 12))
                self.canvas.itemconfig(
                    self._spike_text,
                    text=f"🚨 EXFILTRATION SPIKE: {peak_anomaly_val:.2f} MB/s [{pts}]",
                    state="normal"
                )
        else:
            self.canvas.itemconfig(self._poly_fill, fill="#081324")
            self.canvas.itemconfig(self._curve_glow, fill="#00334d")
            self.canvas.itemconfig(self._curve_line, fill=C_CYAN)
            self.canvas.itemconfig(self._dot_pulse, fill="#ffffff", outline=C_CYAN)
            self.canvas.itemconfig(self._spike_line, state="hidden")
            self.canvas.itemconfig(self._spike_marker, state="hidden")
            self.canvas.itemconfig(self._spike_text, state="hidden")

        # Update header and scrubber labels based on live vs history mode
        if self.is_live:
            self.lbl_mode_badge.configure(text="● LIVE", fg_color="#06281E", text_color=C_SUCCESS)
            self.btn_live.configure(fg_color="#0E2A1E", text_color=C_SUCCESS)
            self.lbl_scrub_info.configure(text="Live Real-Time View", text_color=C_MUTED)
            latest_val = visible_data[-1]["val"]
            pkts = int(latest_val * 980 + random.randint(10, 50))
            if has_anomaly:
                self.lbl_current_rate.configure(
                    text=f"🚨 Surge: {latest_val:.2f} MB/s · {pkts:,} pkts/s",
                    text_color=C_DANGER
                )
            else:
                self.lbl_current_rate.configure(
                    text=f"Throughput: {latest_val:.2f} MB/s · {pkts:,} pkts/s",
                    text_color=C_CYAN
                )
        else:
            sec_back = self.scroll_offset * 2
            t_start = visible_data[0]["time"]
            t_end = visible_data[-1]["time"]
            self.lbl_mode_badge.configure(
                text=f"⏮ -{sec_back}s",
                fg_color="#2A1A06", text_color=C_WARNING
            )
            self.btn_live.configure(fg_color="#10192A", text_color=C_CYAN)
            self.lbl_scrub_info.configure(
                text=f"Replay: {t_start} ➔ {t_end}",
                text_color=C_WARNING
            )
            if has_anomaly:
                self.lbl_current_rate.configure(
                    text=f"🚨 EXFIL SPIKE: {peak_anomaly_val:.2f} MB/s",
                    text_color=C_DANGER
                )
            else:
                self.lbl_current_rate.configure(
                    text=f"History: {visible_data[-1]['val']:.2f} MB/s",
                    text_color=C_CYAN
                )
