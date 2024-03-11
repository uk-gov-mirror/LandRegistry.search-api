# Search API

### Common Development Environment
This application is built to run on our common development environment (common dev-env), which you can read more about here: https://github.com/LandRegistry/common-dev-env

### Local Quick Start (Outside Docker)

```
./go

```

# The go script will run the app pointing to the following sql configurations:

```
export SQL_HOST=localhost
export SQL_DATABASE=llc_register
export SQL_PASSWORD=postgres
export APP_SQL_USERNAME=postgres
export ALEMBIC_SQL_USERNAME=false
export SQL_USE_ALEMBIC_USER=false

```

#### Available Endpoints:
`/local_land_charges` (GET)

#### Schema Versioning
Charge items are converted to a known version number using the llc-schema-dto module during the jsonification of request responses, so the schema version returned remains consistent.  The version to convert to is defined by SCHEMA_VERSION in the config.py file for the application.

## Alembic

### New Revisions

To create a new alembic revision to the database,

From console in _dev-env_:

```bash
vagrant ssh
```

```bash
manage search-api db revision
```

### Upgrading / Downgrading

To upgrade the database,

From console in _dev-env_:

```bash
vagrant ssh
```

```bash
docker-compose exec -T search-api /bin/bash -c "PGUSER=root PGPASSWORD=superroot SQL_USE_ALEMBIC_USER=yes SQL_PASSWORD=superroot python3 manage.py db upgrade"
```

To downgrade the database (one revision at a time),

From console in _dev-env_:

```bash
vagrant ssh
```

```bash
docker-compose exec -T search-api /bin/bash -c "PGUSER=root PGPASSWORD=superroot SQL_USE_ALEMBIC_USER=yes SQL_PASSWORD=superroot python3 manage.py db downgrade"
```

### Revision Creation Consistency Notes
1. Keep table names singular noun
2. Primary Keys are indexed automatically
3. Create foreign keys using sa.ForeignKey() notation for automatic naming


### Statutory Provisions updates
Statutory Provision updates will run when your development environment starts up, but if you need to manually run the statutory provisions updates use:

```docker exec -i search-api python3 manage.py update_stat_provs```


## Unit tests

The unit tests are contained in the unit_tests folder. [Pytest](http://docs.pytest.org/en/latest/) is used for unit testing. 

To run the unit tests if you are using the common dev-env use the following command:

```bash
docker-compose exec search-api make unittest
or, using the alias
unit-test search-api
```

or

```bash
docker-compose exec search-api make report="true" unittest
or, using the alias
unit-test search-api -r
```

# Linting

Linting is performed with [Flake8](http://flake8.pycqa.org/en/latest/). To run linting:
```bash
docker-compose exec search-api make lint
```

### Documentation

The API has been documented using swagger YAML files. 

The swagger files can be found under the [documentation](documentation/swagger.yaml) directory.

At present the documentation is not hooked into any viewer within the dev environment. To edit or view the documentation open the YAML file in swagger.io <http://editor.swagger.io>

## Updating Requirements

To update the requirements for this repo, you can use [pur](https://pypi.org/project/pur/) to find the latest versions for the respective dependencies. To make this happen, change directory (cd) into the desired repo and run each of these commands consecutively:
```
docker run --rm -it -v $PWD:/src python:3.9 bash
cd /src
pip install pip-tools
pip install pur
pur -r requirements.in
pur -r requirements_test.txt
pip-compile
exit
```
