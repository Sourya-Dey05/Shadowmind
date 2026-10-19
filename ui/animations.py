# =============================================================================
# FILE: ui/animations.py
# PURPOSE: Advanced UI Micro-Interactions, Pulse Animations, and Smooth Transitions.
#          Provides professional-grade visual polish, pulsing alert indicators,
#          and seamless frame animations for ShadowMind.
# =============================================================================

import time
import threading
import customtkinter as ctk

class CyberAnimator:
    """
    Handles advanced micro-interactions, pulsing glows, and smooth state transitions.
    """

    @staticmethod
    def apply_button_hover(button: ctk.CTkButton, normal_bg: str, hover_bg: str, normal_text: str = None, hover_text: str = None):
        """Add tactile hover transitions to CTkButton."""
        def on_enter(e):
            try:
                button.configure(fg_color=hover_bg)
                if hover_text:
                    button.configure(text_color=hover_text)
            except Exception:
                pass

        def on_leave(e):
            try:
                button.configure(fg_color=normal_bg)
                if normal_text:
                    button.configure(text_color=normal_text)
            except Exception:
                pass

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    @staticmethod
    def start_pulse_animation(label: ctk.CTkLabel, base_color: str, alert_color: str, interval_sec: float = 1.0):
        """Pulse an indicator label or badge to draw attention during alerts."""
        def pulse_loop():
            is_alt = False
            while getattr(label, "_pulsing", True):
                try:
                    target_color = alert_color if is_alt else base_color
                    label.configure(text_color=target_color)
                    is_alt = not is_alt
                except Exception:
                    break
                time.sleep(interval_sec)

        label._pulsing = True
        t = threading.Thread(target=pulse_loop, daemon=True)
        t.start()

    @staticmethod
    def stop_pulse_animation(label: ctk.CTkLabel, reset_color: str):
        """Stop pulsing and reset label color."""
        label._pulsing = False
        try:
            label.configure(text_color=reset_color)
        except Exception:
            pass
