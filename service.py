import json
import requests
import boto3
import json
import os
import uuid
from datetime import datetime
import logging
import string
import random
from models import Listing, PropertyDetails, Note, Feature, Address, Offer
from pycommon.cases import snake_case_keys, camel_case_keys
from pycommon.utils import random_letters_numbers, remove_empty_values
from pycommon.service import call_service
from pycommon.identity import get_team, is_admin_or_backoffice, get_email
from openpyxl import load_workbook
import views
CONTACTS_LAMBDA = os.getenv("CONTACTS_LAMBDA")
PROFILE_LAMBDA = os.getenv("PROFILE_LAMBDA")
sns_client = boto3.client("sns")
logger = logging.getLogger()

def create_listing(args, identity):

    listing = Listing(
        id=args.get("id") or str(uuid.uuid4()), reference=random_letters_numbers(8)
    )

    if args.get("address"):

        # get your object
        address_details = args.get("address")

        # pythonize js obj
        addr = snake_case_keys(remove_empty_values(address_details))

        # grab keys from the model
        keys = Address.get_attributes().keys()

        # dictionary comprehension to create final obj
        # aka this is making a constructor to match the keys from the model and
        # disregarding anything that doesn't match so there aren't problems
        # later
        listing.address = Address(**{k: v for k, v in addr.items() if k in keys})

        # make default property details
        listing.property_details = PropertyDetails(bedrooms=0, bathrooms=0, carparks=0)

    else:
        raise ValueError("Invalid input, no addressDetails!")

    if args.get("contact_id"):
        contact = call_service(
            CONTACTS_LAMBDA, identity, "getContact", {"id": args["contact_id"]}
        )

        listing.contacts = [remove_empty_values(contact)]

    elif args.get("contacts"):
        contacts = []
        for contact in args["contacts"]:
            result = call_service(
                CONTACTS_LAMBDA,
                identity,
                "createContact",
                {"input": camel_case_keys(contact)},
            )
            contacts.append(remove_empty_values(result))
        listing.contacts = contacts
    else:
        raise ValueError("Invalid input, no contactId or contacts were provided")
    if args.get("primary_agent"):
        listing.agent_usernames = [args["primary_agent"]]

        try:
            logger.debug(
                "Fetching agent team from auth profile for %s", args["primary_agent"]
            )
            agent = call_service(
                PROFILE_LAMBDA, identity, "getUser", {"email": args["primary_agent"]}
            )
            print('agent',agent)

            listing.teams = [agent["team"]]
        except:
            raise ValueError("Provided agent does not have an auth profile!")
    else:
        listing.teams = [get_team(identity)]
        listing.agent_usernames = [get_email(identity)]
    print("json", listing.to_json())
    print("listing_id", listing.id)
    print("fullAddress", listing.address.full_address)
    listing.save()
    # sns_client.publish(
    #     TopicArn=os.environ["LISTING_CREATED_TOPIC_ARN"],
    #     Message=json.dumps(
    #         {"listingId": listing.id, "fullAddress": listing.address.full_address}
    #     ),
    # )
    # get_listing(listing.id)
    return listing.to_json()

@views.property_details
def update_property_details(listing_id, property_details, identity):
    print('listing_id',listing_id)
    print('property_details',property_details)
    pd = PropertyDetails(**property_details)
    listing = Listing.get(listing_id)
    listing.property_details = pd
    listing.save()
    return pd,listing.to_json()

def update_stage(listing_id, old_previous_stage):
    """
    :type listing_id:str
    :param listing_id: listing id
    :type old_previous_stage : str
    :param old_previous_stage : from which stage this stage request came from
    """
    next_stage = {
        "OPPORTUNITY": "PRECAMPAIGN",
        "PRECAMPAIGN": "INCAMPAIGN",
        "INCAMPAIGN": "EXCHANGE",
        "EXCHANGE": "SETTLEMENT",
    }
    listing = Listing.get(listing_id)
    if old_previous_stage != "SETTLEMENT":
        listing.stage_code = next_stage[old_previous_stage.upper()]
        listing.save()


    return listing.stage_code


def get_listing(listing_id):
    listing = Listing.get(listing_id)
    print(listing.to_json())
