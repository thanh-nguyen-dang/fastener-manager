#!/bin/bash

# Send a GET request to list all fasteners, sorted by thread_size
curl -X GET "http://localhost:8000/fasteners/?sort=thread_size&filter=invalid_key:Steel" \
     -H "Accept: application/json"