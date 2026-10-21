# =============================================================================
# FILE: make_svg.py
# PURPOSE: Convert PNG logo to embedded SVG data URI wrapper.
# =============================================================================

import base64

with open("Futuristic Shadowmind Emblem Logo.png", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1404 1120" width="100%" height="100%">
  <image href="data:image/png;base64,{encoded}" width="1404" height="1120" />
</svg>'''

with open("website/logo.svg", "w") as f:
    f.write(svg_content)

print("Created website/logo.svg successfully")
