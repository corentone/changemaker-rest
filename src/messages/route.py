import os
import sys
from flask import jsonify

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
            "maxItems": 5000,
            "items": {
                "type": "string",
                #NANP http://en.wikipedia.org/wiki/North_American_Numbering_Plan
                "pattern": "^\\(?([2-9][0-9]{2})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$"
                },
            # TODO Maybe we should not do the check here but instead after we've converted them to the same format?
            "uniqueItems": True
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