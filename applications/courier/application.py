from applications.models import database, Order
from roleCheck import roleCheck
from flask import Flask, request, Response, jsonify
from applications.configuration import Configuration
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from json import dumps

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/orders_to_deliver", methods=["GET"])
@jwt_required()
@roleCheck("courier")
def orders_to_deliver():

    # dohvatanje svih porudzbina koje nisu usle u fazu dostavljanja
    created_orders = Order.query.filter(Order.order_status == "CREATED").all()

    orders_to_deliver = []
    for order in created_orders:
        result = {
            "id": order.id,
            "email": order.customer_email
        }
        orders_to_deliver.append(result)

    return_string = {"orders": orders_to_deliver}
    return Response(dumps(return_string), status=200, mimetype='application/json')


@application.route("/pick_up_order", methods=["POST"])
@jwt_required()
@roleCheck("courier")
def pick_up_order():
    order_id = request.json.get("id", "")

    if(order_id == ""):
        return Response(dumps({"message": "Missing order id."}), status=400, mimetype='application/json')

    order_to_pick_up = Order.query.filter(Order.id == order_id).first()
    if((order_to_pick_up is None) or (order_to_pick_up.order_status != "CREATED")):
        return Response(dumps({"message": "Invalid order id."}), status=400, mimetype='application/json')

    order_to_pick_up.order_status = "PENDING"
    database.session.commit()

    return Response(status=200)


if ( __name__ == "__main__" ):
    database.init_app ( application )
    application.run ( debug = True,host='0.0.0.0', port = 5003)

