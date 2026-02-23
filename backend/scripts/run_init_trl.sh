#!/bin/bash
echo "Running TRL Definitions Initialization Script..."
cd "$(dirname "$0")/.."
python -m scripts.init_trl
