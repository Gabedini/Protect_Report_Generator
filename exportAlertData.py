#!/usr/bin/env python3

#this script is a modified version of a script from Jamf's GitHub:
#https://github.com/jamf/jamfprotect/blob/main/jamf_protect_api/scripts/python/export_alert_data.py
# This example Python script below does the following:
# - Completes a listAlerts query request that returns all logs reported to Jamf
#   Protect, with filtering by severity.
# - Exports all alert data in JSON format /tmp/ProtectAlerts.json

# Keep the following in mind when using this script:
# - You must define the PROTECT_INSTANCE, CLIENT_ID, and PASSWORD variables to
#   match your Jamf Protect environment. The PROTECT_INSTANCE variable is your
#   tenant name (eg. your-tenant), which is included in your tenant URL (eg.
#   https://your-tenant.protect.jamfcloud.com).
# - This script requires the 3rd party Python library 'requests'


import sys
from datetime import datetime
import json

import requests

PROTECT_INSTANCE = ""
CLIENT_ID = ""
PASSWORD = ""

MIN_SEVERITY = "Low"  # Valid values: "Informational", "Low", "Medium", "High"
MAX_SEVERITY = "High"  # Valid values: "Informational", "Low", "Medium", "High"
JSON_OUTPUT_FILE = f"Jamf_Protect_Alerts_{datetime.utcnow().strftime('%Y-%m-%d')}.json"


def exportAlertDataAPICall(protect_instance, access_token, query, variables=None):
    """Sends a GraphQL query to the Jamf Protect API, and returns the
    response."""
    if variables is None:
        variables = {}
    api_url = f"https://{protect_instance}.protect.jamfcloud.com/graphql"
    payload = {"query": query, "variables": variables}
    headers = {"Authorization": access_token}
    resp = requests.post(
        api_url,
        json=payload,
        headers=headers,
    )
    resp.raise_for_status()
    return resp.json()


LIST_ALERTS_QUERY = """
        query listAlerts(
            $min_severity: SEVERITY
            $max_severity: SEVERITY
            $page_size: Int
            $next: String
        ) {
            listAlerts(
                input: {
                    filter: {
                        severity: { greaterThanOrEqual: $min_severity }
                        and: { severity: { lessThanOrEqual: $max_severity } }
                    }
                    pageSize: $page_size
                    next: $next
                }
            ) {
                items {
                        json
                        severity
                        computer {
                            hostName
                        }
                        created
                    }
                        pageInfo {
                                next
                    }
                }
            }
        """


def exportAlertData(token, url):
    print("running the exportAlertData method")
    global access_token
    access_token = token#passing in the access token that we have fomr the auth screen
    global PROTECT_INSTANCE
    PROTECT_INSTANCE = url
    
    if not set({MIN_SEVERITY, MAX_SEVERITY}).issubset(
        {"Informational", "Low", "Medium", "High"}
    ):
        print(
            "ERROR: Unexpected value(s) for min/max severity. Expected 'Informational', 'Low', 'Medium', or 'High'."
        )
        sys.exit(1)

    """
    if not all([PROTECT_INSTANCE, CLIENT_ID, PASSWORD]):
        print("ERROR: Variables PROTECT_INSTANCE, CLIENT_ID, and PASSWORD must be set.")
        sys.exit(1)
    """

    results = []
    next_token = None
    page_count = 1
    print("Retrieving paginated results:")
    while True:
        print(f"  Retrieving page {page_count} of results...")
        vars = {
            "min_severity": MIN_SEVERITY,
            "max_severity": MAX_SEVERITY,
            "page_size": 100,
            "next": next_token,
        }
        resp = exportAlertDataAPICall(PROTECT_INSTANCE, access_token, LIST_ALERTS_QUERY, vars)
        next_token = resp["data"]["listAlerts"]["pageInfo"]["next"]
        results.extend(resp["data"]["listAlerts"]["items"])
        if next_token is None:
            break
        page_count += 1
    print(f"Found {len(results)} alerts matching filter.\n")
    print(f"Writing results to '{JSON_OUTPUT_FILE}'")
    with open(JSON_OUTPUT_FILE, "w") as output:
        json.dump(results, output, sort_keys=True, indent=4)