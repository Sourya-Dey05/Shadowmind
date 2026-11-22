# =============================================================================
# FILE: proxy.py
# PURPOSE: Multi-Hop Intermediary Proxy Relay Script (For Phone running Python/Termux).
#          Acts as the intermediate compromised relay node (Device B).
#          Listens for attack probes from Laptop 2 (Attacker) and forwards
#          them to Laptop 1 (Target ShadowMind Vault), injecting X-Forwarded-For
#          and MultiHop telemetry so HoneyGraph GNN traces the multi-hop route.
#
# USAGE ON PHONE (Termux or Pydroid 3):
#     python proxy.py [TARGET_URL] [PORT]
# Example:
#     python proxy.py https://your-laptop.trycloudflare.com 9000
# =============================================================================

import http.server
import urllib.request
import urllib.error
import sys
import socket

# =============================================================================
# CONFIGURATION
# =============================================================================
# Laptop 1's Public Cloudflare / Pinggy Tunnel URL or Local LAN IP
DEFAULT_TARGET_HOST = "http://10.60.115.49:8080"
DEFAULT_LISTEN_PORT = 9000

if len(sys.argv) > 1:
    TARGET_HOST = sys.argv[1]
    LISTEN_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_LISTEN_PORT
else:
    print("\n⚠️  TARGET URL NOT SPECIFIED")
    print("Where should the phone forward the attack traffic? (Laptop 1 address)")
    print("  [1] Laptop 1 Local IP (http://10.60.115.49:8080)")
    print("  [2] Laptop 1 Pinggy URL (Paste your Pinggy link)")
    try:
        user_in = input("\n👉 Enter 1 or paste Pinggy URL (Press Enter for Option 1): ").strip()
        if user_in in ("1", "1.", ""):
            TARGET_HOST = "http://10.60.115.49:8080"
        elif user_in in ("2", "2."):
            p_link = input("👉 Paste your Pinggy URL: ").strip()
            TARGET_HOST = p_link if p_link else "http://10.60.115.49:8080"
        else:
            TARGET_HOST = user_in
    except Exception:
        TARGET_HOST = DEFAULT_TARGET_HOST
    LISTEN_PORT = DEFAULT_LISTEN_PORT

# Clean up and normalize URL
TARGET_HOST = TARGET_HOST.strip().rstrip('/')
if TARGET_HOST.startswith("tcp://"):
    TARGET_HOST = "http://" + TARGET_HOST[6:]
elif not TARGET_HOST.startswith("http://") and not TARGET_HOST.startswith("https://"):
    TARGET_HOST = "http://" + TARGET_HOST

def get_phone_ip():
    """Detect the phone's primary network IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# =============================================================================
# PROXY RELAY HANDLER
# =============================================================================
class MultiHopProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        target_url = f"{TARGET_HOST.rstrip('/')}{self.path}"
        attacker_ip = self.headers.get("X-Real-IP") or self.headers.get("X-Forwarded-For") or self.client_address[0]
        if attacker_ip.startswith("::ffff:"):
            attacker_ip = attacker_ip[7:]
        
        print(f"\n[HOP 2 RELAY] ➔ Intercepted Probe from Attacker IP: {attacker_ip}")
        print(f"              Relaying to Target Vault : {target_url}")

        # Inject Multi-Hop tracing headers for ShadowMind HoneyGraph GNN
        headers = {
            "User-Agent": "ShadowMind-ProxyRelay/2.0",
            "X-Attack-Mode": "MultiHop",
            "X-Forwarded-For": attacker_ip,
            "X-Real-IP": attacker_ip,
            "Accept": "*/*"
        }
        
        req = urllib.request.Request(target_url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                payload = resp.read()
                content_type = resp.headers.get("Content-Type", "application/octet-stream")
                content_disp = resp.headers.get("Content-Disposition", "")
                
                self.send_response(resp.status)
                self.send_header("Content-Type", content_type)
                if content_disp:
                    self.send_header("Content-Disposition", content_disp)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                print(f"[HOP 2 RELAY] ✓ Forwarded {len(payload):,} bytes back to Attacker (HTTP {resp.status})")
                
        except urllib.error.HTTPError as e:
            err_body = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(err_body)
            print(f"[HOP 2 RELAY] ⚠ Target returned HTTP {e.code}")
        except Exception as e:
            print(f"[HOP 2 RELAY] ❌ Relay Error: {e}")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Proxy Gateway Error connecting to {target_url}: {e}".encode("utf-8"))

    def log_message(self, format, *args):
        # Suppress default server log lines to keep output clean and readable
        return


# =============================================================================
# SERVER ENTRYPOINT
# =============================================================================
if __name__ == "__main__":
    local_ip = get_phone_ip()
    server_address = ('0.0.0.0', LISTEN_PORT)
    httpd = http.server.ThreadingHTTPServer(server_address, MultiHopProxyHandler)
    
    print("=" * 75)
    print("  🌐 SHADOWMIND MULTI-HOP PROXY RELAY (Device B / Intermediate Node)")
    print("=" * 75)
    print(f" Proxy Listening IP: 0.0.0.0 (Phone Local IP: {local_ip})")
    print(f" Proxy Listening Port: {LISTEN_PORT}")
    print(f" Forwarding Upstream : {TARGET_HOST}")
    print("=" * 75)
    print(f"\n📡 On Laptop 2 (Attacker), run:")
    print(f"   python multihop_attack.py http://{local_ip}:{LISTEN_PORT}\n")
    print("⏳ Ready. Waiting for incoming attack requests...\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Stopping Multi-Hop Proxy Relay...")
        httpd.server_close()
