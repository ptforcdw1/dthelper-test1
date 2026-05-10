#!/usr/bin/env python3
"""
TASK-20260510-001
Creates a Dynatrace metric event alert: host CPU usage > threshold for N minutes.
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
    samples = args.duration_minutes
    return {
        "schemaId": "builtin:anomaly-detection.metric-events",
        "scope": "environment",
        "value": {
            "enabled": True,
            "summary": args.summary,
            "queryDefinition": {
                "type": "METRIC_SELECTOR",
                "metricSelector": "builtin:host.cpu.usage:avg:auto",
            },
            "modelProperties": {
                "type": "STATIC_THRESHOLD",
                "threshold": args.threshold,
                "alertCondition": "ABOVE",
                "alertOnNoData": False,
                "violatingSamples": samples,
                "samples": samples,
                "dealertingSamples": max(1, samples // 2),
            },
            "eventTemplate": {
                "title": "High CPU Usage on Host",
                "description": (
                    f"CPU usage exceeded {args.threshold}% for {args.duration_minutes} "
                    "minutes on {dims:dt.entity.host}"
                ),
                "eventType": "PERFORMANCE",
                "davisMerge": True,
            },
            "alertingScope": [],
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Create Dynatrace host CPU alert")
    parser.add_argument("--threshold", type=float, default=90.0,
                        help="CPU threshold percentage (default: 90)")
    parser.add_argument("--duration-minutes", type=int, default=10,
                        help="Sustained duration in minutes (default: 10)")
    parser.add_argument("--summary", default="High Host CPU Usage Alert",
                        help="Alert summary/name shown in Dynatrace")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print payload without submitting")
    args = parser.parse_args()

    config = load_config()
    tenant_url = config["dynatrace"]["tenant_url"]
    api_path = config["dynatrace"]["settings_api_path"]
    token_var = config["dynatrace"]["api_token_env_var"]
    timeout = config["defaults"]["http_timeout_seconds"]

    api_token = os.environ.get(token_var)
    if not api_token and not args.dry_run:
        print(json.dumps({"error": f"Environment variable '{token_var}' is not set"}))
        sys.exit(1)

    payload = build_payload(args)

    if args.dry_run:
        print(json.dumps({"dry_run": True, "payload": payload}, indent=2))
        sys.exit(0)

    url = f"{tenant_url}{api_path}"
    headers = {
        "Authorization": f"Api-Token {api_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=[payload], headers=headers, timeout=timeout)
        content_type = response.headers.get("content-type", "")
        body = response.json() if "application/json" in content_type else response.text

        result = {
            "task_id": "TASK-20260510-001",
            "action": "create_host_cpu_alert",
            "status_code": response.status_code,
            "response": body,
            "success": response.status_code in (200, 201),
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    except requests.RequestException as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
