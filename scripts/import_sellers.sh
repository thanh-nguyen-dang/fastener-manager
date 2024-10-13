#!/bin/bash

# Path to the script directory and root directory
SCRIPT_DIR="$(python -c "import os, sys; print(os.path.abspath(os.path.dirname('$0')))")"
ROOT_DIR="$(python -c "import os, sys; print(os.path.abspath(os.path.join('$SCRIPT_DIR', '..')))")"

# Path to the JSON file located in the sample_data directory in the root folder
JSON_FILE_PATH="$ROOT_DIR/sample_data/sellers.json"

# Check if the file exists
if [ ! -f "$JSON_FILE_PATH" ]; then
  echo "Error: JSON file not found at $JSON_FILE_PATH"
  exit 1
fi

# Send a POST request to add new sellers from JSON
curl -X POST "http://localhost:8000/sellers" \
     -H "Content-Type: application/json" \
     -d @"$JSON_FILE_PATH"

echo "Sellers imported successfully from $JSON_FILE_PATH"
