import os

VERSION = '/api/v1.0.0'
BASE_API_URL = 'http://worktest.weelabel.com'


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    SECRET_KEY = "iq[qiBYIQ[C82OJNu392d3932HDNJL32kf2q"
class DevelopmentConfig(Config):
    DEBUG = True
    # TODO mysql配置
    DB_USER = 'root'
    DB_HOST = '127.0.0.1'
    DB_PWD = '248536'
    DB_PORT = 3306
    DB_NAME = 'zzn_test'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%d/%s?charset=utf8mb4' % (
    DB_USER, DB_PWD, DB_HOST, DB_PORT, DB_NAME)


class TestingConfig(Config):
    pass

class ProductionConfig(Config):
    # TODO mysql配置
    pass



# TODO 切换配置 default = ProductionConfig 正式服务
config = {
    'Development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}