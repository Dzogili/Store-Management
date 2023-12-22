import csv

from sqlalchemy.sql import functions

from applications.models import Product, ProductCategory, database, Category, OrderProduct, Order
from roleCheck import roleCheck
from flask import Flask, request, Response, jsonify
from applications.configuration import Configuration
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity
from sqlalchemy import and_, func
from json import dumps
import io

application = Flask ( __name__ )
application.config.from_object ( Configuration )

jwt = JWTManager ( application )

@application.route ( "/update", methods = ["POST"] )
@jwt_required()
@roleCheck("owner")
def update():
    file = request.files.get('file', '')
    if file == '':
        return Response(dumps({"message": "Field file is missing."}), status=400, mimetype='application/json')

    content = request.files["file"].stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    reader_list = []

    for index, row in enumerate(reader):
        reader_list.append(row)

        if(len(row) != 3):
            return Response(dumps({"message": f"Incorrect number of values on line {index}."}), status=400, mimetype='application/json')

        is_float = True
        try:
            float(row[2])
        except:
            is_float = False

        if(not is_float or float(row[2]) <= 0):
            return Response(dumps({"message": f"Incorrect price on line {index}."}), status=400, mimetype='application/json')
        if (Product.query.filter(Product.product_name == row[1]).first() is not None):
            return Response(dumps({"message": f"Product {row[1]} already exists."}), status=400, mimetype='application/json')

    for row in reader_list:
        categories = row[0].split("|")

        product = Product(
            product_name = row[1],
            product_price = float(row[2])
        )
        database.session.add(product)
        database.session.commit()

        for category in categories:
            if(Category.query.filter(Category.category_name == category).first() is None):
                new_category = Category(
                    category_name = category
                )
                database.session.add(new_category)
                database.session.commit()

            product_category = ProductCategory(
                product_id = product.id,
                category_id = Category.query.filter(Category.category_name == category).first().id
            )
            database.session.add(product_category)
            database.session.commit()

    return Response(status=200)


@application.route ("/product_statistics", methods = ["GET"])
@jwt_required()
@roleCheck("owner")
def product_statistics():

    products = Product.query.join(OrderProduct).group_by(Product.id).all()

    all_results = []

    for product in products:
        products_sold = (OrderProduct.query.join(Order)
                         .filter(Order.order_status == "COMPLETE", OrderProduct.product_id == product.id)
                         .with_entities(func.sum(OrderProduct.products_ordered)).first())

        products_waiting = (OrderProduct.query.join(Order)
                            .filter(Order.order_status != "COMPLETE", OrderProduct.product_id == product.id)
                            .with_entities(func.sum(OrderProduct.products_ordered)).first())

        total_products_waiting = 0.0
        if(products_waiting[0] is not None):
            total_products_waiting = products_waiting[0]

        total_products_sold = 0.0
        if(products_sold[0] is not None):
            total_products_sold = products_sold[0]

        result = {
            "name" : product.product_name,
            "sold" : int(total_products_sold),
            "waiting" : int(total_products_waiting)
        }

        all_results.append(result)

#    return_string = all_results

    return jsonify({"statistics" : all_results})


@application.route ("/category_statistics", methods = ["GET"])
@jwt_required()
@roleCheck("owner")
def category_statistics():

    category_list_complete = Category.query.join(ProductCategory).join(Product).join(OrderProduct).join(Order)\
        .filter(Order.order_status == "COMPLETE")\
        .group_by(Category.id).order_by(func.sum(OrderProduct.products_ordered).desc(), Category.category_name).all()

    category_list_uncompleted = Category.query.filter().order_by(Category.category_name).all()

    result_string = [category.category_name for category in category_list_complete]

    for category in category_list_uncompleted:
        if(category.category_name not in result_string):
            result_string.append(category.category_name)

    return jsonify({"statistics" : result_string})


if ( __name__ == "__main__" ):
    database.init_app ( application )
    application.run ( debug = True, host='0.0.0.0', port = 5001)