from openpyxl import load_workbook
import json
import service

def create_listing():
    service.create_listing(args, identity)

def update_bed_bath_car():
    pass 

def prepare_payload(address,contacts,primary_agent):
    print('address',address)
    payload={
      "arguments": {
        "input": {
            "address": address,
            "contacts": [
                contacts
            ],
            "primaryAgent": primary_agent
        }
    },"identity":{
        "username": "Google_106600641818143500761",
        "claims": {
            "email": "ajeya@ljx.com.au",
            "custom:office": "corp",
            "custom:manager": "",
            "custom:team": "engineering",
            "cognito:groups": [
                "agents-group"
            ]
        }
    }
    }
    return payload["arguments"]["input"],payload["identity"]
def main(event, context):
    # service.get_listing('be96a009-2e1f-4aff-b7ba-8d6c8a24103a')
    wb = load_workbook(filename='RexImport.xlsx')
    ws = wb['Sheet3']

    for row in ws.iter_rows(min_row=2,min_col=1,max_row=ws.max_row,max_col=3):
        lst=[]
        for cell in row:
            print('cell',cell.row)
            lst.append(cell.value)
        print('lst',lst)
        if (lst[0]!=None and lst[1]!=None and lst[2]!=None ):
            args,identity=prepare_payload(json.loads(lst[0]),json.loads(lst[1]),json.loads(lst[2])["primaryAgent"])
            service.create_listing(args, identity)

        print('-------')

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
