import os
import argparse

from flask import Flask, request, jsonify, Request
from jsonschema import ValidationError, validate

import messages.route

app = Flask(__name__)

class BadRequest(Exception):
    def __init__(self, message, see_also="http://developers.domain.tld/doc/api/"):
        self.message = message
        self.see_also = see_also
    def to_response(self):
        error = {
            'error': "Bad Request",
            'message': self.message }
        if self.see_also:
            error['see_also'] = self.see_also

        response = jsonify(error)
        response.status_code = 400
        response.mimetype = 'application/json'
        return response

class customRequest(Request):
    #Redefining on_json_loading_failed to return a json style error
    # and not a HTML looking error
    def on_json_loading_failed(self, e):
        raise BadRequest('Invalid JSON Request.')

# now, we need to tell Flask to use our Request object
app.request_class = customRequest

@app.errorhandler(ValidationError)
def on_validation_error(e):
    # Raising badRequest here doesnt seem to work as we got out of the try catch
    # already? I guess we just cant raise exceptions from here.

    #TODO make the error more than just e.message... We could also give the context

    return BadRequest(e.message).to_response()

@app.errorhandler(BadRequest)
def handlerBadRequest(e):
    return e.to_response()

@app.route('/messages/route', methods=['POST'])
def route_messages():
    json = request.get_json() #A non-valid JSON would trigger a 400 auto formatted by flask.

    validate(json, messages.route.schema)

    try:
        messages.route.check_phones(json['recipients'])
    except messages.route.InvalidPhone as e:
        raise BadRequest(e.message)

    #TODO maybe remove fictitious 555 numbers?
    #http://en.wikipedia.org/wiki/555_(telephone_number)

    #TODO quote protect the message... Not really at risk here but if we change our mind.

    return messages.route.respond_post(json['message'], json['recipients'])

@app.route('/', methods=['GET'])
def route_root():
    return "Hello World"


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest='host', action='store', default="127.0.0.1")
    parser.add_argument('-d','--debug', dest='debug', action='store_true', default=False)
    parser.add_argument('-p','--port', dest='port', action='store', type=int, default=5000)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse()

    app.debug = args.debug

    #TODO plug into WSGI? Apache?
    app.run(host=args.host, port=args.port )