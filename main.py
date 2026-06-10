import os
import re
import json
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'python3'))

try:
    from XmanagerCrypto import XShellCrypto
except ImportError as e:
    print(f"[!] ERROR: Import failed: {e}")
    print("Hint: If the error mentions 'Crypto', make sure to run: pip install pycryptodome")
    print("Also ensure the 'python3' directory contains 'XmanagerCrypto.py'.")
    sys.exit(1)

# ==============================================================================
# SETTINGS: PLEASE EDIT THIS SECTION ACCORDING TO YOUR ENVIRONMENT
# ==============================================================================
XSHELL_SESSIONS_DIR = r"C:\Users\{USERNAME}\Documents\NetSarang Computer\8\Xshell\Sessions"
MASTER_PASSWORD = "master-password"
XSHELL_VERSION = "7"  # Your Xshell version
# ==============================================================================

WINDTERM_JSON_PATH = "user.sessions"
TUNNEL_REPORT_PATH = "tunnel_report.txt"

windterm_sessions = []
tunnel_logs = []

print("=== Xshell -> WindTerm Direct Converter ===")
print(f"Scanned Directory: {XSHELL_SESSIONS_DIR}\n")

if not os.path.exists(XSHELL_SESSIONS_DIR):
    print("[!] ERROR: Xshell Sessions directory not found! Please check the path.")
    sys.exit(1)

# Crypto version logic: If Master password is set, version is automatically considered 6.0
crypto_version = 6.0 if MASTER_PASSWORD else float(XSHELL_VERSION)

try:
    cipher = XShellCrypto(SessionFileVersion=crypto_version,
                          UserName=None,
                          SID=None,
                          MasterPassword=MASTER_PASSWORD)
except Exception as e:
    print(f"[!] Crypto engine failed to initialize: {e}")
    sys.exit(1)

for root, dirs, files in os.walk(XSHELL_SESSIONS_DIR):
    for file in files:
        if file.endswith(".xsh"):
            file_path = os.path.join(root, file)

            # Extract folder structure
            rel_path = os.path.relpath(root, XSHELL_SESSIONS_DIR)
            group = "" if rel_path == "." else rel_path.replace("\\", "/")
            label = file[:-4]

            host, port, username, encrypted_password = "", "22", "", ""

            # Read file content
            content = ""
            for encoding in ["utf-16", "utf-8", "latin-1"]:
                try:
                    with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                        content = f.read()
                    if "Host=" in content:
                        break
                except Exception:
                    continue

            # Extract data via regex
            h_match = re.search(r"^\s*Host\s*=\s*(.*?)\s*$", content, re.MULTILINE | re.IGNORECASE)
            p_match = re.search(r"^\s*Port\s*=\s*(.*?)\s*$", content, re.MULTILINE | re.IGNORECASE)
            u_match = re.search(r"^\s*UserName\s*=\s*(.*?)\s*$", content, re.MULTILINE | re.IGNORECASE)
            pass_match = re.search(r"^\s*Password\s*=\s*(.*?)\s*$", content, re.MULTILINE | re.IGNORECASE)

            if h_match: host = h_match.group(1).strip()
            if p_match: port = p_match.group(1).strip()
            if u_match: username = u_match.group(1).strip()
            if pass_match: encrypted_password = pass_match.group(1).strip()

            if not host:
                continue

            # --- XSHELL 8 TUNNEL DETECTION ---
            fwd_count_match = re.search(r"^\s*FwdReqCount\s*=\s*(\d+)\s*$", content, re.MULTILINE | re.IGNORECASE)
            if fwd_count_match:
                count = int(fwd_count_match.group(1))
                if count > 0:
                    tunnel_logs.append(f"\n[{group if group else 'Root'} -> {label}]")
                    for i in range(count):
                        inc_m = re.search(rf"^\s*FwdReq_{i}_Incoming\s*=\s*(\d+)\s*$", content, re.MULTILINE)
                        port_m = re.search(rf"^\s*FwdReq_{i}_Port\s*=\s*(\d+)\s*$", content, re.MULTILINE)
                        dhost_m = re.search(rf"^\s*FwdReq_{i}_Host\s*=\s*(.*?)\s*$", content, re.MULTILINE)
                        dport_m = re.search(rf"^\s*FwdReq_{i}_HostPort\s*=\s*(\d+)\s*$", content, re.MULTILINE)
                        desc_m = re.search(rf"^\s*FwdReq_{i}_Description\s*=\s*(.*?)\s*$", content, re.MULTILINE)

                        inc_type = inc_m.group(1) if inc_m else "0"
                        l_port = port_m.group(1) if port_m else "?"
                        d_host = dhost_m.group(1) if dhost_m else "?"
                        d_port = dport_m.group(1) if dport_m else "?"
                        desc = desc_m.group(1) if desc_m else ""

                        direction = "Local" if inc_type == "0" else "Remote"
                        tunnel_str = f"  - Type: {direction} | Local Port: {l_port} | Target: {d_host}:{d_port}"
                        if desc: tunnel_str += f" | Description: {desc}"

                        tunnel_logs.append(tunnel_str)

            # --- DECRYPT PASSWORD ---
            decrypted_password = ""
            if encrypted_password:
                try:
                    decrypted_password = cipher.DecryptString(encrypted_password)
                except Exception as e:
                    print(f"[!] Failed to decrypt password ({label}): {e}")

            # Create WindTerm Session Object
            target = f"{username}@{host}" if username else host
            try:
                session_port = int(port)
            except ValueError:
                session_port = 22

            session_uuid = str(uuid.uuid4())

            session_obj = {
                "session.group": group,
                "session.icon": "session::square-coral",
                "session.label": label,
                "session.port": session_port,
                "session.protocol": "SSH",
                "session.target": target,
                "session.uuid": session_uuid
            }
            if decrypted_password:
                session_obj["session.description"] = decrypted_password

            windterm_sessions.append(session_obj)
            print(f"[+] Decrypted and Added: {group + '/' if group else ''}{label}")

# Output WindTerm user.sessions
with open(WINDTERM_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(windterm_sessions, f, indent=4, ensure_ascii=False)

# Output tunnel report
if tunnel_logs:
    with open(TUNNEL_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("=== XSHELL TUNNEL REPORT ===\n")
        f.write("\n".join(tunnel_logs))

print("\n=========================================================")
print(f"SUCCESS: {len(windterm_sessions)} connections successfully decrypted.")
print(f"Tunnel report saved to '{TUNNEL_REPORT_PATH}'.")
print("=========================================================")