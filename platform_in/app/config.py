import os

basedir = os.path.abspath(os.path.dirname(__file__))

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

class Config(object):

    SECRET_KEY = os.environ.get("SECRET_KEY") or "super-secret-key"
    DEBUG = True
    CSRF_ENABLED = True

    SASL_UNAME = get_env_variable("SASL_UNAME")
    SASL_PASSWORD = get_env_variable("SASL_PASSWORD")
    KAFKA_BROKERS = get_env_variable("KAFKA_BROKERS")
    SECURITY_PROTOCOL = get_env_variable("SECURITY_PROTOCOL")
    SASL_MECHANISM = get_env_variable("SASL_MECHANISM")
    SCHEMA_REGISTRY_URL = get_env_variable("SCHEMA_REGISTRY_URL")

    ELASTIC_APM = {
        'SERVICE_NAME': get_env_variable("ELASTIC_SERVICE_NAME"),
        'SECRET_TOKEN': get_env_variable("ELASTIC_SECRET_TOKEN"),
        'SERVER_URL': get_env_variable("ELASTIC_SERVER_URL"),
        'DEBUG':True
    }

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY") or "prod-secret-key"

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    TESTING = False
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    #ELASTIC_APM['DEBUG']=True
    
class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = os.environ.get("SECRET_KEY") or "test-secret-key"


