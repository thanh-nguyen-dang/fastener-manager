#!/bin/bash

# Path to the script directory and root directory
SCRIPT_DIR="$(python -c 'import os, sys; print(os.path.abspath(os.path.dirname("$0")))')"
ROOT_DIR="$(python -c 'import os, sys; print(os.path.abspath(os.path.join("$SCRIPT_DIR", "..")))')"

# Function to import fasteners for a specific seller
import_fasteners() {
    SELLER_ID=$1
    CSV_FILE_PATH=$2

    # Check if the CSV file exists
    if [ ! -f "$CSV_FILE_PATH" ]; then
      echo "Error: CSV file not found at $CSV_FILE_PATH"
      exit 1
    fi

    # Send a POST request to ingest fasteners via CSV for the seller
    echo "Importing fasteners for Seller ID $SELLER_ID from file $CSV_FILE_PATH"
    curl -X POST "http://localhost:8000/fasteners/$SELLER_ID/" \
         -H "Content-Type: multipart/form-data" \
         -F "file=@$CSV_FILE_PATH"

    echo "Fasteners imported successfully for Seller ID $SELLER_ID from $CSV_FILE_PATH"
}

# Manually call the function for each seller

# Seller 1 -> seller-a.csv
import_fasteners "1" "$ROOT_DIR/sample_data/seller-a.csv"

# Seller 2 -> seller-b.csv
import_fasteners "2" "$ROOT_DIR/sample_data/seller-b.csv"
