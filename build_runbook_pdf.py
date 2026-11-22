# =============================================================================
# FILE: build_runbook_pdf.py
# PURPOSE: Generates a high-quality, professional, printable PDF Runbook
#          for ShadowMind multi-device attack simulations (Serial, Parallel, Multi-Hop).
# =============================================================================

import os
import sys
import shutil
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "SHADOWMIND DEFENSIVE FRAMEWORK // ATTACK SIMULATION RUNBOOK")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)
            
        # Footer
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "CONFIDENTIAL & PROPRIETARY — FOR EVALUATION & DEFENSE TESTING ONLY")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def generate_runbook_pdf(output_pdf_path: str):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0f172a")     # Slate 900
    c_secondary = colors.HexColor("#1e3a8a")   # Blue 900
    c_accent = colors.HexColor("#0284c7")      # Sky 600
    c_dark = colors.HexColor("#1e293b")        # Slate 800
    c_danger = colors.HexColor("#b91c1c")      # Red 700
    c_warning = colors.HexColor("#d97706")     # Amber 600
    c_success = colors.HexColor("#059669")     # Emerald 600
    c_code_bg = colors.HexColor("#f1f5f9")     # Slate 100
    c_callout_bg = colors.HexColor("#f8fafc")  # Slate 50

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_accent,
        spaceAfter=14
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_secondary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_dark,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0f172a"),
        backColor=c_code_bg,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # =========================================================================
    # COVER / HEADER
    # =========================================================================
    story.append(Paragraph("SHADOWMIND CYBERSECURITY FRAMEWORK", title_style))
    story.append(Paragraph("Live Attack Simulation Runbook: Serial, Parallel & Multi-Hop IP Hopping", subtitle_style))
    story.append(Paragraph("<b>Version:</b> 2.4 (Production Standard) &nbsp;|&nbsp; <b>Classification:</b> Operational Lab Runbook &nbsp;|&nbsp; <b>Environment:</b> Multi-Device & Mobile Relay", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=0, spaceAfter=12))

    # =========================================================================
    # SECTION 1: SYSTEM ARCHITECTURE & DEMO MATRIX
    # =========================================================================
    story.append(Paragraph("1. Attack Simulation Overview & Route Matrix", h1_style))
    story.append(Paragraph(
        "ShadowMind employs a hybrid neural architecture (Spatial CNN + Temporal LSTM + HoneyGraph GNN + MLP Fusion) "
        "paired with Poison Pill active defenses (emergency AES-256 key rotation in &lt;1.84ms, dynamic honeypot diversion, "
        "and physical vault auto-encryption). The table below outlines how each attack vector routes and appears on the SOC Dashboard:",
        body_style
    ))

    matrix_data = [
        [
            Paragraph("<b>Attack Vector</b>", body_style),
            Paragraph("<b>Attacker Tool / Script</b>", body_style),
            Paragraph("<b>Network Path & Hop Count</b>", body_style),
            Paragraph("<b>Dashboard Display Behavior</b>", body_style)
        ],
        [
            Paragraph("<b>Serial Attack</b><br/>(Sequential Recon)", body_style),
            Paragraph("<code>serial_attack.py</code><br/>(Attacker Laptop 2)", body_style),
            Paragraph("<b>Direct 2-Node:</b><br/>Laptop 2 ➔ Target Vault", body_style),
            Paragraph("<b>NO IP Hopping</b> (Clean 2-Node Path)<br/>Badge: <code>● SERIAL</code> (Cyan)<br/>Sequential probing rate logged", body_style)
        ],
        [
            Paragraph("<b>Parallel Attack</b><br/>(Concurrent Flood)", body_style),
            Paragraph("<code>parallel_attack.py</code><br/>(Attacker Laptop 2)", body_style),
            Paragraph("<b>Direct 2-Node:</b><br/>Laptop 2 ➔ Target Vault", body_style),
            Paragraph("<b>NO IP Hopping</b> (Clean 2-Node Path)<br/>Badge: <code>● PARALLEL</code> (Amber)<br/>Concurrent threads flood logged", body_style)
        ],
        [
            Paragraph("<b>Multi-Hop Attack</b><br/>(Lateral Movement)", body_style),
            Paragraph("<code>proxy.py</code> (Phone)<br/><code>multihop_attack.py</code>", body_style),
            Paragraph("<b>3-Node Proxy Relay:</b><br/>Laptop 2 ➔ Phone ➔ Target", body_style),
            Paragraph("<b>YES — IP HOPPING DETECTED</b><br/>Badge: <code>● IP HOPPING</code> (Crimson)<br/>Hop 1 ➔ Hop 2 ➔ Target Enclave", body_style)
        ]
    ]

    t_matrix = Table(matrix_data, colWidths=[1.3*inch, 1.5*inch, 1.7*inch, 2.5*inch])
    t_matrix.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_matrix)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 2: HARDWARE & ENVIRONMENT PREPARATION
    # =========================================================================
    story.append(Paragraph("2. Device Setup & Pre-Requisites", h1_style))
    story.append(Paragraph("<b>Device A — Laptop 1 (Target Defense Node):</b>", h2_style))
    story.append(Paragraph("• Running Windows with ShadowMind repository cloned (`d:\\Shadowmind`).", bullet_style))
    story.append(Paragraph("• Active local server listening on port <b>8080</b> (automatically started by UI).", bullet_style))
    story.append(Paragraph("• Public exposure command (for multi-network / cellular routing):", bullet_style))
    story.append(Paragraph("<code>cloudflared tunnel --url http://localhost:8080</code><br/><i>— or using Pinggy: —</i><br/><code>ssh -p 443 -R0:localhost:8080 qr@a.pinggy.io</code>", code_style))

    story.append(Paragraph("<b>Device B — Mobile Phone (Intermediate Relay Node):</b>", h2_style))
    story.append(Paragraph("• Android device with <b>Termux</b> (recommended) or <b>Pydroid 3</b> installed.", bullet_style))
    story.append(Paragraph("• File needed on phone: <code>proxy.py</code> (zero pip dependencies needed).", bullet_style))
    story.append(Paragraph("• Connected to <b>Cellular Data (4G/5G)</b> with <b>Mobile Hotspot enabled</b>.", bullet_style))

    story.append(Paragraph("<b>Device C — Laptop 2 (Attacker Device):</b>", h2_style))
    story.append(Paragraph("• Any laptop with Python 3.8+ installed (Windows, Mac, or Linux/Kali).", bullet_style))
    story.append(Paragraph("• Files needed: <code>serial_attack.py</code>, <code>parallel_attack.py</code>, <code>multihop_attack.py</code>.", bullet_style))
    story.append(Paragraph("• Connected to Phone's Wi-Fi Hotspot for the Multi-Hop demo.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 3: ATTACK VECTOR 1 — SERIAL ATTACK
    # =========================================================================
    story.append(Paragraph("3. Step-by-Step: Serial (Sequential) Attack", h1_style))
    story.append(Paragraph(
        "<b>Concept:</b> The serial attack simulates a stealthy adversary performing low-and-slow reconnaissance. "
        "Each request accesses high-value vault files sequentially with a built-in time delay, aiming to evade simple threshold alarms.",
        body_style
    ))

    story.append(Paragraph("<b>Step 1 — (Optional) Customize Files to Steal:</b>", h2_style))
    story.append(Paragraph("Open <code>serial_attack.py</code> on Laptop 2. The <code>VAULT_FILES</code> list can be customized as desired:", body_style))
    story.append(Paragraph("""VAULT_FILES = [
    ("Database Credentials",         "/vault/credentials.env.enc"),
    ("Customer SQL Database Dump",    "/vault/customer_database_dump.sql"),
    ("Proprietary Source Code",      "/vault/source_code.zip"),
    ("AWS Production Cloud Keys",     "/vault/aws_production_keys.env"),
    ("Corporate Financial Passwords","/vault/financial_passwords_2026.xlsx"),
    ("Executive Payroll & Salaries", "/vault/executive_payroll_salaries.pdf"),
    ("Internal Network Topology",    "/vault/internal_network_topology.txt"),
    ("R&D Secret Project Intel",     "/vault/secret_project_intel.txt"),
]""", code_style))

    story.append(Paragraph("<b>Step 2 — Execute Serial Attack from Laptop 2:</b>", h2_style))
    story.append(Paragraph("Run the attack script passing the Target Laptop's URL (LAN IP or Cloudflare/Pinggy Tunnel):", body_style))
    story.append(Paragraph("# If on the same Wi-Fi network:\npython serial_attack.py http://192.168.29.250:8080\n\n# If connecting over Cloudflare Public Tunnel:\npython serial_attack.py https://when-point-triple-ticket.trycloudflare.com", code_style))

    story.append(Paragraph("<b>Step 3 — Observe Console on Laptop 2:</b>", h2_style))
    story.append(Paragraph("The terminal downloads each requested asset and confirms that Poison Pill defense was engaged:", body_style))
    story.append(Paragraph("""[1/8] 🎯 Requesting: Database Credentials
      Endpoint : GET /vault/credentials.env.enc
      Status   : 200 OK
      Size     : 2,842 bytes (Latency: 28.4ms)
      Defense  : 🔒 [POISON PILL DETECTED] Plaintext destroyed into unrecoverable ciphertext!
      Saved to : exfiltrated_serial_evidence/serial_credentials.env.enc
      ⏳ Pausing 3.0s (simulating stealth reconnaissance)...""", code_style))

    story.append(Paragraph("<b>Step 4 — Verify Results on Laptop 1 (ShadowMind Dashboard):</b>", h2_style))
    story.append(Paragraph("• <b>Pipeline Banner:</b> Displays <code>🔍 DIRECT SERIAL ATTACK DETECTED: Direct Source: [IP] (Sequential Probes) ➔ Target [Vault]</code>.", bullet_style))
    story.append(Paragraph("• <b>NO IP Hopping:</b> Hop 2 and intermediate relay badges are dynamically hidden. Shows clean 2-node path.", bullet_style))
    story.append(Paragraph("• <b>GNN Radar Card:</b> Displays badge <code>● SERIAL</code> in cyan.", bullet_style))
    story.append(Paragraph("• <b>Vault Security:</b> Physical files in <code>d:\\Shadowmind\\Vault</code> are auto-encrypted into <code>.enc</code> ciphertext.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 4: ATTACK VECTOR 2 — PARALLEL ATTACK
    # =========================================================================
    story.append(Paragraph("4. Step-by-Step: Parallel (Concurrent Flood) Attack", h1_style))
    story.append(Paragraph(
        "<b>Concept:</b> The parallel attack simulates a high-intensity distributed credential dump or automated exploit blitz. "
        "Multiple worker threads hit the vault simultaneously across parallel TCP connections.",
        body_style
    ))

    story.append(Paragraph("<b>Step 1 — Execute Parallel Attack from Laptop 2:</b>", h2_style))
    story.append(Paragraph("Launch <code>parallel_attack.py</code> with 8 concurrent worker threads:", body_style))
    story.append(Paragraph("# If on the same Wi-Fi network:\npython parallel_attack.py http://192.168.29.250:8080\n\n# If connecting over Cloudflare Public Tunnel:\npython parallel_attack.py https://when-point-triple-ticket.trycloudflare.com", code_style))

    story.append(Paragraph("<b>Step 2 — Observe Multi-Threaded Execution on Laptop 2:</b>", h2_style))
    story.append(Paragraph("""⚡ [Worker 01] Database Credentials ➔ 200 OK | 2,842 bytes in 19.8ms 🔒 [POISON PILL TRAPPED]
⚡ [Worker 02] Customer SQL Dump     ➔ 200 OK | 2,842 bytes in 21.2ms 🔒 [POISON PILL TRAPPED]
⚡ [Worker 03] Proprietary Code     ➔ 200 OK | 2,842 bytes in 22.5ms 🔒 [POISON PILL TRAPPED]
⚡ [Worker 04] AWS Production Keys  ➔ 200 OK | 2,842 bytes in 24.1ms 🔒 [POISON PILL TRAPPED]
✅ PARALLEL ATTACK COMPLETE in 48.72 ms""", code_style))

    story.append(Paragraph("<b>Step 3 — Verify Results on Laptop 1 (ShadowMind Dashboard):</b>", h2_style))
    story.append(Paragraph("• <b>Pipeline Banner:</b> Displays <code>⚡ DIRECT PARALLEL ATTACK DETECTED: Direct Source: [IP] (Multi-Threaded) ➔ Target [Vault]</code>.", bullet_style))
    story.append(Paragraph("• <b>NO IP Hopping:</b> Direct path; Hop 2 intermediate relay is hidden.", bullet_style))
    story.append(Paragraph("• <b>GNN Radar Card:</b> Displays badge <code>● PARALLEL</code> in amber.", bullet_style))
    story.append(Paragraph("• <b>Active Response:</b> DEFCON 1 triggered, emergency key rotated in &lt;1.84ms.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 5: ATTACK VECTOR 3 — MULTI-HOP ATTACK (IP HOPPING)
    # =========================================================================
    story.append(Paragraph("5. Step-by-Step: Multi-Hop Lateral Movement Attack (IP Hopping)", h1_style))
    story.append(Paragraph(
        "<b>Concept:</b> An external threat actor pivots through an intermediate compromised internal device (the phone) "
        "on a separate network to camouflage their true point of origin. HoneyGraph GNN correlates the proxy headers "
        "and reconstructs the multi-hop attack topology in real-time.",
        body_style
    ))

    # Network Setup Box
    setup_box = [
        [Paragraph("<b>★ HOW TO PUT THE PHONE ON A SEPARATE NETWORK (CELLULAR HOTSPOT SETUP)</b>", h2_style)],
        [Paragraph(
            "1. <b>On Phone:</b> Turn ON <b>Mobile Cellular Data (4G/5G)</b> and enable <b>Wi-Fi Mobile Hotspot</b>.<br/>"
            "2. <b>On Laptop 2 (Attacker):</b> Disconnect from Home Wi-Fi and connect to the <b>Phone's Hotspot</b>.<br/>"
            "3. <b>On Laptop 1 (Target):</b> Stays connected to Home Wi-Fi running ShadowMind + Cloudflare Tunnel.<br/>"
            "<i>Result: Laptop 2 & Phone are on an isolated cellular subnet (192.168.43.x), while Laptop 1 is on Home Wi-Fi!</i>",
            body_style
        )]
    ]
    t_setup = Table(setup_box, colWidths=[7.0*inch])
    t_setup.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_callout_bg),
        ('BOX', (0, 0), (-1, -1), 1, c_accent),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_setup)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Step 1 — Start the Proxy Relay on the Phone:</b>", h2_style))
    story.append(Paragraph("Open <b>Termux</b> on the phone and execute <code>proxy.py</code> passing Laptop 1's tunnel URL:", body_style))
    story.append(Paragraph("# In Termux on Phone:\npython proxy.py https://when-point-triple-ticket.trycloudflare.com 9000", code_style))
    story.append(Paragraph("The phone terminal will output:", body_style))
    story.append(Paragraph("""===========================================================================
  🌐 SHADOWMIND MULTI-HOP PROXY RELAY (Device B / Intermediate Node)
===========================================================================
 Proxy Listening IP  : 0.0.0.0 (Phone Local IP: 192.168.43.1)
 Proxy Listening Port: 9000
 Forwarding Upstream : https://when-point-triple-ticket.trycloudflare.com
===========================================================================
📡 On Laptop 2 (Attacker), run:
   python multihop_attack.py http://192.168.43.1:9000""", code_style))

    story.append(Paragraph("<b>Step 2 — Launch Multi-Hop Attack from Laptop 2:</b>", h2_style))
    story.append(Paragraph("On Laptop 2 (connected to the Phone's hotspot Wi-Fi), run <code>multihop_attack.py</code>:", body_style))
    story.append(Paragraph("python multihop_attack.py http://192.168.43.1:9000", code_style))

    story.append(Paragraph("<b>Step 3 — Observe Proxy Relay in Action:</b>", h2_style))
    story.append(Paragraph("• <b>Phone Terminal:</b> Displays <code>[HOP 2 RELAY] ➔ Intercepted Probe from Attacker IP: 192.168.43.xxx ... Relaying to Target Vault</code>.<br/>"
                           "• <b>Laptop 2 Terminal:</b> Successfully captures the Poison Pill ciphertext dumped through the proxy.", body_style))

    story.append(Paragraph("<b>Step 4 — Verify Results on Laptop 1 (ShadowMind Dashboard):</b>", h2_style))
    story.append(Paragraph("• <b>Pipeline Banner:</b> Flashes bright crimson with full 3-node path:<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;<code>🚨 GNN MULTI-HOP ATTACK PATH (IP HOPPING): Hop 1: [Laptop 2 IP] ➔ Hop 2: [Phone Relay IP] ➔ Target: 10.0.0.50 (Vault)</code>", bullet_style))
    story.append(Paragraph("• <b>GNN Radar Card:</b> Displays badge <code>● IP HOPPING</code> in bright crimson with border highlight.", bullet_style))
    story.append(Paragraph("• <b>HoneyGraph Topology:</b> Multi-hop edge is dynamically constructed and displayed on radar.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 6: FORENSIC VERIFICATION & AUDIT SYNC
    # =========================================================================
    story.append(Paragraph("6. Forensic Verification & Audit Log Refresh", h1_style))
    story.append(Paragraph(
        "<b>Verifying Cryptographic Defense:</b> Open any file in Laptop 2's <code>exfiltrated_evidence</code> folder. "
        "Notice that all plaintext data was annihilated into high-entropy AES ciphertext noise with key zeroization headers.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Syncing Telemetry in Dashboard:</b> Navigate to the <b>Settings Tab</b> in ShadowMind and click <b>[🔄 Refresh Audit Log]</b>. "
        "The button confirms with <code>✓ Telemetry Synchronized!</code> and displays the exact attack classification, timestamp, and IP dossier from disk.",
        body_style
    ))

    # =========================================================================
    # SECTION 7: QUICK REFERENCE COMMAND CHEAT SHEET
    # =========================================================================
    story.append(Spacer(1, 6))
    story.append(Paragraph("7. Quick Command Reference Cheat Sheet", h1_style))
    cheat_data = [
        [Paragraph("<b>Step / Role</b>", body_style), Paragraph("<b>Device</b>", body_style), Paragraph("<b>Command to Execute</b>", body_style)],
        [
            Paragraph("1. Start ShadowMind", body_style),
            Paragraph("Laptop 1", body_style),
            Paragraph("<code>python main.py</code>", code_style)
        ],
        [
            Paragraph("2. Expose Public Tunnel", body_style),
            Paragraph("Laptop 1", body_style),
            Paragraph("<code>cloudflared tunnel --url http://localhost:8080</code>", code_style)
        ],
        [
            Paragraph("3. Run Serial Attack", body_style),
            Paragraph("Laptop 2", body_style),
            Paragraph("<code>python serial_attack.py &lt;TUNNEL_OR_IP_URL&gt;</code>", code_style)
        ],
        [
            Paragraph("4. Run Parallel Attack", body_style),
            Paragraph("Laptop 2", body_style),
            Paragraph("<code>python parallel_attack.py &lt;TUNNEL_OR_IP_URL&gt;</code>", code_style)
        ],
        [
            Paragraph("5. Start Phone Relay", body_style),
            Paragraph("Phone (Hotspot)", body_style),
            Paragraph("<code>python proxy.py &lt;TUNNEL_URL&gt; 9000</code>", code_style)
        ],
        [
            Paragraph("6. Run Multi-Hop Attack", body_style),
            Paragraph("Laptop 2", body_style),
            Paragraph("<code>python multihop_attack.py http://192.168.43.1:9000</code>", code_style)
        ],
    ]
    t_cheat = Table(cheat_data, colWidths=[1.7*inch, 1.2*inch, 4.1*inch])
    t_cheat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_cheat)

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Runbook PDF generated successfully at: {output_pdf_path}")


if __name__ == "__main__":
    out_dir = Path("d:/Shadowmind")
    target_path = out_dir / "ShadowMind_Attack_Simulation_Runbook.pdf"
    generate_runbook_pdf(str(target_path))
