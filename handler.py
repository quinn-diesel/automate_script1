from openpyxl import load_workbook
import json
import service


def update_bed_bath_car():
    pass


def prepare_payload(address, contacts, primary_agent):
    print("address", address)
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
    # service.get_listing('be96a009-2e1f-4aff-b7ba-8d6c8a24103a')
    # service.get_listing('0568088b-abba-4cde-aece-c31da7c8ca18')

    wb = load_workbook(filename="RexImport.xlsx")
    ws = wb["Sheet3"]

    for row in ws.iter_rows(min_row=2, min_col=1, max_row=ws.max_row, max_col=6):
        lst = []
        for cell in row:
            # print('cell',cell.row)
            print("val", cell.value)
            lst.append(cell.value)
        if lst[0] != None and lst[1] != None and lst[2] != None:
            args, identity = prepare_payload(
                json.loads(lst[0]),
                json.loads(lst[1]),
                json.loads(lst[2])["primaryAgent"],
            )
            print("lst", lst)
            # creating a listing
            listing = service.create_listing(args, identity)
            print("listing", listing)
            property_details = listing["property_details"]
            print("property_details", property_details)
            property_details["bedrooms"] = int(lst[3])
            property_details["bathrooms"] = int(lst[4])
            property_details["carparks"] = int(lst[5])
            pd, listing = service.update_property_details(
                listing["id"],
                {
                    "appraisals": [{"value": 123}],
                    "bathrooms": 1,
                    "bedrooms": 2,
                    "carparks": 1,
                    "propertyType": "house",
                    "landSize": 100,
                    "internalSqm": 200,
                    "externalSqm": 300,
                    "zoning": "residential",
                },
                identity,
            )
            print("property_details", property_details)
            print("pd,listing", pd, listing)

            # service.update_property_details(listing.id,)
            # print(listing)

        print("-------")

    # create_listing()

    # listing_id='7e12dbc2-7c6d-4386-8c10-9ea0f5d16426'
    # listing = Listing.get(listing_id)
    # print(listing.to_json())
    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration

    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
