import os
import sys
from flask import jsonify
import re

scriptpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(scriptpath, "..", "lib"))

from router import Router, default_relays

schema = {
    "type": "object",
    "properties": {
        "message": {
            "type": "string"
        },
        "recipients": {
            "type": "array",
            "minItems": 1,
            #doing the check manually since the field is returned when we get an error :(
            #"maxItems": 5000,
            "items": {
                "type": "string",
                #NANP http://en.wikipedia.org/wiki/North_American_Numbering_Plan
                #"pattern": "^\\(?([2-9][0-9]{2})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$"
                },
            # TODO Maybe we should not do the check here but instead after we've converted them to the same format?
            #"uniqueItems": True
        }
    },
    "required": ["message", "recipients"],
    "additionalProperties": False
}


def respond_post(message, phones):

    content = {
        "message": message,
        "routes": []
        }

    r = Router(default_relays())
    relays = r.optimal(len(phones))

    for relay in relays:
        route = { "ip": relay.ip }
        route['recipients'] = phones[-relay.throughput:]
        del phones[-relay.throughput:] #Maybe save the numbers?
        content['routes'].append(route)

    assert(not phones)

    response = jsonify(content)
    response.mimetype = 'application/json'
    return response

class InvalidPhone(Exception):
    def __init__(self, message):
        self.message = message

def allUnique(x):
    seen = set()
    return not any(i in seen or seen.add(i) for i in x)

pattern = re.compile('^(\\+1 ?)?\\(?([2-9][0-9]{2})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')

def check_phones(phones):
    if len(phones) > 5000:
        raise InvalidPhone("'recipients' array is too long.")

    # This check adds a lot of complexity as it goes over N...
    # ... but necessary if we want to avoid duplicate

    for i in range(len(phones)):
        m = pattern.search(phones[i])
        if not m:
            raise InvalidPhone("Invalid value: '"+phones[i]+"'. Must respect pattern '^(\\+1 ?)?\\(?([2-9][0-9]{2})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$'")

        phones[i] = str(m.group(2)) + str(m.group(3)) + str(m.group(4))

    if not allUnique(phones):
        # We could make this part of the loop?
        raise InvalidPhone("Values of 'recipients' must be unique")

