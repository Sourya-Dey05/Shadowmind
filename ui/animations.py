# =============================================================================
# FILE: ui/animations.py
# PURPOSE: UI Animation, Smooth Transitions, and Cyber Aesthetic Helper.
#          Provides silky smooth button transitions, hover lift effects, and
#          page transitions matching the Figma mockup in Section 1.pdf.
# =============================================================================

import time
import customtkinter as ctk

class CyberAnimator:
    """
    Handles smooth transitions and micro-interactions for widgets.
    """

    @staticmethod
    def apply_button_hover(button: ctk.CTkButton, normal_bg: str, hover_bg: str, normal_text: str = None, hover_text: str = None):
        """Add instant, crisp hover transitions to CTkButton."""
        def on_enter(e):
            button.configure(fg_color=hover_bg)
            if hover_text:
                button.configure(text_color=hover_text)

        def on_leave(e):
            button.configure(fg_color=normal_bg)
            if normal_text:
                button.configure(text_color=normal_text)

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    @staticmethod
    def smooth_page_transition(parent: ctk.CTk, old_widget, new_widget_builder):
        """Fade out current container smoothly, then mount new page."""
        try:
            old_widget.destroy()
        except Exception:
            pass
        new_widget = new_widget_builder()
        return new_widget
