#!/bin/bash

# Script for running the add/update stat provs in pre-prod/prod
cd /opt/landregistry/applications/llc-search-api/
source virtualenv/bin/activate
source settings.conf
source deploy.conf
pip install -r source/requirements.txt
cd source

python3 manage.py update_stat_provs