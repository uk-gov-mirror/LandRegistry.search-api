#!/usr/bin/env bash
# Search API
### Local Quick Start (Outside Docker)

# Install the python libs that don't come out of the box if you need them
pip3 install -r requirements.txt
pip3 install -r requirements_test.txt
# For Flask CLI
export FLASK_APP=search_api/main.py
export FLASK_DEBUG=1
# For Python
export PYTHONUNBUFFERED=yes
# For gunicorn
export PORT=9798
# For app's config.py
export LOG_LEVEL=DEBUG
export COMMIT=LOCAL
export APP_NAME=search_api
export ADDRESS_API_URL='http://localhost:9997'

export SQL_HOST=localhost
export SQL_DATABASE=llc_register
export SQL_PASSWORD=postgres
export APP_SQL_USERNAME=postgres
export ALEMBIC_SQL_USERNAME=false
export SQL_USE_ALEMBIC_USER=false

py.test
python3 manage.py runserver
