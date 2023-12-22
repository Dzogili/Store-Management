from flask import Flask
from configuration import Configuration
from models import database, Product, Category, Order, OrderProduct, ProductCategory
from flask_migrate import Migrate

application = Flask ( __name__ )
application.config.from_object ( Configuration )
migrate = Migrate(application, database)

database.init_app(application)

@application.shell_context_processor
def make_shell_context():

    return dict(application=application, database=database, Product=Product, Category=Category, Order=Order, OrderProduct=OrderProduct,
                ProductCategory=ProductCategory)


if ( __name__ == "__main__" ):

    application.run()
