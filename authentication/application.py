from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User, UserRole
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity
from sqlalchemy import and_
from json import dumps
import re


application = Flask ( __name__ )
application.config.from_object ( Configuration )

jwt = JWTManager ( application )

@application.route ( "/register_courier", methods = ["POST"] )
def register_courier():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0
    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0

    if (forenameEmpty):
        return Response(dumps({"message": "Field forename is missing."}), status=400, mimetype='application/json')
    if (surnameEmpty):
        return Response(dumps({"message": "Field surname is missing."}), status=400, mimetype='application/json')
    if (emailEmpty):
        return Response(dumps({"message": "Field email is missing."}), status=400, mimetype='application/json')
    if (passwordEmpty):
        return Response(dumps({"message": "Field password is missing."}), status=400, mimetype='application/json')

    #regular expression - regex
    if not re.match(r'^[a-zA-Z0-9._-]+@([a-zA-Z0-9]{2,}\.)+[a-zA-Z0-9]{2,}$', email):
        return Response(dumps({"message": "Invalid email."}), status=400, mimetype='application/json')

    if not (256 >= len(password) >= 8):
        return Response(dumps({"message": "Invalid password."}), status=400, mimetype='application/json')

    if(User.query.filter(User.email == email).first() is not None):
        return Response(dumps({"message": "Email already exists."}), status=400, mimetype='application/json')

    user = User(email=email, password=password, forename=forename, surname=surname)
    database.session.add(user)
    database.session.commit()

    userRole = UserRole(userId=user.id, roleId=2)
    database.session.add(userRole)
    database.session.commit()

    return Response(status= 200)


@application.route("/register_customer", methods=["POST"])
def register_customer():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0
    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0

    if (forenameEmpty):
        return Response(dumps({"message": "Field forename is missing."}), status=400, mimetype='application/json')
    if (surnameEmpty):
        return Response(dumps({"message": "Field surname is missing."}), status=400, mimetype='application/json')
    if (emailEmpty):
        return Response(dumps({"message": "Field email is missing."}), status=400, mimetype='application/json')
    if (passwordEmpty):
        return Response(dumps({"message": "Field password is missing."}), status=400, mimetype='application/json')

    # regular expression - regex
    if not re.match(r'^[a-zA-Z0-9._-]+@([a-zA-Z0-9]{2,}\.)+[a-zA-Z0-9]{2,}$', email):
        return Response(dumps({"message": "Invalid email."}), status=400, mimetype='application/json')

    if not (256 >= len(password) >= 8):
        return Response(dumps({"message": "Invalid password."}), status=400, mimetype='application/json')

    if (User.query.filter(User.email == email).first() is not None):
        return Response(dumps({"message": "Email already exists."}), status=400, mimetype='application/json')

    user = User(email=email, password=password, forename=forename, surname=surname)
    database.session.add(user)
    database.session.commit()

    userRole = UserRole(userId=user.id, roleId=3)
    database.session.add(userRole)
    database.session.commit()

    return Response(status=200)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    if (emailEmpty):
        return Response(dumps({"message": "Field email is missing."}), status=400, mimetype='application/json')
    if (passwordEmpty):
        return Response(dumps({"message": "Field password is missing."}), status=400, mimetype='application/json')

    #email validation
    if not re.match(r'^[a-zA-Z0-9._-]+@([a-zA-Z0-9]{2,}\.)+[a-zA-Z0-9]{2,}$', email):
        return Response(dumps({"message": "Invalid email."}), status=400, mimetype='application/json')

    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if (user is None):
        return Response(dumps({"message": "Invalid credentials."}), status=400, mimetype='application/json')

    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        #"password": user.password,
        "roles": [role.name for role in user.roles]
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)

    # return Response ( accessToken, status = 200 );
    return jsonify(accessToken=accessToken)


@application.route("/delete", methods=["POST"])
@jwt_required()
def delete():
    user_email = get_jwt_identity()

    if (User.query.filter(User.email == user_email).first() is None):
        return Response(dumps({"message": "Unknown user."}), status=400, mimetype='application/json')

    user = User.query.filter(User.email == user_email).first()

    UserRole.query.filter(UserRole.userId == user.id).delete()

    User.query.filter(User.email == user_email).delete()
    database.session.commit()

    #automatski vraca poruku msg: Missing Authorization Header (postman)
    return Response(status=200)

if ( __name__ == "__main__" ):
    database.init_app ( application )
    application.run ( debug = True, host= "0.0.0.0", port = 5000)