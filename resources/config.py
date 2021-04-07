from flask import Response
import json 

def responseJson(messageIn, statusCode):
    return Response(
            response = json.dumps(messageIn, default=str), 
            status   = statusCode,
            mimetype = "application/json"
            )