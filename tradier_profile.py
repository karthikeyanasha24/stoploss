import os
import requests
from dotenv import load_dotenv  # <-- this must be here, above the call

load_dotenv()  # this reads .env into os.environ

API_KEY = os.environ.get("API_KEY")
BASE_URL = "https://api.tradier.com/v1"
URL = f"{BASE_URL}/user/profile"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
}

def main():
    resp = requests.get(URL, headers=headers, timeout=30)
    print("Status:", resp.status_code)
    try:
        data = resp.json()
    except ValueError:
        print("Raw response:")
        print(resp.text)
        return

    print("JSON response:")
    print(data)

        # Optional: pretty print key fields
    profile = data.get("profile", {})
    print("\nProfile summary:")
    print("ID:", profile.get("id"))
    print("Name:", profile.get("name"))

    account = profile.get("account")
    if isinstance(account, dict):
        # Single account object
        accounts = [account]
    elif isinstance(account, list):
        accounts = account
    else:
        accounts = []

    for acct in accounts:
        print(
            "Account:",
            acct.get("account_number"),
            "| type:", acct.get("type"),
            "| status:", acct.get("status"),
        )
if __name__ == "__main__":
    main()