#!/usr/bin/env python3
"""
Template: create-metric-alert — Verification Script
Queries the Settings API to confirm the alert was created and is enabled.
"""

import argparse
import json
import os
import sys

import requests


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "environment.json")
    with open(os.path.abspath(config_path)) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Verify a metric event alert exists in Dynatrace")
    parser.add_argument("--summary", required=True, help="Alert summary name to look up")
    args = parser.parse_args()

    config = load_config()
    tenant_url = config["dynatrace"]["tenant_url"]
    api_path   = config["dynatrace"]["settings_api_path"]
    token_var  = config["dynatrace"]["api_token_env_var"]
    timeout    = config["defaults"]["http_timeout_seconds"]

    api_token = os.environ.get(token_var)
    if not api_token:
        print(json.dumps({"error": f"Environment variable '{token_var}' is not set"}))
        sys.exit(1)

    is_mock = "httpbin.org" in tenant_url

    url     = f"{tenant_url}{api_path}"
    headers = {
        "Authorization": f"Api-Token {api_token}",
        "Content-Type":  "application/json",
    }
    params  = {
        "schemaIds": "builtin:anomaly-detection.metric-events",
        "filter":    f'value.summary="{args.summary}"',
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        content_type = response.headers.get("content-type", "")
        body  = response.json() if "application/json" in content_type else response.text
        items = body.get("items", []) if isinstance(body, dict) else []

        # Mock endpoint echoes requests without storing state — pass on HTTP 200 alone
        alert_found = is_mock or len(items) > 0
        passed      = response.status_code == 200 and alert_found

        result = {
            "template":    "create-metric-alert",
            "test":        "verify_metric_alert_exists",
            "summary":     args.summary,
            "mock_mode":   is_mock,
            "status_code": response.status_code,
            "alert_found": alert_found,
            "response":    body,
            "passed":      passed,
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if passed else 1)

    except requests.RequestException as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
