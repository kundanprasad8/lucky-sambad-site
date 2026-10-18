#!/usr/bin/env python3
"""Runs on GitHub Actions. Sends URL_UPDATED to Google's Indexing API.

Env: SA_KEY_JSON (service-account JSON from repo secret INDEXING_SA_KEY),
     URLS (comma-separated).
"""
import json
import os
import sys

import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def main():
    try:
        key = json.loads(os.environ["SA_KEY_JSON"])
    except Exception as e:
        print(f"FATAL: bad SA_KEY_JSON: {e}")
        sys.exit(2)
    urls = [u.strip() for u in os.environ.get("URLS", "").split(",") if u.strip()][:50]
    if not urls:
        print("No URLs given.")
        sys.exit(2)

    creds = service_account.Credentials.from_service_account_info(key, scopes=SCOPES)
    creds.refresh(Request())
    token = creds.token

    ok = fail = 0
    for u in urls:
        try:
            r = requests.post(
                ENDPOINT,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"url": u, "type": "URL_UPDATED"},
                timeout=30,
            )
            good = r.status_code == 200
            ok += good
            fail += not good
            print(("OK " if good else f"FAIL {r.status_code} ") + u + " :: " + r.text[:300])
        except Exception as e:
            fail += 1
            print(f"ERROR {u} :: {e}")
    print(f"DONE ok={ok} fail={fail}")
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
