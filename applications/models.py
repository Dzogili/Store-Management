# proizvod - kategorija ime cena
# statistika proizvoda - prodato ceka (polja klase proizvod)
# statistika kategorije proizvoda (deo proizvoda ili odvojena klasa??) - niz prodatih prozivoda date kategorije
# porudzbina
# dostava (odvojena klasa ili deo porudzbine kao enuma SENT RECIEVED
# pregled porudzbina

from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy ( )

class ProductCategory ( database.Model ):
    __tablename__ = "productcategory"

    product_id = database.Column(database.Integer, database.ForeignKey("product.id"), primary_key=True)
    category_id = database.Column(database.Integer, database.ForeignKey("category.id"), primary_key=True)


class OrderProduct (database.Model):
    __tablename__ = "orderproduct"

    order_id = database.Column(database.Integer, database.ForeignKey("order.id"), primary_key=True)
    product_id = database.Column(database.Integer, database.ForeignKey("product.id"), primary_key=True)
    products_ordered = database.Column(database.Integer, nullable=False)

class Order ( database.Model ):
    __tablename__ = "order"

    id = database.Column(database.Integer, primary_key=True)
    order_status = database.Column(database.String(256), nullable=False)
    total_price = database.Column(database.Double, nullable=False)
    time_created = database.Column(database.DateTime, nullable=False)
    customer_email = database.Column(database.String(256), nullable=False)

    product = database.relationship("Product", secondary=OrderProduct.__table__, back_populates="order")


class Category (database.Model):
    __tablename__ = "category"

    id = database.Column(database.Integer, primary_key=True)
    category_name = database.Column(database.String(256), unique=True)

    product = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="category")

#proizvod ima ime kategoriju cenu
class Product ( database.Model ):
    __tablename__ = "product"

    id = database.Column(database.Integer, primary_key=True)
    product_name = database.Column(database.String(256), nullable=False)
    product_price = database.Column(database.Double, nullable=False)

    order = database.relationship("Order", secondary=OrderProduct.__table__, back_populates="product")
    category = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="product")


