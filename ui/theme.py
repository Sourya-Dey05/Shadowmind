# =============================================================================
# FILE: ui/theme.py
# PURPOSE: Design tokens, color palette, and styling metrics extracted directly
#          from the Figma design specification in Section 1.pdf.
# =============================================================================

# Primary Background & Surface Palette
COLOR_BG            = "#07080e"   # Deep Void Background
COLOR_SURFACE       = "#0d1017"   # Panel Surface
COLOR_CARD          = "#10141c"   # Card Background
COLOR_CARD_HOVER    = "#141923"   # Card Highlight State
COLOR_BORDER        = "#1b2230"   # Subtle structural border
COLOR_BORDER_FOCUS  = "#00c2f7"   # Active cyan focus ring

# Brand & Accent Tokens
COLOR_CYAN          = "#00c2f7"   # Primary Brand Cyan
COLOR_CYAN_DIM      = "#008cb3"   # Muted Cyan
COLOR_CYAN_GLOW     = "#052636"   # Soft cyan glow backdrop

# State Tokens
COLOR_SUCCESS       = "#00c663"   # Active / Healthy / Verified Green
COLOR_WARNING       = "#ffaa00"   # Warning / Guard Amber
COLOR_DANGER        = "#ff4343"   # Alert / Confirmed Threat Crimson
COLOR_PURPLE        = "#a855f7"   # Key Reference / Enclave Tag

# Text Hierarchy
COLOR_TEXT_PRIMARY   = "#e8edf2"  # Main high-contrast headings
COLOR_TEXT_SECONDARY = "#94a3b8"  # Subtitles, labels, descriptions
COLOR_TEXT_MUTED     = "#55647a"  # Timestamps, metadata, subtle hints
COLOR_TEXT_DIM       = "#3b4759"  # Borders & decorative marks

# Fonts - Clean, high-readability Windows native fonts matching Figma
FONT_TITLE  = "Segoe UI"
FONT_BODY   = "Segoe UI"
FONT_MONO   = "Consolas"
FONT_BRAND  = "Segoe UI"
