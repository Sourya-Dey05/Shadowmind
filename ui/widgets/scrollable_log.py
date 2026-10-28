# =============================================================================
# FILE: ui/widgets/scrollable_log.py
# PURPOSE: Custom User-Friendly Log Console Widget.
#          - Renders log entries as clean, card-like rows with colored severity tags
#            (GREEN for Benign/Normal, RED for Attacks/Breaches, YELLOW for Suspicious).
#          - Prevents auto-scroll annoyance: only auto-scrolls to bottom when the
#            user is already at the bottom. If the user scrolls up to review history,
#            it preserves their scroll position so new events don't yank them down!
# =============================================================================

import customtkinter as ctk
from ui.theme import (
    COLOR_SURFACE, COLOR_CARD, COLOR_BORDER, COLOR_SUCCESS,
    COLOR_DANGER, COLOR_WARNING, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, FONT_MONO
)


class InteractiveLogViewer(ctk.CTkScrollableFrame):
    """
    A modern, card-based log feed that supports color-coded severity tags,
    full text visibility without truncation, and smart scroll locking.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self._entries = []

    def append_log(self, message: str, level: str = "INFO"):
        """Append a log entry with color coding based on level (INFO, WARN, ALERT)."""
        self._entries.append((message, level))
        if len(self._entries) > 100:  # Cap at 100 entries for memory performance
            self._entries.pop(0)
        self._render()

    def clear(self):
        self._entries.clear()
        self._render()

    def _render(self):
        # Clear existing rows
        for widget in self.winfo_children():
            widget.destroy()

        for msg, level in self._entries:
            # Determine color tags
            if level in ("ALERT", "DANGER", "CRITICAL"):
                badge_color = COLOR_DANGER
                badge_text = "ALERT"
                bg_color = "#211114"  # Subtle reddish tint
            elif level in ("WARN", "WARNING", "SUSPICIOUS"):
                badge_color = COLOR_WARNING
                badge_text = "WARN"
                bg_color = "#211a11"  # Subtle amber tint
            else:
                badge_color = COLOR_SUCCESS
                badge_text = "INFO"
                bg_color = COLOR_SURFACE

            row_card = ctk.CTkFrame(
                self,
                fg_color=bg_color,
                corner_radius=6,
                border_width=1,
                border_color=COLOR_BORDER
                # removed fixed height so long messages expand vertically and never get cut off
            )
            row_card.pack(fill="x", pady=3, padx=4)

            # Severity Badge
            badge = ctk.CTkLabel(
                row_card,
                text=f" {badge_text} ",
                font=ctk.CTkFont(family=FONT_MONO, size=9, weight="bold"),
                fg_color=badge_color,
                text_color="#07080e",
                corner_radius=4,
                width=48,
                height=20
            )
            badge.pack(side="left", padx=10, pady=8, anchor="n")

            # Log Message with full text wrapping enabled
            msg_lbl = ctk.CTkLabel(
                row_card,
                text=msg,
                font=ctk.CTkFont(family=FONT_MONO, size=11),
                text_color=COLOR_TEXT_PRIMARY,
                anchor="w",
                justify="left",
                wraplength=450  # Automatically wraps long IP paths and telemetry text cleanly
            )
            msg_lbl.pack(side="left", padx=4, pady=8, fill="x", expand=True)
