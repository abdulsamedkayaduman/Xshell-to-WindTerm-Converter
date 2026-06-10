# Xshell to WindTerm Converter

A tool to decrypt your Xshell sessions and automatically convert them into WindTerm's `user.sessions` format. It also extracts SSH tunnel configurations and saves them in a separate report.

This repository is built upon [HyperSine's XmanagerCrypto](https://github.com/HyperSine/how-does-Xmanager-encrypt-password), which handles the decryption of passwords from Xshell session files.

## Features

- **Direct Conversion**: Scans your Xshell `Sessions` directory, decrypts passwords, and directly creates a `user.sessions` JSON file compatible with WindTerm.
- **Tunnel Extraction**: Identifies and logs SSH Tunnel (Forwarding) configurations (both Local and Remote) into `tunnel_report.txt`.
- **Directory Structure**: Preserves your nested folder structures from Xshell and translates them to WindTerm session groups.

## How to Use

1. Ensure you have `Python 3` installed.
2. Install the required module:
   ```bash
   pip install pycryptodome
   ```
3. Open `main.py` and modify the **SETTINGS** section according to your environment:
   ```python
   # Example:
   XSHELL_SESSIONS_DIR = r"C:\Users\YourUsername\Documents\NetSarang Computer\8\Xshell\Sessions"
   MASTER_PASSWORD = "your_master_password" # Leave blank if you don't use one
   XSHELL_VERSION = "7"  # Relevant if you do not use a master password
   ```
   **Note on Master Password**: If you do not have a Master Password set in Xshell and want to set one (recommended for easier and more reliable extraction):
   - Open Xshell.
   - Go to **Tools** -> **Options** (or **Tools** -> **Master Password** depending on the version).
   - Navigate to the **Security** tab.
   - Under the "Master Password" section, click on **Set...** or **Change...**.
   - Create your password and wait for Xshell to re-encrypt your sessions with it.
4. Run the script:
   ```bash
   python main.py
   ```
5. **Importing to WindTerm**: The script will generate a `user.sessions` file in the same directory. Move or copy this file into WindTerm's `profiles/default.v10` folder (or your specific profile folder) to import the sessions.

## Dependencies

- Python 3.x
- `pycryptodome`

## Credits

- Password decryption logic by [HyperSine](https://github.com/HyperSine/how-does-Xmanager-encrypt-password).
