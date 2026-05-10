#!/usr/bin/env python3
"""
Template: route-logs-to-bucket — Verification Script
Queries the Settings API to confirm the log storage rule was created.
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
    parser = argparse.ArgumentParser(description="Verify a log storage routing rule exists in Dynatrace")
    parser.add_argument("--matcher-value", required=True, help="The matcher value to look up (e.g. test-ns)")
    args = parser.parse_args()

    config     = load_config()
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
        "schemaIds": "builtin:logmonitoring.log-storage-settings",
        "filter":    f'value.matchers.values="{args.matcher_value}"',
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        content_type = response.headers.get("content-type", "")
        body  = response.json() if "application/json" in content_type else response.text
        items = body.get("items", []) if isinstance(body, dict) else []

        rule_found = is_mock or len(items) > 0
        passed     = response.status_code == 200 and rule_found

        result = {
            "template":     "route-logs-to-bucket",
            "test":         "verify_log_storage_rule_exists",
            "matcher_value": args.matcher_value,
            "mock_mode":    is_mock,
            "status_code":  response.status_code,
            "rule_found":   rule_found,
            "response":     body,
            "passed":       passed,
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if passed else 1)

    except requests.RequestException as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
