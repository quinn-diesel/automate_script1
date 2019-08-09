from openpyxl import load_workbook
import json
import os
import service


def prepare_payload(address, contacts, primary_agent):
    payload = {
        "arguments": {
            "input": {
                "address": address,
                "contacts": [contacts],
                "primary_agent": primary_agent,
            }
        },
        "identity": {
            "username": "Google_106600641818143500761",
            "claims": {
                "email": "ajeya@ljx.com.au",
                "custom:office": "corp",
                "custom:manager": "",
                "custom:team": "engineering",
                "cognito:groups": ["agents-group"],
            },
        },
    }
    return payload["arguments"]["input"], payload["identity"]


def main(event, context):

    wb = load_workbook(filename="RexImport.xlsx")
    ws = wb["Sheet3"]

    for row in ws.iter_rows(min_row=2, min_col=1, max_row=ws.max_row, max_col=6):
        lst = []
        for cell in row:
            lst.append(cell.value)
        if lst[0] != None and lst[1] != None and lst[2] != None:
            args, identity = prepare_payload(
                json.loads(lst[0]),
                json.loads(lst[1]),
                json.loads(lst[2])["primaryAgent"],
            )

            # creating a listing in agent_portal
            listing = service.create_listing(args, identity)
            print(
                "listing created in agent app with id - '{0}' with address- '{1}'".format(
                    listing["id"], listing["address"]["full_address"]
                )
            )

            # updating bed,bath,car in agent_portal
            property_details = listing["property_details"]
            property_details["bedrooms"] = int(lst[3])
            property_details["bathrooms"] = int(lst[4])
            property_details["carparks"] = int(lst[5])
            pd = service.update_property_details(
                listing["id"],
                {
                    "appraisals": property_details.get("appraisals", []),
                    "bathrooms": property_details.get("bathrooms", 0),
                    "bedrooms": property_details.get("bedrooms", 0),
                    "carparks": property_details.get("carparks", 0),
                    "property_type": property_details.get("propertyType", None),
                    "land_size": property_details.get("landSize", 0),
                    "internal_sqm": property_details.get("internalSqm", 0),
                    "external_sqm": property_details.get("externalSqm", 0),
                    "zoning": property_details.get("zoning", None),
                },
                identity
            )

            # moving stage from 'opportunity to 'precampaign'
            updated_staged_code = service.update_stage(
                listing["id"], listing["stage_code"].upper()
            )
            print(
                "listing id -'{0}' moved from '{1}' to '{2}'".format(
                    listing["id"], listing["stage_code"], updated_staged_code
                )
            )

            # creating listing in rex
            rex_listing_id = service.create_listing_in_rex(listing["id"])
            print("listing created in rex with id - ", rex_listing_id)

            # moving agents,bed,bath,car to rex_listing_id
            service.update_property_details_in_rex(
                rex_listing_id,
                identity,
                listing["agent_usernames"],
                pd["bedrooms"],
                pd["bathrooms"],
                pd["carparks"],
            )
        print("--------------------------------------------------------\n\n")
