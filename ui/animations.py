# =============================================================================
# FILE: ui/animations.py
# PURPOSE: High-Performance UI Micro-Interactions, Native Tkinter Schedulers,
#          and Tactile Feedback for ShadowMind Enterprise SOC.
# =============================================================================

import customtkinter as ctk

class CyberAnimator:
    """
    Handles zero-lag tactile micro-interactions, pulse animations via native
    widget.after() loop (preventing GIL/thread locks), and hover highlights.
    """

    @staticmethod
    def apply_button_hover(button: ctk.CTkButton, normal_bg: str, hover_bg: str, normal_text: str = None, hover_text: str = None):
        """Add tactile hover transitions to CTkButton."""
        CyberAnimator.apply_button_cyber_reaction(
            button, normal_bg=normal_bg, hover_bg=hover_bg,
            normal_text=normal_text, hover_text=hover_text
        )

    @staticmethod
    def apply_button_cyber_reaction(button: ctk.CTkButton,
                                    normal_bg: str,
                                    hover_bg: str,
                                    normal_text: str = None,
                                    hover_text: str = None,
                                    border_normal: str = None,
                                    border_hover: str = None,
                                    press_bg: str = None):
        """
        Tactile button reaction:
        - Hover: color shift and border lighting
        - Press: instantaneous tactile inset feedback
        """
        def on_enter(e):
            try:
                button.configure(fg_color=hover_bg)
                if hover_text:
                    button.configure(text_color=hover_text)
                if border_hover:
                    button.configure(border_color=border_hover)
            except Exception:
                pass

        def on_leave(e):
            try:
                button.configure(fg_color=normal_bg)
                if normal_text:
                    button.configure(text_color=normal_text)
                if border_normal:
                    button.configure(border_color=border_normal)
            except Exception:
                pass

        def on_press(e):
            try:
                if press_bg:
                    button.configure(fg_color=press_bg)
            except Exception:
                pass

        def on_release(e):
            try:
                button.configure(fg_color=hover_bg)
            except Exception:
                pass

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.bind("<Button-1>", on_press)
        button.bind("<ButtonRelease-1>", on_release)

    @staticmethod
    def apply_glow_card_hover(frame: ctk.CTkFrame,
                              normal_border: str = "#1E293B",
                              hover_border: str = "#00D5FF",
                              normal_bg: str = None,
                              hover_bg: str = None):
        """
        Card illumination on mouse touch / hover.
        """
        def on_enter(e):
            try:
                frame.configure(border_color=hover_border)
                if hover_bg:
                    frame.configure(fg_color=hover_bg)
            except Exception:
                pass

        def on_leave(e):
            try:
                frame.configure(border_color=normal_border)
                if normal_bg:
                    frame.configure(fg_color=normal_bg)
            except Exception:
                pass

        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)

    @staticmethod
    def apply_entry_focus_glow(entry: ctk.CTkEntry,
                               normal_border: str = "#1E293B",
                               focus_border: str = "#00D5FF",
                               normal_bg: str = "#0D1424",
                               focus_bg: str = "#101827"):
        """
        Terminal entry glow on input focus.
        """
        def on_focus_in(e):
            try:
                entry.configure(border_color=focus_border, fg_color=focus_bg)
            except Exception:
                pass

        def on_focus_out(e):
            try:
                entry.configure(border_color=normal_border, fg_color=normal_bg)
            except Exception:
                pass

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    @staticmethod
    def start_pulse_animation(label: ctk.CTkLabel, base_color: str, alert_color: str, interval: float = 1.0):
        """
        Native Tkinter pulse animation using label.after() instead of python threads,
        completely eliminating thread locks and main loop latency.
        Accepts interval in seconds (e.g. 1.0, 1.2) or milliseconds (e.g. 1000).
        """
        try:
            val = float(interval)
            ms = int(val * 1000) if val < 50 else int(val)
        except Exception:
            ms = 1000

        label._pulse_state = True
        label._pulse_active = True

        def step():
            if not getattr(label, "_pulse_active", False):
                return
            try:
                target = alert_color if label._pulse_state else base_color
                label.configure(text_color=target)
                label._pulse_state = not label._pulse_state
                label.after(ms, step)
            except Exception:
                label._pulse_active = False

        try:
            label.after(ms, step)
        except Exception:
            label._pulse_active = False

    @staticmethod
    def stop_pulse_animation(label: ctk.CTkLabel, reset_color: str):
        """Stop pulsing and reset label color."""
        label._pulse_active = False
        try:
            label.configure(text_color=reset_color)
        except Exception:
            pass
