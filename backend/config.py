import os

basedir = os.path.abspath(os.path.dirname(__file__))

ANALYSIS_SERVICE_URL = os.environ.get("ANALYSIS_SERVICE_URL")


class DefaultConfig:
    """
    Default Configuration
    """

    # Flask Configuration
    APP_NAME = os.environ.get("APP_NAME")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    PROPAGATE_EXCEPTIONS = True
    DEBUG = False
    TESTING = False

    # Config API documents
    API_TITLE = "Intelligent Resume Matching API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # App Environment
    APP_ENV = "local"

    # Logging
    DATE_FMT = "%Y-%m-%d %H:%M:%S"
    LOG_FILE_API = f"{basedir}/logs/api.log"

    # MongoDB configuration
    MONGO_URI = os.environ.get("MONGO_URL")

    # Analysis Service
    ANALYSIS_SERVICE_URL = os.environ.get("ANALYSIS_SERVICE_URL")

# Set default configuration
Config = DefaultConfig
