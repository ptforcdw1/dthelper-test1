#!/usr/bin/env python3
"""
TASK-20260510-003
Creates a Dynatrace log storage rule that routes logs from a k8s namespace
to a specified Grail bucket.
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
    return {
        "schemaId": "builtin:logmonitoring.log-storage-settings",
        "scope": "environment",
        "value": {
            "enabled": True,
            "config-item-title": args.rule_name,
            "matchers": [
                {
                    "attribute": "k8s.namespace.name",
                    "operator": "EQUALS",
                    "values": [args.namespace],
                }
            ],
            "bucketName": args.bucket_name,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Create Dynatrace log storage rule for a k8s namespace")
    parser.add_argument("--namespace",   required=True, help="Kubernetes namespace name")
    parser.add_argument("--bucket-name", required=True, help="Dynatrace Grail bucket name")
    parser.add_argument("--rule-name",   default="",    help="Rule display name (auto-generated if omitted)")
    parser.add_argument("--dry-run",     action="store_true", help="Print payload without submitting")
    args = parser.parse_args()

    if not args.rule_name:
        args.rule_name = f"Route k8s namespace {args.namespace} to {args.bucket_name}"

    config    = load_config()
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
            "task_id":     "TASK-20260510-003",
            "action":      "create_log_storage_rule",
            "namespace":   args.namespace,
            "bucket_name": args.bucket_name,
            "rule_name":   args.rule_name,
            "status_code": response.status_code,
            "response":    body,
            "success":     response.status_code in (200, 201),
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    except requests.RequestException as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
