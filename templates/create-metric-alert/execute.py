#!/usr/bin/env python3
"""
Template: create-metric-alert
Creates a Dynatrace metric event alert with a static threshold.
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
    samples = args.duration_minutes
    description = args.event_description or (
        f"Metric {args.metric_selector} crossed threshold {args.threshold} "
        f"for {args.duration_minutes} minutes"
    )
    return {
        "schemaId": "builtin:anomaly-detection.metric-events",
        "scope": args.scope,
        "value": {
            "enabled": True,
            "summary": args.summary,
            "queryDefinition": {
                "type": "METRIC_SELECTOR",
                "metricSelector": args.metric_selector,
            },
            "modelProperties": {
                "type": "STATIC_THRESHOLD",
                "threshold": args.threshold,
                "alertCondition": args.alert_condition,
                "alertOnNoData": False,
                "violatingSamples": samples,
                "samples": samples,
                "dealertingSamples": max(1, samples // 2),
            },
            "eventTemplate": {
                "title": args.event_title or args.summary,
                "description": description,
                "eventType": args.event_type,
                "davisMerge": True,
            },
            "alertingScope": [],
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Create a Dynatrace metric event alert (static threshold)")
    parser.add_argument("--summary",          required=True,  help="Alert name shown in Dynatrace (unique identifier)")
    parser.add_argument("--metric-selector",  required=True,  help="Dynatrace metric selector (e.g. builtin:host.cpu.usage:avg:auto)")
    parser.add_argument("--threshold",        required=True,  type=float, help="Numeric threshold value")
    parser.add_argument("--alert-condition",  default="ABOVE", choices=["ABOVE", "BELOW"], help="Trigger when metric is ABOVE or BELOW threshold (default: ABOVE)")
    parser.add_argument("--duration-minutes", default=10,     type=int,   help="Sustained minutes before alert fires (default: 10)")
    parser.add_argument("--event-type",       default="PERFORMANCE", choices=["PERFORMANCE", "AVAILABILITY", "ERROR", "RESOURCE_CONTENTION"], help="Davis event type (default: PERFORMANCE)")
    parser.add_argument("--event-title",      default="",     help="Title shown on Davis event (defaults to --summary)")
    parser.add_argument("--event-description", default="",   help="Description shown on Davis event (auto-generated if omitted)")
    parser.add_argument("--scope",            default="environment", help="Settings scope (default: environment)")
    parser.add_argument("--dry-run",          action="store_true", help="Print payload without submitting")
    args = parser.parse_args()

    config = load_config()
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
            "template":    "create-metric-alert",
            "action":      "create_metric_alert",
            "summary":     args.summary,
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
