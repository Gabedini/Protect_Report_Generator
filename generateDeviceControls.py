#!/usr/bin/env python3

# This example Python script below does the following:
# - Obtains an access token.
# - Completes a listAlerts query request that returns all alerts reported to Jamf
#   Protect during a defined time range, with filtering by eventType auth-mount.
# - Creates a CSV file

# - This script requires the 3rd party Python library 'requests'


import sys, json, requests, csv, os, datetime as dt
from datetime import datetime

PROTECT_INSTANCE = ""
CLIENT_ID = ""
PASSWORD = ""


CSV_OUTPUT_FILE = (
    f"Jamf_Protect_Device_Controls_Alerts_{datetime.utcnow().strftime('%Y-%m-%d')}.csv"
)

def generateDeviceControlsAPICall(protect_instance, access_token, query, variables=None):
    """Sends a GraphQL query to the Jamf Protect API, and returns the
    response."""
    if variables is None:
        variables = {}
    api_url = f"https://{protect_instance}.protect.jamfcloud.com/graphql"
    payload = {"query": query, "variables": variables}
    print(payload)
    headers = {"Authorization": access_token}
    resp = requests.post(
        api_url,
        json=payload,
        headers=headers,
    )
    print(resp)
    resp.raise_for_status()
    return resp.json()


LIST_ALERTS_QUERY = """
        query listAlerts(
            $created_cutoff: AWSDateTime
            $event_type: String
            $page_size: Int 
            $next: String
        ) {
            listAlerts(
                input: {
                    filter: {
                        eventType: { equals: $event_type },
                        and: {
                        created: { greaterThan: $created_cutoff }
                    }}
                    pageSize: $page_size
                    next: $next
                }
            ) {
                items {
                        json
                        eventType
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


def generateDeviceControls(token, url, days):

    # Get the access token
    access_token = token
    global PROTECT_INSTANCE
    PROTECT_INSTANCE = url

    cutoff_days = days
    cutoff_date = dt.datetime.now() - dt.timedelta(days=cutoff_days)

    results = []
    next_token = None
    page_count = 1

    print("Retrieving paginated results:")

    while True:
        print(f"  Retrieving page {page_count} of results...")
        vars = {
            "event_type": "auth-mount",
            "created_cutoff": cutoff_date.isoformat() + "Z",
            "page_size": 100,
            "next": next_token,
        }
        resp = generateDeviceControlsAPICall(PROTECT_INSTANCE, access_token, LIST_ALERTS_QUERY, vars)
        next_token = resp["data"]["listAlerts"]["pageInfo"]["next"]
        results.extend(resp["data"]["listAlerts"]["items"])
        if next_token is None:
            break
        page_count += 1
    print(f"Found {len(results)} alerts matching filter.\n")
    print(f"Writing results to '{CSV_OUTPUT_FILE}'")
    data_file = open(CSV_OUTPUT_FILE, "w", newline="")
    csv_writer = csv.writer(data_file)
    headers = [
        "Timestamp",
        "HostName",
        "Serial",
        "Vendor",
        "Vendor ID",
        "Product",
        "Product ID",
        "Device Serial",
        "Encrypted",
        "Action",
    ]
    csv_writer.writerow(headers)
    for o in results:
        raw_json = json.loads(o["json"])
        hostname = raw_json["host"]["hostname"]
        serial = raw_json["host"]["serial"]
        vendorname = raw_json["match"]["event"]["device"]["vendorName"]
        vendorid = raw_json["match"]["event"]["device"]["vendorId"]
        productname = raw_json["match"]["event"]["device"]["productName"]
        productid = raw_json["match"]["event"]["device"]["productId"]
        devicesn = raw_json["match"]["event"]["device"]["serialNumber"]
        isencrypted = raw_json["match"]["event"]["device"]["isEncrypted"]
        action = (
            raw_json["match"]["actions"][0]["name"]
            + ", "
            + raw_json["match"]["actions"][1]["name"]
            + " & "
            + raw_json["match"]["actions"][2]["name"]
        )
        time = raw_json["match"]["event"]["timestamp"]
        timestamp = datetime.utcfromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")

        row = [
            timestamp,
            hostname,
            serial,
            vendorname,
            vendorid,
            productname,
            productid,
            devicesn,
            isencrypted,
            action,
        ]

        csv_writer.writerow(row)
    data_file.close()
    print("done")