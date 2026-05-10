#!/usr/bin/env python3
"""
Template: route-logs-to-bucket
Creates a Dynatrace log storage rule that routes logs matching a given
attribute/value to a specified Grail bucket.
All inputs are passed as arguments — nothing is hardcoded.
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


def build_payload(args):
    rule_name = args.rule_name or f"Route {args.matcher_attribute}={args.matcher_value} to {args.bucket_name}"
    return {
        "schemaId": "builtin:logmonitoring.log-storage-settings",
        "scope": "environment",
        "value": {
            "enabled": True,
            "config-item-title": rule_name,
            "matchers": [
                {
                    "attribute": args.matcher_attribute,
                    "operator":  args.matcher_operator,
                    "values":    [args.matcher_value],
                }
            ],
            "bucketName": args.bucket_name,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Create a Dynatrace log storage routing rule")
    parser.add_argument("--bucket-name",       required=True,  help="Dynatrace Grail bucket name")
    parser.add_argument("--matcher-attribute",  required=True,  help="Log attribute to match on (e.g. k8s.namespace.name)")
    parser.add_argument("--matcher-value",      required=True,  help="Value to match (e.g. test-ns)")
    parser.add_argument("--matcher-operator",   default="EQUALS", choices=["EQUALS", "CONTAINS", "STARTS_WITH"], help="Match operator (default: EQUALS)")
    parser.add_argument("--rule-name",          default="",     help="Rule display name (auto-generated if omitted)")
    parser.add_argument("--dry-run",            action="store_true", help="Print payload without submitting")
    args = parser.parse_args()

    config     = load_config()
    tenant_url = config["dynatrace"]["tenant_url"]
    api_path   = config["dynatrace"]["settings_api_path"]
    token_var  = config["dynatrace"]["api_token_env_var"]
    timeout    = config["defaults"]["http_timeout_seconds"]

    api_token = os.environ.get(token_var)
    if not api_token and not args.dry_run:
        print(json.dumps({"error": f"Environment variable '{token_var}' is not set"}))
        sys.exit(1)

    payload = build_payload(args)

    if args.dry_run:
        print(json.dumps({"dry_run": True, "payload": payload}, indent=2))
        sys.exit(0)

    url     = f"{tenant_url}{api_path}"
    headers = {
        "Authorization": f"Api-Token {api_token}",
        "Content-Type":  "application/json",
    }

    try:
        response = requests.post(url, json=[payload], headers=headers, timeout=timeout)
        content_type = response.headers.get("content-type", "")
        body = response.json() if "application/json" in content_type else response.text

        result = {
            "template":         "route-logs-to-bucket",
            "action":           "create_log_storage_rule",
            "matcher_attribute": args.matcher_attribute,
            "matcher_value":    args.matcher_value,
            "bucket_name":      args.bucket_name,
            "status_code":      response.status_code,
            "response":         body,
            "success":          response.status_code in (200, 201),
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    except requests.RequestException as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
