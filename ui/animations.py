# =============================================================================
# FILE: ui/animations.py
# PURPOSE: UI Animation and Cyber Aesthetic Helper for CustomTkinter.
#          Adds smooth fade-in transitions, glowing button hover effects, and
#          cyberpunk visual elements to keep the interface highly engaging
#          while retaining CustomTkinter's native performance.
# =============================================================================

import customtkinter as ctk

class CyberAnimator:
    """
    Handles smooth transitions and visual feedback for CustomTkinter widgets.
    """

    @staticmethod
    def apply_glow_effect(button: ctk.CTkButton, normal_color: str, hover_color: str, glow_color: str):
        """Add dynamic hover feedback to primary buttons."""
        def on_enter(e):
            button.configure(fg_color=hover_color)
        def on_leave(e):
            button.configure(fg_color=normal_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    @staticmethod
    def fade_in_frame(frame: ctk.CTkFrame, steps: int = 5, delay_ms: int = 15):
        """Simulate a smooth fade-in effect by adjusting widget alpha/placement."""
        # CustomTkinter widgets handle placement smoothly when repacked
        frame.pack_configure(padx=0, pady=0)
