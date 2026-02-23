#!/bin/bash
# Script to initialize database with roles and users

cd "$(dirname "$0")/.."
python -m scripts.init_db
