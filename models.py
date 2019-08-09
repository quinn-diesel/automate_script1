import os

from datetime import datetime

from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    BooleanAttribute,
    MapAttribute,
    ListAttribute,
)


from pycommon.models import BaseModel, BaseMeta
from pycommon.cases import snake_case_keys, camel_case_keys
from pycommon.utils import remove_empty_values


class Location(MapAttribute):
    lat = NumberAttribute(null=False)
    lon = NumberAttribute(null=False)


class Address(MapAttribute):
    id = UnicodeAttribute()
    lot_number = UnicodeAttribute(null=True, attr_name="lotNumber")
    unit_number = UnicodeAttribute(null=True, attr_name="unitNumber")
    address_low = UnicodeAttribute(attr_name="addressLow")
    address_high = UnicodeAttribute(null=True, attr_name="addressHigh")
    street_name = UnicodeAttribute(attr_name="streetName")
    street_type = UnicodeAttribute(null=True, attr_name="streetType")
    street_suffix = UnicodeAttribute(null=True, attr_name="streetSuffix")
    suburb = UnicodeAttribute()
    postcode = UnicodeAttribute()
    state = UnicodeAttribute(null=True)
    full_address = UnicodeAttribute(null=True, attr_name="fullAddress")
    address1 = UnicodeAttribute(null=True)
    address2 = UnicodeAttribute(null=True)
    location = Location(null=False)
    country = UnicodeAttribute(null=True)
    country_code = UnicodeAttribute(null=True, attr_name="countryCode")


class Note(MapAttribute):
    content = UnicodeAttribute(null=True)
    created_at = NumberAttribute(
        attr_name="createdAt", default=int(datetime.now().strftime("%s"))
    )
    created_by = UnicodeAttribute(attr_name="createdBy")


class Feature(MapAttribute):
    name = UnicodeAttribute()
    value = UnicodeAttribute()


class PropertyDetails(MapAttribute):
    appraisals = ListAttribute(default=[])
    bedrooms = NumberAttribute()
    bathrooms = NumberAttribute()
    carparks = NumberAttribute()
    external_sqm = NumberAttribute(null=True, attr_name="externalSqm")
    internal_sqm = NumberAttribute(null=True, attr_name="internalSqm")
    land_size = NumberAttribute(null=True, attr_name="landSize")
    property_type = UnicodeAttribute(null=True, attr_name="propertyType")
    zoning = UnicodeAttribute(null=True)



class Offer(MapAttribute):

    @staticmethod
    def from_dict(data):
        data = snake_case_keys(remove_empty_values(data))
        keys = Offer.get_attributes().keys()
        return Offer(**{k: v for k, v in data.items() if k in keys})

    # Returns offer as a dict with keys in camel case
    def as_cc_dict(self):
        return camel_case_keys(remove_empty_values(self.as_dict()))

    id = UnicodeAttribute(attr_name="id")
    offered_amount = NumberAttribute(attr_name="offeredAmount")
    offered_date = NumberAttribute(attr_name="offeredDate")
    offered_by_first_name = UnicodeAttribute(attr_name="offeredByFirstName")
    offered_by_last_name = UnicodeAttribute(attr_name="offeredByLastName")
    offered_by_phone = UnicodeAttribute(attr_name="offeredByPhone")
    offered_by_email = UnicodeAttribute(attr_name="offeredByEmaiiil")
    notified_vendor_date = NumberAttribute(attr_name="notifiedVendorDate",  null=True)
    # TODO: This should be an enum
    notified_vendor_via = UnicodeAttribute(attr_name="notifiedVendorVia",  null=True)
    vendor_response_type = UnicodeAttribute(attr_name="vendorResponseType",  null=True)
    vendor_response_date = NumberAttribute(attr_name="vendorResponseDate",  null=True)
    vendor_response_reason = UnicodeAttribute(attr_name="vendorResponseReason", null=True)
    created_at = NumberAttribute(
        null=True, attr_name="createdAt", default=int(datetime.now().strftime("%s"))
    )
    created_by = UnicodeAttribute(null=True, attr_name="createdBy")
    updated_at = NumberAttribute(
        null=True, attr_name="updatedAt", default=int(datetime.now().strftime("%s"))
    )
    updated_by = UnicodeAttribute(null=True, attr_name="updatedBy")


class Listing(BaseModel):
    class Meta(BaseMeta):
        table_name = os.getenv("LISTINGS_TABLE_NAME")

    id = UnicodeAttribute(hash_key=True)
    address = Address()
    contacts = ListAttribute(of=MapAttribute, default=[])
    note = Note(null=True)
    features = ListAttribute(of=Feature, default=[])
    offers = ListAttribute(of=Offer, default=[])
    is_deleted = BooleanAttribute(default=False, attr_name="isDeleted")
    reference = UnicodeAttribute()
    stage_code = UnicodeAttribute(
        null=False, attr_name="stageCode", default="OPPORTUNITY"
    )
    listed_date = NumberAttribute(attr_name="listedDate", null=True)
    created_at = NumberAttribute(
        null=True, attr_name="createdAt", default=int(datetime.now().strftime("%s"))
    )
    created_by = UnicodeAttribute(null=True, attr_name="createdBy")
    updated_at = NumberAttribute(
        null=True, attr_name="updatedAt", default=int(datetime.now().strftime("%s"))
    )
    updated_by = UnicodeAttribute(null=True, attr_name="updatedBy")
    teams = ListAttribute(default=[])
    office = UnicodeAttribute(null=True)
    agent_usernames = ListAttribute(default=[], attr_name="agentEmails")
    property_details = PropertyDetails(null=True, attr_name="propertyDetails")

    def save(self):
        self.updated_at = int(datetime.now().strftime("%s"))
        self.created_at = int(datetime.now().strftime("%s"))
        super(Listing, self).save()

    def to_json(self):
        return dict(self)
