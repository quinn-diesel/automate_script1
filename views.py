from functools import wraps


def _to_property_details_view(pd):
    return {
        "appraisals": pd.appraisals,
        "bedrooms": pd.bedrooms,
        "bathrooms": pd.bathrooms,
        "carparks": pd.carparks,
        "externalSqm": pd.external_sqm,
        "internalSqm": pd.internal_sqm,
        "land_size": pd.land_size,
        "propertyType": pd.property_type,
        "zoning": pd.zoning,
    }


def _to_agents_view(agents):
    return agents


def _to_listing_note_view(note):
    return {"createdAt": note.created_at, "content": note.content}


def _to_listing_view(listing):
    address = listing["address"]
    if address and "location" in address:
        address["lat"] = address["location"]["lat"]
        address["lon"] = address["location"]["lon"]
    return listing


def _to_listing_feature_view(feature):
    return {"name": feature.name, "value": feature.value}


def _listed_date(feature):
    return {"listingId": feature.id, "listedDate": feature.listed_date}


def agents(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return _to_agents_view(f(*args, **kwargs))

    return wrapper


def features(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return {"items": [_to_listing_feature_view(f) for f in f(*args, **kwargs)]}

    return wrapper


def note(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return _to_listing_note_view(f(*args, **kwargs))

    return wrapper


def listings(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return [_to_listing_view(lst) for lst in f(*args, **kwargs)]

    return wrapper


def listingsResult(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        return {
            "items": [_to_listing_view(lst) for lst in result.get("items", [])],
            "total": result.get("total", 0),
            "from": result.get("from"),
            "size": result.get("size"),
        }

    return wrapper


def listing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return _to_listing_view(f(*args, **kwargs))

    return wrapper


def property_details(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        pd = f(*args, **kwargs)
        return _to_property_details_view(pd)

    return wrapper


def contacts(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper


def offer(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)

    return wrapper