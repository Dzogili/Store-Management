from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database, Role, UserRole, User
from sqlalchemy_utils import database_exists, create_database

application = Flask ( __name__ )
application.config.from_object ( Configuration )

migrateObject = Migrate ( application, database )

if __name__ == '__main__':
    done = False

    while not done:
        try:
            if ( not database_exists ( application.config["SQLALCHEMY_DATABASE_URI"] ) ):
                create_database ( application.config["SQLALCHEMY_DATABASE_URI"] )

            database.init_app ( application )

            with application.app_context ( ) as context:
                init ( )
                migrate ( message = "Production migration" )
                upgrade ( )

                database.session.add ( Role (name = "owner"))
                database.session.add(Role(name="courier"))
                database.session.add (Role (name = "customer"))
                database.session.commit ( )

                owner = User (
                        email = "onlymoney@gmail.com",
                        password = "evenmoremoney",
                        forename = "Scrooge",
                        surname = "McDuck"
                )

                database.session.add(owner)
                database.session.commit()

                userRole = UserRole (
                        userId = owner.id,
                        roleId = 1
                )
                database.session.add(userRole)
                database.session.commit()

                done = True
        except Exception:
            pass