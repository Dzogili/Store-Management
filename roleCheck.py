from functools import wraps
from json import dumps

from flask import Response
from flask_jwt_extended import get_jwt


def roleCheck (role):
    def innerRole ( function ):
        @wraps ( function )
        def decorator ( *arguments, **keywordArguments):
            claims = get_jwt()       #u koliko uspe dohvastamo payload
            if (("roles" in claims ) and (role in claims["roles"])):   #proveravamo roles i da li se proslednja uloga nalazi medju prosledjenim ulogama
                return function(*arguments, **keywordArguments)     #u koliko pozivamo tu neku funkciju sa tim odredjenim argumentima!
            else:
                return Response(dumps({"msg": "Missing Authorization Header"}), status=401, mimetype="application/json")

        return decorator

    return innerRole
