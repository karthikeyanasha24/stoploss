#!/usr/bin/env python3
"""Generate GOOGLE_PRIVATE_KEY_BASE64 from credentials.json for Render/env vars.
Run: python scripts/encode_private_key.py
Or:  python scripts/encode_private_key.py path/to/credentials.json
"""
import base64
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) > 1:
        creds_path = Path(sys.argv[1])
    else:
        base = Path(__file__).parents[1]
        creds_path = base / "credentials.json"
        if not creds_path.exists():
            creds_path = base.parent / "credentials.json"  # parent dir (e.g. version_b/version_b -> version_b/)
    if not creds_path.exists():
        print(f"Error: {creds_path} not found")
        print("Run: python scripts/encode_private_key.py path/to/credentials.json")
        sys.exit(1)
    with open(creds_path) as f:
        data = json.load(f)
    pk = data.get("private_key")
    if not pk:
        print("Error: no private_key in credentials.json")
        sys.exit(1)
    b64 = base64.b64encode(pk.encode("utf-8")).decode("ascii")
    print("Add this to Render Environment Variables:")
    print()
    print("GOOGLE_PRIVATE_KEY_BASE64=" + b64)
    print()
    print("(Remove GOOGLE_PRIVATE_KEY if you had it set)")

if __name__ == "__main__":
    main()
