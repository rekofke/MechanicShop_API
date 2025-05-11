class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:C%40ntget1n@127.0.0.1/mechanic_db'
    DEBUG = True
    CACHE_TYPE = "SimpleCache"

    class TestingConfig:
        SQLALCHEMY_DATABASE_URI = 'sqlite://testing.db'
        DEBUG = TrueCACHE_TYPE = 'SimpleCache'
    class ProductionConfig:
        pass