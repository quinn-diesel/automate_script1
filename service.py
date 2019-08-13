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
from pyrex.api import listings, properties, users
from pyrex.client import RexClient
import traceback

CLIENT = RexClient(os.getenv("REX_USER_NAME"), os.getenv("REX_PASSWORD"))
l_api = listings.ListingsApi(CLIENT)
p_api = properties.PropertiesApi(CLIENT)
u_api = users.UsersApi(CLIENT)
CONTACTS_LAMBDA = os.getenv("CONTACTS_LAMBDA")
PROFILE_LAMBDA = os.getenv("PROFILE_LAMBDA")
AGENTS_LAMBDA = os.getenv("AGENTS_LAMBDA")
LISTINGS_TASKS_LAMBDA=os.getenv('LISTINGS_TASKS_LAMBDA')

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

            listing.teams = [agent["team"]]
        except:
            raise ValueError("Provided agent does not have an auth profile!")
    else:
        listing.teams = [get_team(identity)]
        listing.agent_usernames = [get_email(identity)]
    listing.save()
    sns_client.publish(
        TopicArn='arn:aws:sns:ap-southeast-2:529618128667:listing-created-dev',
        Message=json.dumps(
            {"listingId": listing.id, "fullAddress": listing.address.full_address}
        ),
    )
    return listing.to_json()


@views.property_details
def update_property_details(listing_id, property_details, identity):
    pd = PropertyDetails(**property_details)
    listing = Listing.get(listing_id)

    listing.property_details = pd
    listing.save()
    return pd


def update_stage(listing_id, identity):
    #getting all the stages,taskgroups,tasks
    call_service(
        LISTINGS_TASKS_LAMBDA, identity, "getCurrentStageTasks", {"listingId": listing_id}
    )

    #updating stage
    return call_service(
        LISTINGS_TASKS_LAMBDA, identity, "completeStage", {"listingId": listing_id}
    )['code']


def get_property_id(listing_id):
    """
    by taking agent listing id,returing rex property id
    form listing  address we are building rex compatable  address, with that address we are searching for rex property, if property found, returning that property id
    else  creating property and  returing new property id
    """
    listing = Listing.get(listing_id)
    rex_property_id = None
    try:
        full_address = listing.address.unit_number
        if full_address is None:
            full_address = ""

        if listing.address.address_low is not None:
            if listing.address.unit_number is not None:
                full_address += " /" + str(listing.address.address_low)
            else:
                full_address += str(listing.address.address_low)

        full_address += (
            listing.address.street_name
            + " "
            + listing.address.suburb
            + " "
            + listing.address.state
            + " "
            + listing.address.postcode
        )
        rex_property_id = p_api.get_property_id(full_address)
    except:
        traceback.print_exc()
    if rex_property_id is None:
        property = properties.Property(
            unit_number=listing.address.unit_number,
            street_number=listing.address.address_low,
            street_name=listing.address.street_name,
            suburb=listing.address.suburb,
            state=listing.address.state,
            postcode=listing.address.postcode,
        )
        rex_property_id = p_api.create(property)["_id"]
    return rex_property_id


def create_listing_in_rex(listing_id):
    """
    create listing in rex crm, returns newly created rex listing id
    :type listing_id:str
    """
    rex_property_id = get_property_id(listing_id)
    location_id = u_api.get_location_id()
    return l_api.create(rex_property_id, "residential_sale", location_id)


def create_agent_in_rex(email, ident, users_api):
    """
    if agent not found it will create, in dev env  this may not  work, because of rex users limit
    """
    agent_id = None
    agent = call_service(AGENTS_LAMBDA, ident, "getAgent", {"email": email})
    rex_agent = users_api.create_account_user(
        agent["email"], agent["firstName"], agent["lastName"], send_invite=False
    )
    if rex_agent["error"] == None:
        agent_id = rex_agent["id"]
        return agent_id
    return agent_id


def update_property_details_in_rex(rex_listing_id, identity, agents, bed, bath, car):
    first_agent_id = None
    second_agent_id = None
    if len(agents) >= 2:
        first_agent_id = u_api.get_agent_id_by_email(agents[0])
        second_agent_id = u_api.get_agent_id_by_email(agents[1])
        if first_agent_id == None:
            first_agent_id = create_agent_in_rex(agents[0], identity, u_api)
        if second_agent_id == None:
            second_agent_id = create_agent_in_rex(agents[1], identity, u_api)

    elif len(agents) == 1:
        first_agent_id = u_api.get_agent_id_by_email(agents[0])
        if first_agent_id == None:
            first_agent_id = create_agent_in_rex(agents[0], identity, u_api)
    l_api.set_listing_details(rex_listing_id, first_agent_id, second_agent_id) 
    print("added agent1-'{0}' and agent2-'{1}' to rex".format(u_api.get_agent_name(first_agent_id), u_api.get_agent_name(second_agent_id)))
    l_api.set_property_attributes(rex_listing_id, bed, bath, car)
    print("added bed-'{0}',bath-'{1}',car-'{2}' in rex".format(bed, bath, car))

def set_headline_and_body_to_rex(rex_listing_id,headline,body):
    return l_api.set_headline_and_body(rex_listing_id,headline,body)
