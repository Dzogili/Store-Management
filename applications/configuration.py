from datetime import timedelta

class Configuration ( ):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@shopDatabase:3306/shop"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)