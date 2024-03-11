# Set the base image to the s2i image
FROM docker-registry/stp/stp-s2i-python-extended:3.9

# Development environment values
# These values are not the same as our production environment
ENV APP_NAME="search-api" \
    SQL_HOST="postgres-13" \
    LOG_LEVEL="DEBUG" \
    COMMIT="LOCAL" \
    SQL_DATABASE="llc_register" \
    SQL_PASSWORD="llc_register_password" \
    APP_SQL_USERNAME="llc_register_user" \
    ALEMBIC_SQL_USERNAME="root" \
    SQL_USE_ALEMBIC_USER="false" \
    _DEPLOY_SQL_PASSWORD="superroot" \
    ADDRESS_API_URL="http://address-api:8080" \
    INDEX_MAP_API_URL="http://index-map-api:8080" \
    INDEX_MAP_TIMEOUT=10 \
    MAX_HEALTH_CASCADE=6 \
    FEEDER_SQL_USERNAME="llc_register_feeder" \
    FEEDER_SQL_PASSWORD="llc_register_feeder_password" \
    AUTHENTICATION_API_URL="http://authentication-api:8080/v2.0" \
    AUTHENTICATION_API_ROOT="http://authentication-api:8080" \
    LA_API_URL="http://local-authority-api:8080" \
    ACCTEST_SQL_USERNAME="llc_register_acceptance_test_user" \
    ACCTEST_SQL_PASSWORD="llc_register_acceptance_test_password" \
    REPORT_API_SQL_USERNAME="llc_register_report_user" \
    REPORT_API_SQL_PASSWORD="llc_register_password" \
    SQLALCHEMY_POOL_RECYCLE="3300" \
    APP_MODULE='search_api.main:app' \
    FLASK_APP='search_api.main' \
    GUNICORN_ARGS='--reload' \
    WEB_CONCURRENCY='2' \
    DEFAULT_TIMEOUT="30" \
    ALLOW_SENSITIVE_CHARGE_RETRIEVE_USERS="LLC Clients;HM Land Registry" \
    PYTHONPATH=/src

# Switch from s2i's non-root user back to root for the following commmands
USER root

# Create a user that matches dev-env runner's host user
# And ensure they have access to the jar folder at runtime
ARG OUTSIDE_UID
ARG OUTSIDE_GID
RUN groupadd --force --gid $OUTSIDE_GID containergroup && \
    useradd --uid $OUTSIDE_UID --gid $OUTSIDE_GID containeruser

ADD requirements_test.txt requirements_test.txt
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && \
    pip3 install -r requirements_test.txt

# Set the user back to a non-root user like the s2i run script expects
# When creating files inside the docker container, this will also prevent the files being owned
# by the root user, which would cause issues if running on a Linux host machine
USER containeruser

CMD ["/usr/libexec/s2i/run"]
