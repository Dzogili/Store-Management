from applications.models import Product, ProductCategory, database, Category, OrderProduct, Order
from roleCheck import roleCheck
from flask import Flask, request, Response, jsonify
from applications.configuration import Configuration
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity
from json import dumps
from datetime import datetime

application = Flask ( __name__ )
application.config.from_object ( Configuration )

jwt = JWTManager ( application )


@application.route("/search", methods=["GET"])
@jwt_required()
@roleCheck("customer")
def search():
    product_name = request.args.get("name", "")
    product_category = request.args.get("category", "")

    results = (Product.query.join(ProductCategory, Product.id == ProductCategory.product_id)
               .join(Category, Category.id == ProductCategory.category_id).add_entity(Category)
               .filter(Product.product_name.like(f'%{product_name}%'), Category.category_name.like(f'%{product_category}%'))
               .all())

    products = []
    categories = []

    for result in results:
        if result[0] not in products:
            products.append(result[0])
        if result[1] not in categories:
            categories.append(result[1])

    products_json = []

    for prod in products:
        category_names = [category.category_name for category in prod.category]
        new_json_product = {
            "categories" : category_names,
            "id" : prod.id,
            "name" : prod.product_name,
            "price" : prod.product_price
        }
        products_json.append(new_json_product)

    return_json = {
        "categories" : [category.category_name for category in categories],
        "products" : products_json
    }

    return Response(dumps(return_json), status=200)


@application.route("/order", methods=["POST"])
@jwt_required()
@roleCheck("customer")
def order():
    products = request.json.get("requests", "")

    # provera da li je lista poslata
    if(len(products) == 0):
        return Response(dumps({"message": "Field requests is missing."}), status=400, mimetype='application/json')

    id_list = []
    quantity_list = []
    #provera da li postoji neki podatak da je id nenaveden
    for index, product in enumerate(products, start=0):
        product_id = product.get("id", "")
        if(product_id == ""):
            return Response(dumps({"message": f"Product id is missing for request number {index}."}), status=400, mimetype='application/json')
        id_list.append(product_id)

    for index, product in enumerate(products, start=0):
        product_quantity = product.get("quantity", "")
        if(product_quantity == ""):
            return Response(dumps({"message": f"Product quantity is missing for request number {index}."}), status=400, mimetype='application/json')
        quantity_list.append(product_quantity)

    for index, prod_id in enumerate(id_list, start=0):
        if(not(isinstance(prod_id, int) and prod_id > 0)):
            return Response(dumps({"message": f"Invalid product id for request number {index}."}), status=400, mimetype='application/json')

    for index, prod_quantity in enumerate(quantity_list, start=0):
        if(not(isinstance(prod_quantity, int) and prod_quantity > 0)):
            return Response(dumps({"message": f"Invalid product quantity for request number {index}."}), status=400, mimetype='application/json')

    total_price = 0
    for index, prod_id in enumerate(id_list, start=0):
        product_to_buy = Product.query.filter(Product.id == prod_id).first()
        if(product_to_buy is None):
            return Response(dumps({"message": f"Invalid product for request number {index}."}), status=400, mimetype='application/json')
        total_price = total_price + product_to_buy.product_price * float(quantity_list[index])

    # kreiranje oredera
    order = Order(
        order_status = "CREATED",
        total_price = total_price,
        time_created = datetime.now(),
        customer_email = get_jwt_identity()
    )
    database.session.add(order)
    database.session.commit()

    # kreiranje order-product
    for index, prod_id in enumerate(id_list, start=0):
        new_order_product = OrderProduct(
            order_id = order.id,
            product_id = prod_id,
            products_ordered = quantity_list[index]
        )
        database.session.add(new_order_product)

    database.session.commit()

    return Response(dumps({"id": order.id}), status=200)


@application.route("/delivered", methods=["POST"])
@jwt_required()
@roleCheck("customer")
def delivered():
    order_id = request.json.get("id", "")

    if(order_id == ""):
        return Response(dumps({"message": "Missing order id."}), status=400, mimetype='application/json')

    if(not(isinstance(order_id, int) and order_id > 0)):
        return Response(dumps({"message": "Invalid order id."}), status=400, mimetype='application/json')

    get_order = Order.query.filter(Order.id == order_id).first()
    if(get_order is None):
        return Response(dumps({"message": "Invalid order id."}), status=400, mimetype='application/json')
    if(get_order.order_status != "PENDING"):
        return Response(dumps({"message": "Invalid order id."}), status=400, mimetype='application/json')

    get_order.order_status = "COMPLETE"
    database.session.commit()

    return Response(status=200)


@application.route("/status", methods=["GET"])
@jwt_required()
@roleCheck("customer")
def status():

    customers_email = get_jwt_identity()

    table = Order.query.join(OrderProduct).join(Product).join(ProductCategory) \
        .filter(Order.customer_email == customers_email).all()

    all_orders = []

    for order in table:
        products_list = []
        for product in order.product:
            product_json = {
                "categories" : [category.category_name for category in product.category],
                "name" : product.product_name,
                "price" : product.product_price,
                "quantity" : OrderProduct.query.filter(OrderProduct.product_id == product.id, OrderProduct.order_id == order.id).first().products_ordered
            }
            products_list.append(product_json)
        order_json = {
            "products" : products_list,
            "price" : order.total_price,
            "status" : order.order_status,
            "timestamp" : order.time_created.isoformat()
        }
        all_orders.append(order_json)


    return Response(dumps({"orders" : all_orders}), status=200)



if ( __name__ == "__main__" ):
    database.init_app ( application )
    application.run ( debug = True,host='0.0.0.0', port = 5002)