#!/bin/bash

mkdir -p ./lambda_layer/requests/python
mkdir -p ./lambda_layer/pytz/python

pip install requests==2.23.0 --target ./lambda_layer/requests/python
pip install pytz==2020.1 --target ./lambda_layer/pytz/python