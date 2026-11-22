# =============================================================================
# FILE: ui/widgets/scrollable_log.py
# PURPOSE: High-Performance, Zero-Lag Real-Time Security Incident Stream.
#          - O(1) incremental DOM updates (zero UI freeze).
#          - Smart Non-Intrusive Auto-Scroll (does NOT yank the user if scrolled up).
#          - Seamless in-place telemetry updates to prevent scrollbar slider creeping.
#          - Color-coded severity chips and smooth hover micro-reactions.
# =============================================================================

import customtkinter as ctk
from typing import Callable, Optional
from ui.theme import (
    COLOR_SURFACE, COLOR_CARD, COLOR_BORDER, COLOR_BORDER_HOVER,
    COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING, COLOR_BLUE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    FONT_MONO, FONT_BODY
)


class InteractiveLogViewer(ctk.CTkScrollableFrame):
    """
    High-density, 60fps security event timeline widget.
    Renders incoming security events with O(1) single-widget insertion,
    severity tags, and smart non-intrusive auto-scrolling.
    """

    def __init__(self, parent, max_entries: int = 150, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.max_entries = max_entries
        self._entries_count = 0
        self.auto_scroll_enabled = True
        self._is_appending = False
        self._on_scroll_callback: Optional[Callable[[bool], None]] = None

        # Intercept scrollbar drag/click events
        try:
            self._orig_scrollbar_cmd = self._parent_canvas.yview
            def _on_scrollbar_drag(*args):
                self._orig_scrollbar_cmd(*args)
                self._evaluate_scroll_position()
            self._scrollbar.configure(command=_on_scrollbar_drag)
        except Exception:
            pass

        # Intercept mouse wheel scrolling across all child widgets
        try:
            self._orig_mouse_wheel = self._mouse_wheel_all
            def _wrapped_mouse_wheel(event):
                res = self._orig_mouse_wheel(event)
                self._evaluate_scroll_position()
                return res
            self._mouse_wheel_all = _wrapped_mouse_wheel
        except Exception:
            pass

        # Intercept yscrollcommand to eliminate scrollbar thumb jumping
        try:
            self._orig_yscrollcommand = self._scrollbar.set
            self._parent_canvas.configure(yscrollcommand=self._custom_yscrollcommand)
        except Exception:
            pass

    def _custom_yscrollcommand(self, start, end):
        """
        Intercept Tkinter canvas yscrollcommand callbacks:
        - When appending new logs while user is at the bottom, lock thumb directly to 1.0,
          completely eliminating visual slider jitter / jumping.
        - When user is scrolled up or interacting, evaluate scroll position cleanly.
        """
        try:
            s, e = float(start), float(end)
            if not self._is_appending:
                self._evaluate_scroll_position()
                self._orig_yscrollcommand(s, e)
            else:
                if self.auto_scroll_enabled:
                    self._parent_canvas.yview_moveto(1.0)
                    self._orig_yscrollcommand(s, 1.0)
                else:
                    self._orig_yscrollcommand(s, e)
        except Exception:
            pass

    def set_scroll_callback(self, callback: Callable[[bool], None]):
        """Register a callback that receives True when at bottom, False when scrolled up."""
        self._on_scroll_callback = callback

    def _evaluate_scroll_position(self):
        """Detect whether user has scrolled up or returned to the latest logs."""
        try:
            top, bottom = self._parent_canvas.yview()
            is_at_bottom = bottom >= 0.99
            if is_at_bottom != self.auto_scroll_enabled:
                self.auto_scroll_enabled = is_at_bottom
                if self._on_scroll_callback:
                    self._on_scroll_callback(is_at_bottom)
                # When user scrolls back to the bottom, trim excess entries accumulated while viewing history
                if is_at_bottom:
                    children = self.winfo_children()
                    while len(children) > self.max_entries:
                        try:
                            children[0].destroy()
                            children.pop(0)
                        except Exception:
                            break
        except Exception:
            pass

    def is_at_bottom(self) -> bool:
        """Return True if currently scrolled to the latest entries."""
        try:
            top, bottom = self._parent_canvas.yview()
            return bottom >= 0.99
        except Exception:
            return True

    def scroll_to_bottom(self):
        """Force scroll view to the bottom / latest log entry and re-pin auto-scroll."""
        try:
            self.auto_scroll_enabled = True
            self.update_idletasks()
            self._parent_canvas.yview_moveto(1.0)
            if self._on_scroll_callback:
                self._on_scroll_callback(True)
        except Exception:
            pass

    def append_log(self, message: str, level: str = "INFO", is_benign: bool = False):
        """
        Append a single row incrementally in O(1) time without re-rendering existing widgets.
        Appends every new entry smoothly (including 2.0s benign telemetry).
        If the user is at the bottom, auto-scroll stays pinned without thumb jumping.
        If the user has scrolled up, NEVER redirects or yanks their view!
        """
        self._is_appending = True
        try:
            level_upper = level.upper()
            if any(k in level_upper for k in ("ALERT", "DANGER", "CRITICAL", "BREACH", "EXFILTRATION")):
                badge_color = COLOR_DANGER
                badge_text = "CRIT"
                bg_color = "#1E121A"
                border_clr = "#3D1724"
            elif any(k in level_upper for k in ("WARN", "WARNING", "SUSPICIOUS", "ANOMALY")):
                badge_color = COLOR_WARNING
                badge_text = "WARN"
                bg_color = "#1C1710"
                border_clr = "#3B2A14"
            elif "INTEL" in level_upper or "GEO" in level_upper:
                badge_color = COLOR_BLUE
                badge_text = "INTEL"
                bg_color = "#10192A"
                border_clr = "#1B2A47"
            else:
                badge_color = COLOR_SUCCESS
                badge_text = "INFO"
                bg_color = "#0E1626"
                border_clr = COLOR_BORDER

            # Only trim oldest entry if user is actively pinned to bottom,
            # so scrolled-up reading position does not shift unexpectedly.
            if self.auto_scroll_enabled:
                children = self.winfo_children()
                if len(children) >= self.max_entries:
                    try:
                        children[0].destroy()
                    except Exception:
                        pass

            # Create row card
            row_card = ctk.CTkFrame(
                self,
                fg_color=bg_color,
                corner_radius=4,
                border_width=1,
                border_color=border_clr
            )
            row_card.pack(fill="x", pady=2, padx=2)

            def on_enter(e, card=row_card, b_clr=badge_color):
                try:
                    card.configure(border_color=b_clr)
                except Exception:
                    pass

            def on_leave(e, card=row_card, orig_border=border_clr):
                try:
                    card.configure(border_color=orig_border)
                except Exception:
                    pass

            row_card.bind("<Enter>", on_enter)
            row_card.bind("<Leave>", on_leave)

            # Severity Badge
            badge = ctk.CTkLabel(
                row_card,
                text=f" {badge_text} ",
                font=ctk.CTkFont(family=FONT_BODY, size=9, weight="bold"),
                fg_color=badge_color,
                text_color="#080D19",
                corner_radius=3,
                width=42,
                height=18
            )
            badge.pack(side="left", padx=8, pady=5, anchor="n")

            # Message with automatic clean wrapping
            msg_lbl = ctk.CTkLabel(
                row_card,
                text=message,
                font=ctk.CTkFont(family=FONT_BODY, size=10),
                text_color=COLOR_TEXT_PRIMARY,
                anchor="w",
                justify="left",
                wraplength=480
            )
            msg_lbl.pack(side="left", padx=4, pady=5, fill="x", expand=True)
            msg_lbl.bind("<Enter>", on_enter)
            msg_lbl.bind("<Leave>", on_leave)

            self._entries_count += 1

            # SMART NON-INTRUSIVE AUTO-SCROLL (Debounced via after_idle to eliminate UI freeze)
            # If user is scrolled up (auto_scroll_enabled is False), NEVER move or yank the view!
            # If user is pinned at bottom (auto_scroll_enabled is True), stay pinned seamlessly without jumping.
            if self.auto_scroll_enabled and not getattr(self, "_scroll_pending", False):
                self._scroll_pending = True
                def _do_scroll():
                    self._scroll_pending = False
                    try:
                        self._parent_canvas.yview_moveto(1.0)
                    except Exception:
                        pass
                self.after_idle(_do_scroll)
        finally:
            self._is_appending = False

    def clear(self):
        """Clear all entries."""
        for widget in self.winfo_children():
            widget.destroy()
        self._entries_count = 0
