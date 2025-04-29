import logging
import json
import functions_framework
from flask import jsonify, make_response, request
from jsonschema import validate, ValidationError

# ——— Logger setup ———
logger = logging.getLogger('order_service')
logger.setLevel(logging.INFO)
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    ))
    logger.addHandler(h)


@functions_framework.http
def sales_event(request):

    logger.info("Received %s %s", request.method, request.path)
    if request.method != "POST":
        logger.warning("Only POST allowed")
        return make_response(jsonify({"error": "Use POST"}), 405)

    data = request.get_json(silent=True)
    if not data:
        logger.error("No JSON body")
        return make_response(jsonify({"error": "Invalid JSON"}), 400)
    
    # read schema file
    try:
        with open('schema.json', 'r') as f:
            schema = json.load(f)
    except FileNotFoundError:
        logger.exception("Error: 'schema.json' not found.")
        return make_response(jsonify({"error": "schema file not found"}), 400) 
    except json.JSONDecodeError:
        logger.exception("Error: Could not decode JSON from 'schema.json'.")
        return make_response(jsonify({"error": "couldn't decode the schema file"}))

    try:
        validate(instance=data, schema=schema)
        logger.info("Payload is valid against the schema.")
    except ValidationError as e:
        logger.exception(f"Payload is invalid: {e}")
        logger.exception(f"Error details: {e}")
        return make_response(jsonify({"error": "payload is invalid"}))
    
    logger.info("Payload processed successfully")
    return make_response(jsonify(data), 200)