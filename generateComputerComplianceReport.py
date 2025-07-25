#!/usr/bin/env python3

# This example Python script below does the following:
# - Obtains an access token.
# - Completes a listComputers query request that returns compliance related data from all computers.
# - Processes compliance summary and technical control status scorecard for each computer. 
# - Exports computer information into a CSV format file.

# - This script requires the 3rd party Python library 'requests'


from datetime import datetime
import csv
import requests

PROTECT_INSTANCE = ""
CLIENT_ID = ""
PASSWORD = ""

CSV_OUTPUT_FILE = (
    f"Jamf_Protect_Compliance_Report_{datetime.utcnow().strftime('%Y-%m-%d')}.csv"
)

#formerly called make_api_call
def generateComplianceReoprtAPICall(protect_instance, access_token, query, variables=None):
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


LIST_COMPUTERS_QUERY = """
    query listComputers($page_size: Int, $next: String) {
      listComputers(input: { pageSize: $page_size, next: $next }) {
        items {
          hostName
          serial
          uuid
          insightsUpdated
          insightsStatsFail
          insightsStatsPass
          insightsStatsUnknown
          scorecard {
            uuid
            label
            description
            section
            pass
            tags
            enabled
          } 
        }
        pageInfo {
          next
        }
      }
    }
    """


def process_scorecard(scorecard_data):

    scorecard_dict = {}
    technical_control_status_dict = {}

    compliant = 0
    noncompliant = 0
    disabled = 0

    if (
        isinstance(scorecard_data, list)
        and scorecard_data
        and {"enabled", "pass"}.issubset(scorecard_data[0].keys())
    ):

        for item in scorecard_data:

            if not item["enabled"]:
                disabled += 1
                status_name = "disabled"
            elif item["pass"]:
                compliant += 1
                status_name = "pass"
            else:
                noncompliant += 1
                status_name = "fail"

            technical_control_status_dict[item["label"]] = status_name

    return scorecard_dict, technical_control_status_dict


def generateComputerComplianceReport(token, url):
    print("running the generateComputerComplianceReport method")
    global access_token
    access_token = token#passing in the access token that we have from the auth screen
    global PROTECT_INSTANCE
    PROTECT_INSTANCE = url
    
    next_token = None
    computers = []
    page_count = 1

    print("Retrieving paginated results:")

    while True:

        print(f"  Retrieving page {page_count} of results...")

        vars = {
            "page_size": 100,
            "next": next_token,
        }

        resp = generateComplianceReoprtAPICall(PROTECT_INSTANCE, access_token, LIST_COMPUTERS_QUERY, vars)
        next_token = resp["data"]["listComputers"]["pageInfo"]["next"]
        computers.extend(resp["data"]["listComputers"]["items"])

        if next_token is None:
            break

        page_count += 1

    print(f"Found total of {len(computers)} computers.")

    if computers:

        print(f"Writing computer compliance report to '{CSV_OUTPUT_FILE}'...")

        with open(CSV_OUTPUT_FILE, "w", newline="") as output:

            fieldnames = list(computers[0].keys())

            technical_control_names = set()

            for computer in computers:

                processed_scorecard, technical_control_statuses = process_scorecard(
                    computer.get("scorecard")
                )

                technical_control_names.update(technical_control_statuses.keys())

                computer.update(processed_scorecard)
                computer.update(technical_control_statuses)

                computer["Raw Scorecard"] = computer.pop("scorecard")

            fieldnames.extend(sorted(technical_control_names))

            # Make hostName the first column if included in results
            if "hostName" in fieldnames:
                fieldnames.insert(0, fieldnames.pop(fieldnames.index("hostName")))

            # Make 'raw' scorecard the last column if included in results
            if "scorecard" in fieldnames:
                fieldnames.pop(fieldnames.index("scorecard"))
                fieldnames.append("Raw Scorecard")

            writer = csv.DictWriter(output, fieldnames=fieldnames, restval="No data")

            writer.writeheader()

            for computer in computers:

                writer.writerow(computer)

    else:
        print("Nothing to write out.")

    print("Done.")