class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:C%40ntget1n@127.0.0.1/mechanic_db'
    DEBUG = True
    CACHE_TYPE = "SimpleCache"

    class TestingConfig:
        pass
    class ProductionConfig:
        pass