import os

from flask import Flask, request, jsonify, Request
from jsonschema import ValidationError, validate

import messages.route

app = Flask(__name__)
app.debug = True

class BadRequest(Exception):
    def __init__(self, message, see_also="http://developers.domain.tld/doc/api/"):
        self.message = message
        self.see_also = see_also
    def to_response(self):
        error = {'message': self.message }
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
    return BadRequest(e.message).to_response()

@app.errorhandler(BadRequest)
def handlerBadRequest(e):
    return e.to_response()

@app.route('/messages/route', methods=['POST'])
def route_messages():
    json = request.get_json() #A non-valid JSON would trigger a 400 auto formatted by flask.

    if json == False:
        raise BadRequest("Request was empty")

    validate(json, messages.route.schema)

    #TODO maybe remove fictitious 555 numbers?
    #http://en.wikipedia.org/wiki/555_(telephone_number)

    return messages.route.respond_post(json['message'], json['recipients'])

if __name__ == '__main__':
    app.run()