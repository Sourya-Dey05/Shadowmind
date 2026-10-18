# =============================================================================
# FILE: proxy.py
# PURPOSE: Multi-hop proxy relay script for Phone 2 (Device B / Termux).
#          Acts as an intermediary "compromised internal workstation" that
#          relays incoming HTTP traffic from an external attacker (Phone 1 /
#          Device A) to the secure ShadowMind Vault server (Laptop / Device C),
#          while preserving the attacker's original IP address in the
#          X-Forwarded-For header so HoneyGraph GNN can trace the multi-hop path.
# =============================================================================

import http.server
import urllib.request
import sys

# --- CONFIGURE THESE BEFORE RUNNING ON PHONE 2 ---
LAPTOP_IP = "192.168.1.50"  # Replace with your laptop's Wi-Fi IPv4 address
PORT = 8080                 # ShadowMind listener port
LISTEN_PORT = 9000          # Port Phone 2 listens on for attacker traffic

class MultiHopProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        target_url = f"http://{LAPTOP_IP}:{PORT}{self.path}"
        attacker_ip = self.client_address[0]
        
        print(f"[HOP 2 PROXY] Intercepted attack request from Attacker IP: {attacker_ip}")
        print(f"[HOP 2 PROXY] Relaying payload to Target Vault: {target_url}")

        # Inject X-Forwarded-For header so ShadowMind traces the multi-hop route
        headers = {"X-Forwarded-For": attacker_ip}
        req = urllib.request.Request(target_url, headers=headers)

        try:
            resp = urllib.request.urlopen(req)
            self.send_response(resp.status)
            self.end_headers()
            self.wfile.write(resp.read())
            print(f"[HOP 2 PROXY] Relay successful.\n")
        except Exception as e:
            print(f"[HOP 2 PROXY] Relay failed: {e}\n")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def log_message(self, format, *args):
        # Keep terminal output clean
        return


if __name__ == "__main__":
    server_address = ('', LISTEN_PORT)
    httpd = http.server.HTTPServer(server_address, MultiHopProxyHandler)
    print("=" * 65)
    print(f" SHADOWMIND MULTI-HOP PROXY RELAY (Phone 2)")
    print(f" Listening on port {LISTEN_PORT}...")
    print(f" Forwarding multi-hop traffic to Laptop Vault -> {LAPTOP_IP}:{PORT}")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nProxy stopped.")
        httpd.server_close()
