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
CONTACTS_LAMBDA = os.getenv("CONTACTS_LAMBDA")
sns_client = boto3.client("sns")



def main(event, context):
    listing_id='26b3d4dc-5efd-4cfd-ac15-2fa4be75f819'
    listing = Listing.get(listing_id)
    print(listing.to_json())

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
